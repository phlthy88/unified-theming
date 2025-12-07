"""Integration tests covering parser → renderer pipelines."""

import json
from pathlib import Path

from unified_theming.parsers import GTKThemeParser, JSONTokenParser
from unified_theming.renderers import GTKRenderer, QtRenderer
from unified_theming.tokens import create_light_tokens


def test_gtk_parse_render_roundtrip(tmp_path):
    """Parse a GTK theme and render it back to CSS."""
    tokens = create_light_tokens(name="RoundtripLight")
    renderer = GTKRenderer()
    css = renderer.render(tokens).files[Path("gtk-4.0/gtk.css")]

    theme_path = tmp_path / "RoundtripTheme"
    (theme_path / "gtk-4.0").mkdir(parents=True)
    (theme_path / "gtk-3.0").mkdir(parents=True)
    (theme_path / "gtk-4.0" / "gtk.css").write_text(css)
    (theme_path / "gtk-3.0" / "gtk.css").write_text(css)

    parser = GTKThemeParser()
    parsed_tokens = parser.parse(theme_path)

    output = renderer.render(parsed_tokens)
    generated_css = output.files[Path("gtk-4.0/gtk.css")]

    assert "@define-color theme_bg_color" in generated_css
    assert "theme_fg_color" in generated_css
    assert output.settings["gtk-theme-name"] == parsed_tokens.name


def test_json_to_gtk_pipeline(tmp_path):
    """Parse JSON tokens and render GTK CSS."""
    json_data = {
        "surface": {
            "primary": {"$value": "#ffffff"},
            "secondary": {"$value": "#f6f6f6"},
            "tertiary": {"$value": "#eeeeee"},
        },
        "content": {"primary": {"$value": "#1a1a1a"}},
        "accent": {"primary": {"$value": "#3584e4"}, "success": {"$value": "#2ec27e"}},
    }
    json_path = tmp_path / "tokens.json"
    json_path.write_text(json.dumps(json_data))

    tokens = JSONTokenParser().parse(json_path)
    output = GTKRenderer().render(tokens)
    css = output.files[Path("gtk-4.0/gtk.css")]

    assert "@define-color accent_color" in css
    assert "theme_bg_color" in css
    assert output.settings["gtk-theme-name"] == "tokens"


def test_json_to_qt_pipeline(tmp_path):
    """Parse JSON tokens and render Qt kdeglobals."""
    json_data = {
        "surface": {
            "primary": {"$value": "#ffffff"},
            "secondary": {"$value": "#f4f4f4"},
            "tertiary": {"$value": "#ededed"},
            "elevated": {"$value": "#fdfdfd"},
        },
        "content": {
            "primary": {"$value": "#1a1a1a"},
            "secondary": {"$value": "#5e5e5e"},
            "inverse": {"$value": "#ffffff"},
            "link": {"$value": "#3584e4"},
            "link_visited": {"$value": "#8035e4"},
        },
        "accent": {
            "primary": {"$value": "#3584e4"},
            "primary_container": {"$value": "#d3e5f9"},
            "success": {"$value": "#2ec27e"},
            "warning": {"$value": "#f5c211"},
            "error": {"$value": "#e01b24"},
        },
    }
    json_path = tmp_path / "qt_tokens.json"
    json_path.write_text(json.dumps(json_data))

    tokens = JSONTokenParser().parse(json_path)
    output = QtRenderer().render(tokens)
    kdeglobals = output.files[Path("kdeglobals")]

    assert "[Colors:Window]" in kdeglobals
    assert "ColorScheme=qt_tokens" in kdeglobals
    assert "BackgroundNormal=255,255,255" in kdeglobals
    assert "BackgroundNormal=53,132,228" in kdeglobals  # selection section
    assert output.settings["color-scheme"] == "qt_tokens"
