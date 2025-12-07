"""Tests for WCAG accessibility calculations."""

import pytest

from unified_theming.color.spaces import Color
from unified_theming.color import wcag


class TestContrastRatio:
    """Test contrast ratio calculations."""

    def test_white_black_max_contrast(self):
        white = Color(255, 255, 255)
        black = Color(0, 0, 0)
        assert wcag.contrast_ratio(white, black) == pytest.approx(21.0, rel=0.01)

    def test_same_color_min_contrast(self):
        gray = Color(128, 128, 128)
        assert wcag.contrast_ratio(gray, gray) == pytest.approx(1.0, rel=0.01)

    def test_order_independent(self):
        white = Color(255, 255, 255)
        red = Color(255, 0, 0)
        assert wcag.contrast_ratio(white, red) == wcag.contrast_ratio(red, white)

    def test_white_red(self):
        white = Color(255, 255, 255)
        red = Color(255, 0, 0)
        assert wcag.contrast_ratio(white, red) == pytest.approx(4.0, rel=0.05)


class TestMeetsAA:
    """Test WCAG AA compliance."""

    def test_white_black_passes(self):
        white = Color(255, 255, 255)
        black = Color(0, 0, 0)
        assert wcag.meets_aa(white, black) is True

    def test_low_contrast_fails(self):
        light_gray = Color(200, 200, 200)
        white = Color(255, 255, 255)
        assert wcag.meets_aa(light_gray, white) is False

    def test_large_text_lower_threshold(self):
        fg = Color(119, 119, 119)
        bg = Color(255, 255, 255)
        assert wcag.meets_aa(fg, bg, large_text=False) is False
        assert wcag.meets_aa(fg, bg, large_text=True) is True

    def test_real_world_brand_pair_passes(self):
        fg = Color.from_hex("#1DB954")
        bg = Color.from_hex("#191414")
        assert wcag.meets_aa(fg, bg)

    def test_real_world_brand_pair_fails(self):
        fg = Color.from_hex("#9ea7b3")
        bg = Color.from_hex("#ffffff")
        assert not wcag.meets_aa(fg, bg)


class TestMeetsAAA:
    """Test WCAG AAA compliance."""

    def test_white_black_passes(self):
        white = Color(255, 255, 255)
        black = Color(0, 0, 0)
        assert wcag.meets_aaa(white, black) is True

    def test_moderate_contrast_fails(self):
        fg = Color(96, 96, 96)
        bg = Color(255, 255, 255)
        ratio = wcag.contrast_ratio(fg, bg)
        assert 4.5 < ratio < 7.0
        assert wcag.meets_aaa(fg, bg) is False

    def test_real_world_brand_passes_small_text(self):
        fg = Color.from_hex("#611f69")
        bg = Color.from_hex("#f4ede4")
        assert wcag.meets_aaa(fg, bg)


class TestEnsureContrast:
    """Test contrast adjustment."""

    def test_already_compliant_unchanged(self):
        fg = Color(0, 0, 0)
        bg = Color(255, 255, 255)
        adjusted = wcag.ensure_contrast(fg, bg, 4.5)
        assert adjusted.r == fg.r
        assert adjusted.g == fg.g
        assert adjusted.b == fg.b

    def test_low_contrast_adjusted(self):
        fg = Color(200, 200, 200)
        bg = Color(255, 255, 255)
        adjusted = wcag.ensure_contrast(fg, bg, 4.5)
        assert wcag.contrast_ratio(adjusted, bg) >= 4.5

    def test_dark_bg_lightens_fg(self):
        fg = Color(50, 50, 50)
        bg = Color(30, 30, 30)
        adjusted = wcag.ensure_contrast(fg, bg, 4.5)
        assert wcag.contrast_ratio(adjusted, bg) >= 4.5
        assert adjusted.luminance() > fg.luminance()

    def test_preserves_hue(self):
        fg = Color.from_hex("#3584e4")
        bg = Color.from_hex("#1e1e1e")
        adjusted = wcag.ensure_contrast(fg, bg, 4.5)
        orig_hue = fg.to_oklch().hue
        adj_hue = adjusted.to_oklch().hue
        hue_diff = abs(orig_hue - adj_hue)
        if hue_diff > 180:
            hue_diff = 360 - hue_diff
        assert hue_diff < 15
