"""Abstract base class for theme renderers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from ..tokens.schema import UniversalTokenSchema


@dataclass
class RenderedTheme:
    """Output from a renderer."""

    toolkit: str
    files: Dict[Path, str] = field(default_factory=dict)  # path → content
    settings: Dict[str, Any] = field(default_factory=dict)  # runtime settings


class BaseRenderer(ABC):
    """
    Abstract base class for rendering tokens to toolkit-specific configs.

    Subclasses implement rendering for specific toolkits (GTK, Qt, etc.)
    and produce config files from UniversalTokenSchema.
    """

    @abstractmethod
    def render(self, tokens: UniversalTokenSchema) -> RenderedTheme:
        """
        Render universal tokens to toolkit-specific output.

        Args:
            tokens: Universal token schema to render

        Returns:
            RenderedTheme with generated files and settings
        """
        pass

    def get_name(self) -> str:
        """Return renderer name for identification."""
        return self.__class__.__name__
