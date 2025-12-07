"""
Unified Theme Manager for Unified Theming Application.

This module implements the UnifiedThemeManager which orchestrates
theme application across all handlers and manages the overall process.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from ..handlers.base import BaseHandler
from ..handlers.flatpak_handler import FlatpakHandler
from ..handlers.gnome_shell_handler import GnomeShellHandler
from ..handlers.gtk_handler import GTKHandler
from ..handlers.qt_handler import QtHandler
from ..handlers.snap_handler import SnapHandler
from ..parsers.json_tokens import JSONTokenParser
from ..renderers import GnomeShellRenderer, GTKRenderer, QtRenderer
from ..tokens.defaults import create_dark_tokens, create_light_tokens
from ..tokens.schema import UniversalTokenSchema
from ..utils.logging_config import get_logger
from .config import ConfigManager
from .exceptions import (
    RollbackError,
    ThemeNotFoundError,
)
from .parser import UnifiedThemeParser
from .types import (
    ApplicationResult,
    HandlerResult,
    PlannedChange,
    PlanResult,
    ThemeData,
    ThemeInfo,
    Toolkit,
    ValidationResult,
)

logger = get_logger(__name__)


class UnifiedThemeManager:
    """
    Central orchestrator for all theme operations.

    This class coordinates all theme-related operations across different toolkits,
    manages the backup/restore process, and aggregates results from different handlers.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the theme manager.

        Args:
            config_path: Path for configuration and backups
        """
        self.config_manager = ConfigManager(config_path)
        self.parser = UnifiedThemeParser()

        # Initialize handlers
        self.handlers: Dict[str, BaseHandler] = {
            "gtk": GTKHandler(),
            "qt": QtHandler(),
            "gnome_shell": GnomeShellHandler(),
            "flatpak": FlatpakHandler(),
            "snap": SnapHandler(),
        }
        self._token_parser = JSONTokenParser()

        logger.info("UnifiedThemeManager initialized with all handlers")

    def discover_themes(self) -> Dict[str, ThemeInfo]:
        """
        Discover all available themes on the system.

        Returns:
            Dictionary mapping theme names to ThemeInfo objects
        """
        logger.info("Discovering themes")
        themes = self.parser.discover_themes()
        logger.info(f"Discovered {len(themes)} themes")
        return themes

    def apply_theme(
        self, theme_name: str, targets: Optional[List[str]] = None
    ) -> ApplicationResult:
        """
        Apply a theme to specified targets.

        This is the main entry point for theme application. It orchestrates
        the entire process including backup, validation, application, and
        result aggregation.

        Args:
            theme_name: Name of theme to apply
            targets: List of targets to apply to (e.g., ['gtk', 'qt'])
                    If None, applies to all available targets

        Returns:
            ApplicationResult with detailed results from each handler

        Raises:
            ThemeNotFoundError: If theme doesn't exist
            ThemeApplicationError: If theme application fails critically
        """
        logger.info(f"Applying theme '{theme_name}' to targets: {targets or 'all'}")

        # Validate theme exists and get theme info
        themes = self.discover_themes()
        if theme_name not in themes:
            raise ThemeNotFoundError(
                theme_name, searched_paths=list(self.parser.theme_directories)
            )

        theme_info = themes[theme_name]

        # Determine which handlers to use
        if targets is None:
            handlers_to_use = self.handlers
        else:
            handlers_to_use = {
                name: handler
                for name, handler in self.handlers.items()
                if name in targets
            }

        # Before applying, create a backup of the current state
        backup_id = None
        try:
            backup_id = self.config_manager.backup_current_state()
            logger.debug(f"Configuration backed up as: {backup_id}")
        except Exception as e:
            logger.error(f"Failed to create backup before theme application: {e}")
            # Continue anyway, but mark this in the result
            backup_id = None

        # Prepare theme data for each toolkit
        theme_results = {}

        # Apply theme through each handler
        critical_failures = 0
        total_handlers = len(handlers_to_use)

        for handler_name, handler in handlers_to_use.items():
            try:
                # Check if handler is available
                if not handler.is_available():
                    logger.info(f"Handler {handler_name} not available, skipping")
                    result = HandlerResult(
                        handler_name=handler_name,
                        toolkit=handler.toolkit,
                        success=False,
                        message="Handler not available",
                        details="Toolkit not installed on system",
                    )
                    theme_results[handler_name] = result
                    continue

                # Validate compatibility
                theme_data = self._prepare_theme_data(theme_info, handler.toolkit)
                validation_result = handler.validate_compatibility(theme_data)

                if validation_result.has_errors():
                    logger.warning(
                        f"Validation errors for {handler_name}: {[msg.message for msg in validation_result.messages]}"
                    )

                # Apply the theme
                success = handler.apply_theme(theme_data)

                result = HandlerResult(
                    handler_name=handler_name,
                    toolkit=handler.toolkit,
                    success=success,
                    message="Applied successfully" if success else "Application failed",
                    details=None,
                    warnings=[
                        msg.message
                        for msg in validation_result.messages
                        if msg.level.name == "WARNING"
                    ],
                )

                theme_results[handler_name] = result

                if not success:
                    logger.error(f"Failed to apply theme to {handler_name}")
                    critical_failures += 1
                else:
                    logger.debug(f"Successfully applied theme to {handler_name}")

            except Exception as e:
                logger.error(f"Error applying theme with {handler_name} handler: {e}")

                result = HandlerResult(
                    handler_name=handler_name,
                    toolkit=handler.toolkit,
                    success=False,
                    message="Application failed",
                    details=str(e),
                )

                theme_results[handler_name] = result
                critical_failures += 1

        # Determine overall success
        success_ratio = (
            (total_handlers - critical_failures) / total_handlers
            if total_handlers > 0
            else 1.0
        )
        overall_success = (
            success_ratio > 0.5
        )  # Consider successful if >50% of handlers succeeded

        # If there were critical failures, consider rolling back
        if critical_failures > 0 and overall_success is False and backup_id:
            logger.warning("Critical failures detected, considering rollback")
            # In a real implementation, you might want to ask user if they want rollback
            # For now, we'll just log it
            # TODO: Implement user confirmation for rollback
            try:
                # Rollback to previous state
                rollback_success = self.config_manager.restore_backup(backup_id)
                if rollback_success:
                    logger.info(
                        "Configuration rolled back to previous state after failures"
                    )
                else:
                    logger.error("Failed to rollback configuration after failures")
            except RollbackError as e:
                logger.error(f"Rollback failed: {e}")

        # Create and return the application result
        application_result = ApplicationResult(
            theme_name=theme_name,
            overall_success=overall_success,
            handler_results=theme_results,
            backup_id=backup_id,
        )

        logger.info(
            f"Theme application completed with overall success: {overall_success}"
        )
        return application_result

    def apply_theme_from_tokens(
        self, token_path: Path, targets: Optional[List[str]] = None
    ) -> ApplicationResult:
        """
        Apply a theme using a token file instead of a discovered theme.

        Args:
            token_path: Path to JSON token file
            targets: Handlers to target (None means all available)

        Returns:
            ApplicationResult capturing per-handler outcomes
        """
        tokens = self._load_tokens(token_path)
        logger.info(
            f"Applying tokens from {token_path} (theme '{tokens.name}') "
            f"to targets: {targets or 'all'}"
        )

        if targets is None:
            handlers_to_use = self.handlers
        else:
            handlers_to_use = {
                name: handler
                for name, handler in self.handlers.items()
                if name in targets
            }

        backup_id = None
        try:
            backup_id = self.config_manager.backup_current_state()
        except Exception as e:
            logger.error(f"Failed to create backup before token application: {e}")

        handler_results: Dict[str, HandlerResult] = {}
        critical_failures = 0
        total_handlers = len(handlers_to_use)

        for handler_name, handler in handlers_to_use.items():
            try:
                if not handler.is_available():
                    handler_results[handler_name] = HandlerResult(
                        handler_name=handler_name,
                        toolkit=handler.toolkit,
                        success=False,
                        message="Handler not available",
                        details="Toolkit not installed on system",
                    )
                    continue

                if not hasattr(handler, "apply_from_tokens"):
                    handler_results[handler_name] = HandlerResult(
                        handler_name=handler_name,
                        toolkit=handler.toolkit,
                        success=False,
                        message="Handler does not support token application",
                    )
                    critical_failures += 1
                    continue

                success = handler.apply_from_tokens(tokens)  # type: ignore[attr-defined]

                handler_results[handler_name] = HandlerResult(
                    handler_name=handler_name,
                    toolkit=handler.toolkit,
                    success=success,
                    message="Applied successfully" if success else "Application failed",
                )

                if not success:
                    critical_failures += 1

            except Exception as e:
                handler_results[handler_name] = HandlerResult(
                    handler_name=handler_name,
                    toolkit=handler.toolkit,
                    success=False,
                    message="Application failed",
                    details=str(e),
                )
                critical_failures += 1

        success_ratio = (
            (total_handlers - critical_failures) / total_handlers
            if total_handlers > 0
            else 1.0
        )
        overall_success = success_ratio > 0.5

        return ApplicationResult(
            theme_name=tokens.name,
            overall_success=overall_success,
            handler_results=handler_results,
            backup_id=backup_id,
        )

    def plan_changes(
        self, theme_name: str, targets: Optional[List[str]] = None
    ) -> PlanResult:
        """
        Plan theme changes without applying them (dry-run mode).

        This method performs all validation and planning steps that would
        occur during theme application, but does not modify any files.

        Args:
            theme_name: Name of theme to plan
            targets: List of targets to plan for (e.g., ['gtk', 'qt'])
                    If None, plans for all available targets

        Returns:
            PlanResult with all planned changes

        Raises:
            ThemeNotFoundError: If theme doesn't exist
        """
        logger.info(f"Planning theme '{theme_name}' for targets: {targets or 'all'}")

        # Validate theme exists and get theme info
        themes = self.discover_themes()
        if theme_name not in themes:
            raise ThemeNotFoundError(
                theme_name, searched_paths=list(self.parser.theme_directories)
            )

        theme_info = themes[theme_name]

        # Determine which handlers to use
        if targets is None:
            handlers_to_use = self.handlers
        else:
            handlers_to_use = {
                name: handler
                for name, handler in self.handlers.items()
                if name in targets
            }

        # Get handler availability
        available_handlers = {
            name: handler.is_available() for name, handler in handlers_to_use.items()
        }

        # Validate theme
        validation_result = self.parser.validate_theme(theme_info.path)

        # Collect planned changes from each handler
        all_planned_changes: List[PlannedChange] = []
        warnings: List[str] = []

        for handler_name, handler in handlers_to_use.items():
            try:
                # Check if handler is available
                if not handler.is_available():
                    logger.info(f"Handler {handler_name} not available, skipping")
                    warnings.append(
                        f"Handler {handler_name} is not available (toolkit not installed)"
                    )
                    continue

                # Prepare theme data for this handler
                theme_data = self._prepare_theme_data(theme_info, handler.toolkit)

                # Get planned changes from handler
                planned_changes = handler.plan_theme(theme_data)
                all_planned_changes.extend(planned_changes)

                logger.debug(
                    f"Handler {handler_name} would make {len(planned_changes)} changes"
                )

            except Exception as e:
                logger.error(f"Error planning changes for {handler_name}: {e}")
                warnings.append(f"Error planning {handler_name}: {str(e)}")

        # Create and return the plan result
        plan_result = PlanResult(
            theme_name=theme_name,
            planned_changes=all_planned_changes,
            validation_result=validation_result,
            available_handlers=available_handlers,
            warnings=warnings,
        )

        logger.info(
            f"Planning completed: {len(all_planned_changes)} changes would be made to {plan_result.estimated_files_affected} files"
        )
        return plan_result

    def convert_theme_to_tokens(self, theme_name: str) -> UniversalTokenSchema:
        """
        Convert a discovered theme into the universal token schema.

        Args:
            theme_name: Name of a theme available to the parser

        Returns:
            UniversalTokenSchema populated from the theme where possible
        """
        logger.info(f"Converting theme '{theme_name}' to tokens")
        themes = self.discover_themes()
        if theme_name not in themes:
            raise ThemeNotFoundError(
                theme_name, searched_paths=list(self.parser.theme_directories)
            )

        theme_info = themes[theme_name]
        bg_color = self._parse_color(theme_info.get_color("theme_bg_color"))
        variant = "dark" if bg_color and bg_color.luminance() < 0.5 else "light"
        tokens = (
            create_dark_tokens(name=theme_info.name)
            if variant == "dark"
            else create_light_tokens(name=theme_info.name)
        )
        tokens.source = "converted-theme"

        mappings = {
            "theme_bg_color": ("surfaces", "primary"),
            "theme_base_color": ("surfaces", "secondary"),
            "theme_fg_color": ("content", "primary"),
            "theme_text_color": ("content", "secondary"),
            "theme_selected_bg_color": ("accents", "primary"),
            "theme_selected_fg_color": ("content", "inverse"),
            "link_color": ("content", "link"),
            "visited_link_color": ("content", "link_visited"),
            "success_color": ("accents", "success"),
            "warning_color": ("accents", "warning"),
            "error_color": ("accents", "error"),
            "borders": ("borders", "default"),
        }

        for color_key, (group, attribute) in mappings.items():
            color_value = self._parse_color(theme_info.get_color(color_key))
            if color_value:
                getattr(tokens, group).__setattr__(attribute, color_value)
                if group == "surfaces" and attribute == "secondary":
                    tokens.surfaces.tertiary = color_value
                    tokens.surfaces.elevated = color_value
                if group == "borders":
                    tokens.borders.subtle = color_value
                    tokens.borders.strong = color_value

        return tokens

    def render_tokens(
        self, token_path: Path, target: str, output_dir: Path
    ) -> List[Path]:
        """
        Render a token file to configuration files for a target toolkit.

        Args:
            token_path: Path to JSON tokens
            target: Target renderer ('gtk', 'qt', 'gnome-shell')
            output_dir: Directory to write rendered files into

        Returns:
            List of written file paths
        """
        tokens = self._load_tokens(token_path)
        renderer = self._get_renderer_for_target(target)
        rendered = renderer.render(tokens)

        written_paths: List[Path] = []
        for rel_path, content in rendered.files.items():
            destination = output_dir / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content)
            written_paths.append(destination)

        return written_paths

    def _prepare_theme_data(
        self, theme_info: ThemeInfo, target_toolkit: Toolkit
    ) -> ThemeData:
        """
        Prepare theme data for a specific toolkit.

        Args:
            theme_info: Source theme information
            target_toolkit: Target toolkit for the theme data

        Returns:
            Prepared ThemeData for the target toolkit
        """
        # For now, just return the theme data as is
        # In a full implementation, we would transform the data
        # based on the target toolkit's requirements
        return ThemeData(
            name=theme_info.name,
            toolkit=target_toolkit,
            colors=theme_info.colors,
            additional_data=theme_info.metadata,
        )

    def get_current_themes(self) -> Dict[str, str]:
        """
        Get currently applied themes for each toolkit.

        Returns:
            Dictionary mapping toolkit names to current theme names
        """
        current_themes = {}

        for handler_name, handler in self.handlers.items():
            if handler.is_available():
                try:
                    current_theme = handler.get_current_theme()
                    current_themes[handler_name] = current_theme
                except Exception as e:
                    logger.warning(
                        f"Could not get current theme for {handler_name}: {e}"
                    )
                    current_themes[handler_name] = "unknown"
            else:
                current_themes[handler_name] = "not_available"

        return current_themes

    def preview_theme(self, theme_name: str, apps: Optional[List[str]] = None) -> None:
        """
        Preview a theme without applying it system-wide.

        Args:
            theme_name: Theme to preview
            apps: List of applications to launch for preview
        """
        logger.info(
            f"Previewing theme '{theme_name}' for apps: {apps or 'default preview apps'}"
        )
        # TODO: Implement theme preview functionality
        # This would involve launching temporary instances of preview applications
        # with the specified theme without affecting the system configuration
        logger.warning("Preview functionality not yet implemented")

    def rollback(self, backup_id: Optional[str] = None) -> bool:
        """
        Rollback to a previous configuration.

        Args:
            backup_id: ID of backup to restore. If None, restores most recent backup

        Returns:
            True if rollback successful, False otherwise
        """
        logger.info(f"Initiating rollback, backup ID: {backup_id}")

        try:
            # If no backup ID specified, get the most recent one
            if backup_id is None:
                backups = self.config_manager.get_backups()
                if not backups:
                    logger.error("No backups available for rollback")
                    return False
                backup_id = backups[0].backup_id

            # Perform the rollback
            success = self.config_manager.restore_backup(backup_id)

            if success:
                logger.info(f"Successfully rolled back to backup: {backup_id}")
            else:
                logger.error(f"Failed to rollback to backup: {backup_id}")

            return success

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def validate_theme(self, theme_name: str) -> ValidationResult:
        """
        Validate a theme for compatibility and correctness.

        Args:
            theme_name: Name of theme to validate

        Returns:
            ValidationResult with validation messages
        """
        logger.info(f"Validating theme: {theme_name}")

        themes = self.discover_themes()
        if theme_name not in themes:
            raise ThemeNotFoundError(
                theme_name, searched_paths=list(self.parser.theme_directories)
            )

        theme_info = themes[theme_name]

        # Use the parser's validation
        validation_result = self.parser.validate_theme(theme_info.path)

        return validation_result

    def get_available_handlers(self) -> Dict[str, bool]:
        """
        Get availability status of all handlers.

        Returns:
            Dictionary mapping handler names to availability status
        """
        availability = {}

        for handler_name, handler in self.handlers.items():
            availability[handler_name] = handler.is_available()

        return availability

    def load_theme(self, theme_name: str) -> ThemeInfo:
        """
        Load theme information by name.

        Args:
            theme_name: Name of theme to load

        Returns:
            ThemeInfo object for the theme

        Raises:
            ThemeNotFoundError: If theme doesn't exist
        """
        logger.info(f"Loading theme: {theme_name}")

        themes = self.discover_themes()
        if theme_name not in themes:
            raise ThemeNotFoundError(
                theme_name, searched_paths=list(self.parser.theme_directories)
            )

        return themes[theme_name]

    def get_theme_info(self, theme_name: str) -> ThemeInfo:
        """
        Get theme information by name.

        Args:
            theme_name: Name of theme

        Returns:
            ThemeInfo object for the theme

        Raises:
            ThemeNotFoundError: If theme doesn't exist
        """
        return self.load_theme(theme_name)

    def _load_tokens(self, token_path: Path) -> UniversalTokenSchema:
        """Load tokens from a JSON file using the token parser."""
        return self._token_parser.parse(token_path)

    def _parse_color(self, value: Optional[str]):
        """Try to parse a hex string to Color, returning None on failure."""
        if value is None:
            return None
        try:
            from ..color.spaces import Color

            return Color.from_hex(value)
        except Exception:
            return None

    def tokens_to_json(self, tokens: UniversalTokenSchema) -> str:
        """Serialize token schema to a JSON string."""

        def color_hex(color):
            return color.to_hex() if color else None

        data = {
            "name": tokens.name,
            "variant": tokens.variant,
            "surface": {
                "primary": color_hex(tokens.surfaces.primary),
                "secondary": color_hex(tokens.surfaces.secondary),
                "tertiary": color_hex(tokens.surfaces.tertiary),
                "elevated": color_hex(tokens.surfaces.elevated),
                "inverse": color_hex(tokens.surfaces.inverse),
            },
            "content": {
                "primary": color_hex(tokens.content.primary),
                "secondary": color_hex(tokens.content.secondary),
                "tertiary": color_hex(tokens.content.tertiary),
                "inverse": color_hex(tokens.content.inverse),
                "link": color_hex(tokens.content.link),
                "link_visited": color_hex(tokens.content.link_visited),
            },
            "accent": {
                "primary": color_hex(tokens.accents.primary),
                "primary_container": color_hex(tokens.accents.primary_container),
                "secondary": color_hex(tokens.accents.secondary),
                "success": color_hex(tokens.accents.success),
                "warning": color_hex(tokens.accents.warning),
                "error": color_hex(tokens.accents.error),
            },
            "state": {
                "hover_overlay": tokens.states.hover_overlay,
                "pressed_overlay": tokens.states.pressed_overlay,
                "focus_ring": (
                    color_hex(tokens.states.focus_ring)
                    if tokens.states.focus_ring
                    else None
                ),
                "disabled_opacity": tokens.states.disabled_opacity,
            },
            "border": {
                "subtle": color_hex(tokens.borders.subtle),
                "default": color_hex(tokens.borders.default),
                "strong": color_hex(tokens.borders.strong),
            },
            "source": tokens.source,
        }
        return json.dumps(data, indent=2)

    def _get_renderer_for_target(self, target: str):
        """Return renderer instance for target string."""
        normalized = target.lower()
        if normalized in {"gtk", "gtk3", "gtk4", "libadwaita"}:
            return GTKRenderer()
        if normalized in {"qt", "qt5", "qt6"}:
            return QtRenderer()
        if normalized in {"gnome-shell", "gnome_shell", "shell"}:
            return GnomeShellRenderer()
        raise ValueError(f"Unsupported render target: {target}")
