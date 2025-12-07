"""Abstract base class for theme parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..tokens.schema import UniversalTokenSchema


class ThemeParser(ABC):
    """
    Abstract base class for parsing themes into universal tokens.

    Subclasses implement parsing for specific theme formats
    (GTK, Qt, JSON tokens, etc.) and produce a UniversalTokenSchema.
    """

    @abstractmethod
    def can_parse(self, source: Path) -> bool:
        """
        Check if this parser can handle the given source.

        Args:
            source: Path to theme directory or file

        Returns:
            True if this parser can parse the source
        """
        pass

    @abstractmethod
    def parse(self, source: Path) -> UniversalTokenSchema:
        """
        Parse theme source into universal tokens.

        Args:
            source: Path to theme directory or file

        Returns:
            UniversalTokenSchema with parsed theme data

        Raises:
            ThemeParseError: If parsing fails
        """
        pass

    def get_name(self) -> str:
        """Return parser name for identification."""
        return self.__class__.__name__


class ThemeParseError(Exception):
    """Raised when theme parsing fails."""

    def __init__(self, message: str, source: Optional[Path] = None):
        self.source = source
        super().__init__(f"{message}" + (f" ({source})" if source else ""))
