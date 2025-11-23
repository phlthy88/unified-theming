"""
Theme parser for Unified Theming Application.

This module implements the UnifiedThemeParser which scans theme directories,
parses theme metadata, extracts color palettes, and validates themes.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..core.exceptions import (
    InvalidThemeError,
    ThemeDiscoveryError,
    ThemeNotFoundError,
)
from ..core.types import ColorPalette, ThemeInfo, Toolkit, ValidationResult
from ..utils.file import read_file_with_fallback
from ..utils.logging_config import get_logger
from ..utils.validation import validate_css_syntax

logger = get_logger(__name__)

# Common theme directories to scan
THEME_DIRECTORIES = [
    Path.home() / ".themes",
    Path.home() / ".local/share/themes",
    Path("/usr/share/themes"),
    Path("/usr/local/share/themes"),
]


class UnifiedThemeParser:
    """
    Parser for discovering, parsing, and validating themes.

    This class handles the discovery of themes across standard directories,
    parsing of theme metadata, extraction of color palettes, and validation
    of theme structures and content.
    """

    def __init__(self, theme_directories: Optional[List[Path]] = None):
        """
        Initialize the parser.

        Args:
            theme_directories: List of directories to scan for themes.
                             Defaults to standard theme directories if None.
        """
        self.theme_directories = theme_directories or THEME_DIRECTORIES
        self._color_regex = re.compile(
            r"@define-color\s+([\w-]+)\s+([^;]+);", re.IGNORECASE
        )
        self._css_comment_regex = re.compile(r"/\*.*?\*/", re.DOTALL)

    def discover_themes(self) -> Dict[str, ThemeInfo]:
        """
        Scan theme directories and return all discovered themes.

        This method scans all configured theme directories in parallel to
        discover available themes. It parses basic metadata for each theme
        and returns a dictionary mapping theme names to ThemeInfo objects.

        Returns:
            Dictionary mapping theme names to ThemeInfo objects

        Raises:
            ThemeDiscoveryError: If theme discovery fails
        """
        logger.info(f"Discovering themes in {len(self.theme_directories)} directories")
        start_time = __import__("time").time()

        all_themes: Dict[str, ThemeInfo] = {}
        errors: List[str] = []

        for theme_dir in self.theme_directories:
            if not theme_dir.exists():
                logger.debug(f"Theme directory does not exist: {theme_dir}")
                continue

            try:
                themes_in_dir = self._discover_themes_in_directory(theme_dir)
                # Merge themes, with later directories taking precedence if names conflict
                all_themes.update(themes_in_dir)
            except Exception as e:
                error_msg = f"Failed to scan {theme_dir}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)

        if errors and len(all_themes) == 0:
            raise ThemeDiscoveryError(
                f"Failed to discover themes: {', '.join(errors)}",
                details="No themes could be discovered from any directory",
            )

        total_time = __import__("time").time() - start_time
        logger.info(f"Discovered {len(all_themes)} themes in {total_time:.2f}s")

        return all_themes

    def _discover_themes_in_directory(self, theme_dir: Path) -> Dict[str, ThemeInfo]:
        """
        Discover themes in a specific directory.

        Args:
            theme_dir: Directory to scan for themes

        Returns:
            Dictionary mapping theme names to ThemeInfo objects
        """
        themes: Dict[str, ThemeInfo] = {}

        logger.debug(f"Scanning {theme_dir} for themes")

        for theme_path in theme_dir.iterdir():
            if not theme_path.is_dir():
                continue

            theme_name = theme_path.name

            # Skip hidden directories
            if theme_name.startswith("."):
                continue

            # Check if this directory looks like a theme
            if self._is_valid_theme_directory(theme_path):
                try:
                    theme_info = self.parse_theme(theme_path)
                    themes[theme_name] = theme_info
                    logger.debug(f"Discovered theme: {theme_name}")
                except Exception as e:
                    logger.warning(f"Failed to parse theme {theme_name}: {str(e)}")

        return themes

    def _is_valid_theme_directory(self, theme_path: Path) -> bool:
        """
        Check if a directory appears to be a valid theme.

        Args:
            theme_path: Path to potential theme directory

        Returns:
            True if directory appears to contain a theme
        """
        # Check for common theme subdirectories
        possible_directories = [
            "gtk-2.0",
            "gtk-3.0",
            "gtk-4.0",
            "cinnamon",
            "gnome-shell",
            "metacity-1",
            "unity",
            "xfwm4",
            "openbox-3",
            "index.theme",
        ]

        for item in theme_path.iterdir():
            if item.name in possible_directories:
                return True

        return False

    def parse_theme(self, theme_path: Path) -> ThemeInfo:
        """
        Parse a single theme and extract metadata.

        Args:
            theme_path: Path to theme directory

        Returns:
            ThemeInfo object with complete theme information

        Raises:
            ThemeNotFoundError: If theme directory doesn't exist
            InvalidThemeError: If theme structure is invalid
        """
        if not theme_path.exists():
            raise ThemeNotFoundError(theme_path.name, searched_paths=[theme_path])

        if not theme_path.is_dir():
            raise InvalidThemeError(
                theme_path.name, "Theme path is not a directory", theme_path=theme_path
            )

        logger.debug(f"Parsing theme: {theme_path.name}")

        # Extract theme name from directory name
        theme_name = theme_path.name

        # Determine supported toolkits
        supported_toolkits = self._get_supported_toolkits(theme_path)

        # Load metadata from index.theme if it exists
        metadata = self._parse_index_theme(theme_path)

        # Create basic ThemeInfo
        theme_info = ThemeInfo(
            name=theme_name,
            path=theme_path,
            supported_toolkits=supported_toolkits,
            metadata=metadata,
        )

        # Validate the theme
        validation_result = self.validate_theme(theme_path)
        theme_info.validation_result = validation_result

        return theme_info

    def _get_supported_toolkits(self, theme_path: Path) -> List[Toolkit]:
        """
        Determine which toolkits a theme supports based on directory structure.

        Args:
            theme_path: Path to theme directory

        Returns:
            List of supported Toolkits
        """
        supported = []

        # Check for GTK support
        if (theme_path / "gtk-2.0").exists():
            supported.append(Toolkit.GTK2)
        if (theme_path / "gtk-3.0").exists():
            supported.append(Toolkit.GTK3)
        if (theme_path / "gtk-4.0").exists():
            supported.append(Toolkit.GTK4)

        # Check for libadwaita support (usually in gtk-4.0)
        if (theme_path / "gtk-4.0" / "gtk.css").exists():
            supported.append(Toolkit.LIBADWAITA)

        # Check for GNOME Shell support
        if (theme_path / "gnome-shell").exists():
            supported.append(Toolkit.GNOME_SHELL)

        # Additional checks could go here for other toolkits
        # (Qt, Flatpak, Snap) based on their specific requirements

        return supported

    def _parse_index_theme(self, theme_path: Path) -> Dict[str, str]:
        """
        Parse index.theme file if it exists.

        Args:
            theme_path: Path to theme directory

        Returns:
            Dictionary of metadata from index.theme
        """
        index_file = theme_path / "index.theme"
        if not index_file.exists():
            return {}

        try:
            content = read_file_with_fallback(index_file)
            metadata = {}

            # Simple INI-style parsing for index.theme
            current_section = None
            for line_num, line in enumerate(content.splitlines(), 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Section header
                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1]
                    continue

                # Key-value pair
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Only store keys from the main section (not sub-sections)
                    if current_section is None or current_section == "Theme":
                        metadata[key] = value

            return metadata

        except Exception as e:
            logger.warning(f"Failed to parse index.theme for {theme_path.name}: {e}")
            return {}

    def extract_colors(self, theme_path: Path, toolkit: str = "gtk") -> ColorPalette:
        """
        Extract color palette from theme CSS files.

        Args:
            theme_path: Path to theme directory
            toolkit: Toolkit to extract colors for ("gtk", "gtk3", "gtk4", "gnome-shell")

        Returns:
            Dictionary mapping color variable names to color values

        Raises:
            ThemeNotFoundError: If theme directory doesn't exist
            ThemeParseError: If CSS parsing fails
        """
        if not theme_path.exists():
            raise ThemeNotFoundError(theme_path.name, searched_paths=[theme_path])

        colors: ColorPalette = {}

        # Determine which CSS files to scan based on toolkit
        if toolkit in ["gtk", "gtk3"]:
            css_paths = [theme_path / "gtk-3.0" / "gtk.css"]
        elif toolkit == "gtk4":
            css_paths = [theme_path / "gtk-4.0" / "gtk.css"]
        elif toolkit == "gnome-shell":
            css_paths = [theme_path / "gnome-shell" / "gnome-shell.css"]
        else:
            # Default to all if toolkit not specified
            css_paths = [
                theme_path / "gtk-3.0" / "gtk.css",
                theme_path / "gtk-4.0" / "gtk.css",
                theme_path / "gnome-shell" / "gnome-shell.css",
            ]

        for css_path in css_paths:
            if css_path.exists():
                try:
                    css_content = read_file_with_fallback(css_path)
                    css_colors = self._parse_css_colors(css_content)
                    colors.update(css_colors)
                    logger.debug(f"Extracted {len(css_colors)} colors from {css_path}")
                except Exception as e:
                    logger.warning(f"Failed to parse colors from {css_path}: {e}")

        return colors

    def _parse_css_colors(self, css_content: str) -> ColorPalette:
        """
        Parse CSS content to extract @define-color statements.

        Args:
            css_content: CSS content as string

        Returns:
            Dictionary of color variable names to values
        """
        # Remove CSS comments to avoid parsing colors inside comments
        css_clean = self._css_comment_regex.sub("", css_content)

        colors: ColorPalette = {}

        for match in self._color_regex.finditer(css_clean):
            var_name = match.group(1).strip()
            color_value = match.group(2).strip()

            # Clean up the color value (remove trailing whitespace, etc.)
            color_value = re.sub(r"\s+", " ", color_value).strip()

            colors[var_name] = color_value

        return colors

    def validate_theme(self, theme_path: Path) -> ValidationResult:
        """
        Validate theme structure and content.

        Args:
            theme_path: Path to theme directory

        Returns:
            ValidationResult with validation messages
        """
        if not theme_path.exists():
            raise ThemeNotFoundError(theme_path.name, searched_paths=[theme_path])

        result = ValidationResult(valid=True)
        theme_name = theme_path.name

        logger.debug(f"Validating theme: {theme_name}")

        # Check for required directories
        required_dirs = ["gtk-3.0", "gtk-4.0"]
        found_required = False
        for req_dir in required_dirs:
            if (theme_path / req_dir).exists():
                found_required = True
                break

        if not found_required:
            result.add_warning(
                f"Theme '{theme_name}' may have limited support - missing standard directories",
                component="parser",
                details=f"Expected at least one of: {', '.join(required_dirs)}",
            )

        # Validate CSS files
        css_files = []
        if (theme_path / "gtk-3.0").exists():
            css_file = theme_path / "gtk-3.0" / "gtk.css"
            if css_file.exists():
                css_files.append(css_file)

        if (theme_path / "gtk-4.0").exists():
            css_file = theme_path / "gtk-4.0" / "gtk.css"
            if css_file.exists():
                css_files.append(css_file)

        for css_file in css_files:
            try:
                css_content = read_file_with_fallback(css_file)
                validation_errors = validate_css_syntax(css_content)

                if validation_errors:
                    result.add_error(
                        f"CSS syntax errors in {css_file.name}",
                        component="parser",
                        details=f"Found {len(validation_errors)} errors: {', '.join(validation_errors)}",
                    )
            except Exception as e:
                result.add_error(
                    f"Failed to read CSS file {css_file}: {str(e)}", component="parser"
                )

        # Check if theme has color definitions
        try:
            colors = self.extract_colors(theme_path)
            if not colors:
                result.add_warning(
                    f"Theme '{theme_name}' contains no color definitions",
                    component="parser",
                    details="No @define-color statements found in CSS files",
                )
        except Exception as e:
            result.add_warning(
                f"Could not extract colors from theme '{theme_name}': {str(e)}",
                component="parser",
            )

        # Check for critical files
        critical_files = ["index.theme"]
        missing_critical = []
        for critical_file in critical_files:
            if not (theme_path / critical_file).exists():
                missing_critical.append(critical_file)

        if missing_critical:
            result.add_info(
                f"Theme '{theme_name}' missing optional files",
                component="parser",
                details=f"Missing: {', '.join(missing_critical)}",
            )

        return result
