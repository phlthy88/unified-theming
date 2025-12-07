"""Universal design token schema for cross-toolkit theming."""

from dataclasses import dataclass, field
from typing import Optional

from ..color.spaces import Color


@dataclass
class SurfaceTokens:
    """Background/surface colors."""

    primary: Color
    secondary: Color
    tertiary: Color
    elevated: Color
    inverse: Color


@dataclass
class ContentTokens:
    """Foreground/text colors."""

    primary: Color
    secondary: Color
    tertiary: Color
    inverse: Color
    link: Color
    link_visited: Color


@dataclass
class AccentTokens:
    """Accent and semantic colors."""

    primary: Color
    primary_container: Color
    secondary: Color
    success: Color
    warning: Color
    error: Color


@dataclass
class StateTokens:
    """Interactive state values."""

    hover_overlay: float = 0.08
    pressed_overlay: float = 0.12
    focus_ring: Optional[Color] = None
    disabled_opacity: float = 0.38


@dataclass
class BorderTokens:
    """Border colors."""

    subtle: Color
    default: Color
    strong: Color


@dataclass
class UniversalTokenSchema:
    """Complete universal token schema for theming."""

    name: str
    variant: str  # "light" or "dark"
    surfaces: SurfaceTokens
    content: ContentTokens
    accents: AccentTokens
    states: StateTokens
    borders: BorderTokens
    source: Optional[str] = None
