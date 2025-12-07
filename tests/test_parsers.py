"""Tests for theme parsers."""

import tempfile
from pathlib import Path

import pytest

from unified_theming.parsers import GTKThemeParser, ThemeParseError, ThemeParser


class TestThemeParserBase:
    """Test abstract parser interface."""

    def test_parser_is_abstract(self):
        with pytest.raises(TypeError):
            ThemeParser()

    def test_gtk_parser_is_theme_parser(self):
        parser = GTKThemeParser()
        assert isinstance(parser, ThemeParser)

    def test_get_name(self):
        parser = GTKThemeParser()
        assert parser.get_name() == "GTKThemeParser"


class TestGTKThemeParser:
    """Test GTK theme parser."""

    @pytest.fixture
    def parser(self):
        return GTKThemeParser()

    @pytest.fixture
    def mock_theme(self, tmp_path):
        """Create a mock GTK theme directory."""
        theme_dir = tmp_path / "TestTheme"
        gtk4_dir = theme_dir / "gtk-4.0"
        gtk4_dir.mkdir(parents=True)

        css_content = """
        @define-color theme_bg_color #ffffff;
        @define-color theme_fg_color #1a1a1a;
        @define-color theme_selected_bg_color #3584e4;
        @define-color accent_color #3584e4;
        @define-color success_color #2ec27e;
        @define-color warning_color #f5c211;
        @define-color error_color #e01b24;
        """
        (gtk4_dir / "gtk.css").write_text(css_content)
        return theme_dir

    @pytest.fixture
    def mock_dark_theme(self, tmp_path):
        """Create a mock dark GTK theme."""
        theme_dir = tmp_path / "DarkTheme"
        gtk4_dir = theme_dir / "gtk-4.0"
        gtk4_dir.mkdir(parents=True)

        css_content = """
        @define-color theme_bg_color #1e1e1e;
        @define-color theme_fg_color #ffffff;
        @define-color accent_color #78aeed;
        """
        (gtk4_dir / "gtk.css").write_text(css_content)
        return theme_dir

    def test_can_parse_valid_gtk4_theme(self, parser, mock_theme):
        assert parser.can_parse(mock_theme) is True

    def test_can_parse_invalid_directory(self, parser, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        assert parser.can_parse(empty_dir) is False

    def test_can_parse_file_returns_false(self, parser, tmp_path):
        file_path = tmp_path / "file.txt"
        file_path.write_text("not a theme")
        assert parser.can_parse(file_path) is False

    def test_parse_light_theme(self, parser, mock_theme):
        tokens = parser.parse(mock_theme)

        assert tokens.name == "TestTheme"
        assert tokens.variant == "light"
        assert tokens.surfaces.primary.r == 255  # White bg
        assert tokens.content.primary.r == 26  # Dark text
        assert tokens.source == "gtk"

    def test_parse_dark_theme(self, parser, mock_dark_theme):
        tokens = parser.parse(mock_dark_theme)

        assert tokens.name == "DarkTheme"
        assert tokens.variant == "dark"
        assert tokens.surfaces.primary.r == 30  # Dark bg

    def test_parse_extracts_accent(self, parser, mock_theme):
        tokens = parser.parse(mock_theme)
        # GNOME blue
        assert tokens.accents.primary.r == 53
        assert tokens.accents.primary.g == 132

    def test_parse_extracts_semantic_colors(self, parser, mock_theme):
        tokens = parser.parse(mock_theme)

        assert tokens.accents.success.to_hex() == "#2ec27e"
        assert tokens.accents.warning.to_hex() == "#f5c211"
        assert tokens.accents.error.to_hex() == "#e01b24"

    def test_parse_nonexistent_raises(self, parser, tmp_path):
        with pytest.raises(ThemeParseError):
            parser.parse(tmp_path / "nonexistent")

    def test_parse_empty_theme_raises(self, parser, tmp_path):
        """Theme with no colors should raise."""
        theme_dir = tmp_path / "EmptyTheme"
        gtk4_dir = theme_dir / "gtk-4.0"
        gtk4_dir.mkdir(parents=True)
        (gtk4_dir / "gtk.css").write_text("/* no colors */")

        with pytest.raises(ThemeParseError):
            parser.parse(theme_dir)

    def test_parse_derives_missing_surfaces(self, parser, mock_theme):
        tokens = parser.parse(mock_theme)

        # Schema should have all surface tokens populated
        assert tokens.surfaces.secondary is not None
        assert tokens.surfaces.tertiary is not None
        assert tokens.surfaces.elevated is not None

    def test_parse_rgb_format(self, parser, tmp_path):
        """Test parsing rgb() color format."""
        theme_dir = tmp_path / "RGBTheme"
        gtk4_dir = theme_dir / "gtk-4.0"
        gtk4_dir.mkdir(parents=True)

        css_content = """
        @define-color theme_bg_color rgb(255, 255, 255);
        @define-color theme_fg_color rgb(26, 26, 26);
        """
        (gtk4_dir / "gtk.css").write_text(css_content)

        tokens = parser.parse(theme_dir)
        assert tokens.surfaces.primary.r == 255

    def test_parse_rgba_format(self, parser, tmp_path):
        """Test parsing rgba() color format."""
        theme_dir = tmp_path / "RGBATheme"
        gtk4_dir = theme_dir / "gtk-4.0"
        gtk4_dir.mkdir(parents=True)

        css_content = """
        @define-color theme_bg_color rgba(255, 255, 255, 1.0);
        @define-color theme_fg_color rgba(26, 26, 26, 0.9);
        """
        (gtk4_dir / "gtk.css").write_text(css_content)

        tokens = parser.parse(theme_dir)
        assert tokens.surfaces.primary.r == 255

    def test_schema_has_all_components(self, parser, mock_theme):
        tokens = parser.parse(mock_theme)

        assert tokens.surfaces is not None
        assert tokens.content is not None
        assert tokens.accents is not None
        assert tokens.states is not None
        assert tokens.borders is not None

    def test_states_have_defaults(self, parser, mock_theme):
        tokens = parser.parse(mock_theme)

        assert tokens.states.hover_overlay == 0.08
        assert tokens.states.pressed_overlay == 0.12
        assert tokens.states.disabled_opacity == 0.38


class TestThemeParseError:
    """Test ThemeParseError exception."""

    def test_error_message(self):
        err = ThemeParseError("Test error")
        assert str(err) == "Test error"

    def test_error_with_source(self):
        err = ThemeParseError("Test error", Path("/some/path"))
        assert "/some/path" in str(err)
        assert err.source == Path("/some/path")
