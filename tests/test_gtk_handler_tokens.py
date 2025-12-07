"""Tests for GTKHandler token integration."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from unified_theming.handlers.gtk_handler import GTKHandler
from unified_theming.renderers.gtk import GTKRenderer
from unified_theming.tokens.defaults import create_light_tokens, create_dark_tokens


class TestGTKHandlerTokenIntegration:
    """Test GTKHandler integration with GTKRenderer."""

    def test_handler_has_renderer(self):
        """GTKHandler should have a GTKRenderer instance."""
        handler = GTKHandler()
        assert hasattr(handler, "renderer")
        assert isinstance(handler.renderer, GTKRenderer)

    @patch("unified_theming.handlers.gtk_handler.write_file_with_backup")
    @patch.object(GTKHandler, "is_available", return_value=False)
    def test_apply_from_tokens_writes_css(self, mock_available, mock_write, tmp_path):
        """apply_from_tokens should write CSS files."""
        handler = GTKHandler()
        handler.config_dir = tmp_path
        handler.gtk4_config_dir = tmp_path / "gtk-4.0"
        handler.gtk3_config_dir = tmp_path / "gtk-3.0"

        mock_write.return_value = True
        tokens = create_light_tokens(name="TestTheme")

        result = handler.apply_from_tokens(tokens)

        assert result is True
        assert mock_write.call_count == 2  # gtk-4.0 and gtk-3.0

    @patch("unified_theming.handlers.gtk_handler.write_file_with_backup")
    @patch.object(GTKHandler, "is_available", return_value=False)
    def test_apply_from_tokens_dark_theme(self, mock_available, mock_write, tmp_path):
        """apply_from_tokens should work with dark tokens."""
        handler = GTKHandler()
        handler.config_dir = tmp_path

        mock_write.return_value = True
        tokens = create_dark_tokens(name="DarkTest")

        result = handler.apply_from_tokens(tokens)

        assert result is True
        # Verify CSS content contains dark theme colors
        call_args = mock_write.call_args_list[0]
        css_content = call_args[0][1]
        assert "DarkTest" in css_content

    @patch("unified_theming.handlers.gtk_handler.write_file_with_backup")
    @patch.object(GTKHandler, "is_available", return_value=False)
    def test_apply_from_tokens_returns_false_on_write_failure(
        self, mock_available, mock_write, tmp_path
    ):
        """apply_from_tokens should return False if file write fails."""
        handler = GTKHandler()
        handler.config_dir = tmp_path

        mock_write.return_value = False
        tokens = create_light_tokens()

        result = handler.apply_from_tokens(tokens)

        assert result is False

    @patch("unified_theming.handlers.gtk_handler.write_file_with_backup")
    @patch("subprocess.run")
    @patch.object(GTKHandler, "is_available", return_value=True)
    def test_apply_from_tokens_applies_gsettings(
        self, mock_available, mock_run, mock_write, tmp_path
    ):
        """apply_from_tokens should apply GSettings when available."""
        handler = GTKHandler()
        handler.config_dir = tmp_path

        mock_write.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        tokens = create_light_tokens(name="GSettingsTest")

        handler.apply_from_tokens(tokens)

        # Verify gsettings was called
        mock_run.assert_called()

    @patch("unified_theming.handlers.gtk_handler.write_file_with_backup")
    @patch.object(GTKHandler, "is_available", return_value=False)
    def test_apply_from_tokens_creates_directories(
        self, mock_available, mock_write, tmp_path
    ):
        """apply_from_tokens should create config directories."""
        handler = GTKHandler()
        handler.config_dir = tmp_path

        mock_write.return_value = True
        tokens = create_light_tokens()

        handler.apply_from_tokens(tokens)

        # Directories should be created
        assert (tmp_path / "gtk-4.0").exists()
        assert (tmp_path / "gtk-3.0").exists()

    def test_backward_compatibility_apply_theme_still_works(self):
        """Original apply_theme method should still work."""
        handler = GTKHandler()
        # Just verify the method exists and has correct signature
        assert hasattr(handler, "apply_theme")
        assert callable(handler.apply_theme)
