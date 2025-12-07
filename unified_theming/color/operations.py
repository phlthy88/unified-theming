"""Color operations for deriving interactive states."""

from .spaces import Color, OKLCHColor


def derive_hover(base: Color, overlay: float) -> Color:
    """
    Derive hover state color by applying overlay.

    Uses OKLCH lightness adjustment to preserve hue and chroma.

    Args:
        base: Base color to modify.
        overlay: Overlay opacity (0.0-1.0), positive for lighten, negative for darken.

    Returns:
        Modified color for hover state.

    Examples:
        >>> base = Color(200, 200, 200)
        >>> derive_hover(base, 0.08)
        Color(r=216, g=216, b=216, a=1.0)
    """
    oklch = base.to_oklch()
    lightness = oklch.lightness + overlay
    adjusted = oklch.with_lightness(lightness)
    return adjusted.to_rgb()


def derive_pressed(base: Color, overlay: float) -> Color:
    """
    Derive pressed state color by applying overlay.

    Uses OKLCH lightness adjustment to preserve hue and chroma.

    Args:
        base: Base color to modify.
        overlay: Overlay opacity (0.0-1.0), positive for lighten, negative for darken.

    Returns:
        Modified color for pressed state.

    Examples:
        >>> base = Color(200, 200, 200)
        >>> derive_pressed(base, 0.12)
        Color(r=224, g=224, b=224, a=1.0)
    """
    oklch = base.to_oklch()
    lightness = oklch.lightness + overlay
    adjusted = oklch.with_lightness(lightness)
    return adjusted.to_rgb()
