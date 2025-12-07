"""Default token values for light and dark modes."""

from typing import Optional

from ..color.spaces import Color
from .schema import (
    AccentTokens,
    BorderTokens,
    ContentTokens,
    StateTokens,
    SurfaceTokens,
    UniversalTokenSchema,
)


def create_light_tokens(
    accent: Optional[Color] = None, name: str = "Light"
) -> UniversalTokenSchema:
    """Create default light mode token schema.

    Args:
        accent: Optional accent color, defaults to GNOME blue.
        name: Theme name, defaults to "Light".

    Returns:
        UniversalTokenSchema configured for light mode.

    Examples:
        >>> tokens = create_light_tokens()
        >>> tokens.name
        'Light'
        >>> tokens.variant
        'light'
        >>> tokens.surfaces.primary
        Color(r=255, g=255, b=255, a=1.0)
    """
    if accent is None:
        accent = Color.from_hex("#3584e4")  # GNOME blue

    return UniversalTokenSchema(
        name=name,
        variant="light",
        surfaces=SurfaceTokens(
            primary=Color(255, 255, 255),
            secondary=Color(246, 246, 246),
            tertiary=Color(237, 237, 237),
            elevated=Color(255, 255, 255),
            inverse=Color(30, 30, 30),
        ),
        content=ContentTokens(
            primary=Color(26, 26, 26),
            secondary=Color(94, 94, 94),
            tertiary=Color(140, 140, 140),
            inverse=Color(255, 255, 255),
            link=accent,
            link_visited=Color.from_hex("#8035e4"),
        ),
        accents=AccentTokens(
            primary=accent,
            primary_container=Color.from_hex("#d3e5f9"),
            secondary=Color(128, 128, 128),
            success=Color.from_hex("#2ec27e"),
            warning=Color.from_hex("#f5c211"),
            error=Color.from_hex("#e01b24"),
        ),
        states=StateTokens(
            hover_overlay=0.08,
            pressed_overlay=0.12,
            focus_ring=accent,
            disabled_opacity=0.38,
        ),
        borders=BorderTokens(
            subtle=Color(230, 230, 230),
            default=Color(200, 200, 200),
            strong=Color(160, 160, 160),
        ),
        source="defaults",
    )


def create_dark_tokens(
    accent: Optional[Color] = None, name: str = "Dark"
) -> UniversalTokenSchema:
    """Create default dark mode token schema.

    Args:
        accent: Optional accent color, defaults to lighter blue for dark mode.
        name: Theme name, defaults to "Dark".

    Returns:
        UniversalTokenSchema configured for dark mode.

    Examples:
        >>> tokens = create_dark_tokens()
        >>> tokens.name
        'Dark'
        >>> tokens.variant
        'dark'
        >>> tokens.surfaces.primary
        Color(r=30, g=30, b=30, a=1.0)
    """
    if accent is None:
        accent = Color.from_hex("#78aeed")  # Lighter blue for dark mode

    return UniversalTokenSchema(
        name=name,
        variant="dark",
        surfaces=SurfaceTokens(
            primary=Color(30, 30, 30),
            secondary=Color(43, 43, 43),
            tertiary=Color(56, 56, 56),
            elevated=Color(50, 50, 50),
            inverse=Color(255, 255, 255),
        ),
        content=ContentTokens(
            primary=Color(255, 255, 255),
            secondary=Color(180, 180, 180),
            tertiary=Color(140, 140, 140),
            inverse=Color(26, 26, 26),
            link=accent,
            link_visited=Color.from_hex("#b78aed"),
        ),
        accents=AccentTokens(
            primary=accent,
            primary_container=Color.from_hex("#1a4a7a"),
            secondary=Color(160, 160, 160),
            success=Color.from_hex("#57e389"),
            warning=Color.from_hex("#f8e45c"),
            error=Color.from_hex("#ff7b63"),
        ),
        states=StateTokens(
            hover_overlay=0.12,
            pressed_overlay=0.16,
            focus_ring=accent,
            disabled_opacity=0.38,
        ),
        borders=BorderTokens(
            subtle=Color(60, 60, 60),
            default=Color(80, 80, 80),
            strong=Color(110, 110, 110),
        ),
        source="defaults",
    )


# Pre-built defaults
ADWAITA_LIGHT = create_light_tokens(name="Adwaita")
ADWAITA_DARK = create_dark_tokens(name="Adwaita-dark")
