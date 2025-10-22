"""
Base handler for Unified Theming Application.

This module defines the abstract base class for all toolkit handlers.
"""

from abc import ABC, abstractmethod
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


class BaseHandler(ABC):
    """
    Base class for all toolkit handlers.

    All specific toolkit handlers (GTK, Qt, etc.) must inherit from this class
    and implement the required abstract methods.
    """

    def __init__(self, toolkit: Toolkit):
        """
        Initialize handler with toolkit type.

        Args:
            toolkit: Type of toolkit this handler manages
        """
        self.toolkit = toolkit

    @abstractmethod
    def apply_theme(self, theme_data: ThemeData) -> bool:
        """
        Apply theme to this toolkit.

        Args:
            theme_data: Prepared theme data for this toolkit

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_current_theme(self) -> str:
        """
        Get currently applied theme name.

        Returns:
            Name of currently applied theme
        """
        pass

    @abstractmethod
    def validate_compatibility(self, theme_data: ThemeData) -> ValidationResult:
        """
        Check if theme is compatible with this toolkit.

        Args:
            theme_data: Theme data to validate

        Returns:
            ValidationResult with any errors/warnings
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this toolkit is available on the system.

        Returns:
            True if toolkit is installed and usable
        """
        pass

    def get_supported_features(self) -> List[str]:
        """
        Get list of features supported by this handler.

        Returns:
            List of supported features (e.g., ['colors', 'fonts', 'icons'])
        """
        return []

    def get_config_paths(self) -> List[Path]:
        """
        Get list of configuration paths used by this handler.

        Returns:
            List of paths that might be modified by this handler
        """
        return []

    def plan_theme(self, theme_data: ThemeData) -> List[PlannedChange]:
        """
        Plan theme changes without applying them (dry-run).

        This method should return a list of all changes that would be made
        if apply_theme() were called with the same theme_data.

        Args:
            theme_data: Theme data to plan for

        Returns:
            List of PlannedChange objects describing what would change
        """
        # Default implementation: returns empty list
        # Subclasses should override to provide detailed planning
        return []
