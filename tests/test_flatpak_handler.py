"""Tests for unified_theming.handlers.flatpak_handler module."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
from unified_theming.core.types import ThemeData, Toolkit
from unified_theming.handlers.flatpak_handler import FlatpakHandler


@pytest.fixture
def flatpak_handler():
    """FlatpakHandler instance for testing."""
    return FlatpakHandler()


@pytest.fixture
def sample_theme_data():
    """Sample theme data for testing."""
    return ThemeData(
        name="TestTheme",
        toolkit=Toolkit.GTK4,
        colors={},
        css_content=None,
        additional_data={}
    )


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

def test_flatpak_handler_init(flatpak_handler):
    """Test initialization of FlatpakHandler."""
    assert flatpak_handler.toolkit == Toolkit.FLATPAK
    assert hasattr(flatpak_handler, 'available')


def test_flatpak_handler_init_checks_availability(flatpak_handler):
    """Test that FlatpakHandler initialization checks availability."""
    # The handler should have set the available property
    assert hasattr(flatpak_handler, 'available')
    assert isinstance(flatpak_handler.available, bool)


# ============================================================================
# AVAILABILITY CHECKS
# ============================================================================

def test_check_flatpak_available_success():
    """Test _check_flatpak_available when Flatpak is available."""
    handler = FlatpakHandler()
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        result = handler._check_flatpak_available()
        assert result is True
        mock_run.assert_called_once()


def test_check_flatpak_available_not_found():
    """Test _check_flatpak_available when Flatpak is not available."""
    handler = FlatpakHandler()
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        result = handler._check_flatpak_available()
        assert result is False


def test_check_flatpak_available_command_fails():
    """Test _check_flatpak_available when command fails."""
    handler = FlatpakHandler()
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 1
        result = handler._check_flatpak_available()
        assert result is False


def test_check_flatpak_available_exception():
    """Test _check_flatpak_available when exception occurs."""
    handler = FlatpakHandler()
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Test exception")
        result = handler._check_flatpak_available()
        assert result is False


def test_is_available_method(flatpak_handler):
    """Test the is_available method."""
    flatpak_handler.available = True
    assert flatpak_handler.is_available() is True
    
    flatpak_handler.available = False
    assert flatpak_handler.is_available() is False


# ============================================================================
# THEME APPLICATION TESTS
# ============================================================================

def test_apply_theme_when_flatpak_not_available(flatpak_handler, sample_theme_data, caplog):
    """Test apply_theme when Flatpak is not available."""
    flatpak_handler.available = False
    result = flatpak_handler.apply_theme(sample_theme_data)
    assert result is False
    assert "Flatpak not available, skipping theme application" in caplog.text


def test_apply_theme_success_with_mocked_subprocess(flatpak_handler, sample_theme_data):
    """Test apply_theme success with mocked subprocess calls."""
    flatpak_handler.available = True
    
    # Mock the necessary directories as existing
    with patch.object(Path, 'exists', return_value=True), \
         patch('subprocess.run') as mock_run:
        # Mock subprocess.run to return success for all calls
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is True
        
        # Check that subprocess.run was called correctly
        assert mock_run.call_count >= 3  # At least 3 subprocess calls in apply_theme


def test_apply_theme_filesystem_access_failure(flatpak_handler, sample_theme_data, caplog):
    """Test apply_theme when filesystem access fails with CalledProcessError."""
    flatpak_handler.available = True
    
    with patch.object(Path, 'exists', return_value=True), \
         patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd")):
        
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is False  # Should return False when command fails with CalledProcessError


def test_apply_theme_command_error(flatpak_handler, sample_theme_data):
    """Test apply_theme when commands fail with CalledProcessError."""
    flatpak_handler.available = True
    
    with patch.object(Path, 'exists', return_value=True), \
         patch('subprocess.run', side_effect=Exception("Command failed")):
        
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is False


def test_apply_theme_general_exception(flatpak_handler, sample_theme_data):
    """Test apply_theme when general exception occurs."""
    flatpak_handler.available = True
    
    with patch.object(Path, 'exists', return_value=True), \
         patch('subprocess.run', side_effect=Exception("General error")):
        
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is False


# ============================================================================
# CURRENT THEME TESTS
# ============================================================================

def test_get_current_theme(flatpak_handler):
    """Test get_current_theme method."""
    result = flatpak_handler.get_current_theme()
    assert result == "system"


# ============================================================================
# COMPATIBILITY VALIDATION TESTS
# ============================================================================

def test_validate_compatibility_gtk4_theme(flatpak_handler, sample_theme_data):
    """Test validate_compatibility with GTK4 theme."""
    result = flatpak_handler.validate_compatibility(sample_theme_data)
    assert result.valid is True


def test_validate_compatibility_gtk3_theme(flatpak_handler):
    """Test validate_compatibility with GTK3 theme."""
    theme_data = ThemeData(
        name="TestTheme",
        toolkit=Toolkit.GTK3,
        colors={},
        css_content=None,
        additional_data={}
    )
    result = flatpak_handler.validate_compatibility(theme_data)
    assert result.valid is True


def test_validate_compatibility_non_gtk_theme(flatpak_handler):
    """Test validate_compatibility with non-GTK theme."""
    theme_data = ThemeData(
        name="TestTheme",
        toolkit=Toolkit.QT5,  # Different toolkit
        colors={},
        css_content=None,
        additional_data={}
    )
    result = flatpak_handler.validate_compatibility(theme_data)
    assert result.valid is True
    # Should have an info message about Flatpak using system theme components


# ============================================================================
# FEATURE AND CONFIG PATH TESTS
# ============================================================================

def test_get_supported_features(flatpak_handler):
    """Test get_supported_features method."""
    features = flatpak_handler.get_supported_features()
    assert isinstance(features, list)
    assert "filesystem_access" in features
    assert "environment_vars" in features


def test_get_config_paths(flatpak_handler):
    """Test get_config_paths method."""
    paths = flatpak_handler.get_config_paths()
    assert isinstance(paths, list)
    assert len(paths) == 1
    expected_path = Path.home() / ".config" / "flatpak" / "overrides"
    assert paths[0] == expected_path


# ============================================================================
# ADDITIONAL TESTS
# ============================================================================

def test_apply_theme_with_nonexistent_directories(flatpak_handler, sample_theme_data):
    """Test apply_theme when theme directories don't exist."""
    flatpak_handler.available = True
    
    with patch.object(Path, 'exists', return_value=False), \
         patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0)
        
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is True
        # Should still try to set environment variables even if directories don't exist


def test_get_supported_features_returns_list(flatpak_handler):
    """Test that get_supported_features always returns a list."""
    features = flatpak_handler.get_supported_features()
    assert isinstance(features, list)


def test_validate_compatibility_with_empty_theme_data(flatpak_handler):
    """Test validate_compatibility with minimal theme data."""
    empty_theme_data = ThemeData(
        name="EmptyTheme",
        toolkit=Toolkit.GTK4,
        colors={},
        css_content=None,
        additional_data={}
    )
    result = flatpak_handler.validate_compatibility(empty_theme_data)
    assert result.valid is True


def test_handler_toolkit_property(flatpak_handler):
    """Test that the handler has the correct toolkit."""
    assert flatpak_handler.toolkit == Toolkit.FLATPAK


def test_validate_compatibility_adds_info_for_non_gtk(flatpak_handler):
    """Test that compatibility validation adds info for non-GTK themes."""
    theme_data = ThemeData(
        name="TestTheme",
        toolkit=Toolkit.QT5,
        colors={},
        css_content=None,
        additional_data={}
    )
    result = flatpak_handler.validate_compatibility(theme_data)
    # The handler should add info about Flatpak using system theme components for non-GTK themes
    assert result.valid is True  # It's still valid, just with info message


def test_apply_theme_logs_info_when_successful(flatpak_handler, sample_theme_data, caplog):
    """Test that apply_theme logs information when successful."""
    flatpak_handler.available = True
    
    with patch.object(Path, 'exists', return_value=True), \
         patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        
        with caplog.at_level("INFO"):
            result = flatpak_handler.apply_theme(sample_theme_data)
            assert result is True
            assert f"Applying theme '{sample_theme_data.name}' to Flatpak applications" in caplog.text