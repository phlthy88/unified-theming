"""
Qt Handler for Unified Theming Application.

This module implements the handler for Qt5/6 theming.
"""

from pathlib import Path
from typing import Dict, List, Optional

from ..core.exceptions import ColorTranslationError, ThemeApplicationError
from ..core.types import (
    HandlerResult,
    ThemeData,
    Toolkit,
    ValidationLevel,
    ValidationResult,
)
from ..renderers.qt import QtRenderer
from ..tokens.schema import UniversalTokenSchema
from ..utils.file import write_file_with_backup
from ..utils.logging_config import get_logger
from .base import BaseHandler

logger = get_logger(__name__)


class QtHandler(BaseHandler):
    """
    Handler for Qt5/6 theming.

    This handler manages theme application for Qt applications by:
    1. Translating GTK colors to Qt color scheme
    2. Generating kdeglobals configuration
    3. Optionally generating Kvantum theme
    """

    def __init__(self):
        """Initialize the Qt handler."""
        super().__init__(Toolkit.QT5)  # Primary toolkit is Qt5 for this handler
        self.config_dir = Path.home() / ".config"
        self.kdeglobals_path = self.config_dir / "kdeglobals"
        self.kvantum_dir = self.config_dir / "Kvantum"
        self.renderer = QtRenderer()

        # Mapping from GTK to Qt color variables
        self.gtk_to_qt_mapping = {
            "theme_bg_color": "BackgroundNormal",
            "theme_fg_color": "ForegroundNormal",
            "theme_base_color": "Base",
            "theme_text_color": "Text",
            "theme_selected_bg_color": "Highlight",
            "theme_selected_fg_color": "HighlightedText",
            "insensitive_bg_color": "BackgroundInactive",
            "insensitive_fg_color": "ForegroundInactive",
            "link_color": "Link",
            "visited_link_color": "VisitedLink",
            "success_color": "ForegroundPositive",
            "warning_color": "ForegroundNeutral",
            "error_color": "ForegroundNegative",
        }

    def apply_from_tokens(self, tokens: UniversalTokenSchema) -> bool:
        """
        Apply theme from universal tokens using QtRenderer.

        Args:
            tokens: Universal token schema to apply

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Applying theme '{tokens.name}' from tokens to Qt toolkit")

        try:
            rendered = self.renderer.render(tokens)

            # Write kdeglobals file
            for rel_path, content in rendered.files.items():
                target = self.config_dir / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                if not write_file_with_backup(target, content):
                    logger.error(f"Failed to write {target}")
                    return False
                logger.debug(f"Wrote configuration to: {target}")

            return True

        except Exception as e:
            logger.error(f"Error applying Qt theme from tokens: {e}")
            raise ThemeApplicationError(
                f"Failed to apply theme '{tokens.name}' from tokens: {str(e)}",
                toolkit="qt",
                recoverable=True,
            )

    def apply_theme(self, theme_data: ThemeData) -> bool:
        """
        Apply theme to Qt5/6.

        Args:
            theme_data: Theme data to apply

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Applying theme '{theme_data.name}' to Qt toolkit")

        try:
            success = True

            # Generate and write kdeglobals
            if not self._generate_kdeglobals(theme_data):
                logger.error(
                    f"Failed to generate kdeglobals for Qt theme: {theme_data.name}"
                )
                success = False

            # Optionally generate Kvantum theme if Kvantum is available
            if self._is_kvantum_available():
                if not self._generate_kvantum_theme(theme_data):
                    logger.warning(
                        f"Failed to generate Kvantum theme: {theme_data.name}"
                    )
                    # Don't consider this a complete failure, kdeglobals will still work
            else:
                logger.info("Kvantum not available, using kdeglobals only")

            return success

        except Exception as e:
            logger.error(f"Error applying Qt theme: {e}")
            raise ThemeApplicationError(
                f"Failed to apply theme '{theme_data.name}' to Qt: {str(e)}",
                toolkit="qt",
                recoverable=True,
            )

    def _generate_kdeglobals(self, theme_data: ThemeData) -> bool:
        """
        Generate kdeglobals configuration file for Qt theming.

        Args:
            theme_data: Theme data with color information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Translate GTK colors to Qt colors
            qt_colors = {}
            for gtk_color, qt_color in self.gtk_to_qt_mapping.items():
                if gtk_color in theme_data.colors:
                    try:
                        # Convert colors to Qt format (RGB values)
                        qt_color_value = self._gtk_color_to_qt_format(
                            theme_data.colors[gtk_color]
                        )
                        qt_colors[qt_color] = qt_color_value
                    except ColorTranslationError as e:
                        logger.warning(f"Failed to translate color {gtk_color}: {e}")

            # Generate kdeglobals content
            kdeglobals_content = self._generate_kdeglobals_content(
                qt_colors, theme_data.name
            )

            # Write to kdeglobals file
            success = write_file_with_backup(self.kdeglobals_path, kdeglobals_content)

            if success:
                logger.debug(f"KDE globals written to: {self.kdeglobals_path}")
            else:
                logger.error(f"Failed to write kdeglobals to: {self.kdeglobals_path}")

            return success

        except Exception as e:
            logger.error(f"Error generating kdeglobals: {e}")
            return False

    def _gtk_color_to_qt_format(self, gtk_color: str) -> str:
        """
        Convert a GTK color format to Qt RGB format (r,g,b).

        Args:
            gtk_color: Color in GTK format (e.g., #RRGGBB, rgba(...))

        Returns:
            Color in Qt format (r,g,b) where r,g,b are 0-255

        Raises:
            ColorTranslationError: If color format is invalid
        """
        gtk_color = gtk_color.strip()

        # Handle hex format (#RRGGBB or #RGB)
        if gtk_color.startswith("#"):
            gtk_color = gtk_color[1:]  # Remove #

            if len(gtk_color) == 3:  # #RGB format
                gtk_color = "".join([c * 2 for c in gtk_color])  # Expand to #RRGGBB
            elif len(gtk_color) != 6:
                raise ColorTranslationError(
                    "gtk", "qt", gtk_color, f"Invalid hex color format: {gtk_color}"
                )

            try:
                r = int(gtk_color[0:2], 16)
                g = int(gtk_color[2:4], 16)
                b = int(gtk_color[4:6], 16)
                return f"{r},{g},{b}"
            except ValueError:
                raise ColorTranslationError(
                    "gtk", "qt", gtk_color, f"Invalid hex color: {gtk_color}"
                )

        # Handle rgb() format
        elif gtk_color.lower().startswith("rgb("):
            # Extract numbers from rgb(r, g, b)
            import re

            match = re.search(
                r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)",
                gtk_color,
                re.IGNORECASE,
            )
            if match:
                r_str, g_str, b_str = match.groups()
                return f"{r_str},{g_str},{b_str}"
            else:
                raise ColorTranslationError(
                    "gtk", "qt", gtk_color, f"Invalid RGB format: {gtk_color}"
                )

        # Handle rgba() format (ignore alpha)
        elif gtk_color.lower().startswith("rgba("):
            # Extract numbers from rgba(r, g, b, a)
            import re

            match = re.search(
                r"rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)",
                gtk_color,
                re.IGNORECASE,
            )
            if match:
                r_str, g_str, b_str = match.groups()
                return f"{r_str},{g_str},{b_str}"
            else:
                raise ColorTranslationError(
                    "gtk", "qt", gtk_color, f"Invalid RGBA format: {gtk_color}"
                )

        # For other formats, raise an error
        raise ColorTranslationError(
            "gtk", "qt", gtk_color, f"Unsupported color format: {gtk_color}"
        )

    def _generate_kdeglobals_content(
        self, qt_colors: Dict[str, str], theme_name: str
    ) -> str:
        """
        Generate the content for kdeglobals file.

        Args:
            qt_colors: Dictionary of Qt color names to RGB values
            theme_name: Name of the theme

        Returns:
            Content for kdeglobals file
        """
        lines = [
            "# Generated by Unified Theming App",
            f"# Theme: {theme_name}",
            f"# Timestamp: {__import__('datetime').datetime.now()}",
            "",
            "[General]",
            f"Name={theme_name}",
            "",
            "[KDE]",
            "contrast=4",
            "",
            "[WM]",
            "activeBackground=255,255,255",
            "inactiveBackground=255,255,255",
            "",
        ]

        # Add color sections for different Qt color groups
        color_sections = {
            "Colors:Window": [
                "BackgroundNormal",
                "BackgroundAlternate",
                "ForegroundNormal",
                "ForegroundInactive",
                "ForegroundActive",
            ],
            "Colors:Button": ["BackgroundNormal", "Button", "ButtonText"],
            "Colors:Selection": [
                "BackgroundNormal",
                "ForegroundNormal",
                "Highlight",
                "HighlightedText",
            ],
            "Colors:Tooltip": [
                "BackgroundNormal",
                "ForegroundNormal",
                "ToolTipBase",
                "ToolTipText",
            ],
            "Colors:View": ["BackgroundNormal", "Base", "Text"],
            "Colors:Header": ["BackgroundNormal", "ForegroundNormal"],
            "Colors:Link": ["ForegroundNormal", "Link", "VisitedLink"],
            "Colors:PositiveText": ["BackgroundNormal", "ForegroundPositive"],
            "Colors:NeutralText": ["BackgroundNormal", "ForegroundNeutral"],
            "Colors:NegativeText": ["BackgroundNormal", "ForegroundNegative"],
        }

        # Add all Qt colors to appropriate sections
        for section, color_keys in color_sections.items():
            lines.append(f"[{section}]")
            for color_key in color_keys:
                if color_key in qt_colors:
                    lines.append(f"{color_key}={qt_colors[color_key]}")
            lines.append("")

        return "\n".join(lines)

    def _generate_kvantum_theme(self, theme_data: ThemeData) -> bool:
        """
        Generate Kvantum theme files.

        Args:
            theme_data: Theme data to use for generating Kvantum theme

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create theme directory
            theme_dir = self.kvantum_dir / theme_data.name
            theme_dir.mkdir(parents=True, exist_ok=True)

            # Generate kvconfig file
            kvconfig_content = self._generate_kvantum_config(theme_data)
            kvconfig_path = theme_dir / f"{theme_data.name}.kvconfig"

            success1 = write_file_with_backup(kvconfig_path, kvconfig_content)

            # Generate svg file with color definitions
            svg_content = self._generate_kvantum_svg(theme_data)
            svg_path = theme_dir / f"{theme_data.name}.svg"

            success2 = write_file_with_backup(svg_path, svg_content)

            if success1 and success2:
                logger.debug(f"Kvantum theme generated in: {theme_dir}")
            else:
                logger.error(f"Failed to generate Kvantum theme in: {theme_dir}")

            return success1 and success2

        except Exception as e:
            logger.error(f"Error generating Kvantum theme: {e}")
            return False

    def _generate_kvantum_config(self, theme_data: ThemeData) -> str:
        """
        Generate Kvantum config file content.

        Args:
            theme_data: Theme data to use

        Returns:
            Content for kvconfig file
        """
        return f"""[General]
name={theme_data.name}
"""

    def _generate_kvantum_svg(self, theme_data: ThemeData) -> str:
        """
        Generate Kvantum SVG file content.

        Args:
            theme_data: Theme data to use

        Returns:
            Content for SVG file
        """
        # Basic SVG template with some color definitions
        # In a full implementation, this would be much more comprehensive
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style type="text/css">
      /* Generated by Unified Theming App */
      /* Theme: {theme_data.name} */
    </style>
  </defs>
  <rect width="200" height="200" fill="{theme_data.colors.get('theme_bg_color', '#ffffff')}"/>
</svg>
"""

    def _is_kvantum_available(self) -> bool:
        """
        Check if Kvantum is available on the system.

        Returns:
            True if Kvantum is available, False otherwise
        """
        import subprocess

        try:
            result = subprocess.run(
                ["kvantummanager", "--version"], capture_output=True, check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def get_current_theme(self) -> str:
        """
        Get currently applied Qt theme name.

        Returns:
            Name of currently applied theme
        """
        # For now, we'll return a default value
        # In a full implementation, we would read from kdeglobals
        return "default"

    def validate_compatibility(self, theme_data: ThemeData) -> ValidationResult:
        """
        Check if theme is compatible with Qt toolkit.

        Args:
            theme_data: Theme data to validate

        Returns:
            ValidationResult with validation messages
        """
        result = ValidationResult(valid=True)

        # Check if theme supports Qt
        if theme_data.toolkit not in [Toolkit.QT5, Toolkit.QT6]:
            result.add_info(
                f"Theme '{theme_data.name}' is not primarily a Qt theme, will translate colors",
                component="qt_handler",
            )

        # Check if required color variables are present
        required_colors = ["theme_bg_color", "theme_fg_color"]
        missing_colors = [
            color for color in required_colors if color not in theme_data.colors
        ]

        if missing_colors:
            result.add_warning(
                f"Theme '{theme_data.name}' missing required colors for Qt: {', '.join(missing_colors)}",
                component="qt_handler",
            )

        return result

    def is_available(self) -> bool:
        """
        Check if Qt is available on the system.

        Returns:
            True if Qt is available, False otherwise
        """
        import subprocess

        try:
            # Check if qmake or qmake6 is available (indicating Qt installation)
            for cmd in ["qmake", "qmake6", "qmake-qt5"]:
                try:
                    result = subprocess.run(
                        [cmd, "-v"], capture_output=True, check=False
                    )
                    if result.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
            return False
        except Exception:
            return False

    def get_supported_features(self) -> List[str]:
        """
        Get list of features supported by this handler.

        Returns:
            List of supported features
        """
        return ["colors", "theme_name", "kdeglobals", "kvantum"]

    def get_config_paths(self) -> List[Path]:
        """
        Get list of configuration paths used by this handler.

        Returns:
            List of paths that might be modified by this handler
        """
        return [self.kdeglobals_path, self.kvantum_dir]
