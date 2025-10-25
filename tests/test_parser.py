"""
Tests for Unified Theme Parser.
"""

import pytest

from unified_theming.core.types import Toolkit


def test_discover_themes(parser, tmp_theme_dir, valid_theme):
    """Test theme discovery."""
    # Add the temp directory to the parser's search paths
    parser.theme_directories = [tmp_theme_dir.parent]

    themes = parser.discover_themes()

    assert "ValidTheme" in themes
    assert themes["ValidTheme"].name == "ValidTheme"


def test_parse_theme(parser, valid_theme):
    """Test parsing a valid theme."""
    theme_info = parser.parse_theme(valid_theme)

    assert theme_info.name == "ValidTheme"
    assert Toolkit.GTK3 in theme_info.supported_toolkits
    assert Toolkit.GTK4 in theme_info.supported_toolkits


def test_extract_colors(parser, valid_theme):
    """Test color extraction."""
    colors = parser.extract_colors(valid_theme, "gtk4")

    assert "theme_bg_color" in colors
    assert colors["theme_bg_color"] == "#ffffff"
    assert len(colors) >= 4


def test_validate_theme(parser, valid_theme):
    """Test theme validation."""
    result = parser.validate_theme(valid_theme)

    assert result.valid is True
    assert not result.has_errors()
