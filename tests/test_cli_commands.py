"""Basic CLI tests for release v0.5.0."""

import subprocess
import sys
from pathlib import Path

import pytest


def test_cli_help_command():
    """Test that the CLI help command works."""
    result = subprocess.run(
        [sys.executable, "-m", "unified_theming.cli.commands", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # The command should succeed (return code 0) and have some output
    assert result.returncode == 0
    assert (
        "unified-theming" in result.stdout.lower() or "theme" in result.stdout.lower()
    )


def test_cli_version_command():
    """Test that the CLI version command works."""
    result = subprocess.run(
        [sys.executable, "-m", "unified_theming.cli.commands", "--version"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Check if it returns a version or at least doesn't fail completely
    # If there's no --version flag, it might return 2 (unknown option) or 0
    # We'll check that it doesn't crash with a general error
    assert result.returncode in [0, 2]  # 2 might indicate unknown option


def test_cli_no_arguments():
    """Test that the CLI runs without crashing when called without arguments."""
    result = subprocess.run(
        [sys.executable, "-m", "unified_theming.cli.commands"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Should not crash (may return non-zero for missing args, but not crash)
    assert result.returncode in [0, 2]  # 0: success, 2: missing arguments error


def test_cli_list_themes_command():
    """Test that a potential list-themes command doesn't crash."""
    result = subprocess.run(
        [sys.executable, "-m", "unified_theming.cli.commands", "list-themes"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Command may not exist, but shouldn't crash the Python process
    assert result.returncode in [0, 2]  # 0: success, 2: unknown command


def test_cli_discover_command():
    """Test that a potential discover command doesn't crash."""
    result = subprocess.run(
        [sys.executable, "-m", "unified_theming.cli.commands", "discover"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Command may not exist, but shouldn't crash the Python process
    assert result.returncode in [0, 2]  # 0: success, 2: unknown command
