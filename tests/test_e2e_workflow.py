"""End-to-end workflow tests for Week 3 integration."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from unified_theming.handlers.gtk_handler import GTKHandler
from unified_theming.handlers.gnome_shell_handler import GnomeShellHandler
from unified_theming.parsers import GTKThemeParser, JSONTokenParser
from unified_theming.renderers import GTKRenderer, QtRenderer, GnomeShellRenderer
from unified_theming.tokens import create_light_tokens, create_dark_tokens


class TestFullWorkflow:
    """Test complete theme workflow: parse → tokens → render → apply."""

    def test_tokens_to_all_renderers(self):
        """Tokens should render to all supported toolkits."""
        tokens = create_dark_tokens(name="UnifiedDark")

        gtk_output = GTKRenderer().render(tokens)
        qt_output = QtRenderer().render(tokens)
        shell_output = GnomeShellRenderer().render(tokens)

        # All renderers produce output
        assert gtk_output.files
        assert qt_output.files
        assert shell_output.files

        # Theme name propagates
        assert gtk_output.settings["gtk-theme-name"] == "UnifiedDark"
        assert qt_output.settings["color-scheme"] == "UnifiedDark"
        assert shell_output.settings["theme-name"] == "UnifiedDark"

    def test_json_to_all_toolkits(self, tmp_path):
        """JSON tokens should render to GTK, Qt, and GNOME Shell."""
        json_data = {
            "name": "CustomTheme",
            "variant": "dark",
            "surface": {
                "primary": {"$value": "#1e1e1e"},
                "secondary": {"$value": "#2b2b2b"},
                "tertiary": {"$value": "#383838"},
                "elevated": {"$value": "#323232"},
            },
            "content": {
                "primary": {"$value": "#ffffff"},
                "secondary": {"$value": "#b4b4b4"},
                "inverse": {"$value": "#1a1a1a"},
                "link": {"$value": "#78aeed"},
                "link_visited": {"$value": "#b78aed"},
            },
            "accent": {
                "primary": {"$value": "#78aeed"},
                "primary_container": {"$value": "#1a4a7a"},
                "success": {"$value": "#57e389"},
                "warning": {"$value": "#f8e45c"},
                "error": {"$value": "#ff7b63"},
            },
        }
        json_path = tmp_path / "custom.json"
        json_path.write_text(json.dumps(json_data))

        tokens = JSONTokenParser().parse(json_path)

        gtk_css = GTKRenderer().render(tokens).files[Path("gtk-4.0/gtk.css")]
        qt_ini = QtRenderer().render(tokens).files[Path("kdeglobals")]
        shell_css = (
            GnomeShellRenderer()
            .render(tokens)
            .files[Path("gnome-shell/gnome-shell-custom.css")]
        )

        # Dark theme colors present
        assert "#1e1e1e" in gtk_css
        assert "30,30,30" in qt_ini or "BackgroundNormal" in qt_ini
        assert "#1e1e1e" in shell_css

    @patch("unified_theming.handlers.gtk_handler.write_file_with_backup")
    @patch.object(GTKHandler, "is_available", return_value=False)
    def test_handler_applies_rendered_tokens(self, mock_avail, mock_write, tmp_path):
        """Handler should apply tokens via renderer."""
        handler = GTKHandler()
        handler.config_dir = tmp_path
        mock_write.return_value = True

        tokens = create_light_tokens(name="ApplyTest")
        result = handler.apply_from_tokens(tokens)

        assert result is True
        assert mock_write.call_count == 2  # gtk-3.0 and gtk-4.0

    @patch("unified_theming.handlers.gnome_shell_handler.write_file_with_backup")
    def test_gnome_shell_handler_applies_tokens(self, mock_write, tmp_path):
        """GNOME Shell handler should apply tokens via renderer."""
        handler = GnomeShellHandler()
        handler.config_dir = tmp_path
        mock_write.return_value = True

        tokens = create_dark_tokens(name="ShellTest")
        result = handler.apply_from_tokens(tokens)

        assert result is True
        content = mock_write.call_args[0][1]
        assert "ShellTest" in content
        assert "@define-color panel_bg_color" in content


class TestParserRendererConsistency:
    """Verify parsers and renderers produce consistent output."""

    def test_gtk_roundtrip_preserves_colors(self, tmp_path):
        """GTK parse → render should preserve key colors."""
        original = create_light_tokens(name="Roundtrip")
        renderer = GTKRenderer()

        # Render to CSS
        css = renderer.render(original).files[Path("gtk-4.0/gtk.css")]

        # Write theme
        theme_dir = tmp_path / "RoundtripTheme"
        (theme_dir / "gtk-4.0").mkdir(parents=True)
        (theme_dir / "gtk-3.0").mkdir(parents=True)
        (theme_dir / "gtk-4.0" / "gtk.css").write_text(css)
        (theme_dir / "gtk-3.0" / "gtk.css").write_text(css)

        # Parse back
        parsed = GTKThemeParser().parse(theme_dir)

        # Key colors should match
        assert parsed.surfaces.primary.to_hex() == original.surfaces.primary.to_hex()
        assert parsed.accents.primary.to_hex() == original.accents.primary.to_hex()

    def test_all_renderers_handle_light_and_dark(self):
        """All renderers should handle both light and dark variants."""
        light = create_light_tokens()
        dark = create_dark_tokens()

        for renderer in [GTKRenderer(), QtRenderer(), GnomeShellRenderer()]:
            light_out = renderer.render(light)
            dark_out = renderer.render(dark)

            assert light_out.files
            assert dark_out.files


class TestWeek3Metrics:
    """Verify Week 3 success metrics."""

    def test_handler_integration_gtk(self):
        """GTK handler should have renderer integration."""
        handler = GTKHandler()
        assert hasattr(handler, "renderer")
        assert hasattr(handler, "apply_from_tokens")

    def test_handler_integration_gnome_shell(self):
        """GNOME Shell handler should have renderer integration."""
        handler = GnomeShellHandler()
        assert hasattr(handler, "renderer")
        assert hasattr(handler, "apply_from_tokens")

    def test_renderers_exported(self):
        """All renderers should be importable from package."""
        from unified_theming.renderers import (
            GTKRenderer,
            QtRenderer,
            GnomeShellRenderer,
        )

        assert GTKRenderer
        assert QtRenderer
        assert GnomeShellRenderer
