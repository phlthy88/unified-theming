# Integration Test Scenarios

**Project:** Unified Theming v1.0.0
**Week:** 3, Days 1-2 (Integration Testing)
**Author:** Claude Code
**Date:** October 21, 2025

---

## Executive Summary

This document defines end-to-end integration test scenarios for the Unified Theming project. Integration tests validate complete workflows across multiple components (parser, manager, handlers, config) to ensure the system works cohesively.

**Scope:** Testing the **interactions between components**, not individual unit functionality (that's covered in Week 1-2 tests).

**Strategic Purpose:**
- Validate multi-component workflows (discover → parse → apply → verify)
- Test error recovery and rollback mechanisms
- Ensure handler coordination works correctly
- Verify data flows correctly between layers (4-layer architecture)

---

## Test Organization

### Test File Structure

```
tests/
├── test_integration.py              # Main integration tests (this document)
├── test_integration_error_recovery.py  # Error handling scenarios
├── test_integration_multi_handler.py   # Multi-handler coordination
└── fixtures/
    ├── integration_themes/          # Complete themes for E2E testing
    │   ├── Adwaita-Test/
    │   ├── Breeze-Test/
    │   └── Corrupted-Test/
    └── integration_configs/         # Mock config files
```

---

## Scenario Categories

1. **Happy Path Scenarios** (everything succeeds)
2. **Partial Failure Scenarios** (some handlers fail, others succeed)
3. **Catastrophic Failure Scenarios** (rollback triggered)
4. **Error Recovery Scenarios** (graceful degradation)
5. **Multi-Handler Coordination** (targeted application)
6. **Theme Switching Scenarios** (consistency across switches)
7. **Backup/Restore Workflows** (state preservation)

---

## 1. Happy Path Scenarios

### Scenario 1.1: Complete Theme Application Workflow

**User Story:** As a user, I want to discover a theme, apply it to all toolkits, and verify it was applied correctly.

**Given:**
- System has ≥1 valid theme installed (Adwaita-dark)
- All toolkits available (GTK2/3/4, Qt, Flatpak, Snap)
- No existing backups

**When:**
1. User runs `unified-theming list`
2. User runs `unified-theming apply Adwaita-dark`
3. User runs `unified-theming current`

**Then:**
- Step 1: Returns list containing "Adwaita-dark"
- Step 2:
  - Backup created automatically
  - Theme applied to all handlers (GTK/Qt/Flatpak/Snap)
  - Success message displayed
  - Exit code 0
- Step 3: All toolkits show "Adwaita-dark" as current theme

**Test Implementation:**
```python
def test_complete_theme_application_workflow(manager, parser):
    """Test full workflow: discover → apply → verify."""

    # Step 1: Discover themes
    themes = parser.discover_themes()
    assert "Adwaita-dark" in themes

    # Step 2: Apply theme
    result = manager.apply_theme("Adwaita-dark")
    assert result.success is True
    assert result.backup_created is True
    assert all(r.success for r in result.handler_results.values())

    # Step 3: Verify application
    current = manager.get_current_theme()
    assert current["gtk3"] == "Adwaita-dark"
    assert current["gtk4"] == "Adwaita-dark"
    assert current["qt"] == "Adwaita-dark"
```

---

### Scenario 1.2: Targeted Theme Application

**User Story:** As a user, I want to apply a theme only to GTK, leaving Qt unchanged.

**Given:**
- System has Adwaita-dark theme
- Current GTK theme: Breeze
- Current Qt theme: Breeze

**When:**
User runs `unified-theming apply Adwaita-dark --targets gtk`

**Then:**
- GTK handlers execute (GTK2/3/4)
- Qt handlers skip (not invoked)
- Flatpak/Snap handlers skip
- Success message: "Applied to 3 of 3 targets"
- GTK theme changes to Adwaita-dark
- Qt theme remains Breeze

**Test Implementation:**
```python
def test_targeted_theme_application_gtk_only(manager):
    """Test targeted application to GTK only."""

    # Initial state
    manager.apply_theme("Breeze")

    # Apply Adwaita-dark to GTK only
    result = manager.apply_theme("Adwaita-dark", targets=["gtk"])

    assert result.success is True
    assert "gtk" in result.handler_results
    assert "qt" not in result.handler_results

    # Verify
    current = manager.get_current_theme()
    assert current["gtk3"] == "Adwaita-dark"
    assert current["qt"] == "Breeze"  # Unchanged
```

---

### Scenario 1.3: Backup and Restore Workflow

**User Story:** As a user, I want to backup my current theme, apply a new theme, then restore the backup if I don't like it.

**Given:**
- Current theme: Adwaita (light)
- User wants to try Adwaita-dark

**When:**
1. User runs `unified-theming backup`
2. User runs `unified-theming apply Adwaita-dark`
3. User dislikes Adwaita-dark
4. User runs `unified-theming list-backups`
5. User runs `unified-theming restore <backup_id>`

**Then:**
- Step 1: Manual backup created, backup ID returned
- Step 2: Adwaita-dark applied, automatic backup also created
- Step 4: Shows 2 backups (manual + automatic)
- Step 5: Restores to Adwaita (light), theme reverted

**Test Implementation:**
```python
def test_backup_and_restore_workflow(manager, config):
    """Test manual backup → theme change → restore."""

    # Step 1: Manual backup
    manager.apply_theme("Adwaita")
    backup1 = config.create_backup("Adwaita")

    # Step 2: Apply new theme
    result = manager.apply_theme("Adwaita-dark")
    assert result.success is True

    # Step 3: Verify new theme
    current = manager.get_current_theme()
    assert current["gtk3"] == "Adwaita-dark"

    # Step 4: List backups
    backups = config.list_backups()
    assert len(backups) == 2  # Manual + automatic

    # Step 5: Restore manual backup
    restored = config.restore_backup(backup1.id)
    assert restored is True

    # Step 6: Verify restoration
    current = manager.get_current_theme()
    assert current["gtk3"] == "Adwaita"
```

---

## 2. Partial Failure Scenarios

### Scenario 2.1: GTK Succeeds, Qt Fails (>50% Success)

**User Story:** As a user with only GTK installed (no Qt), I want to apply a theme successfully without errors.

**Given:**
- GTK2/3/4 installed and available
- Qt NOT installed (is_available() = False)
- Flatpak available

**When:**
User runs `unified-theming apply Adwaita-dark`

**Then:**
- GTK handlers execute successfully
- Qt handler skips (not available)
- Flatpak handler executes successfully
- Overall result: SUCCESS (2/2 available handlers succeeded)
- User sees: "Applied successfully to GTK, Flatpak. Qt not available."
- No rollback triggered

**Test Implementation:**
```python
def test_partial_success_qt_unavailable(manager, mock_handlers):
    """Test success when Qt is not available."""

    # Mock Qt handler as unavailable
    mock_handlers["qt"].is_available.return_value = False
    mock_handlers["gtk"].is_available.return_value = True
    mock_handlers["flatpak"].is_available.return_value = True

    result = manager.apply_theme("Adwaita-dark")

    assert result.success is True  # >50% succeeded
    assert result.handler_results["gtk"].success is True
    assert "qt" not in result.handler_results  # Skipped
    assert result.handler_results["flatpak"].success is True

    # Verify message
    assert "Qt not available" in result.message
```

---

### Scenario 2.2: Flatpak Fails, Others Succeed (>50% Success)

**User Story:** As a user without Flatpak portal support, I want theme application to succeed for GTK/Qt even if Flatpak fails.

**Given:**
- GTK and Qt available
- Flatpak portal not configured (handler fails)

**When:**
User runs `unified-theming apply Adwaita-dark`

**Then:**
- GTK handlers succeed
- Qt handlers succeed
- Flatpak handler fails (portal error)
- Overall result: SUCCESS (2/3 succeeded = 66%)
- User sees: "Applied successfully to GTK, Qt. Flatpak failed: portal not configured."
- No rollback triggered

**Test Implementation:**
```python
def test_partial_success_flatpak_fails(manager, mock_handlers):
    """Test success when Flatpak fails."""

    mock_handlers["gtk"].apply_theme.return_value = True
    mock_handlers["qt"].apply_theme.return_value = True
    mock_handlers["flatpak"].apply_theme.side_effect = Exception("Portal not configured")

    result = manager.apply_theme("Adwaita-dark")

    assert result.success is True  # 2/3 = 66% > 50%
    assert result.handler_results["gtk"].success is True
    assert result.handler_results["qt"].success is True
    assert result.handler_results["flatpak"].success is False

    # Verify no rollback
    assert result.rollback_triggered is False
```

---

## 3. Catastrophic Failure Scenarios

### Scenario 3.1: All Handlers Fail (<50% Success) → Rollback

**User Story:** As a user, if theme application fails catastrophically, I want the system to restore my previous theme automatically.

**Given:**
- Current theme: Adwaita (light)
- Backup of Adwaita exists
- User tries to apply corrupted theme

**When:**
User runs `unified-theming apply CorruptedTheme`

**Then:**
- GTK handler fails (CSS parse error)
- Qt handler fails (invalid colors)
- Flatpak handler fails (permission denied)
- Overall result: FAILURE (0/3 = 0% < 50%)
- Automatic rollback triggered
- Previous theme (Adwaita) restored
- User sees: "Theme application failed. Rolled back to Adwaita."

**Test Implementation:**
```python
def test_catastrophic_failure_triggers_rollback(manager, config, mock_handlers):
    """Test rollback when all handlers fail."""

    # Apply initial theme (creates backup)
    manager.apply_theme("Adwaita")

    # Mock all handlers to fail
    mock_handlers["gtk"].apply_theme.side_effect = Exception("CSS parse error")
    mock_handlers["qt"].apply_theme.side_effect = Exception("Invalid colors")
    mock_handlers["flatpak"].apply_theme.side_effect = Exception("Permission denied")

    # Attempt to apply corrupted theme
    result = manager.apply_theme("CorruptedTheme")

    assert result.success is False  # 0/3 < 50%
    assert result.rollback_triggered is True

    # Verify rollback restored previous theme
    current = manager.get_current_theme()
    assert current["gtk3"] == "Adwaita"

    # Verify error message
    assert "Rolled back" in result.message
```

---

### Scenario 3.2: Rollback Itself Fails (Critical Error)

**User Story:** As a user, if both theme application AND rollback fail, I want clear error messages explaining what to do.

**Given:**
- Theme application fails (all handlers)
- Backup exists but is corrupted
- Rollback attempt fails

**When:**
User runs `unified-theming apply CorruptedTheme`

**Then:**
- All handlers fail
- Rollback triggered
- Rollback fails (corrupted backup)
- Critical error logged
- User sees: "CRITICAL: Theme application failed and rollback failed. Manual recovery required. See ~/.local/state/unified-theming/unified-theming.log"
- Exit code 2 (system error)

**Test Implementation:**
```python
def test_rollback_failure_critical_error(manager, config, mock_handlers):
    """Test critical error when rollback fails."""

    # Mock handlers to fail
    for handler in mock_handlers.values():
        handler.apply_theme.side_effect = Exception("Handler failed")

    # Mock rollback to fail
    config.restore_backup.side_effect = RollbackError("Corrupted backup")

    # Attempt application
    with pytest.raises(RollbackError) as exc_info:
        manager.apply_theme("CorruptedTheme")

    assert "Corrupted backup" in str(exc_info.value)

    # Verify critical log written (check log file or mock logger)
    # assert "CRITICAL" in log_output
```

---

## 4. Error Recovery Scenarios

### Scenario 4.1: Theme Not Found (Graceful Error)

**User Story:** As a user, if I mistype a theme name, I want a helpful error message suggesting available themes.

**Given:**
- Available themes: Adwaita, Adwaita-dark, Breeze

**When:**
User runs `unified-theming apply Adwata` (typo)

**Then:**
- Theme not found error raised
- User sees: "Error: Theme 'Adwata' not found. Did you mean: Adwaita? Available themes: Adwaita, Adwaita-dark, Breeze"
- Exit code 1 (user error)
- No backup created (no operation performed)

**Test Implementation:**
```python
def test_theme_not_found_error_message(manager):
    """Test helpful error message for non-existent theme."""

    with pytest.raises(ThemeNotFoundError) as exc_info:
        manager.apply_theme("Adwata")  # Typo

    error_msg = str(exc_info.value)
    assert "not found" in error_msg
    assert "Adwaita" in error_msg  # Suggestion
    assert "Available themes" in error_msg
```

---

### Scenario 4.2: Backup Fails Before Application (Safety Check)

**User Story:** As a user, if the system can't backup my current theme, I want theme application to abort (safety first).

**Given:**
- Disk full (backup directory write fails)
- User tries to apply new theme

**When:**
User runs `unified-theming apply Adwaita-dark`

**Then:**
- Backup creation fails (disk full error)
- Theme application ABORTED (no changes made)
- User sees: "Error: Cannot create backup (disk full). Theme not applied."
- Exit code 2 (system error)
- Current theme unchanged

**Test Implementation:**
```python
def test_backup_failure_aborts_application(manager, config):
    """Test theme application aborted if backup fails."""

    # Mock backup to fail
    config.create_backup.side_effect = BackupError("Disk full")

    with pytest.raises(BackupError) as exc_info:
        manager.apply_theme("Adwaita-dark")

    assert "Disk full" in str(exc_info.value)

    # Verify theme not applied (no handlers called)
    current = manager.get_current_theme()
    assert current["gtk3"] != "Adwaita-dark"
```

---

### Scenario 4.3: Partial Handler Failure with Detailed Reporting

**User Story:** As a user, when some handlers fail, I want to know exactly which ones succeeded and which failed, with reasons.

**Given:**
- GTK available, Qt available, Flatpak available
- Qt handler fails (kdeglobals permission denied)

**When:**
User runs `unified-theming apply Adwaita-dark`

**Then:**
- Result shows detailed breakdown:
  - ✅ GTK2: SUCCESS
  - ✅ GTK3: SUCCESS
  - ✅ GTK4: SUCCESS
  - ❌ Qt: FAILED (permission denied: ~/.config/kdeglobals)
  - ✅ Flatpak: SUCCESS
- Overall: SUCCESS (4/5 = 80%)
- User sees table of results

**Test Implementation:**
```python
def test_detailed_handler_results_reporting(manager, mock_handlers):
    """Test detailed per-handler results."""

    # Mock Qt to fail, others succeed
    mock_handlers["gtk"].apply_theme.return_value = True
    mock_handlers["qt"].apply_theme.side_effect = PermissionError("Permission denied")
    mock_handlers["flatpak"].apply_theme.return_value = True

    result = manager.apply_theme("Adwaita-dark")

    assert result.success is True  # 2/3 available

    # Verify detailed results
    assert result.handler_results["gtk"].success is True
    assert result.handler_results["qt"].success is False
    assert "Permission denied" in result.handler_results["qt"].error_message
    assert result.handler_results["flatpak"].success is True
```

---

## 5. Multi-Handler Coordination Scenarios

### Scenario 5.1: Apply to Multiple Targets (GTK + Qt)

**User Story:** As a user, I want to apply a theme to both GTK and Qt, but not containers.

**Given:**
- All handlers available

**When:**
User runs `unified-theming apply Adwaita-dark --targets gtk,qt`

**Then:**
- GTK handlers execute (GTK2/3/4)
- Qt handler executes
- Flatpak handler skips
- Snap handler skips
- Success message: "Applied to GTK, Qt"

**Test Implementation:**
```python
def test_multi_target_application(manager):
    """Test applying to multiple specific targets."""

    result = manager.apply_theme("Adwaita-dark", targets=["gtk", "qt"])

    assert result.success is True
    assert "gtk" in result.handler_results
    assert "qt" in result.handler_results
    assert "flatpak" not in result.handler_results
    assert "snap" not in result.handler_results
```

---

### Scenario 5.2: Invalid Target Specified

**User Story:** As a user, if I specify an invalid target, I want a clear error message.

**Given:**
- Valid targets: gtk, qt, flatpak, snap

**When:**
User runs `unified-theming apply Adwaita-dark --targets kde`

**Then:**
- Error: "Invalid target 'kde'. Valid targets: gtk, qt, flatpak, snap"
- Exit code 1
- No theme application

**Test Implementation:**
```python
def test_invalid_target_error(manager):
    """Test error for invalid target specification."""

    with pytest.raises(ValueError) as exc_info:
        manager.apply_theme("Adwaita-dark", targets=["kde"])

    assert "Invalid target" in str(exc_info.value)
    assert "kde" in str(exc_info.value)
```

---

## 6. Theme Switching Scenarios

### Scenario 6.1: Rapid Theme Switching (A → B → A)

**User Story:** As a user experimenting with themes, I want to switch between themes multiple times without issues.

**Given:**
- Themes available: Adwaita, Adwaita-dark

**When:**
1. User applies Adwaita
2. User applies Adwaita-dark
3. User applies Adwaita again

**Then:**
- All three applications succeed
- Final state: Adwaita applied
- No config corruption
- Backups created for each change

**Test Implementation:**
```python
def test_rapid_theme_switching_consistency(manager):
    """Test rapid switching maintains consistency."""

    # Switch: Adwaita → Adwaita-dark → Adwaita
    result1 = manager.apply_theme("Adwaita")
    assert result1.success is True

    result2 = manager.apply_theme("Adwaita-dark")
    assert result2.success is True

    result3 = manager.apply_theme("Adwaita")
    assert result3.success is True

    # Verify final state
    current = manager.get_current_theme()
    assert current["gtk3"] == "Adwaita"
    assert current["gtk4"] == "Adwaita"

    # Verify 3 backups created
    backups = manager.config.list_backups()
    assert len(backups) >= 3
```

---

### Scenario 6.2: Theme Switch with Intermediate Failure

**User Story:** As a user, if a theme switch fails, I want my previous theme to remain intact.

**Given:**
- Current theme: Adwaita
- User tries to apply CorruptedTheme

**When:**
1. User applies Adwaita (initial state)
2. User applies CorruptedTheme (fails)
3. User checks current theme

**Then:**
- Application fails, rollback triggered
- Current theme remains Adwaita (unchanged)
- User sees error message

**Test Implementation:**
```python
def test_theme_switch_failure_preserves_state(manager, mock_handlers):
    """Test failed switch doesn't corrupt state."""

    # Apply initial theme
    manager.apply_theme("Adwaita")

    # Mock handlers to fail for CorruptedTheme
    for handler in mock_handlers.values():
        handler.apply_theme.side_effect = Exception("Corrupted")

    # Attempt application (should fail and rollback)
    result = manager.apply_theme("CorruptedTheme")
    assert result.success is False

    # Verify state preserved
    current = manager.get_current_theme()
    assert current["gtk3"] == "Adwaita"  # Unchanged
```

---

## 7. Backup/Restore Workflows

### Scenario 7.1: Restore from Older Backup (Skip Recent)

**User Story:** As a user, I want to restore from an older backup, not just the most recent one.

**Given:**
- Backups exist:
  1. backup_001 (Adwaita, 2 days ago)
  2. backup_002 (Breeze, 1 day ago)
  3. backup_003 (Adwaita-dark, 1 hour ago - current)

**When:**
User runs `unified-theming restore backup_001`

**Then:**
- System restores backup_001 (Adwaita)
- Current theme changes to Adwaita
- backup_002 and backup_003 remain intact

**Test Implementation:**
```python
def test_restore_specific_older_backup(manager, config):
    """Test restoring non-recent backup."""

    # Create 3 backups
    manager.apply_theme("Adwaita")
    backup1 = config.create_backup("Adwaita")

    manager.apply_theme("Breeze")
    backup2 = config.create_backup("Breeze")

    manager.apply_theme("Adwaita-dark")
    backup3 = config.create_backup("Adwaita-dark")

    # Restore oldest backup (backup1)
    restored = config.restore_backup(backup1.id)
    assert restored is True

    # Verify restoration
    current = manager.get_current_theme()
    assert current["gtk3"] == "Adwaita"

    # Verify other backups still exist
    backups = config.list_backups()
    assert len(backups) == 3
```

---

### Scenario 7.2: Automatic Pruning of Old Backups

**User Story:** As a user, I want old backups to be pruned automatically so they don't fill my disk.

**Given:**
- Backup limit: 10 backups
- User has created 12 backups

**When:**
User applies a new theme (13th backup created)

**Then:**
- Oldest 3 backups deleted
- Newest 10 backups retained
- No errors during pruning

**Test Implementation:**
```python
def test_automatic_backup_pruning(manager, config):
    """Test old backups are pruned automatically."""

    # Create 12 backups
    for i in range(12):
        manager.apply_theme(f"Theme_{i}")

    # Verify 10 newest retained (2 oldest pruned)
    backups = config.list_backups()
    assert len(backups) == 10

    # Apply 13th theme
    manager.apply_theme("Theme_13")

    # Verify still 10 backups
    backups = config.list_backups()
    assert len(backups) == 10

    # Verify oldest backup is NOT backup_001
    backup_ids = [b.id for b in backups]
    assert "backup_001" not in backup_ids
```

---

## Cross-Cutting Scenarios

### Scenario 8.1: Handler Order Independence

**Purpose:** Verify handlers can execute in any order without affecting results.

**Test:**
```python
def test_handler_execution_order_independence(manager):
    """Test handler order doesn't affect outcome."""

    # Apply with handlers in order: GTK, Qt, Flatpak
    result1 = manager.apply_theme("Adwaita-dark")

    # Reorder handlers internally
    manager._reorder_handlers(["qt", "flatpak", "gtk"])

    # Apply again
    result2 = manager.apply_theme("Adwaita-dark")

    # Results should be identical
    assert result1.handler_results.keys() == result2.handler_results.keys()
```

---

### Scenario 8.2: Color Palette Consistency Across Handlers

**Purpose:** Verify GTK colors translate to Qt correctly.

**Test:**
```python
def test_color_translation_consistency(manager):
    """Test GTK colors translate correctly to Qt."""

    result = manager.apply_theme("Adwaita-dark")

    # Extract colors from GTK config
    gtk_colors = read_gtk4_css_colors()

    # Extract colors from Qt config
    qt_colors = read_kdeglobals_colors()

    # Verify background color consistency
    gtk_bg = gtk_colors["theme_bg_color"]
    qt_bg = qt_colors["BackgroundNormal"]

    # Should be same or very close (allowing for translation)
    assert color_similarity(gtk_bg, qt_bg) > 0.95
```

---

## Test Data Requirements

### Integration Test Themes

**Create realistic test themes:**

```python
# tests/fixtures/integration_themes/

# Adwaita-Test: Complete, valid theme
Adwaita-Test/
├── index.theme
├── gtk-2.0/
│   └── gtkrc
├── gtk-3.0/
│   └── gtk.css
└── gtk-4.0/
    └── gtk.css

# Breeze-Test: Complete, valid theme
Breeze-Test/
├── index.theme
├── gtk-3.0/
│   └── gtk.css
└── gtk-4.0/
    └── gtk.css

# Corrupted-Test: Malformed theme (for error testing)
Corrupted-Test/
├── index.theme (malformed)
└── gtk-4.0/
    └── gtk.css (syntax errors)
```

---

## Acceptance Criteria (Week 3, Days 1-2)

### Integration Test Coverage

**MUST HAVE:**
- [ ] 7 happy path scenarios implemented
- [ ] 6 partial failure scenarios implemented
- [ ] 4 catastrophic failure scenarios implemented
- [ ] 3 error recovery scenarios implemented
- [ ] All scenarios pass (100% pass rate)

**SHOULD HAVE:**
- [ ] 5 multi-handler coordination scenarios
- [ ] 3 theme switching scenarios
- [ ] 2 backup/restore workflows

**NICE TO HAVE:**
- [ ] 2 cross-cutting scenarios
- [ ] Color translation consistency tests

---

## Deliverables

1. **Test file:** `tests/test_integration.py` (~500-700 lines)
2. **Error recovery tests:** `tests/test_integration_error_recovery.py`
3. **Multi-handler tests:** `tests/test_integration_multi_handler.py`
4. **Test fixtures:** Integration test themes in `tests/fixtures/`
5. **Documentation:** This file + test docstrings

---

## Handoff to Qwen Coder

**Trigger:** Git tag `handoff/week3-integration`

**Qwen implements:**
- [ ] All happy path scenarios (Scenario 1.1-1.3)
- [ ] All failure scenarios (Scenario 2.1-3.2)
- [ ] Error recovery scenarios (Scenario 4.1-4.3)
- [ ] Multi-handler coordination (Scenario 5.1-5.2)
- [ ] Theme switching (Scenario 6.1-6.2)
- [ ] Backup/restore workflows (Scenario 7.1-7.2)

**Validation by Opencode AI:**
- [ ] All integration tests pass
- [ ] No regressions in unit tests
- [ ] Integration test coverage ≥90% of scenarios documented

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-21 | Initial integration test scenarios | Claude Code |

---

**These scenarios ensure the Unified Theming system works end-to-end, with robust error handling and recovery.** 🔄
