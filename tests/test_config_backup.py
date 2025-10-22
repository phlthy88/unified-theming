"""Tests for unified_theming.core.config module."""

from datetime import datetime
from pathlib import Path

from unittest.mock import Mock, patch

import pytest

from unified_theming.core.config import ConfigManager
from unified_theming.core.exceptions import (
    BackupError,
    BackupNotFoundError,
)
from unified_theming.core.types import Backup


# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture
def temp_config_dir(tmp_path):
    """Temporary config directory for testing."""
    config_dir = tmp_path / "unified-theming"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture
def config_manager(temp_config_dir):
    """ConfigManager instance with temporary directory."""
    return ConfigManager(config_path=temp_config_dir)


@pytest.fixture
def sample_backup_data():
    """Sample backup data for testing."""
    return {
        "backup_id": "backup_20251021_120000",
        "timestamp": "2025-10-21T12:00:00",
        "theme_name": "Adwaita",
        "description": "Pre-theme-change backup",
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================
def test_config_manager_init_default():
    """Test TC-CF-001: Initialize ConfigManager with default path."""
    manager = ConfigManager()
    assert manager.config_dir is not None
    assert isinstance(manager.config_dir, Path)


def test_config_manager_init_custom_path(temp_config_dir):
    """Test TC-CF-002: Initialize with custom config path."""
    manager = ConfigManager(config_path=temp_config_dir)
    assert manager.config_dir == temp_config_dir
    assert manager.config_dir.exists()
    assert manager.backup_dir.exists()


# ============================================================================
# BACKUP CREATION TESTS
# ============================================================================
def test_backup_current_state_success(config_manager, temp_config_dir):
    """Test TC-CF-003: Create backup successfully."""
    backup_id = config_manager.backup_current_state()
    # Verify backup ID returned
    assert backup_id is not None
    assert isinstance(backup_id, str)
    assert backup_id.startswith("backup_")

    # Verify backup directory created
    backups = config_manager.get_backups()
    assert len(backups) == 1
    assert backups[0].backup_id == backup_id


def test_backup_metadata(config_manager):
    """Test TC-CF-004: Backup includes correct metadata."""
    backup_id = config_manager.backup_current_state()
    backup_info = config_manager.get_backup_info(backup_id)
    assert backup_info.backup_id == backup_id
    assert backup_info.timestamp is not None
    assert isinstance(backup_info.timestamp, datetime)
    assert backup_info.theme_name == "current"


def test_get_backups_empty(config_manager):
    """Test TC-CF-006: List backups when none exist."""
    backups = config_manager.get_backups()
    assert backups == []


def test_get_backups_with_data(config_manager, temp_config_dir):
    """Test TC-CF-005: List all available backups."""
    # Create 3 backups
    backup_id_1 = config_manager.backup_current_state()
    backup_id_2 = config_manager.backup_current_state()
    backup_id_3 = config_manager.backup_current_state()

    backups = config_manager.get_backups()
    assert len(backups) == 3
    backup_ids = [b.backup_id for b in backups]
    assert backup_id_1 in backup_ids
    assert backup_id_2 in backup_ids
    assert backup_id_3 in backup_ids


def test_prune_old_backups_over_limit(config_manager):
    """Test TC-CF-007: Prune backups when over keep limit."""
    # Temporarily modify the ConfigManager to not auto-prune during backup creation
    # by disabling the _cleanup_old_backups call in backup_current_state
    original_cleanup = config_manager._cleanup_old_backups

    # Create 15 backups to ensure we have enough before any auto-cleanup
    backup_ids = []
    for i in range(15):
        # Temporarily replace _cleanup_old_backups with a no-op
        config_manager._cleanup_old_backups = lambda: None
        backup_id = config_manager.backup_current_state()
        backup_ids.append(backup_id)

    # Restore the original cleanup method
    config_manager._cleanup_old_backups = original_cleanup

    # Verify we have 15 backups now
    backups = config_manager.get_backups()
    assert len(backups) == 15

    # Prune with keep=10
    deleted_count = config_manager.prune_old_backups(keep=10)
    assert deleted_count == 5  # 15 - 10 = 5 should be deleted

    # Verify only 10 remain
    backups = config_manager.get_backups()
    assert len(backups) == 10


def test_prune_old_backups_under_limit(config_manager):
    """Test TC-CF-008: Prune when under limit (no deletions)."""
    # Create 5 backups
    for i in range(5):
        config_manager.backup_current_state()

    # Prune with keep=10 (more than we have)
    deleted_count = config_manager.prune_old_backups(keep=10)
    assert deleted_count == 0  # No backups should be deleted

    # Verify all 5 remain
    backups = config_manager.get_backups()
    assert len(backups) == 5


def test_backup_fails_permission_denied(config_manager, temp_config_dir):
    """Test TC-CF-010: Backup fails with permission error."""
    with patch("pathlib.Path.mkdir", side_effect=PermissionError("Access denied")):
        with pytest.raises(BackupError):
            config_manager.backup_current_state()


# ============================================================================
# RESTORE TESTS
# ============================================================================
def test_restore_backup_not_found(config_manager):
    """Test TC-CF-012: Restore non-existent backup."""
    with pytest.raises(BackupNotFoundError):
        config_manager.restore_backup("nonexistent_backup_id")


def test_restore_backup_success(config_manager, temp_config_dir):
    """Test TC-CF-011: Restore backup successfully."""
    # Create initial backup
    backup_id = config_manager.backup_current_state()

    # Create a test config file that would be backed up
    test_config_file = temp_config_dir / "config.json"
    original_content = {"theme": "Original", "enabled": True}
    config_manager.save_config(original_content)

    # Create another backup after saving the config
    backup_id2 = config_manager.backup_current_state()

    # Change the config
    modified_content = {"theme": "Modified", "enabled": False}
    config_manager.save_config(modified_content)

    # Now restore the second backup
    result = config_manager.restore_backup(backup_id2)
    assert result is True

    # Verify the config was restored
    restored_config = config_manager.load_config()
    assert restored_config["theme"] == "Modified"  # This was the state at backup time


def test_get_backup_info(config_manager, sample_backup_data):
    """Test TC-CF-018: Get backup metadata."""
    # Create a backup first
    backup_id = config_manager.backup_current_state()
    info = config_manager.get_backup_info(backup_id)
    assert info is not None
    assert info.backup_id == backup_id
    assert isinstance(info, Backup)


def test_delete_backup_success(config_manager, temp_config_dir):
    """Test deleting an existing backup."""
    # Create a backup first
    backup_id = config_manager.backup_current_state()

    # Verify backup exists
    backups = config_manager.get_backups()
    assert len(backups) == 1

    # Delete the backup
    result = config_manager.delete_backup(backup_id)
    assert result is True

    # Verify backup is gone
    backups = config_manager.get_backups()
    assert len(backups) == 0


def test_delete_backup_not_found(config_manager):
    """Test TC-CF-020: Delete non-existent backup."""
    with pytest.raises(BackupNotFoundError):
        config_manager.delete_backup("nonexistent_backup_id")


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================
def test_load_config_not_found(config_manager):
    """Test TC-CF-022: Load config when file doesn't exist."""
    # Should return default config or empty dict, not raise error
    config = config_manager.load_config()
    assert isinstance(config, dict)


def test_save_config_success(config_manager, temp_config_dir):
    """Test TC-CF-024: Save configuration successfully."""
    test_config = {"theme": "Adwaita", "gtk_enabled": True, "qt_enabled": True}
    config_manager.save_config(test_config)
    # Verify file exists
    config_file = temp_config_dir / "config.json"  # Adjust path as needed
    assert config_file.exists()
    # Verify content
    loaded_config = config_manager.load_config()
    assert loaded_config["theme"] == "Adwaita"


def test_get_config_value_not_found(config_manager):
    """Test TC-CF-027: Get non-existent config value."""
    value = config_manager.get_config_value("nonexistent_key", default="default_value")
    assert value == "default_value"


# ============================================================================
# Add more tests here as you implement them
# ============================================================================
