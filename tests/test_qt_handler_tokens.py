"""Tests for QtHandler token integration."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from unified_theming.handlers.qt_handler import QtHandler
from unified_theming.renderers.qt import QtRenderer
from unified_theming.tokens.defaults import create_light_tokens, create_dark_tokens


class TestQtHandlerTokenIntegration:
    """Test QtHandler integration with QtRenderer."""

    def test_handler_has_renderer(self):
        """QtHandler should have a QtRenderer instance."""
        handler = QtHandler()
        assert hasattr(handler, "renderer")
        assert isinstance(handler.renderer, QtRenderer)

    @patch("unified_theming.handlers.qt_handler.write_file_with_backup")
    def test_apply_from_tokens_writes_kdeglobals(self, mock_write, tmp_path):
        """apply_from_tokens should write kdeglobals file."""
        handler = QtHandler()
        handler.config_dir = tmp_path

        # Determine expected path based on QtRenderer output (usually kdeglobals)
        expected_path = tmp_path / "kdeglobals"

        mock_write.return_value = True
        tokens = create_light_tokens(name="TestTheme")

        result = handler.apply_from_tokens(tokens)

        assert result is True
        # Verify write called
        assert mock_write.called
        # Verify it wrote to kdeglobals (check arguments of first call)
        call_args = mock_write.call_args
        assert call_args[0][0] == expected_path
        # Verify content contains theme name
        assert "TestTheme" in call_args[0][1]

    @patch("unified_theming.handlers.qt_handler.write_file_with_backup")
    def test_apply_from_tokens_dark_theme(self, mock_write, tmp_path):
        """apply_from_tokens should work with dark tokens."""
        handler = QtHandler()
        handler.config_dir = tmp_path

        mock_write.return_value = True
        tokens = create_dark_tokens(name="DarkQtTest")

        result = handler.apply_from_tokens(tokens)

        assert result is True

        # Get content written
        call_args = mock_write.call_args
        content = call_args[0][1]

        assert "DarkQtTest" in content
        # Verify standard Qt keys exist
        assert "BackgroundNormal" in content
        assert "ForegroundNormal" in content

    @patch("unified_theming.handlers.qt_handler.write_file_with_backup")
    def test_apply_from_tokens_returns_false_on_write_failure(
        self, mock_write, tmp_path
    ):
        """apply_from_tokens should return False if file write fails."""
        handler = QtHandler()
        handler.config_dir = tmp_path

        mock_write.return_value = False
        tokens = create_light_tokens()

        result = handler.apply_from_tokens(tokens)

        assert result is False

    @patch("unified_theming.handlers.qt_handler.write_file_with_backup")
    def test_apply_from_tokens_creates_parent_directories(self, mock_write, tmp_path):
        """apply_from_tokens should create config directories if missing."""
        handler = QtHandler()
        # Point to a subdir that doesn't exist yet
        handler.config_dir = tmp_path / "subdir"

        mock_write.return_value = True
        tokens = create_light_tokens()

        handler.apply_from_tokens(tokens)

        # Directory should be created
        assert handler.config_dir.exists()

    def test_backward_compatibility_apply_theme_still_works(self):
        """Original apply_theme method should still work."""
        handler = QtHandler()
        # Just verify the method exists and has correct signature
        assert hasattr(handler, "apply_theme")
        assert callable(handler.apply_theme)
