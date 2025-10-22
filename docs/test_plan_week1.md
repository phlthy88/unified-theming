# Week 1 Test Plan: Foundation Testing

**Project:** Unified Theming v1.0.0
**Phase:** 2 (Core Engineering - Testing)
**Week:** 1 of 11-13
**Agent:** Qwen Coder (Implementation) | Opencode AI (Validation)
**Author:** Claude Code
**Date:** October 21, 2025

---

## Executive Summary

Week 1 establishes the testing foundation for the entire project by achieving 70-85% coverage on the four most critical modules: `color.py`, `manager.py`, `config.py`, and `gtk_handler.py`. These modules form the critical path—all handlers and integration tests depend on them.

**Strategic Priority: color.py First!**
All other modules depend on color utilities for GTK→Qt color translation and theme parsing. Completing `color.py` testing on Day 1-2 unblocks the rest of the week.

---

## Coverage Targets

| Module | Current | Target | Gap | LOC (est.) | Test Priority |
|--------|---------|--------|-----|------------|--------------|
| `color.py` | 0% | 80% | +80% | ~200 | **P0 - CRITICAL** |
| `manager.py` | 24% | 85% | +61% | ~300 | **P0 - CRITICAL** |
| `config.py` | 15% | 70% | +55% | ~250 | P0 |
| `gtk_handler.py` | 25% | 70% | +45% | ~200 | P0 |
| **TOTAL** | **~18%** | **≥76%** | **+58%** | **~950 lines** | - |

**Success Criteria:** All four modules meet or exceed targets by Week 1, Day 5 (17:00).

---

## Daily Breakdown

### Day 1-2: Color Utilities Testing (CRITICAL PATH)
**Module:** `unified_theming/utils/color.py`
**Test File:** `tests/test_color_utils.py`
**Current Coverage:** 0%
**Target Coverage:** 80%
**Priority:** P0 - CRITICAL (blocks all handlers)

### Day 2-3: Manager Core Testing
**Module:** `unified_theming/core/manager.py`
**Test File:** `tests/test_manager_integration.py`
**Current Coverage:** 24%
**Target Coverage:** 85%
**Priority:** P0 - CRITICAL (orchestrates all operations)

### Day 3-4: Config & Backup Testing
**Module:** `unified_theming/core/config.py`
**Test File:** `tests/test_config_backup.py`
**Current Coverage:** 15%
**Target Coverage:** 70%
**Priority:** P0 (required for rollback safety)

### Day 4-5: GTK Handler Testing
**Module:** `unified_theming/handlers/gtk_handler.py`
**Test File:** `tests/test_gtk_handler.py`
**Current Coverage:** 25%
**Target Coverage:** 70%
**Priority:** P0 (most complex handler, libadwaita CSS injection)

---

## Test Cases: color.py (Days 1-2)

### Overview
The `color.py` module provides color format normalization, translation, validation, and contrast calculation. It's the foundation for all cross-toolkit theming.

**Key Functions to Test:**
- `normalize_color(color: str, target_format: ColorFormat) -> str`
- `translate_color(color: str, from_toolkit: Toolkit, to_toolkit: Toolkit) -> str`
- `validate_color(color: str) -> ValidationResult`
- `get_derived_color(base_color: str, operation: str, amount: float) -> str`
- `calculate_contrast(fg: str, bg: str) -> float`
- `parse_gtk_color(gtk_color_string: str) -> str` (handles @define-color syntax)

### Test Cases

| Test ID | Function | Scenario | Input | Expected Output | Priority |
|---------|----------|----------|-------|----------------|----------|
| **TC-C-001** | `normalize_color` | Hex 6-digit to RGB | `"#FF5733"` | `"rgb(255, 87, 51)"` | P0 |
| **TC-C-002** | `normalize_color` | Hex 3-digit to Hex 6-digit | `"#F57"` | `"#FF5577"` | P0 |
| **TC-C-003** | `normalize_color` | RGB to RGBA (opaque) | `"rgb(255, 87, 51)"` | `"rgba(255, 87, 51, 1.0)"` | P0 |
| **TC-C-004** | `normalize_color` | RGBA to Hex (discard alpha) | `"rgba(255, 87, 51, 0.5)"` | `"#FF5733"` | P1 |
| **TC-C-005** | `normalize_color` | Named color to Hex | `"red"` | `"#FF0000"` | P1 |
| **TC-C-006** | `normalize_color` | HSL to RGB | `"hsl(9, 100%, 60%)"` | `"rgb(255, 87, 51)"` | P1 |
| **TC-C-007** | `normalize_color` | Invalid format | `"not-a-color"` | Raise `ColorValidationError` | P0 |
| **TC-C-008** | `normalize_color` | Empty string | `""` | Raise `ColorValidationError` | P1 |
| **TC-C-009** | `translate_color` | GTK hex to Qt | `"#FF5733"`, `Toolkit.GTK3`, `Toolkit.QT5` | `"#FF5733"` (passthrough) | P0 |
| **TC-C-010** | `translate_color` | GTK @define-color to Qt | `"@theme_bg_color"`, `GTK3`, `QT5` | Resolve to hex, return hex | P0 |
| **TC-C-011** | `translate_color` | Brightness adjustment | `"#808080"`, `GTK3`, `QT5` (darker Qt) | Adjusted hex (~5% darker) | P2 |
| **TC-C-012** | `validate_color` | Valid hex | `"#FF5733"` | `ValidationResult(valid=True)` | P0 |
| **TC-C-013** | `validate_color` | Invalid hex (wrong length) | `"#FF57"` | `ValidationResult(valid=False)` | P0 |
| **TC-C-014** | `validate_color` | Invalid RGB (out of range) | `"rgb(300, 87, 51)"` | `ValidationResult(valid=False)` | P0 |
| **TC-C-015** | `validate_color` | Valid RGBA | `"rgba(255, 87, 51, 0.5)"` | `ValidationResult(valid=True)` | P1 |
| **TC-C-016** | `get_derived_color` | Lighten by 20% | `"#FF5733"`, `"lighten"`, `0.2` | Lighter hex (calculated) | P1 |
| **TC-C-017** | `get_derived_color` | Darken by 20% | `"#FF5733"`, `"darken"`, `0.2` | Darker hex (calculated) | P1 |
| **TC-C-018** | `get_derived_color` | Saturate | `"#808080"`, `"saturate"`, `0.3` | More saturated hex | P2 |
| **TC-C-019** | `get_derived_color` | Invalid operation | `"#FF5733"`, `"invalid"`, `0.2` | Raise `ValueError` | P1 |
| **TC-C-020** | `calculate_contrast` | Black on white (max) | `"#000000"`, `"#FFFFFF"` | `21.0` (WCAG max) | P0 |
| **TC-C-021** | `calculate_contrast` | White on white (min) | `"#FFFFFF"`, `"#FFFFFF"` | `1.0` (WCAG min) | P0 |
| **TC-C-022** | `calculate_contrast` | Real-world contrast | `"#FF5733"`, `"#FFFFFF"` | ~3.3 (calculated) | P1 |
| **TC-C-023** | `parse_gtk_color` | @define-color syntax | `"@theme_bg_color"` | Resolve from GTK CSS vars | P0 |
| **TC-C-024** | `parse_gtk_color` | shade() function | `"shade(@bg_color, 1.2)"` | Calculate shaded color | P1 |
| **TC-C-025** | `parse_gtk_color` | mix() function | `"mix(@fg_color, @bg_color, 0.5)"` | Mix two colors 50/50 | P2 |

**Edge Cases:**
- **TC-C-026**: Color with whitespace: `"  #FF5733  "` → Trim and validate
- **TC-C-027**: Case insensitivity: `"#ff5733"` vs `"#FF5733"` → Normalize to uppercase
- **TC-C-028**: Alpha channel = 0 (transparent): `"rgba(255, 87, 51, 0.0)"` → Handle correctly
- **TC-C-029**: Negative RGB values: `"rgb(-10, 87, 51)"` → Raise error
- **TC-C-030**: Percentage RGB: `"rgb(100%, 50%, 20%)"` → Convert to 0-255 range

**Fixtures Required:**
- `sample_colors`: Dict of valid colors in all formats (hex, rgb, rgba, hsl, named)
- `invalid_colors`: List of malformed color strings
- `gtk_color_variables`: Mock GTK CSS with @define-color definitions

**Estimated LOC:** ~200 lines (30 test functions)

---

## Test Cases: manager.py (Days 2-3)

### Overview
The `UnifiedThemeManager` is the central orchestrator. It coordinates theme discovery (via parser), backup (via config manager), and application (via handlers). Testing focuses on workflow orchestration, error aggregation, and rollback logic.

**Key Methods to Test:**
- `__init__(config_path: Optional[Path])` - Initialization
- `discover_themes() -> Dict[str, ThemeInfo]` - Delegate to parser
- `apply_theme(theme_name: str, targets: Optional[List[str]]) -> ApplicationResult` - Main workflow
- `get_current_theme() -> Dict[str, str]` - Query handlers
- `backup_current_state() -> Backup` - Delegate to config manager
- `restore_backup(backup_id: str) -> bool` - Rollback
- `_prepare_theme_data(theme_info: ThemeInfo) -> ThemeData` - Internal conversion
- `_should_rollback(results: Dict[str, HandlerResult]) -> bool` - Rollback decision logic

### Test Cases

| Test ID | Method | Scenario | Setup | Expected Behavior | Priority |
|---------|--------|----------|-------|-------------------|----------|
| **TC-M-001** | `__init__` | Initialize with default config | No args | Creates handlers, loads config | P0 |
| **TC-M-002** | `__init__` | Initialize with custom config path | Custom `Path` | Uses custom config location | P1 |
| **TC-M-003** | `discover_themes` | Discover themes (success) | Mock parser with 10 themes | Returns dict of 10 `ThemeInfo` | P0 |
| **TC-M-004** | `discover_themes` | No themes found | Mock parser returns empty dict | Returns empty dict, no error | P1 |
| **TC-M-005** | `discover_themes` | Parser raises error | Mock parser raises `ThemeDiscoveryError` | Propagates exception | P0 |
| **TC-M-006** | `apply_theme` | Apply theme (all handlers succeed) | Mock handlers return success | `ApplicationResult.success=True` | P0 |
| **TC-M-007** | `apply_theme` | Apply theme (partial success - 2/3 succeed) | Mock: GTK ok, Qt ok, Flatpak fail | `success=True` (>50%), details show failure | P0 |
| **TC-M-008** | `apply_theme` | Apply theme (catastrophic failure - 1/3 succeed) | Mock: GTK fail, Qt fail, Flatpak ok | `success=False`, triggers rollback | P0 |
| **TC-M-009** | `apply_theme` | Theme not found | Request non-existent theme | Raises `ThemeNotFoundError` | P0 |
| **TC-M-010** | `apply_theme` | Backup fails before application | Mock config manager backup fails | Raises `BackupError`, no theme applied | P0 |
| **TC-M-011** | `apply_theme` | Rollback succeeds after failure | Mock handlers fail, rollback ok | Restores previous state | P0 |
| **TC-M-012** | `apply_theme` | Rollback fails (critical) | Mock handlers + rollback both fail | Raises `RollbackError`, logs critical | P1 |
| **TC-M-013** | `apply_theme` | Targeted application (GTK only) | `targets=["gtk"]` | Only GTK handler called | P1 |
| **TC-M-014** | `apply_theme` | Targeted application (Qt + Flatpak) | `targets=["qt", "flatpak"]` | Only Qt and Flatpak handlers called | P1 |
| **TC-M-015** | `apply_theme` | Invalid target specified | `targets=["invalid"]` | Raises `ValueError` or logs warning | P1 |
| **TC-M-016** | `get_current_theme` | Query all handlers | Mock handlers return theme names | Returns dict {toolkit: theme_name} | P0 |
| **TC-M-017** | `get_current_theme` | Handler unavailable | Mock Qt handler `is_available()=False` | Skips Qt, returns others | P1 |
| **TC-M-018** | `backup_current_state` | Create backup (success) | Mock config manager | Returns `Backup` object with metadata | P0 |
| **TC-M-019** | `backup_current_state` | Backup fails (disk full) | Mock config manager raises `BackupError` | Propagates exception | P1 |
| **TC-M-020** | `restore_backup` | Restore valid backup | Mock config manager with backup | Returns `True`, handlers reconfigured | P0 |
| **TC-M-021** | `restore_backup` | Backup not found | Request non-existent backup ID | Raises `BackupError` | P0 |
| **TC-M-022** | `_prepare_theme_data` | Convert ThemeInfo to ThemeData | Valid `ThemeInfo` | Returns `ThemeData` with colors/paths | P0 |
| **TC-M-023** | `_prepare_theme_data` | Missing color palette | `ThemeInfo` with no colors | Uses defaults or raises error | P1 |
| **TC-M-024** | `_should_rollback` | Success rate 100% (3/3) | All handlers succeed | Returns `False` (no rollback) | P0 |
| **TC-M-025** | `_should_rollback` | Success rate 66% (2/3) | 2 succeed, 1 fails | Returns `False` (>50%) | P0 |
| **TC-M-026** | `_should_rollback` | Success rate 33% (1/3) | 1 succeeds, 2 fail | Returns `True` (<50%) | P0 |
| **TC-M-027** | `_should_rollback` | Success rate 0% (0/3) | All handlers fail | Returns `True` (catastrophic) | P0 |

**Edge Cases:**
- **TC-M-028**: Apply theme twice in a row (idempotency) → Second application succeeds without errors
- **TC-M-029**: Concurrent theme applications (threading) → Ensure thread safety (may require lock)
- **TC-M-030**: Apply theme with no handlers available → Raises error or returns failure immediately

**Fixtures Required:**
- `mock_parser`: Returns predefined `ThemeInfo` objects
- `mock_handlers`: GTK/Qt/Flatpak handlers with configurable success/failure
- `mock_config_manager`: Backup/restore operations with configurable behavior
- `sample_theme_info`: Valid `ThemeInfo` for Adwaita-dark
- `sample_theme_data`: Converted `ThemeData` for Adwaita-dark

**Estimated LOC:** ~300 lines (30 test functions)

---

## Test Cases: config.py (Days 3-4)

### Overview
The `ConfigManager` handles backup creation, restoration, rollback, and pruning of old backups. It ensures users can safely revert theme changes.

**Key Methods to Test:**
- `create_backup(theme_name: str) -> Backup` - Create timestamped backup
- `restore_backup(backup_id: str) -> bool` - Restore from backup
- `list_backups() -> List[Backup]` - Get all available backups
- `prune_old_backups(keep: int = 10) -> int` - Delete old backups
- `get_backup_metadata(backup_id: str) -> Backup` - Query backup details
- `_copy_config_files(dest: Path) -> None` - Internal backup logic
- `_restore_config_files(src: Path) -> None` - Internal restore logic

### Test Cases

| Test ID | Method | Scenario | Setup | Expected Behavior | Priority |
|---------|--------|----------|-------|-------------------|----------|
| **TC-CF-001** | `create_backup` | Create backup (success) | Mock config files exist | Backup created, metadata correct | P0 |
| **TC-CF-002** | `create_backup` | Backup with theme name | `theme_name="Adwaita-dark"` | Backup ID includes theme name | P0 |
| **TC-CF-003** | `create_backup` | Backup directory created | No backup dir exists | Creates `~/.config/unified-theming/backups/` | P0 |
| **TC-CF-004** | `create_backup` | Backup includes all config files | GTK4, kdeglobals, Kvantum exist | All files copied to backup dir | P0 |
| **TC-CF-005** | `create_backup` | Backup fails (permission denied) | Mock disk write error | Raises `BackupError` | P1 |
| **TC-CF-006** | `create_backup` | Backup fails (disk full) | Mock `OSError` on write | Raises `BackupError` | P1 |
| **TC-CF-007** | `restore_backup` | Restore valid backup | Backup exists | Config files restored, returns `True` | P0 |
| **TC-CF-008** | `restore_backup` | Backup not found | Invalid backup ID | Raises `BackupError` | P0 |
| **TC-CF-009** | `restore_backup` | Restore overwrites current config | Current config differs from backup | Current config replaced | P0 |
| **TC-CF-010** | `restore_backup` | Restore fails (corrupted backup) | Backup dir missing files | Raises `BackupError` or `RollbackError` | P1 |
| **TC-CF-011** | `list_backups` | List all backups (10 exist) | 10 backups in dir | Returns list of 10 `Backup` objects | P0 |
| **TC-CF-012** | `list_backups` | No backups exist | Empty backup dir | Returns empty list | P1 |
| **TC-CF-013** | `list_backups` | Backups sorted by timestamp | Backups created out of order | Returns sorted (newest first) | P1 |
| **TC-CF-014** | `prune_old_backups` | Prune with 15 backups, keep 10 | 15 backups exist | Deletes 5 oldest, returns 5 | P0 |
| **TC-CF-015** | `prune_old_backups` | Prune with 5 backups, keep 10 | Only 5 backups exist | Deletes 0, returns 0 | P1 |
| **TC-CF-016** | `prune_old_backups` | Prune keeps newest backups | 15 backups, various timestamps | Oldest 5 deleted, newest 10 remain | P0 |
| **TC-CF-017** | `prune_old_backups` | Prune fails (permission denied) | Mock file delete error | Logs warning, continues (partial prune) | P1 |
| **TC-CF-018** | `get_backup_metadata` | Get metadata for valid backup | Backup exists | Returns `Backup` with correct metadata | P0 |
| **TC-CF-019** | `get_backup_metadata` | Metadata for non-existent backup | Invalid backup ID | Raises `BackupError` | P1 |
| **TC-CF-020** | `_copy_config_files` | Copy all GTK4/Qt config files | Files exist | All files copied to dest | P0 |
| **TC-CF-021** | `_copy_config_files` | Handle missing config file | gtk-4.0/gtk.css missing | Logs warning, continues (partial backup) | P1 |
| **TC-CF-022** | `_copy_config_files` | Preserve directory structure | Nested dirs (Kvantum themes) | Directory tree preserved in backup | P1 |
| **TC-CF-023** | `_restore_config_files` | Restore all files from backup | Valid backup | All files restored to original locations | P0 |
| **TC-CF-024** | `_restore_config_files` | Create missing directories | Config dir doesn't exist | Creates dirs before restoring files | P1 |

**Edge Cases:**
- **TC-CF-025**: Backup with same timestamp (unlikely) → Adds suffix to avoid collision
- **TC-CF-026**: Restore while app is running → Ensures file handles closed before overwrite
- **TC-CF-027**: Backup size limit (very large Kvantum themes) → Handles or warns about large backups
- **TC-CF-028**: Symbolic links in config (e.g., gtk.css → shared theme) → Preserves symlinks or copies target

**Fixtures Required:**
- `tmp_backup_dir`: Temporary directory for backups (pytest `tmp_path`)
- `sample_config_files`: Mock GTK4/Qt config files
- `sample_backup`: Pre-created backup for restore tests
- `mock_datetime`: Control timestamp generation for consistent backup IDs

**Estimated LOC:** ~250 lines (28 test functions)

---

## Test Cases: gtk_handler.py (Days 4-5)

### Overview
The `GTKHandler` is the most complex handler. It must generate config files for GTK2 (`.gtkrc-2.0`), GTK3 (`settings.ini`), GTK4 (`gtk.css`), and libadwaita (CSS injection with color variable mapping). Testing focuses on file generation correctness and color variable mapping.

**Key Methods to Test:**
- `apply_theme(theme_data: ThemeData) -> bool` - Main application logic
- `get_current_theme() -> str` - Read current GTK theme
- `validate_compatibility(theme_data: ThemeData) -> ValidationResult` - Check theme structure
- `is_available() -> bool` - Check GTK installation
- `_generate_gtk2_config(theme_data: ThemeData) -> str` - .gtkrc-2.0 content
- `_generate_gtk3_config(theme_data: ThemeData) -> str` - settings.ini content
- `_generate_gtk4_css(theme_data: ThemeData) -> str` - gtk.css with variables
- `_map_libadwaita_colors(gtk_colors: Dict[str, str]) -> Dict[str, str]` - GTK → libadwaita

### Test Cases

| Test ID | Method | Scenario | Input | Expected Output | Priority |
|---------|--------|----------|-------|-----------------|----------|
| **TC-G-001** | `apply_theme` | Apply GTK theme (all versions) | Valid `ThemeData` | Generates .gtkrc-2.0, settings.ini, gtk.css | P0 |
| **TC-G-002** | `apply_theme` | Apply theme (GTK4 only) | `ThemeData` with gtk-4.0 dir | Generates gtk.css only | P1 |
| **TC-G-003** | `apply_theme` | Apply theme (missing GTK2) | No gtk-2.0 in theme | Skips .gtkrc-2.0, generates GTK3/4 | P1 |
| **TC-G-004** | `apply_theme` | File write succeeds | Mock file system | Returns `True`, files written | P0 |
| **TC-G-005** | `apply_theme` | File write fails (permission) | Mock permission error | Returns `False`, logs error | P0 |
| **TC-G-006** | `apply_theme` | Backup existing configs | Files already exist | Old files backed up before overwrite | P1 |
| **TC-G-007** | `get_current_theme` | Read GTK3 theme from settings.ini | settings.ini exists | Returns theme name | P0 |
| **TC-G-008** | `get_current_theme` | No theme set | settings.ini missing or empty | Returns "unknown" or None | P1 |
| **TC-G-009** | `validate_compatibility` | Valid GTK3/4 theme | Complete theme structure | `ValidationResult(valid=True)` | P0 |
| **TC-G-010** | `validate_compatibility` | Missing gtk.css | GTK4 dir exists but no gtk.css | `ValidationResult(valid=False, error)` | P0 |
| **TC-G-011** | `validate_compatibility` | Malformed CSS | CSS syntax errors | `ValidationResult(valid=False, warnings)` | P1 |
| **TC-G-012** | `is_available` | GTK installed | GTK3/4 present on system | Returns `True` | P0 |
| **TC-G-013** | `is_available` | GTK not installed | Mock GTK missing | Returns `False` | P1 |
| **TC-G-014** | `_generate_gtk2_config` | Generate .gtkrc-2.0 | Theme with gtk-2.0 | Valid .gtkrc-2.0 content | P1 |
| **TC-G-015** | `_generate_gtk3_config` | Generate settings.ini | Theme name + icon theme | INI format with `[Settings]` | P0 |
| **TC-G-016** | `_generate_gtk4_css` | Generate gtk.css with variables | Theme with color palette | CSS with @define-color statements | P0 |
| **TC-G-017** | `_generate_gtk4_css` | Include libadwaita colors | Color palette provided | CSS includes libadwaita mappings | P0 |
| **TC-G-018** | `_generate_gtk4_css` | Handle missing colors | Incomplete palette | Uses fallback colors or logs warning | P1 |
| **TC-G-019** | `_map_libadwaita_colors` | Map all core colors | Full GTK palette | Maps bg → window_bg, selected_bg → accent_bg | P0 |
| **TC-G-020** | `_map_libadwaita_colors` | Mapping table correctness | Specific colors | Verify all 15+ mappings (see gtk_handler.py) | P0 |
| **TC-G-021** | `_map_libadwaita_colors` | Missing GTK color | Palette missing `theme_bg_color` | Uses default or logs warning | P1 |
| **TC-G-022** | `_map_libadwaita_colors` | Derived colors (shade) | Base colors only | Generates derived colors (darker/lighter) | P1 |

**Edge Cases:**
- **TC-G-023**: Theme with custom CSS (non-standard variables) → Preserves custom CSS or warns
- **TC-G-024**: Very long theme name (>255 chars) → Truncates or validates length
- **TC-G-025**: Theme path with spaces → Handles path quoting correctly
- **TC-G-026**: Concurrent writes (multiple GTK apps) → Ensures atomic writes or locks
- **TC-G-027**: Theme with RGBA colors (alpha channel) → Converts to opaque or preserves alpha

**Fixtures Required:**
- `sample_theme_data_gtk`: `ThemeData` with GTK2/3/4 structure
- `sample_color_palette`: Dict of GTK color variables (theme_bg_color, etc.)
- `expected_gtkrc`: Expected .gtkrc-2.0 content for comparison
- `expected_gtk4_css`: Expected gtk.css content with libadwaita mappings
- `tmp_config_dir`: Temporary GTK config directory (pytest `tmp_path`)

**Estimated LOC:** ~200 lines (27 test functions)

---

## Shared Fixtures (conftest.py)

### Existing Fixtures (from conftest.py)
- `tmp_theme_dir`: Temporary theme directory
- `valid_theme`: Complete GTK2/3/4 theme
- `incomplete_theme`: GTK3 only (missing GTK4)
- `malformed_theme`: Contains CSS syntax errors
- `parser`: UnifiedThemeParser instance
- `sample_theme_data`: ThemeData for testing

### New Fixtures Required for Week 1

```python
# tests/conftest.py additions

@pytest.fixture
def sample_colors():
    """Valid colors in all formats for color.py testing."""
    return {
        "hex6": "#FF5733",
        "hex3": "#F57",
        "rgb": "rgb(255, 87, 51)",
        "rgba": "rgba(255, 87, 51, 0.5)",
        "hsl": "hsl(9, 100%, 60%)",
        "named": "red",
    }

@pytest.fixture
def invalid_colors():
    """Malformed color strings for validation testing."""
    return [
        "not-a-color",
        "#FF57",  # Wrong length
        "rgb(300, 87, 51)",  # Out of range
        "rgba(255, 87, 51)",  # Missing alpha
        "",  # Empty
    ]

@pytest.fixture
def gtk_color_variables():
    """Mock GTK CSS with @define-color definitions."""
    return """
        @define-color theme_bg_color #FFFFFF;
        @define-color theme_fg_color #000000;
        @define-color theme_selected_bg_color #3584E4;
        @define-color theme_selected_fg_color #FFFFFF;
    """

@pytest.fixture
def mock_handlers():
    """Mock GTK/Qt/Flatpak handlers for manager testing."""
    from unittest.mock import Mock

    gtk = Mock(spec=GTKHandler)
    gtk.is_available.return_value = True
    gtk.apply_theme.return_value = True

    qt = Mock(spec=QtHandler)
    qt.is_available.return_value = True
    qt.apply_theme.return_value = True

    flatpak = Mock(spec=FlatpakHandler)
    flatpak.is_available.return_value = True
    flatpak.apply_theme.return_value = True

    return {"gtk": gtk, "qt": qt, "flatpak": flatpak}

@pytest.fixture
def mock_parser():
    """Mock parser returning predefined themes."""
    from unittest.mock import Mock

    parser = Mock(spec=UnifiedThemeParser)
    parser.discover_themes.return_value = {
        "Adwaita-dark": ThemeInfo(...),
        "Breeze": ThemeInfo(...),
    }
    return parser

@pytest.fixture
def mock_config_manager():
    """Mock config manager for backup/restore testing."""
    from unittest.mock import Mock

    config = Mock(spec=ConfigManager)
    config.create_backup.return_value = Backup(...)
    config.restore_backup.return_value = True
    return config

@pytest.fixture
def tmp_backup_dir(tmp_path):
    """Temporary backup directory."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    return backup_dir

@pytest.fixture
def sample_config_files(tmp_path):
    """Mock GTK4/Qt config files."""
    gtk4_dir = tmp_path / ".config" / "gtk-4.0"
    gtk4_dir.mkdir(parents=True)
    (gtk4_dir / "gtk.css").write_text("@define-color theme_bg_color #FFFFFF;")

    (tmp_path / ".config" / "kdeglobals").write_text("[General]\nColorScheme=Breeze")

    return tmp_path / ".config"

@pytest.fixture
def sample_backup(tmp_backup_dir):
    """Pre-created backup for restore testing."""
    backup_id = "backup_20251021_120000_Adwaita"
    backup_path = tmp_backup_dir / backup_id
    backup_path.mkdir()
    (backup_path / "gtk.css").write_text("@define-color theme_bg_color #000000;")

    return Backup(
        id=backup_id,
        timestamp=datetime(2025, 10, 21, 12, 0, 0),
        theme_name="Adwaita",
        path=backup_path,
    )

@pytest.fixture
def sample_theme_data_gtk():
    """ThemeData with GTK structure for handler testing."""
    return ThemeData(
        name="Adwaita-dark",
        display_name="Adwaita Dark",
        color_palette={
            "theme_bg_color": "#353535",
            "theme_fg_color": "#EEEEEE",
            "theme_selected_bg_color": "#3584E4",
        },
        gtk2_path=Path("/usr/share/themes/Adwaita-dark/gtk-2.0"),
        gtk3_path=Path("/usr/share/themes/Adwaita-dark/gtk-3.0"),
        gtk4_path=Path("/usr/share/themes/Adwaita-dark/gtk-4.0"),
    )
```

---

## Test Execution Guidelines

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all Week 1 tests
pytest tests/test_color_utils.py tests/test_manager_integration.py tests/test_config_backup.py tests/test_gtk_handler.py -v

# Run with coverage
pytest tests/test_color_utils.py tests/test_manager_integration.py tests/test_config_backup.py tests/test_gtk_handler.py --cov=unified_theming --cov-report=html --cov-report=term

# Run specific module tests
pytest tests/test_color_utils.py -v

# Run specific test case
pytest tests/test_color_utils.py::test_normalize_hex_to_rgb -v

# Generate coverage XML for Opencode AI validation
pytest --cov=unified_theming --cov-report=xml --cov-report=html
```

### Coverage Validation (Opencode AI - Day 5)

```bash
# Check coverage per module
coverage report --include="unified_theming/utils/color.py"
coverage report --include="unified_theming/core/manager.py"
coverage report --include="unified_theming/core/config.py"
coverage report --include="unified_theming/handlers/gtk_handler.py"

# Generate HTML report for visual inspection
coverage html
# Open htmlcov/index.html in browser

# Validate against targets
# Expected output:
# color.py: ≥80%
# manager.py: ≥85%
# config.py: ≥70%
# gtk_handler.py: ≥70%
```

---

## Quality Standards

### Test Quality Requirements
1. **Assertions:** Every test must have ≥1 assertion (prefer pytest assertions over assert)
2. **Isolation:** Tests must not depend on each other (use fixtures for shared state)
3. **Naming:** Use descriptive names: `test_{function}_{scenario}_{expected_result}`
4. **Documentation:** Complex tests should have docstrings explaining the scenario
5. **Edge Cases:** P0 functions must test edge cases (empty, null, invalid, boundary)
6. **Mocking:** Use `unittest.mock` for file I/O, external dependencies (not pure logic)
7. **Parametrization:** Use `@pytest.mark.parametrize` for repetitive tests with different inputs

### Code Style
- **Format:** Black (line length 88)
- **Imports:** isort (stdlib, third-party, local)
- **Type Hints:** Required on all test functions
- **Docstrings:** Google style for complex test functions

### Example Test Function

```python
def test_normalize_color_hex_to_rgb(sample_colors: Dict[str, str]) -> None:
    """
    Test color normalization from hex to RGB format.

    Verifies that a 6-digit hex color (#FF5733) is correctly converted
    to RGB format (rgb(255, 87, 51)).
    """
    from unified_theming.utils.color import normalize_color, ColorFormat

    result = normalize_color(sample_colors["hex6"], ColorFormat.RGB)

    assert result == "rgb(255, 87, 51)"
    assert isinstance(result, str)
```

---

## Risk Mitigation

### Risk: color.py Blocks All Other Tests
**Impact:** If color.py tests slip to Day 3, manager/handler tests cannot be properly implemented
**Mitigation:**
- Prioritize color.py above all else (Days 1-2 strict)
- Use placeholder/mock color functions if color.py tests incomplete by Day 2 noon
- Escalate to Claude Code if color.py tests not at 50% by Day 1 EOD

### Risk: Manager Tests Exceed Scope (300 LOC ambitious)
**Impact:** Manager tests incomplete by Day 3, blocking config tests
**Mitigation:**
- Focus on P0 tests first (apply_theme, rollback, initialization)
- Defer P2 tests (targeted application, edge cases) to Week 2 if needed
- Accept 75% manager.py coverage if critical paths covered

### Risk: GTK Handler Complexity Underestimated
**Impact:** Libadwaita color mapping tests incomplete, blocking Qt handler Week 2
**Mitigation:**
- Focus on gtk.css generation (core functionality) first
- Simplify libadwaita mapping tests (test 5 core mappings, defer full 15 to Week 2)
- Accept 60% gtk_handler.py coverage if file generation tests pass

---

## Success Metrics

### Week 1 Completion Criteria (GO/NO-GO for Week 2)

**MUST HAVE (Blockers):**
- [ ] `color.py`: ≥80% coverage
- [ ] `manager.py`: ≥80% coverage (target 85%, floor 80%)
- [ ] All P0 tests pass (no failures)
- [ ] All fixtures documented in conftest.py
- [ ] Coverage reports generated (HTML + XML)

**SHOULD HAVE (Deferrable to Week 2):**
- [ ] `config.py`: ≥70% coverage (acceptable: 60%)
- [ ] `gtk_handler.py`: ≥70% coverage (acceptable: 60%)
- [ ] All P1 tests implemented

**NICE TO HAVE (Optional):**
- [ ] P2 tests implemented
- [ ] Performance benchmarks for color operations

### Handoff to Opencode AI (Day 5)

**Deliverables:**
1. Four test files: `test_color_utils.py`, `test_manager_integration.py`, `test_config_backup.py`, `test_gtk_handler.py`
2. Updated `conftest.py` with new fixtures
3. Coverage report: `coverage.xml` + `htmlcov/`
4. Implementation summary: `docs/test_implementation_week1.md`

**Trigger:** Git tag `qa/week1-tests`

**Opencode AI validates:**
- Coverage targets met
- All tests pass
- No blocking issues (P0 bugs)
- Test quality (assertions, isolation, naming)

**Output:** `docs/qa_report_week1.md` with GO/NO-GO for Week 2

---

## Timeline

| Day | Tasks | Agent | Deliverables | Hours |
|-----|-------|-------|--------------|-------|
| **1** | color.py tests (TC-C-001 to TC-C-030) | Qwen | test_color_utils.py (50% complete) | 8 |
| **2** | Finish color.py, start manager.py (TC-M-001 to TC-M-015) | Qwen | test_color_utils.py (100%), test_manager_integration.py (50%) | 8 |
| **3** | Finish manager.py, start config.py (TC-CF-001 to TC-CF-015) | Qwen | test_manager_integration.py (100%), test_config_backup.py (60%) | 8 |
| **4** | Finish config.py, start gtk_handler.py (TC-G-001 to TC-G-015) | Qwen | test_config_backup.py (100%), test_gtk_handler.py (50%) | 8 |
| **5** | Finish gtk_handler.py, coverage validation | Qwen + Opencode | All tests complete, coverage reports, QA report | 8 |

**Total:** 40 hours (5 days × 8 hours)

---

## Appendix: Quick Reference

### Test Case Priority Legend
- **P0 - Critical:** Must be implemented, blocks progress if missing
- **P1 - High:** Should be implemented, acceptable to defer if time-constrained
- **P2 - Medium:** Nice to have, defer to Week 2 if needed

### Coverage Calculation
```bash
# Line coverage formula
coverage = (lines_executed / total_lines) * 100

# Branch coverage (optional, tracked separately)
branch_coverage = (branches_taken / total_branches) * 100
```

### Contact Escalation
- **Coverage <75% by Day 4:** Escalate to Claude Code for scope adjustment
- **Tests failing >10%:** Escalate to Qwen Coder for debugging support
- **Blocker bugs found:** Escalate to Opencode AI for triage

---

**This test plan is the foundation for the entire project. Execute methodically, prioritize color.py, and achieve ≥80% coverage. Week 2 success depends on Week 1 completion.** ✅

**Handoff to Qwen Coder: Git tag `handoff/week1-plan` when ready to begin implementation.** 🚀
