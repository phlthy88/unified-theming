"""Tests for theme renderers."""

from pathlib import Path

import pytest

from unified_theming.renderers import BaseRenderer, GTKRenderer, RenderedTheme
from unified_theming.tokens import create_dark_tokens, create_light_tokens


class TestBaseRenderer:
    """Test abstract renderer interface."""

    def test_renderer_is_abstract(self):
        with pytest.raises(TypeError):
            BaseRenderer()

    def test_gtk_renderer_is_base_renderer(self):
        renderer = GTKRenderer()
        assert isinstance(renderer, BaseRenderer)

    def test_get_name(self):
        renderer = GTKRenderer()
        assert renderer.get_name() == "GTKRenderer"


class TestRenderedTheme:
    """Test RenderedTheme dataclass."""

    def test_default_values(self):
        theme = RenderedTheme(toolkit="test")
        assert theme.toolkit == "test"
        assert theme.files == {}
        assert theme.settings == {}

    def test_with_files(self):
        theme = RenderedTheme(
            toolkit="gtk",
            files={Path("test.css"): "content"},
            settings={"key": "value"},
        )
        assert Path("test.css") in theme.files
        assert theme.settings["key"] == "value"


class TestGTKRenderer:
    """Test GTK renderer."""

    @pytest.fixture
    def renderer(self):
        return GTKRenderer()

    @pytest.fixture
    def light_tokens(self):
        return create_light_tokens(name="TestLight")

    @pytest.fixture
    def dark_tokens(self):
        return create_dark_tokens(name="TestDark")

    def test_render_returns_rendered_theme(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        assert isinstance(result, RenderedTheme)
        assert result.toolkit == "gtk"

    def test_render_generates_gtk4_css(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        assert Path("gtk-4.0/gtk.css") in result.files

    def test_render_generates_gtk3_css(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        assert Path("gtk-3.0/gtk.css") in result.files

    def test_render_css_has_define_color(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        css = result.files[Path("gtk-4.0/gtk.css")]
        assert "@define-color" in css

    def test_render_css_has_theme_bg(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        css = result.files[Path("gtk-4.0/gtk.css")]
        assert "theme_bg_color" in css

    def test_render_css_has_theme_fg(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        css = result.files[Path("gtk-4.0/gtk.css")]
        assert "theme_fg_color" in css

    def test_render_css_has_accent(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        css = result.files[Path("gtk-4.0/gtk.css")]
        assert "accent_color" in css

    def test_render_css_has_semantic_colors(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        css = result.files[Path("gtk-4.0/gtk.css")]
        assert "success_color" in css
        assert "warning_color" in css
        assert "error_color" in css

    def test_render_light_theme_settings(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        assert result.settings["gtk-theme-name"] == "TestLight"
        assert result.settings["color-scheme"] == "default"

    def test_render_dark_theme_settings(self, renderer, dark_tokens):
        result = renderer.render(dark_tokens)
        assert result.settings["gtk-theme-name"] == "TestDark"
        assert result.settings["color-scheme"] == "prefer-dark"

    def test_render_css_has_hex_colors(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        css = result.files[Path("gtk-4.0/gtk.css")]
        # Should contain hex color format
        assert "#" in css

    def test_render_css_has_borders(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        css = result.files[Path("gtk-4.0/gtk.css")]
        assert "borders" in css

    def test_render_includes_header_comment(self, renderer, light_tokens):
        result = renderer.render(light_tokens)
        css = result.files[Path("gtk-4.0/gtk.css")]
        assert "Generated from" in css
        assert "TestLight" in css
