#!/usr/bin/env python3
"""
Example usage of the unified theming token system.

This script demonstrates:
- Creating light and dark token schemas
- Validating tokens for accessibility
- Using color operations for interactive states
- Converting between color spaces
"""

from unified_theming.color import (
    Color,
    OKLCHColor,
    contrast_ratio,
    derive_hover,
    derive_pressed,
    meets_aa,
)
from unified_theming.tokens import (
    create_light_tokens,
    create_dark_tokens,
    validate_tokens,
    ADWAITA_LIGHT,
    ADWAITA_DARK,
)


def main():
    print("=== Unified Theming Token System Demo ===\n")

    # 1. Create custom tokens
    print("1. Creating custom light tokens with blue accent:")
    custom_light = create_light_tokens(
        accent=Color.from_hex("#007acc"),
        name="Custom Blue"
    )
    print(f"   Theme: {custom_light.name}")
    print(f"   Variant: {custom_light.variant}")
    print(f"   Primary surface: {custom_light.surfaces.primary.to_hex()}")
    print(f"   Accent: {custom_light.accents.primary.to_hex()}")
    print()

    # 2. Validate tokens
    print("2. Validating token accessibility:")
    result = validate_tokens(custom_light)
    print(f"   Valid: {result.valid}")
    if result.errors:
        print(f"   Errors: {len(result.errors)}")
        for error in result.errors:
            print(f"     - {error}")
    if result.warnings:
        print(f"   Warnings: {len(result.warnings)}")
        for warning in result.warnings:
            print(f"     - {warning}")
    print()

    # 3. Color space conversions
    print("3. Color space conversions:")
    blue = Color.from_hex("#007acc")
    print(f"   RGB: {blue.to_hex()}")
    oklch = blue.to_oklch()
    print(f"   OKLCH: L={oklch.lightness:.3f}, C={oklch.chroma:.3f}, H={oklch.hue:.1f}")
    back_to_rgb = oklch.to_rgb()
    print(f"   Roundtrip: {back_to_rgb.to_hex()}")
    print()

    # 4. Contrast checking
    print("4. Contrast analysis:")
    fg = custom_light.content.primary
    bg = custom_light.surfaces.primary
    ratio = contrast_ratio(fg, bg)
    aa_pass = meets_aa(fg, bg)
    print(f"   Content/Surface ratio: {ratio:.2f}:1")
    print(f"   Meets WCAG AA: {aa_pass}")
    print()

    # 5. Interactive state derivation
    print("5. Interactive state colors:")
    base = custom_light.surfaces.secondary
    hover = derive_hover(base, custom_light.states.hover_overlay)
    pressed = derive_pressed(base, custom_light.states.pressed_overlay)
    print(f"   Base: {base.to_hex()}")
    print(f"   Hover: {hover.to_hex()}")
    print(f"   Pressed: {pressed.to_hex()}")
    print()

    # 6. Using presets
    print("6. Using Adwaita presets:")
    print(f"   Light accent: {ADWAITA_LIGHT.accents.primary.to_hex()}")
    print(f"   Dark accent: {ADWAITA_DARK.accents.primary.to_hex()}")
    print()

    print("Demo complete! 🎨")


if __name__ == "__main__":
    main()