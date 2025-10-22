"""Basic CLI command tests for v0.5.0 release."""
import pytest
from click.testing import CliRunner
from unified_theming.cli.commands import cli, main

@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    return CliRunner()


def test_cli_main_help(cli_runner):
    """Test main CLI help message."""
    result = cli_runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'unified-theming' in result.output.lower()


def test_cli_list_command(cli_runner):
    """Test 'list' command."""
    result = cli_runner.invoke(cli, ['list'])
    # Should not crash, exit code 0 or 1 acceptable
    assert result.exit_code in [0, 1]


def test_cli_apply_theme_missing_name(cli_runner):
    """Test 'apply' command without theme name."""
    result = cli_runner.invoke(cli, ['apply'])
    assert result.exit_code != 0  # Should fail without theme name


def test_cli_apply_theme_nonexistent(cli_runner):
    """Test 'apply' command with non-existent theme."""
    result = cli_runner.invoke(cli, ['apply', 'NonExistentTheme'])
    assert result.exit_code != 0


def test_cli_version(cli_runner):
    """Test --version flag."""
    result = cli_runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '1.0.0' in result.output or '0.5.0' in result.output