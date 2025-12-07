"""
Flatpak Handler for Unified Theming Application.

This module implements the handler for Flatpak application theming.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from ..core.exceptions import ThemeApplicationError
from ..core.types import ThemeData, Toolkit, ValidationLevel, ValidationResult
from ..utils.logging_config import get_logger
from .base import BaseHandler

logger = get_logger(__name__)


class FlatpakHandler(BaseHandler):
    """
    Handler for Flatpak application theming.

    This handler manages theme application for Flatpak applications by:
    1. Configuring portal settings
    2. Setting up filesystem overrides
    3. Managing environment variables
    """

    def __init__(self):
        """Initialize the Flatpak handler."""
        super().__init__(Toolkit.FLATPAK)
        self.available = self._check_flatpak_available()

    def _check_flatpak_available(self) -> bool:
        """
        Check if Flatpak is available on the system.

        Returns:
            True if Flatpak is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["flatpak", "--version"], capture_output=True, check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def apply_theme(self, theme_data: ThemeData) -> bool:
        """
        Apply theme to Flatpak applications.

        Args:
            theme_data: Theme data to apply

        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            logger.warning("Flatpak not available, skipping theme application")
            return False

        logger.info(f"Applying theme '{theme_data.name}' to Flatpak applications")

        try:
            # Grant filesystem access to theme directories
            theme_dirs = [
                Path.home() / ".themes",
                Path.home() / ".local/share/themes",
                Path("/usr/share/themes"),
            ]

            success_count = 0
            existing_dirs = 0

            for theme_dir in theme_dirs:
                if theme_dir.exists():
                    existing_dirs += 1
                    try:
                        subprocess.run(
                            [
                                "flatpak",
                                "override",
                                "--user",
                                f"--filesystem={theme_dir}:ro",
                            ],
                            check=True,
                            capture_output=True,
                        )
                        logger.debug(f"Granted access to theme directory: {theme_dir}")
                        success_count += 1
                    except subprocess.CalledProcessError:
                        logger.warning(
                            f"Failed to grant access to theme directory: {theme_dir}"
                        )

            # Return False if all existing directories failed
            if existing_dirs > 0 and success_count == 0:
                logger.error("All Flatpak override commands failed")
                return False

            logger.debug(f"Flatpak theme access configured for: {theme_data.name}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Flatpak command failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error applying Flatpak theme: {e}")
            return False

    def get_current_theme(self) -> str:
        """
        Get currently applied Flatpak theme name.

        Returns:
            Name of currently applied theme
        """
        # Flatpak doesn't have a distinct theme setting, it follows the system theme
        # In a full implementation, we could check the override settings
        return "system"

    def validate_compatibility(self, theme_data: ThemeData) -> ValidationResult:
        """
        Check if theme is compatible with Flatpak.

        Args:
            theme_data: Theme data to validate

        Returns:
            ValidationResult with validation messages
        """
        result = ValidationResult(valid=True)

        # Flatpak applications typically follow system theme
        # but we can add warnings if the theme doesn't have common components
        if theme_data.toolkit not in [Toolkit.GTK3, Toolkit.GTK4, Toolkit.LIBADWAITA]:
            result.add_info(
                "Flatpak applications typically use system theme components",
                component="flatpak_handler",
            )

        return result

    def is_available(self) -> bool:
        """
        Check if Flatpak is available on the system.

        Returns:
            True if Flatpak is available, False otherwise
        """
        return self.available

    def get_supported_features(self) -> List[str]:
        """
        Get list of features supported by this handler.

        Returns:
            List of supported features
        """
        return ["filesystem_access", "environment_vars"]

    def get_config_paths(self) -> List[Path]:
        """
        Get list of configuration paths used by this handler.

        Returns:
            List of paths that might be modified by this handler
        """
        return [Path.home() / ".config" / "flatpak" / "overrides"]
