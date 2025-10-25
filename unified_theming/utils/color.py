"""
Color utilities for Unified Theming Application.

This module provides utility functions for color format conversions,
validation, and translation between different toolkit color systems.
"""

import re
from typing import Dict, Optional, Tuple

from ..core.exceptions import ColorValidationError
from ..core.types import ColorFormat


def validate_color_format(color_value: str) -> bool:
    """
    Validate if a color value is in a valid format.

    Args:
        color_value: Color value string to validate

    Returns:
        True if color format is valid, False otherwise
    """
    # Normalize the color value
    original_value = color_value
    color_value = color_value.strip().lower()

    # Check hex format with value validation
    hex_match = re.match(r"^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$", color_value)
    if hex_match:
        return True

    # Check RGB format
    rgb_match = re.match(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$", color_value)
    if rgb_match:
        r, g, b = [int(x) for x in rgb_match.groups()]
        # RGB values must be between 0 and 255
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            return True
        return False

    # Check RGBA format
    rgba_match = re.match(
        r"rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(0|1|0?\.\d+)\s*\)$",
        color_value,
    )
    if rgba_match:
        r_str, g_str, b_str, a_str = rgba_match.groups()
        r, g, b = int(r_str), int(g_str), int(b_str)
        a = float(a_str)
        # RGB values must be between 0 and 255, alpha between 0 and 1
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0 <= a <= 1:
            return True
        return False

    # Check HSL format
    hsl_match = re.match(
        r"hsl\s*\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)$", color_value
    )
    if hsl_match:
        h, s, l = [int(x) for x in hsl_match.groups()]
        # H value must be 0-360, S and L must be 0-100
        if 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100:
            return True
        return False

    # Check HSLA format
    hsla_match = re.match(
        r"hsla\s*\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*,\s*(0|1|0?\.\d+)\s*\)$",
        color_value,
    )
    if hsla_match:
        h_str, s_str, l_str, a_str = hsla_match.groups()
        h, s, l = int(h_str), int(s_str), int(l_str)
        a = float(a_str)
        # H value must be 0-360, S and L must be 0-100, alpha must be 0-1
        if 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100 and 0 <= a <= 1:
            return True
        return False

    # Check for named colors
    named_colors = {
        "aqua",
        "black",
        "blue",
        "fuchsia",
        "gray",
        "green",
        "lime",
        "maroon",
        "navy",
        "olive",
        "purple",
        "red",
        "silver",
        "teal",
        "white",
        "yellow",
        "orange",
        "pink",
        "turquoise",
        "violet",
        "wheat",
        "tan",
        "plum",
        "chocolate",
        "salmon",
        "coral",
        "firebrick",
        "indigo",
        "gold",
        "tomato",
        "cyan",
        "crimson",
        "darkblue",
        "darkcyan",
        "darkgoldenrod",
        "darkgray",
        "darkgreen",
        "darkkhaki",
        "darkmagenta",
        "darkolivegreen",
        "darkorange",
        "darkorchid",
        "darkred",
        "darksalmon",
        "darkseagreen",
        "darkslateblue",
        "darkslategray",
        "darkturquoise",
        "darkviolet",
        "deeppink",
        "deepskyblue",
        "dimgray",
        "dodgerblue",
        "forestgreen",
        "goldenrod",
        "gray",
        "indianred",
        "indigo",
        "lavenderblush",
        "lawngreen",
        "lemonchiffon",
        "lightcoral",
        "lightcyan",
        "lightgray",
        "lightgreen",
        "lightpink",
        "magenta",
        "mediumvioletred",
        "olivedrab",
        "orangered",
        "orchid",
        "palevioletred",
        "peru",
        "plum",
        "rosybrown",
        "royalblue",
        "saddlebrown",
        "salmon",
        "sandybrown",
        "seagreen",
        "sienna",
        "skyblue",
        "slateblue",
        "slategray",
        "springgreen",
        "steelblue",
        "violet",
        "yellowgreen",
        "rebeccapurple",
    }

    if color_value in named_colors:
        return True

    return False


def normalize_color_format(
    color_value: str, target_format: ColorFormat = ColorFormat.HEX
) -> str:
    """
    Normalize a color value to a specific format.

    Args:
        color_value: Color value to normalize
        target_format: Target format (defaults to HEX)

    Returns:
        Normalized color value in requested format

    Raises:
        ColorValidationError: If color value is invalid or format conversion fails
    """
    if not validate_color_format(color_value):
        raise ColorValidationError("unknown", color_value, "Invalid color format")

    color_value = color_value.strip().lower()

    if target_format == ColorFormat.HEX:
        return _to_hex(color_value)
    elif target_format == ColorFormat.RGB:
        return _to_rgb(color_value)
    elif target_format == ColorFormat.RGBA:
        return _to_rgba(color_value)
    elif target_format == ColorFormat.HSL:
        return _to_hsl(color_value)
    elif target_format == ColorFormat.NAMED:
        return _to_named(color_value)
    else:
        return color_value  # Return as is for unknown formats


def _to_hex(color_value: str) -> str:
    """Convert color to hex format."""
    color_value = color_value.strip().lower()

    # If already hex format
    if color_value.startswith("#"):
        # Expand #RGB to #RRGGBB
        if len(color_value) == 4:
            return f"#{color_value[1]*2}{color_value[2]*2}{color_value[3]*2}".upper()
        return color_value.upper()

    # If RGB format
    if color_value.startswith("rgb("):
        # Extract RGB values
        match = re.match(
            r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color_value, re.IGNORECASE
        )
        if match:
            r, g, b = [int(x) for x in match.groups()]
            return f"#{r:02x}{g:02x}{b:02x}".upper()

    # If RGBA format
    if color_value.startswith("rgba("):
        # Extract RGB values (ignore alpha)
        match = re.match(
            r"rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)",
            color_value,
            re.IGNORECASE,
        )
        if match:
            r, g, b = [int(x) for x in match.groups()]
            return f"#{r:02x}{g:02x}{b:02x}".upper()

    # If HSL format
    if color_value.startswith("hsl("):
        # Convert HSL to RGB then to hex
        match = re.match(
            r"hsl\s*\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)",
            color_value,
            re.IGNORECASE,
        )
        if match:
            h, s, l = [int(x) for x in match.groups()]
            r, g, b = hsl_to_rgb(h, s, l)
            return f"#{r:02x}{g:02x}{b:02x}".upper()

    # If named color, convert to hex
    named_colors = {
        "black": "#000000",
        "white": "#FFFFFF",
        "red": "#FF0000",
        "green": "#008000",
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "cyan": "#00FFFF",
        "magenta": "#FF00FF",
        "orange": "#FFA500",
        "purple": "#800080",
        "brown": "#A52A2A",
        "pink": "#FFC0CB",
        "gray": "#808080",
        "silver": "#C0C0C0",
        "gold": "#FFD700",
        "violet": "#EE82EE",
    }

    if color_value in named_colors:
        return named_colors[color_value]

    # If we can't convert, return the original
    return color_value


def _to_rgb(color_value: str) -> str:
    """Convert color to RGB format."""
    color_value = color_value.strip().lower()

    # If already RGB format
    if color_value.startswith("rgb("):
        return color_value

    # If RGBA format, convert to RGB
    if color_value.startswith("rgba("):
        match = re.match(
            r"rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)",
            color_value,
            re.IGNORECASE,
        )
        if match:
            r, g, b = [int(x) for x in match.groups()]
            return f"rgb({r}, {g}, {b})"

    # If hex format, convert to RGB
    if color_value.startswith("#"):
        hex_color = color_value[1:]
        if len(hex_color) == 3:
            hex_color = f"{hex_color[0]*2}{hex_color[1]*2}{hex_color[2]*2}"

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"rgb({r}, {g}, {b})"
        except ValueError:
            pass

    # If HSL format, convert to RGB
    if color_value.startswith("hsl("):
        match = re.match(
            r"hsl\s*\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)",
            color_value,
            re.IGNORECASE,
        )
        if match:
            h, s, l = [int(x) for x in match.groups()]
            r, g, b = hsl_to_rgb(h, s, l)
            return f"rgb({r}, {g}, {b})"

    # If named color, convert to RGB
    named_colors = {
        "black": "rgb(0, 0, 0)",
        "white": "rgb(255, 255, 255)",
        "red": "rgb(255, 0, 0)",
        "green": "rgb(0, 128, 0)",
        "blue": "rgb(0, 0, 255)",
        "yellow": "rgb(255, 255, 0)",
        "cyan": "rgb(0, 255, 255)",
        "magenta": "rgb(255, 0, 255)",
        "orange": "rgb(255, 165, 0)",
        "purple": "rgb(128, 0, 128)",
        "brown": "rgb(165, 42, 42)",
        "pink": "rgb(255, 192, 203)",
        "gray": "rgb(128, 128, 128)",
        "silver": "rgb(192, 192, 192)",
        "gold": "rgb(255, 215, 0)",
        "violet": "rgb(238, 130, 238)",
    }

    if color_value in named_colors:
        return named_colors[color_value]

    # If we can't convert, return the original
    return color_value


def _to_rgba(color_value: str) -> str:
    """Convert color to RGBA format."""
    color_value = color_value.strip().lower()

    # If already RGBA format
    if color_value.startswith("rgba("):
        return color_value

    # If RGB format, convert to RGBA with full opacity
    if color_value.startswith("rgb("):
        match = re.match(
            r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color_value, re.IGNORECASE
        )
        if match:
            r, g, b = [int(x) for x in match.groups()]
            return f"rgba({r}, {g}, {b}, 1.0)"

    # If hex format, convert to RGBA
    if color_value.startswith("#"):
        hex_color = color_value[1:]
        if len(hex_color) == 3:
            hex_color = f"{hex_color[0]*2}{hex_color[1]*2}{hex_color[2]*2}"
        elif len(hex_color) == 8:  # Has alpha
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                a = int(hex_color[6:8], 16) / 255.0
                return f"rgba({r}, {g}, {b}, {a:.3f})"
            except ValueError:
                pass

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"rgba({r}, {g}, {b}, 1.0)"
        except ValueError:
            pass

    # For other formats, convert to RGB first then RGBA
    rgb = _to_rgb(color_value)
    if rgb.startswith("rgb("):
        return rgb.replace("rgb(", "rgba(", 1).replace(")", ", 1.0)", 1)

    # If we can't convert, return the original
    return color_value


def _to_hsl(color_value: str) -> str:
    """Convert color to HSL format."""
    color_value = color_value.strip().lower()

    # If already HSL format
    if color_value.startswith("hsl("):
        return color_value

    # If hex format, convert to HSL
    if color_value.startswith("#"):
        hex_color = color_value[1:]
        if len(hex_color) == 3:
            hex_color = f"{hex_color[0]*2}{hex_color[1]*2}{hex_color[2]*2}"

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            h, s, l = rgb_to_hsl(r, g, b)
            return f"hsl({h}, {s}%, {l}%)"
        except ValueError:
            pass

    # If RGB format, convert to HSL
    if color_value.startswith("rgb("):
        match = re.match(
            r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color_value, re.IGNORECASE
        )
        if match:
            r, g, b = [int(x) for x in match.groups()]
            h, s, l = rgb_to_hsl(r, g, b)
            return f"hsl({h}, {s}%, {l}%)"

    # If RGBA format, convert to HSL (ignore alpha)
    if color_value.startswith("rgba("):
        match = re.match(
            r"rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)",
            color_value,
            re.IGNORECASE,
        )
        if match:
            r, g, b = [int(x) for x in match.groups()]
            h, s, l = rgb_to_hsl(r, g, b)
            return f"hsl({h}, {s}%, {l}%)"

    # If named color, convert to HSL
    rgb = _to_rgb(color_value)
    if rgb.startswith("rgb("):
        match = re.match(
            r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", rgb, re.IGNORECASE
        )
        if match:
            r, g, b = [int(x) for x in match.groups()]
            h, s, l = rgb_to_hsl(r, g, b)
            return f"hsl({h}, {s}%, {l}%)"

    # If we can't convert, return the original
    return color_value


def _to_named(color_value: str) -> str:
    """Convert color to named format (if possible)."""
    color_value = color_value.strip().lower()

    # First convert to hex to identify the color
    hex_color = _to_hex(color_value)

    # Known named colors with their hex values (uppercase)
    named_colors = {
        "#000000": "black",
        "#FFFFFF": "white",
        "#FF0000": "red",
        "#008000": "green",
        "#0000FF": "blue",
        "#FFFF00": "yellow",
        "#00FFFF": "cyan",
        "#FF00FF": "magenta",
        "#FFA500": "orange",
        "#800080": "purple",
        "#A52A2A": "brown",
        "#FFC0CB": "pink",
        "#808080": "gray",
        "#C0C0C0": "silver",
        "#FFD700": "gold",
        "#EE82EE": "violet",
    }

    if hex_color in named_colors:
        return named_colors[hex_color]

    # If we can't convert, return the original
    return color_value


def hsl_to_rgb(h: int, s: int, l: int) -> Tuple[int, int, int]:
    """
    Convert HSL color to RGB.

    Args:
        h: Hue (0-360)
        s: Saturation (0-100)
        l: Lightness (0-100)

    Returns:
        Tuple of (r, g, b) values in range 0-255
    """
    h_norm = h / 360.0
    s_norm = s / 100.0
    l_norm = l / 100.0

    if s_norm == 0:
        r = g = b = l_norm
    else:

        def hue2rgb(p: float, q: float, t: float) -> float:
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = l_norm * (1 + s_norm) if l_norm < 0.5 else l_norm + s_norm - l_norm * s_norm
        p = 2 * l_norm - q
        r = hue2rgb(p, q, h_norm + 1 / 3)
        g = hue2rgb(p, q, h_norm)
        b = hue2rgb(p, q, h_norm - 1 / 3)

    return round(r * 255), round(g * 255), round(b * 255)


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """
    Convert RGB color to HSL.

    Args:
        r: Red (0-255)
        g: Green (0-255)
        b: Blue (0-255)

    Returns:
        Tuple of (h, s, l) values (h in 0-360, s and l in 0-100)
    """
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    max_val = max(r_norm, g_norm, b_norm)
    min_val = min(r_norm, g_norm, b_norm)
    diff = max_val - min_val

    # Lightness
    l_val = (max_val + min_val) / 2

    # Saturation
    if diff == 0:
        s_val = 0.0
    else:
        s_val = (
            diff / (2 - max_val - min_val)
            if l_val > 0.5
            else diff / (max_val + min_val)
        )

    # Hue
    if diff == 0:
        h_val = 0.0
    elif max_val == r_norm:
        h_val = (g_norm - b_norm) / diff + (6 if g_norm < b_norm else 0)
    elif max_val == g_norm:
        h_val = (b_norm - r_norm) / diff + 2
    elif max_val == b_norm:
        h_val = (r_norm - g_norm) / diff + 4

    h_result = round(h_val * 60)
    s_result = round(s_val * 100)
    l_result = round(l_val * 100)

    return h_result, s_result, l_result


def gtk_to_qt_colors(gtk_colors: Dict[str, str]) -> Dict[str, str]:
    """
    Translate GTK color variables to Qt equivalents.

    Args:
        gtk_colors: Dictionary of GTK color names to values

    Returns:
        Dictionary of Qt color names to values
    """
    # Mapping from GTK to Qt color variables
    gtk_to_qt_mapping = {
        "theme_bg_color": "BackgroundNormal",
        "theme_fg_color": "ForegroundNormal",
        "theme_base_color": "Base",
        "theme_text_color": "Text",
        "theme_selected_bg_color": "Highlight",
        "theme_selected_fg_color": "HighlightedText",
        "insensitive_bg_color": "BackgroundInactive",
        "insensitive_fg_color": "ForegroundInactive",
        "link_color": "Link",
        "visited_link_color": "VisitedLink",
        "success_color": "ForegroundPositive",
        "warning_color": "ForegroundNeutral",
        "error_color": "ForegroundNegative",
    }

    qt_colors = {}

    for gtk_color, qt_color in gtk_to_qt_mapping.items():
        if gtk_color in gtk_colors:
            try:
                # Convert GTK color format to Qt format (RGB values)
                gtk_color_value = gtk_colors[gtk_color]
                qt_color_value = gtk_color_to_qt_format(gtk_color_value)
                qt_colors[qt_color] = qt_color_value
            except ColorValidationError as e:
                # If translation fails, skip this color
                continue

    return qt_colors


def gtk_color_to_qt_format(gtk_color: str) -> str:
    """
    Convert a GTK color format to Qt RGB format (r,g,b).

    Args:
        gtk_color: Color in GTK format (e.g., #RRGGBB, rgba(...))

    Returns:
        Color in Qt format (r,g,b) where r,g,b are 0-255

    Raises:
        ColorValidationError: If color format is invalid
    """
    gtk_color = gtk_color.strip()

    # Handle hex format (#RRGGBB or #RGB)
    if gtk_color.startswith("#"):
        gtk_color = gtk_color[1:]  # Remove #

        if len(gtk_color) == 3:  # #RGB format
            gtk_color = "".join([c * 2 for c in gtk_color])  # Expand to #RRGGBB
        elif len(gtk_color) != 6:
            raise ColorValidationError(
                "unknown", gtk_color, f"Invalid hex color format: {gtk_color}"
            )

        try:
            r = int(gtk_color[0:2], 16)
            g = int(gtk_color[2:4], 16)
            b = int(gtk_color[4:6], 16)
            return f"{r},{g},{b}"
        except ValueError:
            raise ColorValidationError(
                "unknown", gtk_color, f"Invalid hex color: {gtk_color}"
            )

    # Handle rgb() format
    elif gtk_color.lower().startswith("rgb("):
        # Extract numbers from rgb(r, g, b)
        match = re.search(
            r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", gtk_color, re.IGNORECASE
        )
        if match:
            r_str, g_str, b_str = match.groups()
            return f"{r_str},{g_str},{b_str}"
        else:
            raise ColorValidationError(
                "unknown", gtk_color, f"Invalid RGB format: {gtk_color}"
            )

    # Handle rgba() format (ignore alpha)
    elif gtk_color.lower().startswith("rgba("):
        # Extract numbers from rgba(r, g, b, a)
        match = re.search(
            r"rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)",
            gtk_color,
            re.IGNORECASE,
        )
        if match:
            r_str, g_str, b_str = match.groups()
            return f"{r_str},{g_str},{b_str}"
        else:
            raise ColorValidationError(
                "unknown", gtk_color, f"Invalid RGBA format: {gtk_color}"
            )

    # For other formats, raise an error
    raise ColorValidationError(
        "unknown", gtk_color, f"Unsupported color format: {gtk_color}"
    )
