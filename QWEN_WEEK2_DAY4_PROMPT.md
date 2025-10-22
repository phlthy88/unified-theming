# Qwen Coder: Week 2 Day 4 - Config & Backup Testing

**Date:** October 21, 2025
**Agent:** Qwen Coder
**Task:** Implement comprehensive tests for `unified_theming/core/config.py`
**Priority:** P0 - CRITICAL PATH
**Estimated Time:** 6-8 hours

---

## Mission Objective

Test the **ConfigManager** class to achieve **70% coverage** (current: 15%). This module handles backup/restore operations and configuration management - critical for rollback functionality.

---

## Current Status

### Module: `unified_theming/core/config.py`
- **Current Coverage:** 15% (24/155 statements)
- **Target Coverage:** 70%
- **Gap:** +55% (+86 statements)
- **Priority:** P0 (blocks rollback testing)

### Dependencies
✅ **color.py:** 86% coverage (Week 1 complete)
✅ **manager.py:** 93% coverage (Week 2 Day 3 complete)
⏳ **config.py:** 15% coverage (Week 2 Day 4 target)

### Test File Location
**Create:** `tests/test_config_backup.py`

---

## Test Cases to Implement

Reference: `docs/test_plan_week1.md` (TC-CF-001 to TC-CF-030)

### Category 1: Backup Operations (10 tests)

**TC-CF-001:** Initialize ConfigManager with default path
- **Test:** `test_config_manager_init_default()`
- **Expects:** Creates `~/.config/unified-theming/` directory

**TC-CF-002:** Initialize with custom path
- **Test:** `test_config_manager_init_custom_path(tmp_path)`
- **Expects:** Uses provided path

**TC-CF-003:** Create backup (success)
- **Test:** `test_backup_current_state_success()`
- **Setup:** Mock file operations
- **Expects:** Returns backup ID, creates backup directory

**TC-CF-004:** Create backup with metadata
- **Test:** `test_backup_metadata()`
- **Expects:** Backup includes timestamp, theme name, description

**TC-CF-005:** List all backups
- **Test:** `test_get_backups()`
- **Setup:** Create 3 mock backups
- **Expects:** Returns list of 3 Backup objects, sorted by timestamp

**TC-CF-006:** List backups (empty)
- **Test:** `test_get_backups_empty()`
- **Expects:** Returns empty list, no errors

**TC-CF-007:** Prune old backups (success)
- **Test:** `test_prune_old_backups()`
- **Setup:** Create 12 backups (keep limit: 10)
- **Expects:** Deletes 2 oldest backups, keeps 10 most recent

**TC-CF-008:** Prune old backups (under limit)
- **Test:** `test_prune_old_backups_under_limit()`
- **Setup:** Create 5 backups (keep limit: 10)
- **Expects:** Keeps all 5 backups, deletes none

**TC-CF-009:** Backup fails (disk full)
- **Test:** `test_backup_current_state_disk_full()`
- **Setup:** Mock `OSError` with errno.ENOSPC
- **Expects:** Raises `BackupError`

**TC-CF-010:** Backup fails (permission denied)
- **Test:** `test_backup_current_state_permission_denied()`
- **Setup:** Mock `PermissionError`
- **Expects:** Raises `BackupError`

### Category 2: Restore Operations (10 tests)

**TC-CF-011:** Restore backup (success)
- **Test:** `test_restore_backup_success()`
- **Setup:** Create backup, modify config, restore
- **Expects:** Config restored to backup state, returns True

**TC-CF-012:** Restore backup (not found)
- **Test:** `test_restore_backup_not_found()`
- **Setup:** Request non-existent backup ID
- **Expects:** Raises `BackupError`

**TC-CF-013:** Restore backup (corrupted)
- **Test:** `test_restore_backup_corrupted()`
- **Setup:** Backup with missing files
- **Expects:** Raises `BackupError`, logs warning

**TC-CF-014:** Restore backup with validation
- **Test:** `test_restore_backup_validation()`
- **Setup:** Backup with invalid data
- **Expects:** Validation fails, raises `ValidationError`

**TC-CF-015:** Restore creates backup before restore
- **Test:** `test_restore_creates_pre_restore_backup()`
- **Setup:** Restore backup
- **Expects:** Creates "pre-restore" backup before applying

**TC-CF-016:** Restore most recent backup
- **Test:** `test_restore_most_recent_backup()`
- **Setup:** Create 3 backups
- **Expects:** Restores newest backup when ID not specified

**TC-CF-017:** Restore rollback on failure
- **Test:** `test_restore_rollback_on_failure()`
- **Setup:** Restore fails midway
- **Expects:** Rolls back to pre-restore state

**TC-CF-018:** Get backup info
- **Test:** `test_get_backup_info()`
- **Setup:** Create backup with metadata
- **Expects:** Returns Backup object with correct metadata

**TC-CF-019:** Delete backup
- **Test:** `test_delete_backup()`
- **Setup:** Create backup, delete it
- **Expects:** Backup removed, returns True

**TC-CF-020:** Delete backup (not found)
- **Test:** `test_delete_backup_not_found()`
- **Expects:** Raises `BackupError`

### Category 3: Configuration Management (10 tests)

**TC-CF-021:** Load config (success)
- **Test:** `test_load_config_success()`
- **Setup:** Create valid config file
- **Expects:** Returns config dict

**TC-CF-022:** Load config (not found)
- **Test:** `test_load_config_not_found()`
- **Expects:** Returns default config, no error

**TC-CF-023:** Load config (corrupted)
- **Test:** `test_load_config_corrupted()`
- **Setup:** Create malformed JSON
- **Expects:** Raises `ConfigurationError`

**TC-CF-024:** Save config (success)
- **Test:** `test_save_config_success()`
- **Setup:** Modify config, save
- **Expects:** Config written to disk

**TC-CF-025:** Save config (permission denied)
- **Test:** `test_save_config_permission_denied()`
- **Setup:** Mock `PermissionError`
- **Expects:** Raises `ConfigurationError`

**TC-CF-026:** Get config value
- **Test:** `test_get_config_value()`
- **Setup:** Load config with `{"theme": "Adwaita"}`
- **Expects:** `get_config_value("theme")` returns "Adwaita"

**TC-CF-027:** Get config value (not found)
- **Test:** `test_get_config_value_not_found()`
- **Expects:** Returns default value or None

**TC-CF-028:** Set config value
- **Test:** `test_set_config_value()`
- **Setup:** Set `theme="Nordic"`
- **Expects:** Config updated, persisted on save

**TC-CF-029:** Config validation
- **Test:** `test_validate_config()`
- **Setup:** Create config with invalid keys
- **Expects:** Validation fails, returns ValidationResult

**TC-CF-030:** Config merge (defaults + user)
- **Test:** `test_config_merge_defaults()`
- **Setup:** User config missing some keys
- **Expects:** Merged config has all default keys + user overrides

---

## Implementation Guide

### Step 1: Read Existing Implementation

```bash
# Read the config.py file to understand the API
cat unified_theming/core/config.py
```

**Key Classes/Methods to Test:**
- `ConfigManager.__init__(config_path)`
- `ConfigManager.backup_current_state()` → str (backup_id)
- `ConfigManager.get_backups()` → List[Backup]
- `ConfigManager.restore_backup(backup_id)` → bool
- `ConfigManager.prune_old_backups(keep=10)` → int (deleted count)
- `ConfigManager.get_backup_info(backup_id)` → Backup
- `ConfigManager.delete_backup(backup_id)` → bool

### Step 2: Create Test File Structure

```python
# tests/test_config_backup.py

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from unified_theming.core.config import ConfigManager
from unified_theming.core.types import Backup
from unified_theming.core.exceptions import BackupError, ConfigurationError

# Fixtures
@pytest.fixture
def config_manager(tmp_path):
    """Create ConfigManager with temporary directory."""
    return ConfigManager(config_path=tmp_path / "test_config")

@pytest.fixture
def mock_backups(tmp_path):
    """Create mock backup directories."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    # Create 3 mock backups
    backups = []
    for i in range(3):
        backup_path = backup_dir / f"backup_{i}"
        backup_path.mkdir()
        # Create metadata file
        # ...

    return backups

# Test initialization
def test_config_manager_init_default():
    """Test TC-CF-001: Initialize with default path."""
    manager = ConfigManager()
    assert manager.config_path.exists()
    assert manager.config_path.name == "unified-theming"

def test_config_manager_init_custom_path(tmp_path):
    """Test TC-CF-002: Initialize with custom path."""
    custom_path = tmp_path / "custom_config"
    manager = ConfigManager(config_path=custom_path)
    assert manager.config_path == custom_path
    assert custom_path.exists()

# Test backup operations
def test_backup_current_state_success(config_manager):
    """Test TC-CF-003: Create backup successfully."""
    # TODO: Implement test
    pass

# ... continue with remaining tests
```

### Step 3: Implement Tests Incrementally

**Order of Implementation:**
1. **Initialization tests** (TC-CF-001, TC-CF-002) - Easiest, test setup
2. **Backup creation tests** (TC-CF-003 to TC-CF-010) - Core functionality
3. **Backup listing/query tests** (TC-CF-005, TC-CF-006, TC-CF-018) - Read operations
4. **Restore tests** (TC-CF-011 to TC-CF-017) - Critical path
5. **Delete/prune tests** (TC-CF-007, TC-CF-008, TC-CF-019, TC-CF-020) - Cleanup
6. **Config management tests** (TC-CF-021 to TC-CF-030) - Configuration

**Run tests after each category:**
```bash
pytest tests/test_config_backup.py -v --cov=unified_theming/core/config.py --cov-report=term
```

### Step 4: Mock Strategy

**Mock File Operations:**
```python
from unittest.mock import patch, mock_open

@patch('unified_theming.core.config.Path.mkdir')
@patch('unified_theming.core.config.Path.exists', return_value=True)
def test_backup_creation_mocked(mock_exists, mock_mkdir, config_manager):
    backup_id = config_manager.backup_current_state()
    assert backup_id is not None
    mock_mkdir.assert_called_once()
```

**Mock Disk Full Error:**
```python
import errno

@patch('unified_theming.core.config.Path.mkdir')
def test_backup_disk_full(mock_mkdir, config_manager):
    mock_mkdir.side_effect = OSError(errno.ENOSPC, "No space left on device")

    with pytest.raises(BackupError) as exc_info:
        config_manager.backup_current_state()

    assert "disk full" in str(exc_info.value).lower()
```

**Mock Time for Backup IDs:**
```python
from unittest.mock import patch
import datetime

@patch('unified_theming.core.config.datetime')
def test_backup_timestamp(mock_datetime, config_manager):
    mock_datetime.now.return_value = datetime.datetime(2025, 10, 21, 12, 0, 0)
    backup_id = config_manager.backup_current_state()
    assert "20251021_120000" in backup_id
```

---

## Coverage Target Breakdown

**Current Coverage:** 15% (24/155 statements)
**Target Coverage:** 70% (109/155 statements)
**New Coverage Needed:** +55% (+85 statements)

**Expected Coverage by Category:**
- Backup operations: 25-30 statements → 90% coverage
- Restore operations: 25-30 statements → 80% coverage
- Configuration: 20-25 statements → 60% coverage
- Error handling: 10-15 statements → 50% coverage (acceptable)

**Estimated Test Count:** 25-30 tests

---

## Success Criteria

### Must Have (P0 - Required for GO decision)
- [ ] **Coverage ≥70%** (current: 15%)
- [ ] **Test pass rate ≥95%** (target: 100%)
- [ ] **All critical paths tested:**
  - [ ] Backup creation and listing
  - [ ] Restore backup (success and failure)
  - [ ] Prune old backups
  - [ ] Error handling (disk full, permissions, corruption)

### Nice to Have (P1 - Bonus)
- [ ] Coverage ≥75% (+5% buffer)
- [ ] All 30 test cases implemented
- [ ] Integration test with manager.py rollback

---

## Files to Create/Modify

### Create:
- `tests/test_config_backup.py` - Main test file (25-30 tests)

### Read (for reference):
- `unified_theming/core/config.py` - Implementation to test
- `unified_theming/core/types.py` - Backup dataclass
- `unified_theming/core/exceptions.py` - BackupError, ConfigurationError
- `docs/test_plan_week1.md` - Full test specifications

---

## Testing Commands

```bash
# Activate virtual environment
cd /home/joshu/unified-theming
source venv/bin/activate

# Run config tests only
pytest tests/test_config_backup.py -v

# Run with coverage
pytest tests/test_config_backup.py --cov=unified_theming/core/config.py --cov-report=term-missing

# Run full test suite
pytest -v --cov=unified_theming --cov-report=html

# Check coverage HTML
xdg-open htmlcov/config_py.html
```

---

## Expected Timeline

| Hour | Task | Deliverable |
|------|------|-------------|
| 0-1 | Read config.py, plan tests | Test structure outline |
| 1-3 | Implement backup tests (TC-CF-001 to TC-CF-010) | 10 tests passing, ~30% coverage |
| 3-5 | Implement restore tests (TC-CF-011 to TC-CF-020) | 20 tests passing, ~55% coverage |
| 5-7 | Implement config tests (TC-CF-021 to TC-CF-030) | 30 tests passing, ~70% coverage |
| 7-8 | Coverage verification, edge case tests | ≥70% coverage, all tests passing |

**Estimated Completion:** End of Day 4 (8 hours)

---

## Common Pitfalls to Avoid

1. **Don't test file operations on real filesystem**
   - ❌ BAD: Create real files in `/home/joshu/`
   - ✅ GOOD: Use `tmp_path` fixture or mocks

2. **Don't skip error handling tests**
   - These are critical for robustness
   - Use `pytest.raises()` for exception tests

3. **Don't hardcode paths**
   - ❌ BAD: `Path("/home/joshu/.config")`
   - ✅ GOOD: `tmp_path / "config"` or `config_manager.config_path`

4. **Don't forget to test edge cases**
   - Empty backups list
   - Corrupted backup data
   - Permission errors
   - Disk full scenarios

5. **Don't test implementation details**
   - ❌ BAD: Test internal variable names
   - ✅ GOOD: Test public API behavior

---

## Reference Documents

**Test Specifications:**
- `docs/test_plan_week1.md` - Full test plan (TC-CF-001 to TC-CF-030)
- `docs/HANDOFF_PROTOCOL.md` - Multi-agent workflow

**Implementation Reference:**
- `unified_theming/core/config.py` - ConfigManager implementation
- `unified_theming/core/types.py` - Backup dataclass definition
- `unified_theming/core/exceptions.py` - Exception hierarchy

**Previous Handoffs:**
- `WEEK1_DAY2_COMPLETE.md` - color.py testing (86% coverage)
- `WEEK2_DAY3_COMPLETE.md` - manager.py testing (93% coverage)

---

## Deliverables

When complete, create:
1. **Test file:** `tests/test_config_backup.py` (25-30 tests)
2. **Coverage report:** Run pytest with `--cov-report=html`
3. **Status document:** `WEEK2_DAY4_COMPLETE.md`
4. **Git commit:** With message format below

**Git Commit Message:**
```
Week 2 Day 4 Complete: config.py XX% coverage, YY/YY tests passing

✅ Target: 70% coverage → Achieved: XX%
✅ Test pass rate: 100% (YY/YY tests)
✅ Backup/restore operations tested
✅ Error handling verified

Test Coverage by Module:
- color.py: 86% (Week 1)
- manager.py: 93% (Week 2 Day 3)
- config.py: XX% (Week 2 Day 4)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Final Checklist

Before marking complete:
- [ ] All tests passing (≥95% pass rate)
- [ ] Coverage ≥70% achieved
- [ ] No syntax errors in test file
- [ ] Coverage report generated (HTML + XML)
- [ ] Status document created
- [ ] Git commit with proper tags

---

**Good luck, Qwen! You've got this. Follow the test plan methodically, and you'll hit 70% coverage by Day 4 EOD.** 🚀

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
