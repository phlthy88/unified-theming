# Unified Theming Project - Complete State Memory

**Last Updated:** 2025-10-21
**Location:** `/home/live/Downloads/unified-theming/`
**Purpose:** Complete project state for future reference

---

## Project Identity

**Name:** Unified Theming Application
**Goal:** Apply consistent themes across GTK, Qt, and containerized Linux applications
**Architecture:** 4-layer design (UI → Core → Handlers → System Integration)
**Language:** Python 3.10+
**Current Status:** Phase 2 ~70% complete, need to reach 80%+ test coverage

---

## Project History & Development Workflow

### Three-Agent Workflow (Planned)
1. **Claude Code (Phase 1):** Planning, Architecture, Documentation ✅ COMPLETE
2. **Qwen Coder (Phase 2):** Core Implementation ⚠️ ~70% COMPLETE
3. **Opencode AI (Phase 3):** GUI, Packaging, Release ⏳ PENDING

### Current Reality
- Phase 1 completed successfully with comprehensive documentation
- Phase 2 implementation is functional but undertested (25% vs 80% target)
- Core engine WORKS - successfully discovers 59 themes on the system
- All 6 existing tests pass
- CLI commands implemented but untested

---

## Critical File Locations

### Documentation (All Complete)
```
docs/requirements_specification.md    - 35 pages, all requirements
docs/architecture.md                  - 40 pages, system design
docs/developer_guide.md               - 30 pages, development guide
docs/HANDOFF_TO_QWEN_CODER.md        - 25 pages, Phase 2 instructions
PHASE1_COMPLETE.md                    - Phase 1 summary
DIAGNOSTIC_REPORT.md                  - Current status assessment
CLAUDE.md                             - Guide for Claude Code instances
PROJECT_STATE_MEMORY.md               - This file
```

### Core Implementation
```
unified_theming/
├── core/
│   ├── manager.py      - UnifiedThemeManager (24% coverage) ❌ NEEDS TESTS
│   ├── parser.py       - UnifiedThemeParser (87% coverage) ✅ GOOD
│   ├── config.py       - ConfigManager (15% coverage) ❌ NEEDS TESTS
│   ├── types.py        - Data classes (89% coverage) ✅ GOOD
│   └── exceptions.py   - Exception hierarchy (30% coverage)
│
├── handlers/
│   ├── base.py              - BaseHandler interface (83% coverage)
│   ├── gtk_handler.py       - GTK/libadwaita (25% coverage) ❌ NEEDS TESTS
│   ├── qt_handler.py        - Qt5/6 (19% coverage) ❌ NEEDS TESTS
│   ├── flatpak_handler.py   - Flatpak (39% coverage)
│   └── snap_handler.py      - Snap (50% coverage)
│
├── utils/
│   ├── color.py         - Color translation (0% coverage) ❌ CRITICAL
│   ├── file.py          - File operations (23% coverage)
│   ├── validation.py    - Validation (43% coverage)
│   └── logging_config.py - Logging (37% coverage)
│
├── cli/
│   └── commands.py      - Click CLI (0% coverage) ❌ NEEDS TESTS
│
└── gui/
    ├── application.py   - GTK4 app (0% coverage) - Phase 3
    ├── dialogs.py       - Dialogs (0% coverage) - Phase 3
    └── widgets.py       - Widgets (0% coverage) - Phase 3
```

### Tests
```
tests/
├── conftest.py          - Shared fixtures (valid_theme, parser, etc.)
├── test_parser.py       - 4 tests passing ✅
├── test_manager.py      - 2 tests passing ✅
└── fixtures/            - Test theme directories
    ├── ValidTheme/
    ├── IncompleteTheme/
    └── MalformedTheme/
```

---

## How The System Works

### Core Architecture (4 Layers)

**1. User Interface Layer**
- CLI: Click-based commands (list, apply, current, rollback, validate)
- GUI: GTK4/Libadwaita (Phase 3, not yet started)

**2. Application Core Layer**
- `UnifiedThemeManager`: Orchestrates all operations
  - Discovers themes via parser
  - Creates backups via config manager
  - Applies via handlers
  - Aggregates results
  - Rolls back on critical failure

- `UnifiedThemeParser`: Scans theme directories
  - Looks in ~/.themes, ~/.local/share/themes, /usr/share/themes
  - Parses @define-color statements from CSS
  - Extracts metadata from index.theme

- `ConfigManager`: Handles backup/restore
  - Backs up to ~/.config/unified-theming/backups/
  - Keeps last 10 backups
  - Includes gtk.css, kdeglobals, Kvantum configs

**3. Toolkit Handler Layer**
Each handler implements BaseHandler interface:
- `apply_theme(theme_data)` - Apply theme to toolkit
- `get_current_theme()` - Get current theme name
- `validate_compatibility(theme_data)` - Check theme compatibility
- `is_available()` - Check if toolkit installed

**Handlers:**
- GTKHandler: Applies via GSettings + libadwaita CSS injection
- QtHandler: Generates kdeglobals + optional Kvantum theme
- FlatpakHandler: Configures portals and overrides
- SnapHandler: Connects interfaces and portals

**4. System Integration Layer**
- Color utilities: Format conversion, validation, translation
- File utilities: Safe read/write with error handling
- Validation: CSS syntax, theme structure
- Logging: Colored console + rotating file logs

### Theme Application Flow

```
User: "unified-theming apply Nord"
  ↓
1. Manager validates theme exists (via parser)
2. ConfigManager backs up current state
3. Manager prepares ThemeData for each handler
4. Each handler applies theme:
   - GTK: Write CSS to ~/.config/gtk-4.0/gtk.css
   - Qt: Write kdeglobals to ~/.config/kdeglobals
   - Flatpak: Run flatpak override commands
   - Snap: Connect snap interfaces
5. Manager aggregates results
6. If >50% fail, auto-rollback
7. Return ApplicationResult to user
```

### Libadwaita CSS Injection (Key Innovation)

Instead of patching libadwaita (complex, high maintenance), we use CSS injection:
1. Map GTK colors to libadwaita variables:
   - `theme_bg_color` → `window_bg_color`
   - `theme_selected_bg_color` → `accent_bg_color`
   - etc.
2. Generate CSS file with @define-color statements
3. Write to `~/.config/gtk-4.0/gtk.css`
4. Achieves ~70% coverage (colors only, no widget structure)

### Qt Color Translation

1. Parse GTK @define-color from CSS
2. Normalize format (hex, rgb, rgba → #RRGGBB)
3. Map semantic colors:
   - GTK `theme_bg_color` → Qt `BackgroundNormal`
   - GTK `theme_selected_bg_color` → Qt `Highlight`
4. Generate derived colors (hover, disabled states)
5. Write kdeglobals INI file
6. Optionally create Kvantum theme for enhanced styling

---

## Type System

All code is fully type-hinted. Key types:

```python
# Data classes
ThemeInfo          # Complete theme metadata (name, path, colors, etc.)
ThemeData          # Processed theme ready for handler
ApplicationResult  # Aggregated results from all handlers
HandlerResult      # Per-handler result (success, message, warnings)
ValidationResult   # Validation outcome with messages
Backup             # Backup metadata

# Enums
Toolkit           # GTK2, GTK3, GTK4, LIBADWAITA, QT5, QT6, FLATPAK, SNAP
ValidationLevel   # ERROR, WARNING, INFO
ColorFormat       # HEX, RGB, RGBA, HSL, NAMED
```

---

## Exception Hierarchy

All inherit from `UnifiedThemingError`:

**Theme Discovery:**
- ThemeDiscoveryError
- ThemeNotFoundError
- ThemeParseError
- InvalidThemeError

**Theme Application:**
- ThemeApplicationError
- HandlerNotAvailableError
- ColorTranslationError
- CSSGenerationError

**Configuration:**
- BackupError
- RollbackError
- ConfigurationError

**Validation:**
- ValidationError
- ColorValidationError
- CSSValidationError

---

## Testing Strategy

### Current Status: 25% coverage (6 tests passing)

**Test Fixtures (in conftest.py):**
- `tmp_theme_dir` - Temporary theme directory
- `valid_theme` - Complete GTK2/3/4 theme
- `incomplete_theme` - Only GTK3 (missing GTK4)
- `malformed_theme` - CSS syntax errors
- `parser` - UnifiedThemeParser instance
- `sample_theme_data` - ThemeData for testing

**Existing Tests:**
```python
# test_parser.py (4 tests)
test_discover_themes()     # Scans directories
test_parse_theme()         # Parses single theme
test_extract_colors()      # Extracts @define-color
test_validate_theme()      # Validates structure

# test_manager.py (2 tests)
test_manager_initialization()  # Creates manager
test_discover_themes()         # Manager uses parser
```

### Required Tests (to reach 80%)

**Priority 1 - CRITICAL:**
1. test_manager_apply_theme() - Full theme application
2. test_config_backup_restore() - Backup/rollback cycle
3. test_gtk_handler_apply() - GTK theme application
4. test_qt_handler_apply() - Qt theme application
5. test_color_translation() - GTK → Qt color mapping
6. test_css_generation() - Libadwaita CSS output

**Priority 2 - HIGH:**
7. test_cli_commands() - All CLI operations
8. test_file_operations() - Safe read/write
9. test_error_handling() - Exception scenarios
10. test_flatpak_handler() - Container theming

---

## Performance Requirements

| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| Theme discovery (100 themes) | <5s | ~3.7s (59 themes) | ✅ PASS |
| Single theme parsing | <50ms | Not measured | ⏳ TODO |
| Color extraction | <20ms | Not measured | ⏳ TODO |
| Theme application | <2s | Not tested | ⏳ TODO |
| CSS generation | <100ms | Not measured | ⏳ TODO |

---

## Installation & Setup

### Virtual Environment Setup
```bash
cd /home/live/Downloads/unified-theming
python3 -m venv venv
source venv/bin/activate
```

### Current Installation (Without PyGObject)
```bash
pip install -e . --no-deps
pip install click pytest pytest-cov
```

### Full Installation (Requires System Deps)
```bash
# Install system packages first
sudo apt install -y \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0 \
    gir1.2-adw-1

# Then install with all deps
pip install -e ".[dev,gui]"
```

### Running Tests
```bash
source venv/bin/activate
pytest -v                           # Run all tests
pytest --cov --cov-report=html      # With coverage
pytest tests/test_parser.py         # Single file
pytest -k "test_discover"           # Match pattern
```

### Running CLI
```bash
source venv/bin/activate
unified-theming list                # List themes
unified-theming apply ThemeName     # Apply theme
unified-theming current             # Show current
unified-theming rollback            # Rollback
unified-theming validate ThemeName  # Validate
```

---

## System State

### Handler Availability (On Current System)
- ✅ GTK: Available (GNOME system)
- ❌ Qt: Not detected (expected on GNOME)
- ✅ Flatpak: Available
- ❌ Snap: Not detected

### Discovered Themes (59 total)
Sample: Default, Emacs, Fluent-round (multiple variants), etc.

### Configuration Locations
- Backups: `~/.config/unified-theming/backups/`
- Logs: `~/.local/state/unified-theming/unified-theming.log`
- GTK4 CSS: `~/.config/gtk-4.0/gtk.css`
- Qt config: `~/.config/kdeglobals`
- Kvantum: `~/.config/Kvantum/`

---

## Critical Design Decisions

### 1. CSS Injection for Libadwaita (Not Patching)
**Why:** Low maintenance, safe, proven by Gradience
**Trade-off:** 70% coverage vs 95% with patching
**Status:** Correct choice for MVP

### 2. Synchronous Operations (Not Async)
**Why:** <2s operations, simpler code
**Trade-off:** Not scalable to thousands of themes
**Status:** Appropriate for desktop app

### 3. Backup Before Every Change
**Why:** Safety first, easy rollback
**Trade-off:** Disk space (mitigated by pruning)
**Status:** Essential for user trust

### 4. Graceful Degradation
**Why:** Some toolkits won't be installed
**How:** Check availability, skip gracefully, report in results
**Status:** Implemented, needs testing

### 5. >50% Success = Overall Success
**Why:** Partial theming better than nothing
**How:** Aggregate results, only rollback on catastrophic failure
**Status:** Implemented in manager

---

## Known Issues & Limitations

### Current Issues
1. **Test coverage too low** (25% vs 80% target)
2. **PyGObject won't install** - missing system deps
3. **No integration tests** - haven't tested full workflows
4. **CLI untested** - commands work but no test coverage
5. **Color utilities completely untested** - 0% coverage

### Design Limitations
1. **Libadwaita: 70% coverage only** - CSS injection can't modify widgets
2. **Qt translation imperfect** - Semantic differences between toolkits
3. **Flatpak: 70% coverage** - Depends on app permissions
4. **Snap: 65% coverage** - Limited by snap confinement
5. **AppImage: 20% coverage** - Very limited (deferred)

### Non-Goals
- ❌ Theme creation tools (post-1.0)
- ❌ libAdapta integration (evaluate Phase 3+)
- ❌ Library patching (post-1.0)
- ❌ Remote theme repository (post-2.0)
- ❌ Per-app theme overrides (future)

---

## Next Steps Decision Point

### Option 1: Complete Phase 2 Testing (RECOMMENDED)
**Goal:** Reach 80%+ test coverage
**Time:** 2-3 weeks
**Tasks:**
1. Write manager tests (apply_theme, rollback)
2. Write config tests (backup, restore)
3. Write handler tests (gtk, qt, flatpak, snap)
4. Write utility tests (color, file, validation)
5. Write CLI tests (all commands)

**Benefits:**
- Meets original specification
- Catches bugs before GUI complexity
- Demonstrates reliability
- Easier to maintain

**Risks:**
- Delays visible progress (no GUI yet)
- May find bugs requiring refactoring

### Option 2: Start Phase 3 (GUI) Now
**Goal:** Build GTK4/Libadwaita interface
**Prerequisites:**
1. Install system dependencies (pkg-config, cairo, etc.)
2. Fix PyGObject installation
3. Create GUI mockups

**Benefits:**
- Visible progress
- More impressive demo
- User-friendly interface

**Risks:**
- Building on undertested foundation
- GUI bugs + backend bugs = harder debugging
- May need to refactor after finding issues

---

## Code Quality Status

### ✅ Passing
- All 6 tests passing
- Black formatting compliant
- Flake8 linting clean
- MyPy type checking passes

### ⚠️ Needs Work
- Test coverage: 25% → need 80%
- Integration tests: none → need comprehensive
- Performance benchmarks: not measured
- User documentation: not written

---

## File Statistics

### Code Volume
- Total Python files: ~25 files
- Total lines of code: ~2,424 lines
- Documentation: 130+ pages
- Test files: 2 (need ~15-20 more)

### Git Status
- Not yet committed to repository
- All files local in `/home/live/Downloads/unified-theming/`

---

## Key Quotes from Specifications

**Requirements (NFR-4.2):**
> "Test Coverage: Minimum 80% code coverage"

**Architecture Decision:**
> "CSS Injection for Libadwaita (MVP): Low maintenance burden, safe, proven approach"

**Success Criteria:**
> "All core modules implemented ✅"
> "80%+ test coverage achieved ❌" (currently 25%)

---

## Memory Checkpoint Questions

**If future Claude asks:** "What is this project?"
→ Linux desktop theming tool, applies consistent themes across GTK/Qt/containers

**If future Claude asks:** "What's the current status?"
→ Phase 2 ~70% done, core works but needs tests (25% → 80% coverage)

**If future Claude asks:** "What should I do next?"
→ Write comprehensive tests for manager, config, handlers, utilities

**If future Claude asks:** "How do I run tests?"
→ `source venv/bin/activate && pytest -v --cov`

**If future Claude asks:** "Where's the documentation?"
→ docs/ folder has everything, CLAUDE.md is the quick reference

**If future Claude asks:** "Does it work?"
→ Yes! Core engine works, discovered 59 themes, all 6 tests pass

**If future Claude asks:** "What's the architecture?"
→ 4 layers: UI → Core (manager/parser/config) → Handlers → System Integration

**If future Claude asks:** "Why is coverage so low?"
→ Implementation done but comprehensive test suite not written yet

---

## Commit This to Memory

**Project:** Unified Theming - Linux theme manager
**Location:** /home/live/Downloads/unified-theming/
**Status:** Phase 2 implementation complete, testing incomplete (25% vs 80%)
**Next:** Write tests for manager, config, handlers, utilities
**Timeline:** 2-3 weeks to reach 80%, then Phase 3 (GUI)
**Key Files:** CLAUDE.md (quickstart), DIAGNOSTIC_REPORT.md (current state)
**Critical:** All 6 tests pass, core works, just needs comprehensive testing

---

**END OF PROJECT STATE MEMORY**
