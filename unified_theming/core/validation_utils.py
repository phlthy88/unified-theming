"""
Utility functions for theme validation, including accessibility checks.
"""

from typing import List, Tuple
from ..color.spaces import Color
from ..color.wcag import contrast_ratio, meets_aa
from ..core.types import ThemeData, ValidationMessage, ValidationLevel

def validate_wcag_contrast(
    theme_data: ThemeData,
    color_pairs: List[Tuple[str, str]],
    component_name: str,
    min_contrast: float = 4.5,  # Default to AA for normal text
) -> List[ValidationMessage]:
    """
    Validate WCAG contrast for a list of foreground/background color pairs.

    Args:
        theme_data: The ThemeData object containing color information.
        color_pairs: A list of (foreground_variable_name, background_variable_name) tuples.
        component_name: The name of the component performing the validation (e.g., "GTK Handler").
        min_contrast: The minimum contrast ratio required (e.g., 4.5 for AA, 7.0 for AAA).

    Returns:
        A list of ValidationMessage objects for any contrast issues found.
    """
    messages: List[ValidationMessage] = []

    for fg_var, bg_var in color_pairs:
        fg_hex = theme_data.colors.get(fg_var)
        bg_hex = theme_data.colors.get(bg_var)

        if fg_hex and bg_hex:
            try:
                fg_color = Color.from_hex(fg_hex)
                bg_color = Color.from_hex(bg_hex)

                ratio = contrast_ratio(fg_color, bg_color)

                if ratio < min_contrast:
                    messages.append(
                        ValidationMessage(
                            level=ValidationLevel.WARNING,
                            message=(
                                f"Insufficient contrast ratio ({ratio:.2f}) for "
                                f"'{fg_var}' (foreground: {fg_hex}) and "
                                f"'{bg_var}' (background: {bg_hex}). "
                                f"Required: {min_contrast:.2f}."
                            ),
                            component=component_name,
                            details=f"Contrast check for {fg_var}/{bg_var}",
                        )
                    )
            except ValueError:
                messages.append(
                    ValidationMessage(
                        level=ValidationLevel.WARNING,
                        message=(
                            f"Could not parse hex color for contrast check: "
                            f"'{fg_var}' ('{fg_hex}') or '{bg_var}' ('{bg_hex}')."
                        ),
                        component=component_name,
                        details=f"Malformed hex color encountered.",
                    )
                )
        # else:
        #     messages.append(
        #         ValidationMessage(
        #             level=ValidationLevel.INFO,
        #             message=f"Skipped contrast check for {fg_var}/{bg_var}: "
        #                     f"one or both color variables not found in theme data.",
        #             component=component_name,
        #         )
        #     )
    return messages
