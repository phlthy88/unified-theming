"""
Integration Test Fixtures for Unified Theming.

Provides comprehensive pytest fixtures for integration testing.
All fixtures are isolated, reusable, and use realistic data.

Author: Claude Code (Strategic Architect)
Date: October 22, 2025
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from datetime import datetime
from typing import Dict, Any

from unified_theming.core.types import (
    ThemeInfo, ThemeData, Toolkit,
    ValidationResult, ValidationLevel, ValidationMessage
)
from unified_theming.core.manager import UnifiedThemeManager
from unified_theming.core.config import ConfigManager


# ============================================================================
# FILE SYSTEM FIXTURES
# ============================================================================

@pytest.fixture
def mock_file_system(tmp_path, monkeypatch):
    """
    Mock file system with proper directory structure for theming.

    Creates a temporary home directory with all required subdirectories:
    - .themes/ (user themes)
    - .config/ (GTK, Qt, unified-theming configs)
    - .local/share/flatpak/ (Flatpak overrides)

    All tests write to tmp_path, not real filesystem.

    Usage:
        def test_something(mock_file_system):
            home = mock_file_system['home']
            themes_dir = mock_file_system['themes']
            # Test uses these paths automatically

    Returns:
        Dict with paths: home, config, themes, local_share
    """
    # Create mock home directory structure
    home = tmp_path / "home" / "testuser"
    home.mkdir(parents=True)

    config = home / ".config"
    config.mkdir()

    themes = home / ".themes"
    themes.mkdir()

    local_share = home / ".local" / "share"
    local_share.mkdir(parents=True)

    # Create subdirectories
    (config / "gtk-3.0").mkdir(parents=True)
    (config / "gtk-4.0").mkdir(parents=True)
    (config / "unified-theming" / "backups").mkdir(parents=True)
    (local_share / "flatpak" / "overrides").mkdir(parents=True)

    # Mock Path.home() to return test directory
    monkeypatch.setattr(Path, "home", lambda: home)

    # Mock Path.expanduser to use test home
    original_expanduser = Path.expanduser

    def mock_expanduser(self):
        path_str = str(self)
        if path_str.startswith("~"):
            return Path(str(self).replace("~", str(home), 1))
        return original_expanduser(self)

    monkeypatch.setattr(Path, "expanduser", mock_expanduser)

    return {
        'home': home,
        'config': config,
        'themes': themes,
        'local_share': local_share,
        'gtk3_config': config / "gtk-3.0",
        'gtk4_config': config / "gtk-4.0",
        'flatpak_overrides': local_share / "flatpak" / "overrides",
        'backups': config / "unified-theming" / "backups"
    }


# ============================================================================
# THEME DATA FIXTURES
# ============================================================================

@pytest.fixture
def mock_theme_adwaita_dark(mock_file_system):
    """
    Complete Adwaita-dark theme for happy path testing.

    Creates a realistic theme with:
    - Full color palette (8 colors)
    - GTK2, GTK3, GTK4 theme files
    - index.theme metadata
    - All files written to mock filesystem

    Usage:
        def test_apply_theme(mock_theme_adwaita_dark):
            theme_info = mock_theme_adwaita_dark
            # Theme is already on "disk" in mock_file_system

    Returns:
        ThemeInfo object for Adwaita-dark
    """
    themes_dir = mock_file_system['themes']
    theme_path = themes_dir / "Adwaita-dark"
    theme_path.mkdir(parents=True)

    # Create index.theme
    index_content = """[Desktop Entry]
Type=X-GNOME-Metatheme
Name=Adwaita-dark
Comment=Dark variant of Adwaita theme
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=Adwaita-dark
IconTheme=Adwaita
CursorTheme=Adwaita
"""
    (theme_path / "index.theme").write_text(index_content)

    # Create GTK2 theme
    gtk2_dir = theme_path / "gtk-2.0"
    gtk2_dir.mkdir(parents=True)
    gtk2_content = """gtk-theme-name="Adwaita-dark"
gtk-icon-theme-name="Adwaita"
"""
    (gtk2_dir / "gtkrc").write_text(gtk2_content)

    # Create GTK3 theme with colors
    gtk3_dir = theme_path / "gtk-3.0"
    gtk3_dir.mkdir(parents=True)
    gtk3_content = """/* Adwaita-dark GTK3 Theme */
@define-color theme_bg_color #303030;
@define-color theme_fg_color #ffffff;
@define-color theme_selected_bg_color #3584e4;
@define-color theme_selected_fg_color #ffffff;
@define-color borders #1c1c1c;
@define-color accent_bg_color #3584e4;
@define-color accent_fg_color #ffffff;
@define-color window_bg_color #303030;
"""
    (gtk3_dir / "gtk.css").write_text(gtk3_content)

    # Create GTK4 theme with colors
    gtk4_dir = theme_path / "gtk-4.0"
    gtk4_dir.mkdir(parents=True)
    gtk4_content = """/* Adwaita-dark GTK4 Theme */
@define-color theme_bg_color #303030;
@define-color theme_fg_color #ffffff;
@define-color theme_selected_bg_color #3584e4;
@define-color theme_selected_fg_color #ffffff;
@define-color borders #1c1c1c;
@define-color accent_bg_color #3584e4;
@define-color accent_fg_color #ffffff;
@define-color window_bg_color #303030;
"""
    (gtk4_dir / "gtk.css").write_text(gtk4_content)

    # Create ThemeInfo object
    return ThemeInfo(
        name="Adwaita-dark",
        path=theme_path,
        supported_toolkits=[Toolkit.GTK2, Toolkit.GTK3, Toolkit.GTK4],
        metadata={
            'GtkTheme': 'Adwaita-dark',
            'IconTheme': 'Adwaita',
            'CursorTheme': 'Adwaita',
            'display_name': 'Adwaita Dark',
            'comment': 'Dark variant of Adwaita theme'
        },
        colors={
            'theme_bg_color': '#303030',
            'theme_fg_color': '#ffffff',
            'theme_selected_bg_color': '#3584e4',
            'theme_selected_fg_color': '#ffffff',
            'borders': '#1c1c1c',
            'accent_bg_color': '#3584e4',
            'accent_fg_color': '#ffffff',
            'window_bg_color': '#303030'
        }
    )


@pytest.fixture
def mock_theme_nordic(mock_file_system):
    """
    Complete Nordic theme for theme switching tests.

    Similar to Adwaita-dark but with Nordic color palette.

    Returns:
        ThemeInfo object for Nordic
    """
    themes_dir = mock_file_system['themes']
    theme_path = themes_dir / "Nordic"
    theme_path.mkdir(parents=True)

    # Create index.theme
    index_content = """[Desktop Entry]
Type=X-GNOME-Metatheme
Name=Nordic
Comment=Nordic dark theme
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=Nordic
IconTheme=Nordic
"""
    (theme_path / "index.theme").write_text(index_content)

    # Create GTK3 theme with Nordic colors
    gtk3_dir = theme_path / "gtk-3.0"
    gtk3_dir.mkdir(parents=True)
    gtk3_content = """/* Nordic GTK3 Theme */
@define-color theme_bg_color #2e3440;
@define-color theme_fg_color #d8dee9;
@define-color theme_selected_bg_color #88c0d0;
@define-color theme_selected_fg_color #2e3440;
@define-color borders #3b4252;
@define-color accent_bg_color #5e81ac;
@define-color accent_fg_color #eceff4;
@define-color window_bg_color #2e3440;
"""
    (gtk3_dir / "gtk.css").write_text(gtk3_content)

    # Create GTK4 theme
    gtk4_dir = theme_path / "gtk-4.0"
    gtk4_dir.mkdir(parents=True)
    (gtk4_dir / "gtk.css").write_text(gtk3_content)  # Same colors

    return ThemeInfo(
        name="Nordic",
        path=theme_path,
        supported_toolkits=[Toolkit.GTK3, Toolkit.GTK4],
        metadata={
            'GtkTheme': 'Nordic',
            'display_name': 'Nordic',
            'comment': 'Nordic dark theme'
        },
        colors={
            'theme_bg_color': '#2e3440',
            'theme_fg_color': '#d8dee9',
            'theme_selected_bg_color': '#88c0d0',
            'theme_selected_fg_color': '#2e3440',
            'borders': '#3b4252',
            'accent_bg_color': '#5e81ac',
            'accent_fg_color': '#eceff4',
            'window_bg_color': '#2e3440'
        }
    )


@pytest.fixture
def mock_theme_incomplete(mock_file_system):
    """
    Incomplete theme for validation testing.

    Has GTK3 only, missing:
    - GTK4 theme files
    - Qt support
    - Some color definitions

    Returns:
        ThemeInfo object for IncompleteTheme
    """
    themes_dir = mock_file_system['themes']
    theme_path = themes_dir / "IncompleteTheme"
    theme_path.mkdir(parents=True)

    # Create index.theme
    index_content = """[Desktop Entry]
Type=X-GNOME-Metatheme
Name=IncompleteTheme
Comment=Incomplete theme for testing
"""
    (theme_path / "index.theme").write_text(index_content)

    # Create GTK3 only (missing GTK4)
    gtk3_dir = theme_path / "gtk-3.0"
    gtk3_dir.mkdir(parents=True)
    gtk3_content = """/* Incomplete Theme */
@define-color theme_bg_color #cccccc;
@define-color theme_fg_color #000000;
/* Missing: theme_selected_bg_color, borders, etc. */
"""
    (gtk3_dir / "gtk.css").write_text(gtk3_content)

    return ThemeInfo(
        name="IncompleteTheme",
        path=theme_path,
        supported_toolkits=[Toolkit.GTK3],  # Missing GTK4, Qt
        metadata={
            'display_name': 'Incomplete Theme',
            'comment': 'Incomplete theme for testing'
        },
        colors={
            'theme_bg_color': '#cccccc',
            'theme_fg_color': '#000000'
            # Missing colors: theme_selected_bg_color, borders, etc.
        }
    )


# ============================================================================
# SUBPROCESS MOCKING
# ============================================================================

@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """
    Mock subprocess.run for Flatpak/Snap commands.

    Prevents actual subprocess execution during tests.
    Returns successful mock by default.

    Usage:
        def test_flatpak(mock_subprocess_run):
            # Flatpak commands automatically mocked
            result = manager.apply_theme("Adwaita-dark")
            # No real 'flatpak' command was run

    Can be customized per test:
        def test_flatpak_failure(mock_subprocess_run, monkeypatch):
            mock_subprocess_run.return_value = Mock(returncode=1, stderr="Error")
            # Now flatpak commands will "fail"

    Returns:
        Mock object representing subprocess.run
    """
    import subprocess

    mock_run = Mock(
        return_value=Mock(
            returncode=0,
            stdout="",
            stderr=""
        )
    )

    monkeypatch.setattr(subprocess, 'run', mock_run)

    return mock_run


# ============================================================================
# MANAGER AND CONFIG FIXTURES
# ============================================================================

@pytest.fixture
def mock_manager(mock_file_system, mock_subprocess_run):
    """
    Fully configured UnifiedThemeManager for testing.

    Uses mock file system and mocked subprocess.
    Ready to use immediately in tests.

    Usage:
        def test_apply_theme(mock_manager, mock_theme_adwaita_dark):
            result = mock_manager.apply_theme("Adwaita-dark")
            assert result.overall_success

    Returns:
        UnifiedThemeManager instance
    """
    from unified_theming.core.parser import UnifiedThemeParser
    
    # Create config path in the mocked filesystem
    config_path = mock_file_system['config'] / "unified-theming"
    
    # Create manager instance
    manager = UnifiedThemeManager(config_path=config_path)
    
    # Update parser to look in the mocked theme directories
    theme_directories = [
        mock_file_system['themes']  # This is where our mock themes are created
    ]
    manager.parser = UnifiedThemeParser(theme_directories=theme_directories)

    return manager


@pytest.fixture
def mock_config_manager(mock_file_system):
    """
    ConfigManager for backup/restore testing.

    Uses mock file system for backups.

    Usage:
        def test_backup(mock_config_manager):
            backup_id = mock_config_manager.backup_current_state()
            assert backup_id is not None

    Returns:
        ConfigManager instance
    """
    config_path = mock_file_system['config'] / "unified-theming"
    return ConfigManager(config_path=config_path)


# ============================================================================
# THEME REPOSITORY FIXTURES
# ============================================================================

@pytest.fixture
def integration_test_theme_repository(
    mock_file_system,
    mock_theme_adwaita_dark,
    mock_theme_nordic,
    mock_theme_incomplete
):
    """
    Complete theme repository with multiple themes.

    Creates a realistic ~/.themes directory with:
    - Adwaita-dark (complete)
    - Nordic (complete)
    - IncompleteTheme (partial)

    Usage:
        def test_discover_themes(integration_test_theme_repository):
            manager = UnifiedThemeManager()
            themes = manager.discover_themes()
            assert len(themes) == 3

    Returns:
        Dict mapping theme names to ThemeInfo objects
    """
    return {
        'Adwaita-dark': mock_theme_adwaita_dark,
        'Nordic': mock_theme_nordic,
        'IncompleteTheme': mock_theme_incomplete
    }


# ============================================================================
# VALIDATION FIXTURES
# ============================================================================

@pytest.fixture
def sample_validation_result():
    """
    Sample ValidationResult for testing.

    Returns:
        ValidationResult with warnings and errors
    """
    return ValidationResult(
        valid=False,
        messages=[
            ValidationMessage(
                level=ValidationLevel.WARNING,
                message="Missing GTK4 theme files",
                context="GTK4 support incomplete"
            ),
            ValidationMessage(
                level=ValidationLevel.ERROR,
                message="No color definitions found",
                context="Theme parsing failed"
            )
        ]
    )


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def file_comparison_utility():
    """
    Utility functions for file comparison in tests.

    Usage:
        def test_restore(file_comparison_utility):
            utils = file_comparison_utility
            assert utils.compare_files(path1, path2)

    Returns:
        Dict with utility functions
    """
    def compare_files(path1: Path, path2: Path) -> bool:
        """Compare two files byte-for-byte."""
        if not (path1.exists() and path2.exists()):
            return False
        return path1.read_bytes() == path2.read_bytes()

    def verify_backup_contains_file(backup_id: str, file_path: Path) -> bool:
        """Check if backup contains a specific file."""
        backup_dir = Path.home() / ".config/unified-theming/backups" / backup_id
        relative_path = file_path.relative_to(Path.home())
        return (backup_dir / relative_path).exists()

    def count_files_in_directory(directory: Path, pattern: str = "*") -> int:
        """Count files matching pattern in directory."""
        if not directory.exists():
            return 0
        return len(list(directory.glob(pattern)))

    return {
        'compare_files': compare_files,
        'verify_backup_contains_file': verify_backup_contains_file,
        'count_files': count_files_in_directory
    }


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """
    Configure pytest markers for integration tests.

    Registers custom markers:
    - integration: Marks integration tests
    - slow: Marks slow tests (can be skipped with -m "not slow")
    """
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# ============================================================================
# FIXTURE CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test(mock_file_system):
    """
    Automatically cleanup after each test.

    Ensures no test pollution between tests.
    Runs after every test automatically (autouse=True).
    """
    yield  # Test runs here

    # Cleanup (if needed)
    # tmp_path is automatically cleaned by pytest
    pass
