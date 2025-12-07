"""Tests for token-based GNOME Shell handler integration."""

from unittest.mock import patch

from unified_theming.handlers.gnome_shell_handler import GnomeShellHandler
from unified_theming.renderers.gnome_shell import GnomeShellRenderer
from unified_theming.tokens.defaults import create_dark_tokens, create_light_tokens


class TestGnomeShellHandlerTokenIntegration:
    """Ensure GnomeShellHandler works with GnomeShellRenderer and tokens."""

    def test_handler_has_renderer(self):
        """Handler should expose a renderer instance."""
        handler = GnomeShellHandler()
        assert hasattr(handler, "renderer")
        assert isinstance(handler.renderer, GnomeShellRenderer)

    @patch("unified_theming.handlers.gnome_shell_handler.write_file_with_backup")
    def test_apply_from_tokens_writes_css(self, mock_write, tmp_path):
        """apply_from_tokens should render and write shell CSS."""
        handler = GnomeShellHandler()
        handler.config_dir = tmp_path

        mock_write.return_value = True
        tokens = create_light_tokens(name="ShellTokens")

        result = handler.apply_from_tokens(tokens)

        assert result is True
        expected_path = tmp_path / "gnome-shell" / "gnome-shell-custom.css"

        call_args = mock_write.call_args
        assert call_args[0][0] == expected_path
        content = call_args[0][1]
        assert "ShellTokens" in content
        assert "@define-color panel_bg_color #ffffff;" in content

    @patch("unified_theming.handlers.gnome_shell_handler.write_file_with_backup")
    def test_apply_from_tokens_dark_theme(self, mock_write, tmp_path):
        """apply_from_tokens should work with dark tokens."""
        handler = GnomeShellHandler()
        handler.config_dir = tmp_path

        mock_write.return_value = True
        tokens = create_dark_tokens(name="NightShell")

        result = handler.apply_from_tokens(tokens)

        assert result is True
        content = mock_write.call_args[0][1]
        assert "NightShell" in content
        assert "@define-color panel_bg_color #1e1e1e;" in content
        assert "@define-color selected_bg_color" in content

    @patch("unified_theming.handlers.gnome_shell_handler.write_file_with_backup")
    def test_apply_from_tokens_returns_false_on_write_failure(
        self, mock_write, tmp_path
    ):
        """apply_from_tokens should surface write failures."""
        handler = GnomeShellHandler()
        handler.config_dir = tmp_path

        mock_write.return_value = False
        tokens = create_light_tokens()

        result = handler.apply_from_tokens(tokens)

        assert result is False

    @patch("unified_theming.handlers.gnome_shell_handler.write_file_with_backup")
    def test_apply_from_tokens_creates_parent_directories(self, mock_write, tmp_path):
        """apply_from_tokens should ensure config directories exist."""
        handler = GnomeShellHandler()
        handler.config_dir = tmp_path / "nested" / "config"

        mock_write.return_value = True
        tokens = create_light_tokens()

        handler.apply_from_tokens(tokens)

        assert handler.config_dir.exists()
        assert (handler.config_dir / "gnome-shell").exists()
