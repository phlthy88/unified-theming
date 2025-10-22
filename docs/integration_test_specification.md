# Integration Test Specification - Week 3 Day 1

**Date:** October 22, 2025
**Author:** Claude Code (Strategic Architect)
**Purpose:** Define integration test scenarios for Week 3 testing sprint
**Status:** ✅ COMPLETE - Ready for Implementation

---

## Overview

This document specifies 5 core integration test scenarios that validate the Unified Theming system works end-to-end. These tests go beyond unit testing to verify component interaction, workflow completeness, and system resilience.

**Coverage Goal:** These 5 scenarios should add +3-5% to overall project coverage (48% → 51-53%)

**Success Criteria:**
- All 5 scenarios implemented and passing
- Tests run in <5 seconds total
- Zero regressions in existing 149 tests
- Realistic data and mocking
- Clear failure messages

---

## Test Scenario Index

| ID | Scenario | Priority | Complexity | Est. Time |
|-----|----------|----------|------------|-----------|
| **IT-001** | Happy Path - Full Theme Application | P0 - Critical | Medium | 30 min |
| **IT-002** | Error Recovery - Handler Failure with Rollback | P0 - Critical | High | 45 min |
| **IT-003** | Multi-Handler Coordination | P0 - Critical | Medium | 30 min |
| **IT-004** | Backup/Restore Workflow | P1 - High | Medium | 30 min |
| **IT-005** | Theme Validation - Compatibility Checking | P1 - High | Low | 20 min |

**Total Implementation Time:** ~2.5 hours

---

## IT-001: Happy Path - Full Theme Application

**Test ID:** IT-001
**Priority:** P0 (Critical)
**File:** `tests/test_integration.py::test_happy_path_full_theme_application`

### Description
Validates the most common user workflow: discovering themes, selecting a theme, applying it across all handlers, and verifying it's active. This is the golden path every user should experience.

### Test Flow

1. **Setup:** Mock file system with ~/.themes directory containing Adwaita-dark theme
2. **Discover:** Call `manager.discover_themes()`
3. **Select:** Retrieve theme "Adwaita-dark" from discovered themes
4. **Apply:** Call `manager.apply_theme("Adwaita-dark")`
5. **Verify GTK:** Check ~/.gtkrc-2.0, ~/.config/gtk-3.0/settings.ini, ~/.config/gtk-4.0/gtk.css exist and contain correct theme name
6. **Verify Flatpak:** Check ~/.local/share/flatpak/overrides/global contains correct GTK_THEME
7. **Verify Backup:** Check backup directory created in ~/.config/unified-theming/backups/
8. **Verify Result:** Assert `result.overall_success == True`

### Expected Results

- ✅ `manager.discover_themes()` returns dict with "Adwaita-dark" key
- ✅ Theme parsing succeeds (colors extracted from CSS)
- ✅ GTK handler writes 3 files:
  - `~/.gtkrc-2.0` contains `gtk-theme-name="Adwaita-dark"`
  - `~/.config/gtk-3.0/settings.ini` contains `gtk-theme-name=Adwaita-dark`
  - `~/.config/gtk-4.0/gtk.css` contains `@import 'Adwaita-dark'` or color definitions
- ✅ Flatpak override file exists and contains `GTK_THEME=Adwaita-dark`
- ✅ Backup directory created with timestamp format `backup_YYYYMMDD_HHMMSS_microseconds`
- ✅ `result.overall_success == True`
- ✅ `result.handler_results` shows all handlers succeeded

### Edge Cases

- **Theme with special characters:** Test theme name "Nord-Dark (v2.0)" with parentheses and spaces
- **Empty theme directory:** What happens if theme has no CSS files? (Should fail gracefully)
- **Symlinked theme:** Theme is a symlink to another directory (Should follow symlink)

### Mock Requirements

**File System (use `tmp_path` fixture):**
```python
# Mock directory structure:
tmp_path/
  .themes/
    Adwaita-dark/
      index.theme           # Theme metadata
      gtk-2.0/
        gtkrc               # GTK2 theme
      gtk-3.0/
        gtk.css             # GTK3 theme with colors
      gtk-4.0/
        gtk.css             # GTK4 theme with colors
  .config/
    unified-theming/
      backups/              # Backup directory
    gtk-3.0/                # GTK3 config
    gtk-4.0/                # GTK4 config
  .local/
    share/
      flatpak/
        overrides/          # Flatpak overrides
```

**Subprocess (for Flatpak):**
```python
# Mock subprocess.run for flatpak commands
mock_subprocess = Mock(return_value=Mock(returncode=0, stdout="", stderr=""))
monkeypatch.setattr('subprocess.run', mock_subprocess)
```

**Why these mocks:**
- File system: Don't write to real user config
- Subprocess: Don't require Flatpak installed

### Assertions

```python
# Discovery
themes = manager.discover_themes()
assert "Adwaita-dark" in themes
assert themes["Adwaita-dark"].name == "Adwaita-dark"

# Application
result = manager.apply_theme("Adwaita-dark")
assert result.overall_success == True
assert len(result.handler_results) >= 2  # At least GTK and Flatpak

# File verification
gtk2_config = Path.home() / ".gtkrc-2.0"
assert gtk2_config.exists()
assert "Adwaita-dark" in gtk2_config.read_text()

gtk3_config = Path.home() / ".config/gtk-3.0/settings.ini"
assert gtk3_config.exists()
assert "Adwaita-dark" in gtk3_config.read_text()

# Backup verification
backup_dir = Path.home() / ".config/unified-theming/backups"
assert backup_dir.exists()
backups = list(backup_dir.glob("backup_*"))
assert len(backups) >= 1
assert result.backup_id in [b.name for b in backups]
```

---

## IT-002: Error Recovery - Handler Failure with Rollback

**Test ID:** IT-002
**Priority:** P0 (Critical)
**File:** `tests/test_integration.py::test_error_recovery_handler_failure_rollback`

### Description
Validates system resilience when things go wrong. Specifically tests that when a handler fails (e.g., permission denied), the system automatically rolls back to the previous state, leaving the user's config intact and consistent.

### Test Flow

1. **Setup:** Mock file system with existing theme configuration (Adwaita theme already applied)
2. **Backup Original:** Record original GTK config file contents
3. **Inject Failure:** Mock one handler (GTK) to raise PermissionError on apply_theme()
4. **Attempt Apply:** Call `manager.apply_theme("Nordic")`
5. **Verify Failure Detected:** Assert `result.overall_success == False`
6. **Verify Rollback Triggered:** Check that ConfigManager.restore_backup() was called
7. **Verify Original Restored:** Assert GTK config file still contains "Adwaita" (original theme)
8. **Verify User Notification:** Assert error message is clear (not a stack trace)
9. **Verify Consistent State:** No partial application (either all handlers succeed or all rollback)

### Expected Results

- ✅ Handler raises PermissionError
- ✅ Manager catches exception (doesn't crash)
- ✅ `result.overall_success == False`
- ✅ Rollback is triggered automatically (>50% handlers failed)
- ✅ Backup is restored (original files back in place)
- ✅ Error message is user-friendly: "Failed to apply theme: Permission denied when writing GTK config"
- ✅ System is consistent (not partially applied - no mix of old and new themes)

### Edge Cases

- **All handlers fail:** 100% failure rate, rollback should still work
- **Rollback itself fails:** What happens if restore_backup() raises error? (Should log critical error)
- **Partial failure (50%):** Exactly 50% handlers fail - should this rollback? (Current logic: no, >50% needed)

### Mock Requirements

**Handler Failure Injection:**
```python
# Mock GTKHandler.apply_theme to fail
def mock_apply_theme_failure(theme_data):
    raise PermissionError("Permission denied: /home/user/.config/gtk-3.0/settings.ini")

monkeypatch.setattr(GTKHandler, 'apply_theme', mock_apply_theme_failure)
```

**ConfigManager Spy:**
```python
# Track calls to restore_backup
original_restore = ConfigManager.restore_backup
restore_called = []

def spy_restore_backup(self, backup_id):
    restore_called.append(backup_id)
    return original_restore(self, backup_id)

monkeypatch.setattr(ConfigManager, 'restore_backup', spy_restore_backup)
```

**Why these mocks:**
- Handler failure: Simulate real-world permission errors
- ConfigManager spy: Verify rollback was actually called (not just claimed)

### Assertions

```python
# Setup: Apply initial theme
manager.apply_theme("Adwaita")
original_gtk_config = (Path.home() / ".config/gtk-3.0/settings.ini").read_text()
assert "Adwaita" in original_gtk_config

# Inject failure and attempt apply
with monkeypatch.context() as m:
    m.setattr(GTKHandler, 'apply_theme', lambda self, td: (_ for _ in ()).throw(PermissionError("Access denied")))

    result = manager.apply_theme("Nordic")

# Verify failure handling
assert result.overall_success == False
assert any("Permission" in hr.details or "Access denied" in hr.details
           for hr in result.handler_results.values())

# Verify rollback
assert len(restore_called) >= 1
current_gtk_config = (Path.home() / ".config/gtk-3.0/settings.ini").read_text()
assert "Adwaita" in current_gtk_config  # Original theme restored
assert "Nordic" not in current_gtk_config  # Failed theme not applied
```

---

## IT-003: Multi-Handler Coordination

**Test ID:** IT-003
**Priority:** P0 (Critical)
**File:** `tests/test_integration.py::test_multi_handler_coordination`

### Description
Validates that multiple handlers can apply simultaneously without conflicts or data corruption. Each handler receives correct data (GTK colors vs Qt translated colors), and no handler interferes with another's files.

### Test Flow

1. **Setup:** Mock file system + theme with comprehensive color palette
2. **Apply:** Call `manager.apply_theme("Nord", targets=["gtk", "qt", "flatpak"])`
3. **Verify GTK:** GTK files contain GTK color format (`@define-color theme_bg_color #2e3440`)
4. **Verify Qt:** kdeglobals contains Qt color format (`[Colors:Window]\nBackgroundNormal=#2e3440`)
5. **Verify Flatpak:** Override contains GTK_THEME environment variable
6. **Verify Color Consistency:** Same semantic color has same hex value across all handlers
7. **Verify No Interference:** GTK files don't contain Qt syntax, Qt files don't contain GTK syntax
8. **Verify Atomic Success:** All handlers succeed or all rollback (no partial state)

### Expected Results

- ✅ GTK handler receives GTK-formatted theme data
- ✅ Qt handler receives translated Qt color format
- ✅ Flatpak handler receives GTK theme name
- ✅ All handlers write to separate directories (no file conflicts)
- ✅ Color values are consistent:
  - GTK: `@define-color theme_bg_color #2e3440`
  - Qt kdeglobals: `BackgroundNormal=#2e3440`
  - Both use same hex `#2e3440`
- ✅ `result.overall_success == True`
- ✅ `len(result.handler_results) == 3` (gtk, qt, flatpak)

### Edge Cases

- **Color translation edge cases:** GTK named colors (e.g., `@blue_3`) vs Qt hex colors
- **Handler ordering:** Does order matter? (Should not - handlers are independent)
- **Conflicting settings:** GTK wants light theme, Qt wants dark - how is this handled? (Each handler independent)

### Mock Requirements

**Complete Theme with Colors:**
```python
theme_colors = {
    # Background colors
    'theme_bg_color': '#2e3440',
    'theme_fg_color': '#d8dee9',

    # Selection colors
    'theme_selected_bg_color': '#88c0d0',
    'theme_selected_fg_color': '#2e3440',

    # Border colors
    'borders': '#3b4252',

    # Accent colors
    'accent_bg_color': '#5e81ac',
    'accent_fg_color': '#eceff4'
}
```

**File System for Multiple Handlers:**
```python
# All handler target directories exist
tmp_path / ".gtkrc-2.0"                    # GTK2
tmp_path / ".config/gtk-3.0/settings.ini"   # GTK3
tmp_path / ".config/gtk-4.0/gtk.css"        # GTK4
tmp_path / ".config/kdeglobals"             # Qt
tmp_path / ".config/Kvantum/"               # Kvantum (Qt)
tmp_path / ".local/share/flatpak/overrides/global"  # Flatpak
```

**Why these mocks:**
- Complete color palette: Test color translation accurately
- All handler directories: Ensure no conflicts

### Assertions

```python
# Apply to multiple handlers
result = manager.apply_theme("Nord", targets=["gtk", "qt", "flatpak"])

assert result.overall_success == True
assert "gtk" in result.handler_results
assert "qt" in result.handler_results
assert "flatpak" in result.handler_results

# Verify GTK color format
gtk4_css = (Path.home() / ".config/gtk-4.0/gtk.css").read_text()
assert "@define-color theme_bg_color #2e3440" in gtk4_css or \
       "--theme-bg-color: #2e3440" in gtk4_css

# Verify Qt color format (INI style)
kdeglobals = (Path.home() / ".config/kdeglobals").read_text()
assert "[Colors:Window]" in kdeglobals or "[ColorScheme]" in kdeglobals
assert "2e3440" in kdeglobals.lower()  # Hex value present

# Verify Flatpak environment
flatpak_override = (Path.home() / ".local/share/flatpak/overrides/global").read_text()
assert "GTK_THEME" in flatpak_override
assert "Nord" in flatpak_override

# Verify color consistency (same hex across handlers)
import re
gtk_bg_hex = re.search(r'theme_bg_color[:\s]+#?([0-9a-f]{6})', gtk4_css, re.I)
qt_bg_hex = re.search(r'BackgroundNormal[=\s]+#?([0-9a-f]{6})', kdeglobals, re.I)

if gtk_bg_hex and qt_bg_hex:
    assert gtk_bg_hex.group(1).lower() == qt_bg_hex.group(1).lower()
```

---

## IT-004: Backup/Restore Workflow

**Test ID:** IT-004
**Priority:** P1 (High)
**File:** `tests/test_integration.py::test_backup_restore_workflow`

### Description
Validates users can safely experiment with themes and undo changes. Tests manual backup creation, theme switching, and restore functionality to ensure no data loss.

### Test Flow

1. **Setup:** Apply Theme-A (Adwaita), verify active
2. **Create Backup:** Call `config_manager.backup_current_state()`, get backup_id
3. **Apply Theme-B:** Call `manager.apply_theme("Nordic")`, verify Theme-B active
4. **Restore Backup:** Call `config_manager.restore_backup(backup_id)`
5. **Verify Theme-A Restored:** Check GTK config contains "Adwaita" again
6. **Verify No Data Loss:** Compare restored files to original, should be identical
7. **Verify Backup Persists:** Backup directory still exists after restore

### Expected Results

- ✅ Manual backup creation succeeds, returns valid backup_id
- ✅ Backup contains all relevant files (GTK configs, Qt configs, Flatpak overrides)
- ✅ Theme switching works (Theme-A → Theme-B confirmed)
- ✅ Restore actually restores (not just claims to)
- ✅ Restored files are byte-for-byte identical to original
- ✅ No data loss during restore
- ✅ Backup directory persists (not deleted during restore)

### Edge Cases

- **Restore to non-existent backup:** backup_id="nonexistent" should raise BackupError
- **Restore after file deletion:** User deleted theme files, restore should recreate them
- **Multiple restores:** Restore twice in a row, should be idempotent

### Mock Requirements

**File Comparison Utility:**
```python
def compare_files(path1: Path, path2: Path) -> bool:
    """Compare two files byte-for-byte."""
    if not (path1.exists() and path2.exists()):
        return False
    return path1.read_bytes() == path2.read_bytes()
```

**Backup Verification:**
```python
def verify_backup_contains_file(backup_id: str, file_path: Path) -> bool:
    """Check if backup contains a specific file."""
    backup_dir = Path.home() / ".config/unified-theming/backups" / backup_id
    relative_path = file_path.relative_to(Path.home())
    return (backup_dir / relative_path).exists()
```

**Why these utilities:**
- File comparison: Verify exact restoration
- Backup verification: Ensure backup is complete

### Assertions

```python
# Apply Theme-A and record state
manager.apply_theme("Adwaita")
gtk3_original = (Path.home() / ".config/gtk-3.0/settings.ini").read_text()
assert "Adwaita" in gtk3_original

# Create backup
backup_id = config_manager.backup_current_state()
assert backup_id is not None
assert len(backup_id) > 0

# Verify backup exists
backup_dir = Path.home() / ".config/unified-theming/backups" / backup_id
assert backup_dir.exists()

# Apply Theme-B
manager.apply_theme("Nordic")
gtk3_new = (Path.home() / ".config/gtk-3.0/settings.ini").read_text()
assert "Nordic" in gtk3_new
assert "Adwaita" not in gtk3_new

# Restore backup
success = config_manager.restore_backup(backup_id)
assert success == True

# Verify Theme-A restored
gtk3_restored = (Path.home() / ".config/gtk-3.0/settings.ini").read_text()
assert "Adwaita" in gtk3_restored
assert "Nordic" not in gtk3_restored

# Verify exact restoration (byte-for-byte)
assert gtk3_restored == gtk3_original
```

---

## IT-005: Theme Validation - Compatibility Checking

**Test ID:** IT-005
**Priority:** P1 (High)
**File:** `tests/test_integration.py::test_theme_validation_compatibility_checking`

### Description
Validates users get warnings before applying incomplete or incompatible themes. Tests validation logic, compatibility reporting, and the ability to proceed with warnings or cancel.

### Test Flow

1. **Setup:** Create incomplete theme (has GTK3 but missing GTK4, no Qt support)
2. **Validate:** Call `manager.validate_theme("IncompleteTheme")`
3. **Check Report:** Assert `ValidationResult` contains warnings about missing components
4. **Attempt Apply (Force):** Call `manager.apply_theme("IncompleteTheme", force=True)`
5. **Verify Partial Application:** GTK3 handler succeeds, GTK4/Qt handlers skip or warn
6. **Verify User Warned:** Result message mentions incompleteness
7. **Verify No Crash:** Incomplete theme doesn't break the system

### Expected Results

- ✅ Incomplete themes are detected during validation
- ✅ `ValidationResult` contains specific warnings:
  - "Missing GTK4 theme files"
  - "No Qt theme support"
  - "Incomplete color palette (missing accent colors)"
- ✅ Validation is accurate (doesn't false-positive on valid themes)
- ✅ User can proceed anyway with `force=True` parameter
- ✅ Partial application works (only compatible handlers apply)
- ✅ System doesn't crash on incomplete themes

### Edge Cases

- **Completely empty theme:** No files at all, should fail validation entirely
- **Theme with only colors, no files:** Can CSS-only themes work? (Should generate files)
- **Theme with malformed CSS:** Syntax errors in theme files, should detect

### Mock Requirements

**Incomplete Theme Structure:**
```python
# Theme with GTK3 only, missing GTK4 and Qt
incomplete_theme_path/
  index.theme          # Metadata
  gtk-3.0/
    gtk.css            # Has GTK3 theme
  # Missing: gtk-4.0/, no qt/ directory
```

**Validation Result Verification:**
```python
def has_warning(validation_result: ValidationResult, warning_text: str) -> bool:
    """Check if validation result contains specific warning."""
    return any(warning_text in msg.message
               for msg in validation_result.messages
               if msg.level == ValidationLevel.WARNING)
```

**Why these mocks:**
- Incomplete theme: Test real-world scenario (many themes lack Qt support)
- Validation checker: Verify specific warnings are present

### Assertions

```python
# Validate incomplete theme
validation_result = manager.validate_theme("IncompleteTheme")

# Check validation detected issues
assert validation_result.has_warnings() == True
assert any("GTK4" in msg.message or "missing" in msg.message.lower()
           for msg in validation_result.messages)

# Attempt to apply (should warn but not crash)
result = manager.apply_theme("IncompleteTheme")

# Verify partial application (or complete failure, both acceptable)
if result.overall_success:
    # Partial application succeeded
    assert "gtk" in result.handler_results
    assert result.handler_results["gtk"].success == True

    # Qt handler should skip or fail gracefully
    if "qt" in result.handler_results:
        assert result.handler_results["qt"].success == False or \
               "not supported" in result.handler_results["qt"].message.lower()
else:
    # Complete failure is also acceptable for incomplete themes
    assert "incomplete" in result.message.lower() or \
           "validation" in result.message.lower()

# Verify no crash (we got here without exception)
assert True  # If we reach this line, no crash occurred
```

---

## Implementation Notes

### Test File Structure

All 5 scenarios should be in a single file: `tests/test_integration.py`

```python
"""
Integration tests for Unified Theming system.

Tests complete workflows and component interaction.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from unified_theming.core.manager import UnifiedThemeManager
from unified_theming.core.config import ConfigManager
from unified_theming.core.types import ValidationLevel

# Import fixtures from fixtures/integration_fixtures.py
from fixtures.integration_fixtures import (
    mock_file_system,
    mock_theme_adwaita_dark,
    mock_theme_nordic,
    mock_theme_incomplete,
    mock_subprocess_run,
    integration_test_theme_repository
)

class TestIntegrationScenarios:
    """Integration test scenarios for Week 3 Day 1."""

    def test_happy_path_full_theme_application(
        self,
        mock_file_system,
        mock_theme_adwaita_dark,
        mock_subprocess_run
    ):
        """IT-001: Happy path - full theme application workflow."""
        # Implementation here
        pass

    # ... other 4 tests
```

### Execution Order

Tests should be independent and can run in any order. However, logical reading order:
1. IT-001 (Happy Path) - Establishes baseline functionality
2. IT-003 (Multi-Handler) - Builds on happy path with multiple handlers
3. IT-004 (Backup/Restore) - Tests data safety
4. IT-002 (Error Recovery) - Tests failure scenarios
5. IT-005 (Validation) - Tests pre-application checks

### Performance Target

All 5 tests combined should run in **<5 seconds**:
- Each test: ~1 second (fast mocking, no real I/O)
- Total: 5 seconds
- Acceptable: <10 seconds if tests are comprehensive

### Coverage Impact

**Expected coverage gain:** +3-5% overall project coverage

**Why:**
- Integration tests execute complete workflows (touch many modules)
- Validates code paths not covered by unit tests (error recovery, multi-handler coordination)
- Tests real-world scenarios (user workflows)

**Modules most impacted:**
- `manager.py`: +5-10% (tests apply_theme, rollback logic)
- `config.py`: +3-5% (tests backup/restore workflows)
- `handlers/*.py`: +2-3% each (tests apply in realistic contexts)

---

## Success Criteria

### Functional Requirements
- [ ] All 5 test scenarios implemented
- [ ] All tests passing (green)
- [ ] Tests run in <5 seconds combined
- [ ] No regressions (existing 149 tests still pass)

### Quality Requirements
- [ ] Tests use realistic data (not minimal mocks)
- [ ] Tests are isolated (no shared state)
- [ ] Tests have clear failure messages
- [ ] Edge cases documented and tested
- [ ] Assertions are specific (not just `assert True`)

### Documentation Requirements
- [ ] Each test has clear docstring
- [ ] Test flow documented in comments
- [ ] Expected results documented
- [ ] Mock requirements documented

---

## Handoff to Implementation

**Next Step:** Qwen Coder implements these 5 scenarios using fixtures defined in `integration_fixtures.py`

**Implementation Order:**
1. Start with IT-001 (Happy Path) - simplest, validates foundation
2. Move to IT-003 (Multi-Handler) - builds on happy path
3. Implement IT-004 (Backup/Restore) - uses same fixtures
4. Add IT-002 (Error Recovery) - requires failure injection
5. Finish with IT-005 (Validation) - uses incomplete theme fixture

**Estimated Time:** 2.5 hours (30-45 min per test)

**EOD Target:** All 5 tests implemented and passing by Day 1 EOD (17:00)

---

**Document Status:** ✅ COMPLETE - Ready for Implementation

**Author:** Claude Code (Strategic Architect)
**Date:** October 22, 2025
**Review Status:** Awaiting Qwen Coder implementation

