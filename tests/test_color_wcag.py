"""Tests for WCAG accessibility calculations."""

import pytest

from unified_theming.color.spaces import Color
from unified_theming.color.wcag import (
    contrast_ratio,
    ensure_contrast,
    meets_aa,
    meets_aaa,
)


class TestContrastRatio:
    """Test contrast ratio calculations."""

    def test_white_black_max_contrast(self):
        white = Color(255, 255, 255)
        black = Color(0, 0, 0)
        assert contrast_ratio(white, black) == pytest.approx(21.0, rel=0.01)

    def test_same_color_min_contrast(self):
        gray = Color(128, 128, 128)
        assert contrast_ratio(gray, gray) == pytest.approx(1.0, rel=0.01)

    def test_order_independent(self):
        white = Color(255, 255, 255)
        red = Color(255, 0, 0)
        assert contrast_ratio(white, red) == contrast_ratio(red, white)

    def test_white_red(self):
        white = Color(255, 255, 255)
        red = Color(255, 0, 0)
        assert contrast_ratio(white, red) == pytest.approx(4.0, rel=0.05)


class TestMeetsAA:
    """Test WCAG AA compliance."""

    def test_white_black_passes(self):
        white = Color(255, 255, 255)
        black = Color(0, 0, 0)
        assert meets_aa(white, black) is True

    def test_low_contrast_fails(self):
        light_gray = Color(200, 200, 200)
        white = Color(255, 255, 255)
        assert meets_aa(light_gray, white) is False

    def test_large_text_lower_threshold(self):
        # Color pair that passes for large text but not normal
        fg = Color(119, 119, 119)  # ~3.5:1 on white
        bg = Color(255, 255, 255)
        assert meets_aa(fg, bg, large_text=False) is False
        assert meets_aa(fg, bg, large_text=True) is True


class TestMeetsAAA:
    """Test WCAG AAA compliance."""

    def test_white_black_passes(self):
        white = Color(255, 255, 255)
        black = Color(0, 0, 0)
        assert meets_aaa(white, black) is True

    def test_moderate_contrast_fails(self):
        # 4.5:1 passes AA but not AAA for normal text
        fg = Color(96, 96, 96)
        bg = Color(255, 255, 255)
        ratio = contrast_ratio(fg, bg)
        assert 4.5 < ratio < 7.0
        assert meets_aaa(fg, bg) is False


class TestEnsureContrast:
    """Test contrast adjustment."""

    def test_already_compliant_unchanged(self):
        fg = Color(0, 0, 0)
        bg = Color(255, 255, 255)
        adjusted = ensure_contrast(fg, bg, 4.5)
        assert adjusted.r == fg.r
        assert adjusted.g == fg.g
        assert adjusted.b == fg.b

    def test_low_contrast_adjusted(self):
        fg = Color(200, 200, 200)  # Light gray on white
        bg = Color(255, 255, 255)
        adjusted = ensure_contrast(fg, bg, 4.5)
        assert contrast_ratio(adjusted, bg) >= 4.5

    def test_dark_bg_lightens_fg(self):
        fg = Color(50, 50, 50)  # Dark gray on dark bg
        bg = Color(30, 30, 30)
        adjusted = ensure_contrast(fg, bg, 4.5)
        assert contrast_ratio(adjusted, bg) >= 4.5
        assert adjusted.luminance() > fg.luminance()

    def test_preserves_hue(self):
        fg = Color.from_hex("#3584e4")  # GNOME blue
        bg = Color.from_hex("#1e1e1e")  # Dark bg
        adjusted = ensure_contrast(fg, bg, 4.5)

        # Hue should be similar (within 10 degrees)
        orig_hue = fg.to_oklch().hue
        adj_hue = adjusted.to_oklch().hue
        hue_diff = abs(orig_hue - adj_hue)
        if hue_diff > 180:
            hue_diff = 360 - hue_diff
        assert hue_diff < 15
