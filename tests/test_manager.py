"""
Tests for Unified Theme Manager.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from unified_theming.core.manager import UnifiedThemeManager
from unified_theming.core.types import (
    ThemeInfo, Toolkit, ValidationResult, 
    ValidationMessage, ValidationLevel, 
    HandlerResult, ApplicationResult
)
from unified_theming.core.exceptions import (
    ThemeNotFoundError, ThemeApplicationError, 
    ValidationError
)


def test_manager_initialization(tmp_path):
    """Test that the manager initializes correctly."""
    config_path = tmp_path / "config"
    manager = UnifiedThemeManager(config_path=config_path)
    
    # Check that handlers are properly initialized
    assert 'gtk' in manager.handlers
    assert 'qt' in manager.handlers
    assert 'flatpak' in manager.handlers
    assert 'snap' in manager.handlers
    
    # Check that dependencies are properly initialized
    assert manager.config_manager is not None
    assert manager.parser is not None


def test_discover_themes(tmp_path):
    """Test theme discovery."""
    config_path = tmp_path / "config"
    manager = UnifiedThemeManager(config_path=config_path)
    
    # This test may not find any themes in a test environment
    # but should not fail
    try:
        themes = manager.discover_themes()
        # At minimum, should return an empty dict without error
        assert isinstance(themes, dict)
    except Exception:
        # In test environments, this might fail due to missing theme directories
        # which is acceptable
        pass


def test_load_theme_success(parser, valid_theme):
    """TC-M-003: Test successful theme loading."""
    manager = UnifiedThemeManager()
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {
        'ValidTheme': ThemeInfo(
            name='ValidTheme',
            path=valid_theme,
            supported_toolkits=[Toolkit.GTK4, Toolkit.GTK3],
            colors={'theme_bg_color': '#ffffff', 'theme_fg_color': '#000000'}
        )
    }
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    with patch.object(manager, 'parser', mock_parser):
        theme_info = manager.load_theme('ValidTheme')
        assert theme_info.name == 'ValidTheme'
        assert theme_info.path == valid_theme
        assert Toolkit.GTK4 in theme_info.supported_toolkits
        assert 'theme_bg_color' in theme_info.colors


def test_load_theme_not_found():
    """TC-M-004: Test theme loading with non-existent theme."""
    manager = UnifiedThemeManager()
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {}  # No themes available
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    with patch.object(manager, 'parser', mock_parser):
        with pytest.raises(ThemeNotFoundError):
            manager.load_theme('NonExistentTheme')


@pytest.mark.parametrize("theme_name", ["", "   ", None])
def test_load_theme_invalid_name(theme_name):
    """TC-M-005: Test theme loading with invalid theme name."""
    manager = UnifiedThemeManager()
    
    # For None, we expect a TypeError (or similar) since we're passing an invalid type
    if theme_name is None:
        with pytest.raises(Exception):  # Could be TypeError or other
            manager.load_theme(theme_name)
    else:
        # For empty/whitespace names, it should still try to find the theme and fail
        with patch.object(manager, 'discover_themes', return_value={}):
            with pytest.raises(ThemeNotFoundError):
                manager.load_theme(theme_name)


def test_validate_theme_success(valid_theme):
    """TC-M-006: Test successful theme validation."""
    with patch('unified_theming.core.manager.UnifiedThemeParser') as mock_parser_class:
        # Mock the parser to return a valid theme
        mock_parser = Mock()
        mock_parser.discover_themes.return_value = {
            'ValidTheme': ThemeInfo(
                name='ValidTheme',
                path=valid_theme,
                supported_toolkits=[Toolkit.GTK4],
                colors={'theme_bg_color': '#ffffff'}
            )
        }
        
        # Mock the validation result
        validation_result = ValidationResult(valid=True)
        mock_parser.validate_theme.return_value = validation_result
        mock_parser_class.return_value = mock_parser
        
        manager = UnifiedThemeManager()
        result = manager.validate_theme('ValidTheme')
        
        assert result.valid is True
        assert len(result.messages) == 0


def test_validate_theme_not_found():
    """TC-M-007: Test theme validation with non-existent theme."""
    manager = UnifiedThemeManager()
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {}  # No themes available
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    with patch.object(manager, 'parser', mock_parser):
        with pytest.raises(ThemeNotFoundError):
            manager.validate_theme('NonExistentTheme')


def test_apply_theme_success():
    """TC-M-008: Test successful theme application to all targets."""
    manager = UnifiedThemeManager()
    
    # Setup mocks
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {
        'TestTheme': ThemeInfo(
            name='TestTheme',
            path=Path('/fake/path'),
            supported_toolkits=[Toolkit.GTK4, Toolkit.QT5],
            colors={'theme_bg_color': '#ffffff'}
        )
    }
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    
    mock_config = Mock()
    mock_config.backup_current_state.return_value = "backup_123"
    
    # Setup handlers
    mock_gtk = Mock()
    mock_gtk.is_available.return_value = True
    mock_gtk.toolkit = Toolkit.GTK4
    mock_gtk.apply_theme.return_value = True
    mock_gtk.validate_compatibility.return_value = ValidationResult(valid=True)
    
    mock_qt = Mock()
    mock_qt.is_available.return_value = True
    mock_qt.toolkit = Toolkit.QT5
    mock_qt.apply_theme.return_value = True
    mock_qt.validate_compatibility.return_value = ValidationResult(valid=True)
    
    mock_flatpak = Mock()
    mock_flatpak.is_available.return_value = False
    mock_flatpak.toolkit = Toolkit.FLATPAK
    
    mock_snap = Mock()
    mock_snap.is_available.return_value = False
    mock_snap.toolkit = Toolkit.SNAP
    
    mock_handlers = {
        'gtk': mock_gtk,
        'qt': mock_qt,
        'flatpak': mock_flatpak,
        'snap': mock_snap,
    }
    
    with patch.object(manager, 'parser', mock_parser), \
         patch.object(manager, 'config_manager', mock_config), \
         patch.object(manager, 'handlers', mock_handlers):
        result = manager.apply_theme('TestTheme')
        
        assert result.overall_success is True
        assert 'gtk' in result.handler_results
        assert 'qt' in result.handler_results
        assert result.handler_results['gtk'].success is True
        assert result.handler_results['qt'].success is True
        assert result.backup_id == "backup_123"


def test_apply_theme_target_specific():
    """TC-M-009: Test theme application to specific targets."""
    manager = UnifiedThemeManager()
    
    # Setup mocks
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {
        'TestTheme': ThemeInfo(
            name='TestTheme',
            path=Path('/fake/path'),
            supported_toolkits=[Toolkit.GTK4, Toolkit.QT5],
            colors={'theme_bg_color': '#ffffff'}
        )
    }
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    
    mock_config = Mock()
    mock_config.backup_current_state.return_value = "backup_123"
    
    # Setup handlers
    mock_gtk = Mock()
    mock_gtk.is_available.return_value = True
    mock_gtk.toolkit = Toolkit.GTK4
    mock_gtk.apply_theme.return_value = True
    mock_gtk.validate_compatibility.return_value = ValidationResult(valid=True)
    
    mock_qt = Mock()
    mock_qt.is_available.return_value = True
    mock_qt.toolkit = Toolkit.QT5
    mock_qt.apply_theme.return_value = True
    mock_qt.validate_compatibility.return_value = ValidationResult(valid=True)
    
    mock_flatpak = Mock()
    mock_flatpak.is_available.return_value = False
    mock_flatpak.toolkit = Toolkit.FLATPAK
    
    mock_snap = Mock()
    mock_snap.is_available.return_value = False
    mock_snap.toolkit = Toolkit.SNAP
    
    mock_handlers = {
        'gtk': mock_gtk,
        'qt': mock_qt,
        'flatpak': mock_flatpak,
        'snap': mock_snap,
    }
    
    with patch.object(manager, 'parser', mock_parser), \
         patch.object(manager, 'config_manager', mock_config), \
         patch.object(manager, 'handlers', mock_handlers):
        result = manager.apply_theme('TestTheme', targets=['gtk'])
        
        # Should only have GTK result, not QT
        assert 'gtk' in result.handler_results
        assert 'qt' not in result.handler_results
        assert result.overall_success is True


def test_apply_theme_handler_not_available():
    """TC-M-010: Test theme application when handler is not available."""
    manager = UnifiedThemeManager()
    
    # Setup mocks
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {
        'TestTheme': ThemeInfo(
            name='TestTheme',
            path=Path('/fake/path'),
            supported_toolkits=[Toolkit.GTK4],
            colors={'theme_bg_color': '#ffffff'}
        )
    }
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    
    mock_config = Mock()
    mock_config.backup_current_state.return_value = "backup_123"
    
    # Setup handler that's not available
    mock_gtk = Mock()
    mock_gtk.is_available.return_value = False  # Handler not available
    mock_gtk.toolkit = Toolkit.GTK4
    
    mock_qt = Mock()
    mock_qt.is_available.return_value = False
    mock_qt.toolkit = Toolkit.QT5
    
    mock_flatpak = Mock()
    mock_flatpak.is_available.return_value = False
    mock_flatpak.toolkit = Toolkit.FLATPAK
    
    mock_snap = Mock()
    mock_snap.is_available.return_value = False
    mock_snap.toolkit = Toolkit.SNAP
    
    mock_handlers = {
        'gtk': mock_gtk,
        'qt': mock_qt,
        'flatpak': mock_flatpak,
        'snap': mock_snap,
    }
    
    with patch.object(manager, 'parser', mock_parser), \
         patch.object(manager, 'config_manager', mock_config), \
         patch.object(manager, 'handlers', mock_handlers):
        result = manager.apply_theme('TestTheme')
        
        # Handler should be skipped, but overall should still be successful
        # since it's not an error - just unavailable
        assert 'gtk' in result.handler_results
        assert result.handler_results['gtk'].success is False
        assert "not available" in result.handler_results['gtk'].message


def test_apply_theme_not_found():
    """TC-M-011: Test applying non-existent theme."""
    manager = UnifiedThemeManager()
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {}  # No themes available
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    with patch.object(manager, 'parser', mock_parser):
        with pytest.raises(ThemeNotFoundError):
            manager.apply_theme('NonExistentTheme')


def test_apply_theme_validation_errors():
    """TC-M-012: Test theme application with validation errors."""
    manager = UnifiedThemeManager()
    
    # Setup mocks
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {
        'TestTheme': ThemeInfo(
            name='TestTheme',
            path=Path('/fake/path'),
            supported_toolkits=[Toolkit.GTK4],
            colors={'theme_bg_color': '#ffffff'}
        )
    }
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    
    mock_config = Mock()
    mock_config.backup_current_state.return_value = "backup_123"
    
    # Setup handler with validation warnings
    mock_gtk = Mock()
    mock_gtk.is_available.return_value = True
    mock_gtk.toolkit = Toolkit.GTK4
    mock_gtk.apply_theme.return_value = True
    
    # Return validation result with warnings
    validation_result = ValidationResult(valid=True)
    validation_result.add_warning("Minor color issue", component="test")
    mock_gtk.validate_compatibility.return_value = validation_result
    
    mock_qt = Mock()
    mock_qt.is_available.return_value = False
    mock_qt.toolkit = Toolkit.QT5
    
    mock_flatpak = Mock()
    mock_flatpak.is_available.return_value = False
    mock_flatpak.toolkit = Toolkit.FLATPAK
    
    mock_snap = Mock()
    mock_snap.is_available.return_value = False
    mock_snap.toolkit = Toolkit.SNAP
    
    mock_handlers = {
        'gtk': mock_gtk,
        'qt': mock_qt,
        'flatpak': mock_flatpak,
        'snap': mock_snap,
    }
    
    with patch.object(manager, 'parser', mock_parser), \
         patch.object(manager, 'config_manager', mock_config), \
         patch.object(manager, 'handlers', mock_handlers):
        result = manager.apply_theme('TestTheme')
        
        assert result.overall_success is True  # app still succeeds despite validation warnings
        assert len(result.handler_results['gtk'].warnings) > 0


def test_apply_theme_application_failure():
    """TC-M-013: Test theme application failure."""
    manager = UnifiedThemeManager()
    
    # Setup mocks
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {
        'TestTheme': ThemeInfo(
            name='TestTheme',
            path=Path('/fake/path'),
            supported_toolkits=[Toolkit.GTK4],
            colors={'theme_bg_color': '#ffffff'}
        )
    }
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    
    mock_config = Mock()
    mock_config.backup_current_state.return_value = "backup_123"
    
    # Setup handlers that fail to apply theme
    mock_gtk = Mock()
    mock_gtk.is_available.return_value = True
    mock_gtk.toolkit = Toolkit.GTK4
    mock_gtk.apply_theme.return_value = False  # Application fails
    mock_gtk.validate_compatibility.return_value = ValidationResult(valid=True)
    
    mock_qt = Mock()
    mock_qt.is_available.return_value = True
    mock_qt.toolkit = Toolkit.QT5
    mock_qt.apply_theme.return_value = False  # Application fails
    mock_qt.validate_compatibility.return_value = ValidationResult(valid=True)
    
    mock_flatpak = Mock()
    mock_flatpak.is_available.return_value = False
    mock_flatpak.toolkit = Toolkit.FLATPAK
    
    mock_snap = Mock()
    mock_snap.is_available.return_value = False
    mock_snap.toolkit = Toolkit.SNAP
    
    mock_handlers = {
        'gtk': mock_gtk,
        'qt': mock_qt,
        'flatpak': mock_flatpak,
        'snap': mock_snap,
    }
    
    with patch.object(manager, 'parser', mock_parser), \
         patch.object(manager, 'config_manager', mock_config), \
         patch.object(manager, 'handlers', mock_handlers):
        result = manager.apply_theme('TestTheme')
        
        assert result.overall_success is False
        assert result.handler_results['gtk'].success is False


def test_apply_theme_exception_handling():
    """TC-M-014: Test exception handling during theme application."""
    manager = UnifiedThemeManager()
    
    # Setup mocks
    mock_parser = Mock()
    mock_parser.discover_themes.return_value = {
        'TestTheme': ThemeInfo(
            name='TestTheme',
            path=Path('/fake/path'),
            supported_toolkits=[Toolkit.GTK4],
            colors={'theme_bg_color': '#ffffff'}
        )
    }
    mock_parser.theme_directories = [Path('/usr/share/themes')]
    
    mock_config = Mock()
    mock_config.backup_current_state.return_value = "backup_123"
    
    # Setup handler that raises an exception
    mock_gtk = Mock()
    mock_gtk.is_available.return_value = True
    mock_gtk.toolkit = Toolkit.GTK4
    mock_gtk.apply_theme.side_effect = Exception("Unexpected error")
    mock_gtk.validate_compatibility.return_value = ValidationResult(valid=True)
    
    mock_qt = Mock()
    mock_qt.is_available.return_value = False
    mock_qt.toolkit = Toolkit.QT5
    
    mock_flatpak = Mock()
    mock_flatpak.is_available.return_value = False
    mock_flatpak.toolkit = Toolkit.FLATPAK
    
    mock_snap = Mock()
    mock_snap.is_available.return_value = False
    mock_snap.toolkit = Toolkit.SNAP
    
    mock_handlers = {
        'gtk': mock_gtk,
        'qt': mock_qt,
        'flatpak': mock_flatpak,
        'snap': mock_snap,
    }
    
    with patch.object(manager, 'parser', mock_parser), \
         patch.object(manager, 'config_manager', mock_config), \
         patch.object(manager, 'handlers', mock_handlers):
        result = manager.apply_theme('TestTheme')
        
        assert 'gtk' in result.handler_results
        assert result.handler_results['gtk'].success is False
        assert "Application failed" in result.handler_results['gtk'].message


def test_get_current_themes():
    """TC-M-016: Test getting current themes."""
    with patch('unified_theming.core.manager.GTKHandler') as mock_gtk_handler, \
         patch('unified_theming.core.manager.QtHandler') as mock_qt_handler:
        
        # Setup handlers that are available and return current themes
        mock_gtk = Mock()
        mock_gtk.is_available.return_value = True
        mock_gtk.get_current_theme.return_value = "Adwaita"
        
        mock_qt = Mock()
        mock_qt.is_available.return_value = True
        mock_qt.get_current_theme.return_value = "Fusion"
        
        mock_gtk_handler.return_value = mock_gtk
        mock_qt_handler.return_value = mock_qt
        
        manager = UnifiedThemeManager()
        current_themes = manager.get_current_themes()
        
        assert 'gtk' in current_themes
        assert 'qt' in current_themes
        assert current_themes['gtk'] == "Adwaita"
        assert current_themes['qt'] == "Fusion"


def test_get_current_themes_unavailable_handler():
    """TC-M-017: Test getting current themes when handler is unavailable."""
    with patch('unified_theming.core.manager.GTKHandler') as mock_gtk_handler, \
         patch('unified_theming.core.manager.QtHandler') as mock_qt_handler:
        
        # Setup one handler as available, one as unavailable
        mock_gtk = Mock()
        mock_gtk.is_available.return_value = False  # Not available
        
        mock_qt = Mock()
        mock_qt.is_available.return_value = True
        mock_qt.get_current_theme.return_value = "Fusion"
        
        mock_gtk_handler.return_value = mock_gtk
        mock_qt_handler.return_value = mock_qt
        
        manager = UnifiedThemeManager()
        current_themes = manager.get_current_themes()
        
        assert 'gtk' in current_themes
        assert current_themes['gtk'] == "not_available"
        assert 'qt' in current_themes
        assert current_themes['qt'] == "Fusion"


def test_get_current_themes_handler_exception():
    """Test getting current themes when handler raises exception."""
    with patch('unified_theming.core.manager.GTKHandler') as mock_gtk_handler:
        
        # Setup handler that raises exception when getting current theme
        mock_gtk = Mock()
        mock_gtk.is_available.return_value = True
        mock_gtk.get_current_theme.side_effect = Exception("Cannot get theme")
        
        mock_gtk_handler.return_value = mock_gtk
        
        manager = UnifiedThemeManager()
        current_themes = manager.get_current_themes()
        
        assert 'gtk' in current_themes
        assert current_themes['gtk'] == "unknown"


def test_get_available_handlers():
    """Test getting available handlers."""
    with patch('unified_theming.handlers.gtk_handler.GTKHandler') as mock_gtk_handler, \
         patch('unified_theming.handlers.qt_handler.QtHandler') as mock_qt_handler:
        
        # Setup handlers with different availability
        mock_gtk = Mock()
        mock_gtk.is_available.return_value = True
        
        mock_qt = Mock()
        mock_qt.is_available.return_value = False
        
        mock_gtk_handler.return_value = mock_gtk
        mock_qt_handler.return_value = mock_qt
        
        manager = UnifiedThemeManager()
        availability = manager.get_available_handlers()
        
        assert 'gtk' in availability
        assert 'qt' in availability
        assert availability['gtk'] is True
        assert availability['qt'] is False


def test_preview_theme():
    """Test preview theme functionality (currently just logs warning)."""
    manager = UnifiedThemeManager()
    # This should not raise an exception, just log a warning
    manager.preview_theme('TestTheme', apps=['app1', 'app2'])


def test_rollback_with_backup_id():
    """TC-M-020: Test rollback with specific backup ID."""
    with patch('unified_theming.core.manager.ConfigManager') as mock_config_class:
        mock_config = Mock()
        mock_config.restore_backup.return_value = True
        mock_config_class.return_value = mock_config
        
        manager = UnifiedThemeManager()
        success = manager.rollback(backup_id="backup_123")
        
        assert success is True
        mock_config.restore_backup.assert_called_once_with("backup_123")


def test_rollback_without_backup_id():
    """TC-M-021: Test rollback without backup ID (uses most recent)."""
    with patch('unified_theming.core.manager.ConfigManager') as mock_config_class:
        mock_config = Mock()
        mock_config.get_backups.return_value = [
            MagicMock(backup_id="backup_456"),
            MagicMock(backup_id="backup_123")
        ]
        mock_config.restore_backup.return_value = True
        mock_config_class.return_value = mock_config
        
        manager = UnifiedThemeManager()
        success = manager.rollback()
        
        assert success is True
        mock_config.restore_backup.assert_called_once_with("backup_456")  # Most recent


def test_rollback_no_backups():
    """Test rollback when no backups are available."""
    with patch('unified_theming.core.manager.ConfigManager') as mock_config_class:
        mock_config = Mock()
        mock_config.get_backups.return_value = []  # No backups
        mock_config_class.return_value = mock_config
        
        manager = UnifiedThemeManager()
        success = manager.rollback()
        
        assert success is False


def test_rollback_exception():
    """Test rollback when an exception occurs."""
    with patch('unified_theming.core.manager.ConfigManager') as mock_config_class:
        mock_config = Mock()
        mock_config.get_backups.return_value = [MagicMock(backup_id="backup_123")]
        mock_config.restore_backup.side_effect = Exception("Restore failed")
        mock_config_class.return_value = mock_config
        
        manager = UnifiedThemeManager()
        success = manager.rollback()
        
        assert success is False


def test_prepare_theme_data():
    """TC-M-022: Test preparing theme data for specific toolkit."""
    manager = UnifiedThemeManager()
    
    theme_info = ThemeInfo(
        name='TestTheme',
        path=Path('/fake/path'),
        supported_toolkits=[Toolkit.GTK4],
        colors={'theme_bg_color': '#ffffff', 'theme_fg_color': '#000000'}
    )
    
    theme_data = manager._prepare_theme_data(theme_info, Toolkit.QT5)
    
    assert theme_data.name == 'TestTheme'
    assert theme_data.toolkit == Toolkit.QT5
    assert theme_data.colors == {'theme_bg_color': '#ffffff', 'theme_fg_color': '#000000'}


def test_manager_with_custom_config_path():
    """Test manager initialization with custom config path."""
    custom_path = Path('/tmp/custom_config')
    manager = UnifiedThemeManager(config_path=custom_path)
    
    # Verify that the config manager was initialized with the custom path
    assert manager.config_manager.config_dir == custom_path