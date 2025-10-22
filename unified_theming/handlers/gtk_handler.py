"""
GTK Handler for Unified Theming Application.

This module implements the handler for GTK2/3/4 and libadwaita theming.
"""
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from ..utils.logging_config import get_logger
from ..utils.file import write_file_with_backup
from ..core.types import (
    ThemeData, ValidationResult, Toolkit, 
    ValidationLevel, HandlerResult
)
from ..core.exceptions import (
    ThemeApplicationError, GSettingsError, FileWriteError
)
from .base import BaseHandler

logger = get_logger(__name__)

class GTKHandler(BaseHandler):
    """
    Handler for GTK2/3/4 and libadwaita theming.
    
    This handler manages theme application for GTK applications by:
    1. Applying GTK2/3 themes via GSettings
    2. Generating and applying libadwaita CSS
    3. Managing GTK4 configurations
    """

    def __init__(self):
        """Initialize the GTK handler."""
        super().__init__(Toolkit.GTK3)  # Primary toolkit is GTK3 for this handler
        self.config_dir = Path.home() / ".config"
        self.gtk4_config_dir = self.config_dir / "gtk-4.0"
        self.gtk3_config_dir = self.config_dir / "gtk-3.0"
        self.gtk2_config_path = Path.home() / ".gtkrc-2.0"

        # Mapping from GTK to libadwaita color variables
        self.gtk_to_libadwaita_mapping = {
            "theme_bg_color": "window_bg_color",
            "theme_fg_color": "window_fg_color",
            "theme_base_color": "view_bg_color",
            "theme_text_color": "view_fg_color",
            "theme_selected_bg_color": "accent_bg_color",
            "theme_selected_fg_color": "accent_fg_color",
            "insensitive_bg_color": "disabled_bg_color",
            "insensitive_fg_color": "disabled_fg_color",
            "borders": "borders",
            "link_color": "link_color",
            "success_color": "success_bg_color",
            "warning_color": "warning_bg_color",
            "error_color": "error_bg_color",
        }

    def apply_theme(self, theme_data: ThemeData) -> bool:
        """
        Apply theme to GTK2/3/4/libadwaita.
        
        Args:
            theme_data: Theme data to apply
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Applying theme '{theme_data.name}' to GTK toolkit")
        
        try:
            success = True
            
            # Apply to GTK2/3 via GSettings
            if self.is_available():
                if not self._apply_gtk3_theme(theme_data.name):
                    logger.error(f"Failed to apply GTK3 theme: {theme_data.name}")
                    success = False
            
            # Generate and apply libadwaita CSS
            if not self._apply_libadwaita_theme(theme_data):
                logger.error(f"Failed to apply libadwaita theme: {theme_data.name}")
                success = False
            
            # Apply to GTK4 by linking CSS
            if not self._apply_gtk4_theme(theme_data):
                logger.error(f"Failed to apply GTK4 theme: {theme_data.name}")
                success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Error applying GTK theme: {e}")
            raise ThemeApplicationError(
                f"Failed to apply theme '{theme_data.name}' to GTK: {str(e)}",
                toolkit="gtk",
                recoverable=True
            )

    def _apply_gtk3_theme(self, theme_name: str) -> bool:
        """
        Apply theme to GTK3 via GSettings.
        
        Args:
            theme_name: Name of theme to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Set GTK theme
            subprocess.run([
                "gsettings", "set", 
                "org.gnome.desktop.interface", 
                "gtk-theme", 
                theme_name
            ], check=True, capture_output=True)
            
            logger.debug(f"GTK theme set to: {theme_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"GSettings failed to set GTK theme: {e}")
            return False
        except FileNotFoundError:
            logger.warning("gsettings command not found, skipping GTK theme application")
            return False
        except Exception as e:
            logger.warning(f"Error applying GTK3 theme: {e}")
            return False

    def _apply_libadwaita_theme(self, theme_data: ThemeData) -> bool:
        """
        Apply theme to libadwaita by generating CSS file.
        
        Args:
            theme_data: Theme data with color information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate libadwaita CSS
            css_content = self._generate_libadwaita_css(theme_data)
            
            # Ensure config directory exists
            self.gtk4_config_dir.mkdir(parents=True, exist_ok=True)
            
            # Write CSS to config directory
            css_file = self.gtk4_config_dir / "gtk.css"
            success = write_file_with_backup(css_file, css_content)
            
            if success:
                logger.debug(f"Libadwaita CSS written to: {css_file}")
            else:
                logger.error(f"Failed to write libadwaita CSS to: {css_file}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error generating libadwaita CSS: {e}")
            return False

    def _apply_gtk4_theme(self, theme_data: ThemeData) -> bool:
        """
        Apply theme to GTK4 by linking CSS file.
        
        Args:
            theme_data: Theme data to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # For GTK4, we use the same CSS file as libadwaita
            # This method exists for consistency but mainly ensures the CSS file exists
            return True  # This is handled by _apply_libadwaita_theme
            
        except Exception as e:
            logger.error(f"Error applying GTK4 theme: {e}")
            return False

    def _generate_libadwaita_css(self, theme_data: ThemeData) -> str:
        """
        Generate CSS for libadwaita theming.
        
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
            "/* Color Variables */"
        ]
        
        # Map GTK colors to libadwaita names
        for gtk_color, adw_color in self.gtk_to_libadwaita_mapping.items():
            if gtk_color in theme_data.colors:
                color_value = theme_data.colors[gtk_color]
                css_parts.append(f"@define-color {adw_color} {color_value};")
        
        # Add any additional CSS from the theme data
        if theme_data.css_content:
            css_parts.extend([
                "",
                "/* Additional CSS */",
                theme_data.css_content
            ])
        
        return "\n".join(css_parts)

    def get_current_theme(self) -> str:
        """
        Get currently applied GTK theme name.
        
        Returns:
            Name of currently applied theme
        """
        try:
            result = subprocess.run([
                "gsettings", "get", 
                "org.gnome.desktop.interface", 
                "gtk-theme"
            ], capture_output=True, text=True, check=True)
            
            # Extract theme name from gsettings output (format: "'ThemeName'")
            theme_name = result.stdout.strip().strip("'\"")
            return theme_name
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.debug("Could not get current GTK theme, gsettings not available")
            return "default"

    def validate_compatibility(
        self,
        theme_data: ThemeData
    ) -> ValidationResult:
        """
        Check if theme is compatible with GTK toolkits.
        
        Args:
            theme_data: Theme data to validate
            
        Returns:
            ValidationResult with validation messages
        """
        result = ValidationResult(valid=True)
        
        # Check if theme supports GTK
        if theme_data.toolkit not in [Toolkit.GTK2, Toolkit.GTK3, Toolkit.GTK4, Toolkit.LIBADWAITA]:
            result.add_warning(
                f"Theme '{theme_data.name}' is not primarily a GTK theme",
                component="gtk_handler"
            )
        
        # Check if required color variables are present
        required_colors = ["theme_bg_color", "theme_fg_color"]
        missing_colors = [
            color for color in required_colors 
            if color not in theme_data.colors
        ]
        
        if missing_colors:
            result.add_warning(
                f"Theme '{theme_data.name}' missing required colors for GTK: {', '.join(missing_colors)}",
                component="gtk_handler"
            )
        
        return result

    def is_available(self) -> bool:
        """
        Check if GTK is available on the system.
        
        Returns:
            True if GTK is available, False otherwise
        """
        try:
            # Check if gsettings is available (indicating GNOME/GTK environment)
            result = subprocess.run(
                ["gsettings", "--version"], 
                capture_output=True, 
                check=False
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
        return ["colors", "theme_name", "css_customization"]

    def get_config_paths(self) -> List[Path]:
        """
        Get list of configuration paths used by this handler.
        
        Returns:
            List of paths that might be modified by this handler
        """
        return [
            self.gtk4_config_dir / "gtk.css",
            self.gtk3_config_dir / "settings.ini",  # GTK3 config
            self.gtk2_config_path  # GTK2 config
        ]