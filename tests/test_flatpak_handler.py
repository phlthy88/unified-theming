"""Tests for unified_theming.handlers.flatpak_handler module."""

import subprocess
from pathlib import Path

from unittest.mock import Mock, patch

import pytest


from unified_theming.core.types import ThemeData, Toolkit, ValidationResult
from unified_theming.handlers.flatpak_handler import FlatpakHandler

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def flatpak_handler():
    """FlatpakHandler instance for testing."""
    return FlatpakHandler()


@pytest.fixture
def sample_theme_data():
    """Sample theme data for testing."""
    return ThemeData(
        name="Adwaita-dark",
        toolkit=Toolkit.FLATPAK,
        colors={
            "theme_bg_color": "#2e3436",
            "theme_fg_color": "#eeeeec",
            "theme_selected_bg_color": "#3584e4",
        },
        additional_data={},
    )


@pytest.fixture
def mock_flatpak_list():
    """Mock Flatpak application list."""
    return """
org.gnome.Calculator
org.mozilla.firefox
com.spotify.Client
"""


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================


def test_flatpak_handler_init(flatpak_handler):
    """Test TC-FP-001: Initialize FlatpakHandler."""
    assert flatpak_handler is not None
    assert flatpak_handler.toolkit == Toolkit.FLATPAK


@patch("subprocess.run")
def test_flatpak_handler_available(mock_run, flatpak_handler):
    """Test TC-FP-002: Check Flatpak is available."""
    mock_run.return_value = Mock(returncode=0)
    # Create a new handler instance to trigger the check again
    handler = FlatpakHandler()
    assert handler.is_available() is True


@patch("subprocess.run")
def test_flatpak_handler_not_available(mock_run, flatpak_handler):
    """Test TC-FP-003: Check Flatpak not available."""
    mock_run.side_effect = FileNotFoundError()
    handler = FlatpakHandler()
    assert handler.is_available() is False


# ============================================================================
# OVERRIDE CREATION TESTS
# ============================================================================


@patch("pathlib.Path.exists", return_value=True)
@patch("subprocess.run")
def test_apply_theme_success(mock_run, mock_exists, flatpak_handler, sample_theme_data):
    """Test TC-FP-004: Apply theme successfully."""
    # Mock the availability check
    flatpak_handler.available = True

    # Mock the subprocess.run calls
    mock_run.return_value = Mock(returncode=0)

    result = flatpak_handler.apply_theme(sample_theme_data)
    assert result is True

    # Check that subprocess.run was called for both filesystem access grants and environment variables
    assert (
        mock_run.call_count >= 3
    )  # At least 3 calls: 3 theme dirs + GTK_THEME + env vars


@patch("pathlib.Path.exists", return_value=True)
@patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "flatpak"))
def test_apply_theme_permission_denied(
    mock_run, mock_exists, flatpak_handler, sample_theme_data
):
    """Test TC-FP-005: Handle permission denied when writing overrides."""
    flatpak_handler.available = True

    with patch("unified_theming.handlers.flatpak_handler.logger") as mock_logger:
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is False
        mock_logger.error.assert_called_once()


@patch("subprocess.run")
def test_apply_theme_flatpak_not_installed(
    mock_run, flatpak_handler, sample_theme_data
):
    """Test TC-FP-006: Handle Flatpak not installed."""
    flatpak_handler.available = False

    with patch("unified_theming.handlers.flatpak_handler.logger") as mock_logger:
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is False
        mock_logger.warning.assert_called_once()


def test_get_current_theme(flatpak_handler):
    """Test TC-FP-007: Get currently applied Flatpak theme."""
    result = flatpak_handler.get_current_theme()
    assert result == "system"


# ============================================================================
# THEME VARIABLE MAPPING TESTS
# ============================================================================


def test_validate_compatibility_gtk_theme(flatpak_handler, sample_theme_data):
    """Test TC-FP-008: Validate GTK theme compatibility."""
    # Modify the theme data to be a GTK theme
    gtk_theme_data = ThemeData(
        name="Adwaita", toolkit=Toolkit.GTK4, colors={}, additional_data={}
    )

    result = flatpak_handler.validate_compatibility(gtk_theme_data)
    assert isinstance(result, ValidationResult)
    assert result.valid is True


def test_validate_compatibility_non_gtk_theme(flatpak_handler, sample_theme_data):
    """Test TC-FP-009: Validate non-GTK theme compatibility."""
    # Modify the theme data to be a non-GTK theme
    qt_theme_data = ThemeData(
        name="Breeze", toolkit=Toolkit.QT5, colors={}, additional_data={}
    )

    result = flatpak_handler.validate_compatibility(qt_theme_data)
    assert isinstance(result, ValidationResult)
    assert result.valid is True


# ============================================================================
# PORTAL DETECTION TESTS
# ============================================================================


@patch("subprocess.run")
def test_detect_portal_available(mock_run, flatpak_handler):
    """Test TC-FP-010: Detect xdg-desktop-portal is available."""
    mock_run.return_value = Mock(returncode=0)

    handler = FlatpakHandler()
    assert handler.is_available() is True


@patch("subprocess.run")
def test_detect_portal_not_available(mock_run, flatpak_handler):
    """Test TC-FP-011: Handle missing xdg-desktop-portal."""
    mock_run.side_effect = FileNotFoundError()

    handler = FlatpakHandler()
    assert handler.is_available() is False


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


@patch("pathlib.Path.exists", return_value=True)
@patch("subprocess.run", side_effect=Exception("Unexpected error"))
def test_apply_theme_unexpected_error(
    mock_run, mock_exists, flatpak_handler, sample_theme_data
):
    """Test TC-FP-012: Handle unexpected error during theme application."""
    flatpak_handler.available = True

    with patch("unified_theming.handlers.flatpak_handler.logger") as mock_logger:
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is False
        mock_logger.error.assert_called_once()


@patch("pathlib.Path.exists", return_value=True)
@patch(
    "subprocess.run",
    side_effect=[
        Mock(returncode=0),
        Mock(returncode=0),
        subprocess.CalledProcessError(1, "flatpak"),
    ],
)
def test_apply_theme_partial_failure(
    mock_run, mock_exists, flatpak_handler, sample_theme_data
):
    """Test TC-FP-013: Handle partial command failures."""
    flatpak_handler.available = True

    # Only the first two commands succeed, the third fails
    with patch("unified_theming.handlers.flatpak_handler.logger"):
        result = flatpak_handler.apply_theme(sample_theme_data)
        # Should still return False because of the failure in the third command
        assert result is False


# ============================================================================
# ACCESSIBILITY TESTS
# ============================================================================


def test_get_supported_features(flatpak_handler):
    """Test TC-FP-014: Get supported features."""
    features = flatpak_handler.get_supported_features()
    assert "filesystem_access" in features
    assert "environment_vars" in features


def test_get_config_paths(flatpak_handler):
    """Test TC-FP-015: Get configuration paths."""
    paths = flatpak_handler.get_config_paths()
    expected_path = Path.home() / ".config" / "flatpak" / "overrides"
    assert expected_path in paths


# ============================================================================
# ADDITIONAL FUNCTIONALITY TESTS
# ============================================================================


@patch("pathlib.Path.exists", return_value=False)
@patch("subprocess.run")
def test_apply_theme_no_theme_dirs(
    mock_run, mock_exists, flatpak_handler, sample_theme_data
):
    """Test TC-FP-016: Apply theme when no theme directories exist."""
    flatpak_handler.available = True
    mock_run.return_value = Mock(returncode=0)

    result = flatpak_handler.apply_theme(sample_theme_data)
    assert result is True
    # Should still succeed, but with less subprocess calls


@patch("pathlib.Path.exists", side_effect=[True, True, True])  # All theme dirs exist
@patch("subprocess.run")
def test_apply_theme_all_dirs_exist(
    mock_run, mock_exists, flatpak_handler, sample_theme_data
):
    """Test TC-FP-017: Apply theme when all theme directories exist."""
    flatpak_handler.available = True
    mock_run.return_value = Mock(returncode=0)

    result = flatpak_handler.apply_theme(sample_theme_data)
    assert result is True
    # Should call subprocess.run multiple times for each dir and environment variable


@patch("subprocess.run")
def test__check_flatpak_available_success(mock_run, flatpak_handler):
    """Test TC-FP-018: _check_flatpak_available returns True when Flatpak is available."""
    mock_run.return_value = Mock(returncode=0)

    result = flatpak_handler._check_flatpak_available()
    assert result is True


@patch("subprocess.run", side_effect=FileNotFoundError())
def test__check_flatpak_available_not_found(mock_run, flatpak_handler):
    """Test TC-FP-019: _check_flatpak_available returns False when Flatpak is not installed."""
    result = flatpak_handler._check_flatpak_available()
    assert result is False


@patch("subprocess.run", side_effect=Exception("Other error"))
def test__check_flatpak_available_exception(mock_run, flatpak_handler):
    """Test TC-FP-020: _check_flatpak_available returns False when other exception occurs."""
    result = flatpak_handler._check_flatpak_available()
    assert result is False


def test_toolkit_assignment(flatpak_handler):
    """Test TC-FP-021: Handler is correctly associated with Flatpak toolkit."""
    assert flatpak_handler.toolkit == Toolkit.FLATPAK


def test_validate_compatibility_result_structure(flatpak_handler, sample_theme_data):
    """Test TC-FP-022: validate_compatibility returns proper ValidationResult."""
    result = flatpak_handler.validate_compatibility(sample_theme_data)
    assert isinstance(result, ValidationResult)
    assert hasattr(result, "valid")
    assert hasattr(result, "messages")


@patch("pathlib.Path.exists", side_effect=[True, False, True])  # First and third exist
@patch("subprocess.run")
def test_apply_theme_mixed_theme_dirs(
    mock_run, mock_exists, flatpak_handler, sample_theme_data
):
    """Test TC-FP-023: Apply theme with mixed existing/non-existing theme directories."""
    flatpak_handler.available = True
    mock_run.return_value = Mock(returncode=0)

    result = flatpak_handler.apply_theme(sample_theme_data)
    assert result is True


@patch("pathlib.Path.exists", return_value=True)
@patch(
    "subprocess.run",
    side_effect=[
        Mock(returncode=0),  # First theme dir success
        Mock(returncode=1),  # Second theme dir fails
        Mock(returncode=0),  # Third theme dir success
        Mock(returncode=0),  # GTK_THEME success
        Mock(returncode=0),  # Additional env vars success
    ],
)
def test_apply_theme_with_some_dir_failures(
    mock_run, mock_exists, flatpak_handler, sample_theme_data
):
    """Test TC-FP-024: Apply theme when some theme directory commands fail."""
    flatpak_handler.available = True

    with patch("unified_theming.handlers.flatpak_handler.logger"):
        result = flatpak_handler.apply_theme(sample_theme_data)
        # Should still succeed since only one dir command failed
        assert result is True


@patch("pathlib.Path.exists", return_value=True)
@patch(
    "subprocess.run",
    side_effect=subprocess.CalledProcessError(1, ["flatpak", "override"]),
)
def test_apply_theme_all_dirs_fail(
    mock_run, mock_exists, flatpak_handler, sample_theme_data
):
    """Test TC-FP-025: Apply theme when all theme directory commands fail."""
    flatpak_handler.available = True

    with patch("unified_theming.handlers.flatpak_handler.logger") as mock_logger:
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is False
        # At least one error log should occur
        assert (
            mock_logger.warning.call_count >= 3
        )  # For each failed directory access grant
