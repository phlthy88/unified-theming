"""WCAG accessibility calculations for color contrast."""
from .spaces import Color


def contrast_ratio(fg: Color, bg: Color) -> float:
    """
    Calculate WCAG 2.1 contrast ratio between two colors.

    Args:
        fg: Foreground color
        bg: Background color

    Returns:
        Contrast ratio (1.0 to 21.0)
    """
    l1 = fg.luminance()
    l2 = bg.luminance()
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def meets_aa(fg: Color, bg: Color, large_text: bool = False) -> bool:
    """
    Check if colors meet WCAG AA contrast requirements.

    Args:
        fg: Foreground color
        bg: Background color
        large_text: True for large text (18pt+ or 14pt+ bold)

    Returns:
        True if contrast meets AA requirements
    """
    ratio = contrast_ratio(fg, bg)
    return ratio >= 3.0 if large_text else ratio >= 4.5


def meets_aaa(fg: Color, bg: Color, large_text: bool = False) -> bool:
    """
    Check if colors meet WCAG AAA contrast requirements.

    Args:
        fg: Foreground color
        bg: Background color
        large_text: True for large text (18pt+ or 14pt+ bold)

    Returns:
        True if contrast meets AAA requirements
    """
    ratio = contrast_ratio(fg, bg)
    return ratio >= 4.5 if large_text else ratio >= 7.0


def ensure_contrast(fg: Color, bg: Color, min_ratio: float = 4.5) -> Color:
    """
    Adjust foreground color to meet minimum contrast ratio.

    Uses OKLCH lightness adjustment to preserve hue and chroma.

    Args:
        fg: Foreground color to adjust
        bg: Background color (unchanged)
        min_ratio: Minimum contrast ratio (default 4.5 for WCAG AA)

    Returns:
        Adjusted foreground color meeting contrast requirement
    """
    if contrast_ratio(fg, bg) >= min_ratio:
        return fg

    oklch = fg.to_oklch()
    bg_light = bg.luminance() < 0.5
    step = 0.02
    max_iterations = 50

    for _ in range(max_iterations):
        if bg_light:
            oklch = oklch.with_lightness(oklch.lightness + step)
        else:
            oklch = oklch.with_lightness(oklch.lightness - step)

        adjusted = oklch.to_rgb()
        if contrast_ratio(adjusted, bg) >= min_ratio:
            return adjusted

    # Return best effort (white or black)
    return Color(255, 255, 255) if bg_light else Color(0, 0, 0)
