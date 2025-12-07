"""Tests for color space implementations."""

import math

import pytest

from unified_theming.color.spaces import Color, OKLCHColor


class TestColorFromHex:
    """Test hex parsing."""

    def test_six_digit_hex(self):
        c = Color.from_hex("#ff5500")
        assert c.r == 255
        assert c.g == 85
        assert c.b == 0
        assert c.a == 1.0

    def test_three_digit_hex(self):
        c = Color.from_hex("#f50")
        assert c.r == 255
        assert c.g == 85
        assert c.b == 0

    def test_eight_digit_hex_with_alpha(self):
        c = Color.from_hex("#ff550080")
        assert c.r == 255
        assert c.g == 85
        assert c.b == 0
        assert c.a == pytest.approx(0.502, rel=0.01)

    def test_no_hash_prefix(self):
        c = Color.from_hex("3584e4")
        assert c.r == 53
        assert c.g == 132
        assert c.b == 228

    def test_lowercase_hex(self):
        c = Color.from_hex("#aabbcc")
        assert c.r == 170
        assert c.g == 187
        assert c.b == 204


class TestColorToHex:
    """Test hex output."""

    def test_roundtrip_six_digit(self):
        original = "#3584e4"
        c = Color.from_hex(original)
        assert c.to_hex() == original

    def test_with_alpha(self):
        c = Color(255, 0, 0, 0.5)
        assert c.to_hex() == "#ff00007f"  # 0.5 * 255 = 127 = 0x7f

    def test_full_alpha_no_suffix(self):
        c = Color(255, 0, 0, 1.0)
        assert c.to_hex() == "#ff0000"

    def test_black(self):
        c = Color(0, 0, 0)
        assert c.to_hex() == "#000000"

    def test_white(self):
        c = Color(255, 255, 255)
        assert c.to_hex() == "#ffffff"


class TestLinearRGB:
    """Test gamma correction."""

    def test_black_is_zero(self):
        c = Color(0, 0, 0)
        lr, lg, lb = c.to_linear_rgb()
        assert lr == 0
        assert lg == 0
        assert lb == 0

    def test_white_is_one(self):
        c = Color(255, 255, 255)
        lr, lg, lb = c.to_linear_rgb()
        assert lr == pytest.approx(1.0, rel=0.01)
        assert lg == pytest.approx(1.0, rel=0.01)
        assert lb == pytest.approx(1.0, rel=0.01)

    def test_mid_gray_nonlinear(self):
        # sRGB 128 is NOT 0.5 in linear space
        c = Color(128, 128, 128)
        lr, _, _ = c.to_linear_rgb()
        assert lr == pytest.approx(0.2158, rel=0.01)


class TestLuminance:
    """Test WCAG luminance calculation."""

    def test_white_luminance(self):
        c = Color(255, 255, 255)
        assert c.luminance() == pytest.approx(1.0, rel=0.01)

    def test_black_luminance(self):
        c = Color(0, 0, 0)
        assert c.luminance() == 0

    def test_red_luminance(self):
        c = Color(255, 0, 0)
        assert c.luminance() == pytest.approx(0.2126, rel=0.01)

    def test_green_luminance(self):
        c = Color(0, 255, 0)
        assert c.luminance() == pytest.approx(0.7152, rel=0.01)

    def test_blue_luminance(self):
        c = Color(0, 0, 255)
        assert c.luminance() == pytest.approx(0.0722, rel=0.01)


class TestOKLCHConversion:
    """Test OKLCH color space conversion."""

    def test_white_to_oklch(self):
        c = Color(255, 255, 255)
        oklch = c.to_oklch()
        assert oklch.lightness == pytest.approx(1.0, rel=0.01)
        assert oklch.chroma == pytest.approx(0, abs=0.01)

    def test_black_to_oklch(self):
        c = Color(0, 0, 0)
        oklch = c.to_oklch()
        assert oklch.lightness == pytest.approx(0, abs=0.01)
        assert oklch.chroma == pytest.approx(0, abs=0.01)

    def test_red_hue(self):
        c = Color(255, 0, 0)
        oklch = c.to_oklch()
        # Red should be around 29° in OKLCH
        assert 20 < oklch.hue < 40

    def test_green_hue(self):
        c = Color(0, 255, 0)
        oklch = c.to_oklch()
        # Green should be around 142° in OKLCH
        assert 130 < oklch.hue < 150

    def test_blue_hue(self):
        c = Color(0, 0, 255)
        oklch = c.to_oklch()
        # Blue should be around 264° in OKLCH
        assert 260 < oklch.hue < 270

    def test_roundtrip_primary_colors(self):
        """Primary colors should roundtrip accurately."""
        for hex_color in ["#ff0000", "#00ff00", "#0000ff"]:
            original = Color.from_hex(hex_color)
            roundtrip = original.to_oklch().to_rgb()
            assert abs(roundtrip.r - original.r) <= 1
            assert abs(roundtrip.g - original.g) <= 1
            assert abs(roundtrip.b - original.b) <= 1

    def test_roundtrip_gnome_blue(self):
        """GNOME accent blue should roundtrip."""
        original = Color.from_hex("#3584e4")
        roundtrip = original.to_oklch().to_rgb()
        assert abs(roundtrip.r - original.r) <= 1
        assert abs(roundtrip.g - original.g) <= 1
        assert abs(roundtrip.b - original.b) <= 1

    def test_roundtrip_grays(self):
        """Grays should roundtrip accurately."""
        for v in [0, 64, 128, 192, 255]:
            original = Color(v, v, v)
            roundtrip = original.to_oklch().to_rgb()
            assert abs(roundtrip.r - original.r) <= 1
            assert abs(roundtrip.g - original.g) <= 1
            assert abs(roundtrip.b - original.b) <= 1


class TestOKLCHOperations:
    """Test OKLCH manipulation methods."""

    def test_with_lightness(self):
        oklch = OKLCHColor(0.5, 0.1, 180)
        lighter = oklch.with_lightness(0.8)
        assert lighter.lightness == 0.8
        assert lighter.chroma == 0.1
        assert lighter.hue == 180

    def test_with_lightness_clamped(self):
        oklch = OKLCHColor(0.5, 0.1, 180)
        assert oklch.with_lightness(1.5).lightness == 1.0
        assert oklch.with_lightness(-0.5).lightness == 0.0

    def test_with_chroma(self):
        oklch = OKLCHColor(0.5, 0.1, 180)
        saturated = oklch.with_chroma(0.2)
        assert saturated.chroma == 0.2
        assert saturated.lightness == 0.5

    def test_rotate_hue(self):
        oklch = OKLCHColor(0.5, 0.1, 90)
        rotated = oklch.rotate_hue(180)
        assert rotated.hue == 270

    def test_rotate_hue_wraps(self):
        oklch = OKLCHColor(0.5, 0.1, 300)
        rotated = oklch.rotate_hue(120)
        assert rotated.hue == 60
