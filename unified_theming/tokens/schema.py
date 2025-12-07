"""Universal design token schema for cross-toolkit theming."""

from dataclasses import dataclass, field
from typing import Optional

from ..color.spaces import Color


@dataclass
class SurfaceTokens:
    """Background/surface colors for UI elements.

    Attributes:
        primary: Main background color for the application.
        secondary: Secondary background for cards, panels, and grouped elements.
        tertiary: Tertiary background for subtle distinctions.
        elevated: Background for elevated surfaces like dialogs and popovers.
        inverse: High contrast background for overlays and inverse themes.

    Examples:
        >>> surfaces = SurfaceTokens(
        ...     primary=Color(255, 255, 255),
        ...     secondary=Color(246, 246, 246),
        ...     tertiary=Color(237, 237, 237),
        ...     elevated=Color(255, 255, 255),
        ...     inverse=Color(30, 30, 30)
        ... )
    """

    primary: Color
    secondary: Color
    tertiary: Color
    elevated: Color
    inverse: Color


@dataclass
class ContentTokens:
    """Foreground/text colors for content hierarchy.

    Attributes:
        primary: Primary text color with highest emphasis.
        secondary: Secondary text for subtitles and less important content.
        tertiary: Tertiary text for captions and metadata.
        inverse: Text color for inverse surfaces.
        link: Color for hyperlinks.
        link_visited: Color for visited hyperlinks.

    Examples:
        >>> content = ContentTokens(
        ...     primary=Color(26, 26, 26),
        ...     secondary=Color(94, 94, 94),
        ...     tertiary=Color(140, 140, 140),
        ...     inverse=Color(255, 255, 255),
        ...     link=Color.from_hex("#3584e4"),
        ...     link_visited=Color.from_hex("#8035e4")
        ... )
    """

    primary: Color
    secondary: Color
    tertiary: Color
    inverse: Color
    link: Color
    link_visited: Color


@dataclass
class AccentTokens:
    """Accent and semantic colors for interactive elements.

    Attributes:
        primary: Primary accent color for buttons and active states.
        primary_container: Background color for primary accent containers.
        secondary: Secondary accent color for less prominent actions.
        success: Color for success states and positive feedback.
        warning: Color for warning states and caution.
        error: Color for error states and destructive actions.

    Examples:
        >>> accents = AccentTokens(
        ...     primary=Color.from_hex("#3584e4"),
        ...     primary_container=Color.from_hex("#d3e5f9"),
        ...     secondary=Color(128, 128, 128),
        ...     success=Color.from_hex("#2ec27e"),
        ...     warning=Color.from_hex("#f5c211"),
        ...     error=Color.from_hex("#e01b24")
        ... )
    """

    primary: Color
    primary_container: Color
    secondary: Color
    success: Color
    warning: Color
    error: Color


@dataclass
class StateTokens:
    """Interactive state values for UI components.

    Attributes:
        hover_overlay: Opacity for hover state overlays (0.0-1.0).
        pressed_overlay: Opacity for pressed state overlays (0.0-1.0).
        focus_ring: Color for focus rings, None for default.
        disabled_opacity: Opacity for disabled elements (0.0-1.0).

    Examples:
        >>> states = StateTokens(
        ...     hover_overlay=0.08,
        ...     pressed_overlay=0.12,
        ...     focus_ring=Color.from_hex("#3584e4"),
        ...     disabled_opacity=0.38
        ... )
    """

    hover_overlay: float = 0.08
    pressed_overlay: float = 0.12
    focus_ring: Optional[Color] = None
    disabled_opacity: float = 0.38


@dataclass
class BorderTokens:
    """Border colors for UI element boundaries.

    Attributes:
        subtle: Subtle border color for separators and dividers.
        default: Default border color for form elements and cards.
        strong: Strong border color for emphasis and focus states.

    Examples:
        >>> borders = BorderTokens(
        ...     subtle=Color(230, 230, 230),
        ...     default=Color(200, 200, 200),
        ...     strong=Color(160, 160, 160)
        ... )
    """

    subtle: Color
    default: Color
    strong: Color


@dataclass
class UniversalTokenSchema:
    """Complete universal token schema for cross-toolkit theming.

    Attributes:
        name: Human-readable name for the theme.
        variant: Theme variant ("light" or "dark").
        surfaces: Surface color tokens.
        content: Content/text color tokens.
        accents: Accent and semantic color tokens.
        states: Interactive state tokens.
        borders: Border color tokens.
        source: Optional source identifier for the tokens.

    Examples:
        >>> schema = UniversalTokenSchema(
        ...     name="My Theme",
        ...     variant="light",
        ...     surfaces=SurfaceTokens(...),
        ...     content=ContentTokens(...),
        ...     accents=AccentTokens(...),
        ...     states=StateTokens(),
        ...     borders=BorderTokens(...),
        ...     source="custom"
        ... )
    """

    name: str
    variant: str  # "light" or "dark"
    surfaces: SurfaceTokens
    content: ContentTokens
    accents: AccentTokens
    states: StateTokens
    borders: BorderTokens
    source: Optional[str] = None
