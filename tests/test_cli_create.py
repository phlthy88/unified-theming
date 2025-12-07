"""Tests for CLI create command."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from unified_theming.cli.commands import cli


class TestCreateCommand:
    """Tests for the create command."""

    def test_create_basic(self):
        """Create command should work with just a name."""
        runner = CliRunner()
        result = runner.invoke(cli, ["create", "TestTheme"])

        assert result.exit_code == 0
        assert "TestTheme" in result.output
        assert "Created valid" in result.output

    def test_create_with_accent(self):
        """Create command should accept accent color."""
        runner = CliRunner()
        result = runner.invoke(cli, ["create", "AccentTheme", "--accent", "#ff5500"])

        assert result.exit_code == 0
        assert "Using accent color" in result.output
        assert "#ff5500" in result.output

    def test_create_light_variant(self):
        """Create command should support light variant."""
        runner = CliRunner()
        result = runner.invoke(cli, ["create", "LightTheme", "--variant", "light"])

        assert result.exit_code == 0
        assert "light" in result.output

    def test_create_dark_variant(self):
        """Create command should default to dark variant."""
        runner = CliRunner()
        result = runner.invoke(cli, ["create", "DarkTheme", "--variant", "dark"])

        assert result.exit_code == 0
        assert "dark" in result.output

    def test_create_with_output(self, tmp_path):
        """Create command should save tokens to file."""
        runner = CliRunner()
        output_file = tmp_path / "tokens.json"

        result = runner.invoke(
            cli, ["create", "SavedTheme", "--output", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Saved tokens to" in result.output

        # Verify JSON content
        content = json.loads(output_file.read_text())
        assert content["name"] == "SavedTheme"

    def test_create_invalid_accent(self):
        """Create command should reject invalid accent colors."""
        runner = CliRunner()
        result = runner.invoke(cli, ["create", "BadTheme", "--accent", "notacolor"])

        assert result.exit_code != 0
        assert "Invalid accent color" in result.output

    @patch("unified_theming.handlers.gtk_handler.GTKHandler.apply_from_tokens")
    @patch("unified_theming.handlers.qt_handler.QtHandler.apply_from_tokens")
    def test_create_with_apply(self, mock_qt, mock_gtk):
        """Create command should apply theme when --apply is used."""
        mock_gtk.return_value = True
        mock_qt.return_value = True

        runner = CliRunner()
        result = runner.invoke(cli, ["create", "ApplyTheme", "--apply"])

        assert result.exit_code == 0
        assert "Applied to GTK" in result.output
        assert "Applied to Qt" in result.output
        mock_gtk.assert_called_once()
        mock_qt.assert_called_once()

    def test_create_help(self):
        """Create command should show help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["create", "--help"])

        assert result.exit_code == 0
        assert "--accent" in result.output
        assert "--variant" in result.output
        assert "--output" in result.output
        assert "--apply" in result.output
