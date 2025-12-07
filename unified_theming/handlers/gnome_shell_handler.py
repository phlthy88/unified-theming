"""
GNOME Shell Handler for Unified Theming Application.

This module implements the handler for GNOME Shell theming, managing
shell themes through gsettings and the User Theme extension.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from ..core.exceptions import ThemeApplicationError
from ..core.types import (
    HandlerResult,
    PlannedChange,
    ThemeData,
    Toolkit,
    ValidationResult,
)
from ..renderers.gnome_shell import GnomeShellRenderer
from ..tokens.schema import UniversalTokenSchema
from ..utils.file import read_file_with_fallback, write_file_with_backup
from ..utils.logging_config import get_logger
from .base import BaseHandler

logger = get_logger(__name__)


class GnomeShellHandler(BaseHandler):
    """
    Handler for GNOME Shell theming.

    This handler manages theme application for GNOME Shell by:
    1. Checking for User Theme extension availability
    2. Applying shell themes via GSettings
    3. Generating custom shell CSS when needed
    4. Managing shell theme configurations
    """

    # GNOME Shell theme directories
    USER_SHELL_THEMES_DIR = Path.home() / ".local/share/themes"
    SYSTEM_SHELL_THEMES_DIR = Path("/usr/share/themes")
    GNOME_SHELL_EXTENSIONS_DIR = Path.home() / ".local/share/gnome-shell/extensions"

    # User Theme extension UUID
    USER_THEME_EXTENSION_UUID = "user-theme@gnome-shell-extensions.gcampax.github.com"

    # GSettings schema for shell theme
    SHELL_THEME_SCHEMA = "org.gnome.shell.extensions.user-theme"
    SHELL_THEME_KEY = "name"

    # Mapping from GTK color variables to GNOME Shell equivalents
    GTK_TO_SHELL_MAPPING = {
        "theme_bg_color": "panel_bg_color",
        "theme_fg_color": "panel_fg_color",
        "theme_base_color": "dialog_bg_color",
        "theme_text_color": "dialog_fg_color",
        "theme_selected_bg_color": "selected_bg_color",
        "theme_selected_fg_color": "selected_fg_color",
        "borders": "panel_border_color",
        "success_color": "success_color",
        "warning_color": "warning_color",
        "error_color": "error_color",
    }

    def __init__(self):
        """Initialize the GNOME Shell handler."""
        super().__init__(Toolkit.GNOME_SHELL)
        self.config_dir = Path.home() / ".config"
        self.shell_config_dir = self.config_dir / "gnome-shell"
        self._user_theme_available: Optional[bool] = None
        self.renderer = GnomeShellRenderer()

    def apply_from_tokens(self, tokens: UniversalTokenSchema) -> bool:
        """
        Apply theme from universal tokens using GnomeShellRenderer.

        Args:
            tokens: Universal token schema to apply

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Applying theme '{tokens.name}' from tokens to GNOME Shell")

        try:
            rendered = self.renderer.render(tokens)

            for rel_path, content in rendered.files.items():
                target = self.config_dir / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                if not write_file_with_backup(target, content):
                    logger.error(f"Failed to write {target}")
                    return False
                logger.debug(f"Wrote configuration to: {target}")

            return True

        except Exception as e:
            logger.error(f"Error applying GNOME Shell theme from tokens: {e}")
            raise ThemeApplicationError(
                f"Failed to apply theme '{tokens.name}' from tokens: {str(e)}",
                toolkit="gnome-shell",
                recoverable=True,
            )

    def apply_theme(self, theme_data: ThemeData) -> bool:
        """
        Apply theme to GNOME Shell.

        Args:
            theme_data: Theme data to apply

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Applying theme '{theme_data.name}' to GNOME Shell")

        try:
            success = True

            # Check if User Theme extension is available
            if not self._is_user_theme_extension_enabled():
                logger.warning(
                    "User Theme extension not enabled, attempting to apply "
                    "shell theme via alternative method"
                )
                # Try to apply theme without extension (limited support)
                return self._apply_shell_theme_fallback(theme_data)

            # Apply shell theme via GSettings
            if not self._apply_shell_theme_gsettings(theme_data.name):
                logger.warning(
                    f"Could not apply shell theme: {theme_data.name} (extension may not be installed)"
                )
                success = False

            # Generate and apply custom shell CSS if colors are provided
            if theme_data.colors:
                if not self._apply_shell_css(theme_data):
                    logger.warning(
                        f"Failed to apply custom shell CSS for: {theme_data.name}"
                    )
                    # Don't fail entirely if CSS generation fails

            return success

        except Exception as e:
            logger.error(f"Error applying GNOME Shell theme: {e}")
            raise ThemeApplicationError(
                f"Failed to apply theme '{theme_data.name}' to GNOME Shell: {str(e)}",
                toolkit="gnome-shell",
                recoverable=True,
            )

    def _apply_shell_theme_gsettings(self, theme_name: str) -> bool:
        """
        Apply shell theme via GSettings.

        Args:
            theme_name: Name of the shell theme to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(
                [
                    "gsettings",
                    "set",
                    self.SHELL_THEME_SCHEMA,
                    self.SHELL_THEME_KEY,
                    theme_name,
                ],
                check=True,
                capture_output=True,
            )

            logger.debug(f"GNOME Shell theme set to: {theme_name}")
            return True

        except subprocess.CalledProcessError as e:
            logger.warning(f"GSettings failed to set shell theme: {e}")
            return False
        except FileNotFoundError:
            logger.warning("gsettings command not found, cannot apply shell theme")
            return False
        except Exception as e:
            logger.warning(f"Error applying shell theme via GSettings: {e}")
            return False

    def _apply_shell_theme_fallback(self, theme_data: ThemeData) -> bool:
        """
        Apply shell theme using fallback method (without User Theme extension).

        This method generates custom shell CSS and places it in the appropriate
        location for GNOME Shell to pick up.

        Args:
            theme_data: Theme data to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate shell CSS from GTK colors
            css_content = self._generate_shell_css(theme_data)

            # Ensure config directory exists
            self.shell_config_dir.mkdir(parents=True, exist_ok=True)

            # Write CSS to GNOME Shell config
            css_file = self.shell_config_dir / "gnome-shell.css"
            success = write_file_with_backup(css_file, css_content)

            if success:
                logger.debug(f"Shell CSS written to: {css_file}")
                logger.info(
                    "Shell CSS applied. Note: Full theme support requires "
                    "the User Theme extension."
                )
            else:
                logger.error(f"Failed to write shell CSS to: {css_file}")

            return success

        except Exception as e:
            logger.error(f"Error applying shell theme fallback: {e}")
            return False

    def _apply_shell_css(self, theme_data: ThemeData) -> bool:
        """
        Generate and apply custom shell CSS based on theme colors.

        Args:
            theme_data: Theme data with color information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if theme has a gnome-shell directory
            if "theme_path" in theme_data.additional_data:
                theme_path = Path(theme_data.additional_data["theme_path"])
                shell_css_path = theme_path / "gnome-shell" / "gnome-shell.css"

                if shell_css_path.exists():
                    # Theme already has shell CSS, no need to generate
                    logger.debug(
                        f"Theme {theme_data.name} has native shell CSS, "
                        "using existing stylesheet"
                    )
                    return True

            # Generate custom CSS from colors
            css_content = self._generate_shell_css(theme_data)

            # Ensure config directory exists
            self.shell_config_dir.mkdir(parents=True, exist_ok=True)

            # Write CSS file
            css_file = self.shell_config_dir / "gnome-shell-custom.css"
            success = write_file_with_backup(css_file, css_content)

            if success:
                logger.debug(f"Custom shell CSS written to: {css_file}")

            return success

        except Exception as e:
            logger.error(f"Error generating shell CSS: {e}")
            return False

    def _generate_shell_css(self, theme_data: ThemeData) -> str:
        """
        Generate CSS for GNOME Shell theming.

        Args:
            theme_data: Theme data with color information

        Returns:
            Generated CSS content as string
        """
        css_parts = [
            "/* Generated by Unified Theming App */",
            f"/* Theme: {theme_data.name} */",
            f"/* Timestamp: {__import__('datetime').datetime.now()} */",
            "",
            "/* Color Variables */",
        ]

        # Map GTK colors to shell color variables
        shell_colors: Dict[str, str] = {}
        for gtk_color, shell_color in self.GTK_TO_SHELL_MAPPING.items():
            if gtk_color in theme_data.colors:
                shell_colors[shell_color] = theme_data.colors[gtk_color]

        # Add color definitions
        for color_name, color_value in shell_colors.items():
            css_parts.append(f"@define-color {color_name} {color_value};")

        css_parts.extend(["", "/* Panel Styling */"])

        # Generate panel styles if we have the colors
        if "panel_bg_color" in shell_colors:
            css_parts.extend(
                [
                    "#panel {",
                    f"  background-color: {shell_colors['panel_bg_color']};",
                ]
            )
            if "panel_fg_color" in shell_colors:
                css_parts.append(f"  color: {shell_colors['panel_fg_color']};")
            if "panel_border_color" in shell_colors:
                css_parts.append(
                    f"  border-bottom: 1px solid {shell_colors['panel_border_color']};"
                )
            css_parts.append("}")

        # Generate overview styles
        if "dialog_bg_color" in shell_colors:
            css_parts.extend(
                [
                    "",
                    "/* Overview Styling */",
                    ".workspace-background {",
                    f"  background-color: {shell_colors['dialog_bg_color']};",
                    "}",
                ]
            )

        # Generate selection styles
        if "selected_bg_color" in shell_colors:
            css_parts.extend(
                [
                    "",
                    "/* Selection Styling */",
                    ".selected, :focus {",
                    f"  background-color: {shell_colors['selected_bg_color']};",
                ]
            )
            if "selected_fg_color" in shell_colors:
                css_parts.append(f"  color: {shell_colors['selected_fg_color']};")
            css_parts.append("}")

        # Generate popup menu styles
        if "dialog_bg_color" in shell_colors:
            css_parts.extend(
                [
                    "",
                    "/* Popup Menu Styling */",
                    ".popup-menu-content {",
                    f"  background-color: {shell_colors['dialog_bg_color']};",
                ]
            )
            if "dialog_fg_color" in shell_colors:
                css_parts.append(f"  color: {shell_colors['dialog_fg_color']};")
            css_parts.append("}")

        return "\n".join(css_parts)

    def _is_user_theme_extension_enabled(self) -> bool:
        """
        Check if the User Theme extension is enabled.

        Returns:
            True if User Theme extension is enabled, False otherwise
        """
        if self._user_theme_available is not None:
            return self._user_theme_available

        try:
            # Check if extension is in enabled extensions list
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.shell", "enabled-extensions"],
                capture_output=True,
                text=True,
                check=True,
            )

            enabled_extensions = result.stdout.strip()
            self._user_theme_available = (
                self.USER_THEME_EXTENSION_UUID in enabled_extensions
            )

            logger.debug(f"User Theme extension enabled: {self._user_theme_available}")
            return self._user_theme_available

        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.debug("Could not check User Theme extension status")
            self._user_theme_available = False
            return False

    def get_current_theme(self) -> str:
        """
        Get currently applied GNOME Shell theme name.

        Returns:
            Name of currently applied shell theme
        """
        try:
            result = subprocess.run(
                ["gsettings", "get", self.SHELL_THEME_SCHEMA, self.SHELL_THEME_KEY],
                capture_output=True,
                text=True,
                check=True,
            )

            # Extract theme name from gsettings output (format: "'ThemeName'")
            theme_name = result.stdout.strip().strip("'\"")
            return theme_name if theme_name else "default"

        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.debug("Could not get current shell theme, GSettings not available")
            return "default"

    def validate_compatibility(self, theme_data: ThemeData) -> ValidationResult:
        """
        Check if theme is compatible with GNOME Shell.

        Args:
            theme_data: Theme data to validate

        Returns:
            ValidationResult with validation messages
        """
        result = ValidationResult(valid=True)

        # Check if theme has GNOME Shell support
        if theme_data.toolkit != Toolkit.GNOME_SHELL:
            # Check if theme has gnome-shell directory
            if "theme_path" in theme_data.additional_data:
                theme_path = Path(theme_data.additional_data["theme_path"])
                if not (theme_path / "gnome-shell").exists():
                    result.add_warning(
                        f"Theme '{theme_data.name}' has no gnome-shell directory, "
                        "will generate CSS from GTK colors",
                        component="gnome_shell_handler",
                    )

        # Check for User Theme extension
        if not self._is_user_theme_extension_enabled():
            result.add_warning(
                "User Theme extension is not enabled. Shell theme support "
                "will be limited. Enable it via GNOME Extensions app.",
                component="gnome_shell_handler",
            )

        # Check for required color variables
        if not theme_data.colors:
            result.add_warning(
                f"Theme '{theme_data.name}' has no color definitions, "
                "shell styling may not be applied correctly",
                component="gnome_shell_handler",
            )

        return result

    def is_available(self) -> bool:
        """
        Check if GNOME Shell is available on the system.

        Returns:
            True if GNOME Shell is available, False otherwise
        """
        try:
            # Check if GNOME Shell is running
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.shell", "enabled-extensions"],
                capture_output=True,
                check=False,
            )
            return result.returncode == 0

        except FileNotFoundError:
            return False
        except Exception:
            return False

    def get_supported_features(self) -> List[str]:
        """
        Get list of features supported by this handler.

        Returns:
            List of supported features
        """
        features = ["colors", "theme_name"]
        if self._is_user_theme_extension_enabled():
            features.append("full_shell_theme")
        return features

    def get_config_paths(self) -> List[Path]:
        """
        Get list of configuration paths used by this handler.

        Returns:
            List of paths that might be modified by this handler
        """
        return [
            self.shell_config_dir / "gnome-shell.css",
            self.shell_config_dir / "gnome-shell-custom.css",
        ]

    def plan_theme(self, theme_data: ThemeData) -> List[PlannedChange]:
        """
        Plan theme changes without applying them (dry-run).

        Args:
            theme_data: Theme data to plan for

        Returns:
            List of PlannedChange objects describing what would change
        """
        planned_changes = []

        # Plan GSettings change
        if self._is_user_theme_extension_enabled():
            current_theme = self.get_current_theme()
            if current_theme != theme_data.name:
                planned_changes.append(
                    PlannedChange(
                        handler_name="GnomeShellHandler",
                        file_path=Path("dconf/org.gnome.shell.extensions.user-theme"),
                        change_type="modify",
                        description=f"Set shell theme to '{theme_data.name}'",
                        current_value=current_theme,
                        new_value=theme_data.name,
                        toolkit=Toolkit.GNOME_SHELL,
                    )
                )

        # Plan CSS file changes
        if theme_data.colors:
            css_file = self.shell_config_dir / "gnome-shell-custom.css"
            current_content = None
            if css_file.exists():
                try:
                    current_content = read_file_with_fallback(css_file)
                except Exception:
                    pass

            planned_changes.append(
                PlannedChange(
                    handler_name="GnomeShellHandler",
                    file_path=css_file,
                    change_type="modify" if css_file.exists() else "create",
                    description="Generate custom shell CSS from theme colors",
                    current_value=(
                        current_content[:200] + "..."
                        if current_content and len(current_content) > 200
                        else current_content
                    ),
                    new_value="[Generated CSS based on theme colors]",
                    toolkit=Toolkit.GNOME_SHELL,
                )
            )

        return planned_changes

    def get_available_shell_themes(self) -> List[str]:
        """
        Get list of available GNOME Shell themes.

        Returns:
            List of theme names that have gnome-shell directories
        """
        themes = []

        # Check user themes directory
        if self.USER_SHELL_THEMES_DIR.exists():
            for theme_dir in self.USER_SHELL_THEMES_DIR.iterdir():
                if theme_dir.is_dir():
                    shell_dir = theme_dir / "gnome-shell"
                    if shell_dir.exists():
                        themes.append(theme_dir.name)

        # Check system themes directory
        if self.SYSTEM_SHELL_THEMES_DIR.exists():
            for theme_dir in self.SYSTEM_SHELL_THEMES_DIR.iterdir():
                if theme_dir.is_dir():
                    shell_dir = theme_dir / "gnome-shell"
                    if shell_dir.exists() and theme_dir.name not in themes:
                        themes.append(theme_dir.name)

        return sorted(themes)
