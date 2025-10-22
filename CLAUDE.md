# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Unified Theming is a Linux desktop application that applies consistent themes across different GUI toolkits (GTK2/3/4, libadwaita, Qt5/6) and containerized applications (Flatpak, Snap). The project uses a **4-layer architecture** with clear separation between UI, core logic, toolkit-specific handlers, and system integration.

**Current Status:** Phase 2 (~70% complete) - Core implementation functional but needs test coverage improvement (currently 25%, target 80%+).

## Development Commands

### Setup and Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e ".[dev,gui]"
```

### Testing

```bash
# Run all tests (from project root, venv activated)
pytest

# Run with coverage report
pytest --cov=unified_theming --cov-report=html

# Run specific test file
pytest tests/test_parser.py

# Run specific test function
pytest tests/test_parser.py::test_discover_themes

# Run without slow tests
pytest -m "not slow"
```

### Code Quality

```bash
# Format code (required before commits)
black unified_theming/

# Type check (required, project is fully typed)
mypy unified_theming/

# Lint code
flake8 unified_theming/

# Sort imports
isort unified_theming/
```

### Running the Application

```bash
# Test theme discovery (works now)
python3 -m unified_theming.cli.commands list

# Apply a theme (implemented but untested)
python3 -m unified_theming.cli.commands apply ThemeName
```

## Architecture Overview

### 4-Layer Design

1. **User Interface Layer** (`cli/`, `gui/`)
   - CLI: Click-based command interface
   - GUI: GTK4/Libadwaita interface (Phase 3)

2. **Application Core Layer** (`core/`)
   - `manager.py`: Central orchestrator (UnifiedThemeManager)
   - `parser.py`: Theme discovery and parsing (UnifiedThemeParser)
   - `config.py`: Backup/restore management (ConfigManager)
   - `types.py`: Data classes and type definitions
   - `exceptions.py`: Custom exception hierarchy

3. **Toolkit Handler Layer** (`handlers/`)
   - `base.py`: Abstract BaseHandler interface
   - `gtk_handler.py`: GTK2/3/4/libadwaita theming
   - `qt_handler.py`: Qt5/6 theming (kdeglobals + Kvantum)
   - `flatpak_handler.py`: Flatpak portal configuration
   - `snap_handler.py`: Snap interface management

4. **System Integration Layer** (`utils/`)
   - `color.py`: Color format conversion and validation
   - `file.py`: File operations with error handling
   - `validation.py`: Theme validation utilities
   - `logging_config.py`: Centralized logging setup

### Key Workflows

**Theme Application Flow:**
```
User Request → UnifiedThemeManager.apply_theme()
  ├─ 1. Discover and validate theme (ThemeParser)
  ├─ 2. Create backup (ConfigManager)
  ├─ 3. Prepare theme data for each toolkit
  ├─ 4. Apply via handlers (GTKHandler, QtHandler, etc.)
  ├─ 5. Aggregate results
  └─ 6. Rollback on critical failure (if needed)
```

**Theme Discovery Flow:**
```
UnifiedThemeParser.discover_themes()
  ├─ Scan: ~/.themes, ~/.local/share/themes, /usr/share/themes
  ├─ For each theme directory:
  │   ├─ Check structure (gtk-2.0, gtk-3.0, gtk-4.0 dirs)
  │   ├─ Parse index.theme metadata
  │   └─ Extract color palette from CSS (lazy)
  └─ Return Dict[theme_name, ThemeInfo]
```

## Critical Implementation Details

### Handler Pattern

All toolkit handlers inherit from `BaseHandler` (abstract base class) and must implement:
- `apply_theme(theme_data: ThemeData) -> bool` - Apply theme to toolkit
- `get_current_theme() -> str` - Get currently applied theme
- `validate_compatibility(theme_data: ThemeData) -> ValidationResult` - Check compatibility
- `is_available() -> bool` - Check if toolkit is installed

**Key principle:** Handlers should gracefully degrade. If a handler fails or toolkit is unavailable, the system continues with other handlers and aggregates results.

### Libadwaita CSS Injection

The GTKHandler uses CSS injection for libadwaita (not library patching). It:
1. Maps GTK color variables to libadwaita equivalents:
   - `theme_bg_color` → `window_bg_color`
   - `theme_selected_bg_color` → `accent_bg_color`
   - (See full mapping table in `unified_theming/handlers/gtk_handler.py`)
2. Generates CSS file at `~/.config/gtk-4.0/gtk.css`
3. Achieves ~70% coverage (colors only, no widget structure changes)
4. **Important:** This is the MVP approach. Future enhancement would be a LibAdapta-style library patch for 95%+ coverage.

### Qt Color Translation

The QtHandler translates GTK colors to Qt format (critical for cross-toolkit consistency):
1. Normalizes color formats using `utils/color.py` (hex, rgb, rgba → #RRGGBB)
2. Maps semantic GTK variables to Qt equivalents:
   - `theme_bg_color` → `BackgroundNormal`
   - `theme_selected_bg_color` → `Highlight`
   - (Full semantic mapping in `unified_theming/handlers/qt_handler.py`)
3. Generates kdeglobals INI file at `~/.config/kdeglobals`
4. Optionally creates Kvantum theme for enhanced styling
5. **Caveat:** Color translation is approximate; Qt and GTK have different semantic color models

### Backup Strategy

ConfigManager automatically backs up before every theme change:
- Location: `~/.config/unified-theming/backups/`
- Format: `backup_YYYYMMDD_HHMMSS_ThemeName/`
- Keeps last 10 backups, prunes older ones
- Includes: gtk-4.0/gtk.css, kdeglobals, Kvantum themes, Flatpak/Snap configs
- **Critical:** Always call `ConfigManager.backup_current_state()` before any theme application

## Type System

The project is **fully type-hinted** using Python 3.10+ features. Key types:

```python
# Core data structures
ThemeInfo       # Complete theme metadata
ThemeData       # Processed theme for handlers
ApplicationResult  # Aggregated results from handlers
HandlerResult   # Per-handler application result
ValidationResult  # Validation outcome with messages
Backup          # Backup metadata

# Enums
Toolkit         # GTK2, GTK3, GTK4, LIBADWAITA, QT5, QT6, FLATPAK, SNAP
ValidationLevel # ERROR, WARNING, INFO
ColorFormat     # HEX, RGB, RGBA, HSL, NAMED
```

Always use type hints. Run `mypy unified_theming/` to validate.

## Error Handling Strategy

### Exception Hierarchy

All exceptions inherit from `UnifiedThemingError`:
- **Theme Discovery**: `ThemeDiscoveryError`, `ThemeNotFoundError`, `ThemeParseError`
- **Theme Application**: `ThemeApplicationError`, `HandlerNotAvailableError`, `ColorTranslationError`
- **Configuration**: `BackupError`, `RollbackError`, `ConfigurationError`
- **Validation**: `ValidationError`, `ColorValidationError`, `CSSValidationError`

### Graceful Degradation

- If a toolkit is not installed, skip it gracefully (don't fail)
- If a handler fails, continue with others (aggregate results)
- Overall success = >50% of handlers succeeded
- Auto-rollback only on catastrophic failure (<50% success)

## Testing Strategy

### Test Organization

```
tests/
├── conftest.py           # Shared fixtures (valid_theme, parser, etc.)
├── test_parser.py        # Theme discovery and parsing tests
├── test_manager.py       # Manager orchestration tests
└── fixtures/             # Test theme directories
    ├── ValidTheme/
    ├── IncompleteTheme/
    └── MalformedTheme/
```

### Key Fixtures (in conftest.py)

- `tmp_theme_dir` - Temporary theme directory
- `valid_theme` - Complete GTK2/3/4 theme
- `incomplete_theme` - GTK3 only (missing GTK4)
- `malformed_theme` - Contains CSS syntax errors
- `parser` - UnifiedThemeParser instance
- `sample_theme_data` - ThemeData for testing

### Test Coverage Requirements

- Core modules (parser, manager, config): 90%+
- Handlers: 85%+
- Utilities: 80%+
- Overall: 80% minimum

## Performance Requirements

Critical benchmarks to maintain:
- Theme discovery (100 themes): <5 seconds
- Single theme parsing: <50ms
- Color extraction: <20ms
- Theme application: <2 seconds
- CSS generation: <100ms

Use `time.time()` for profiling. Consider caching and parallel processing.

## Logging Guidelines

```python
from unified_theming.utils.logging_config import get_logger
logger = get_logger(__name__)

# Appropriate log levels:
logger.debug("Parsing theme file: %s", theme_path)  # Diagnostic details
logger.info("Applying theme '%s'", theme_name)      # Major operations
logger.warning("Kvantum not installed")             # Non-critical issues
logger.error("Failed to apply Qt theme: %s", e)     # Errors preventing operation
logger.critical("Backup restoration failed")        # System-breaking errors
```

Logging is configured in `utils/logging_config.py` with:
- Colored console output (auto-detected TTY)
- Rotating file logs (~/.local/state/unified-theming/unified-theming.log)
- Configurable verbosity via CLI `-v` flags

## Code Style Conventions

- **Line length**: 88 characters (Black default)
- **Docstrings**: Google style with type information
- **Imports**: Organized with isort (stdlib, third-party, local)
- **Type hints**: Required on all public functions/methods
- **String quotes**: Double quotes preferred

Example function signature:
```python
def apply_theme(
    self,
    theme_name: str,
    targets: Optional[List[str]] = None
) -> ApplicationResult:
    """
    Apply a theme to specified targets.

    Args:
        theme_name: Name of theme to apply
        targets: List of toolkit targets (None = all)

    Returns:
        ApplicationResult with per-handler results

    Raises:
        ThemeNotFoundError: If theme doesn't exist
    """
```

## Common Pitfalls

1. **Never modify system files** - Only touch user config (`~/.config`, `~/.themes`)
2. **Always backup before changes** - Use ConfigManager.backup_current_state()
3. **Handle missing toolkits gracefully** - Check `handler.is_available()`
4. **Don't fail on partial success** - Aggregate results, report individual failures
5. **Validate theme paths** - Prevent directory traversal attacks
6. **Normalize color formats** - GTK uses various formats; standardize before translation
7. **Test with real themes** - Use actual GTK/Qt themes from the system

## Module Dependencies

```
CLI/GUI → Manager → Parser
              ↓         ↓
           Config    Validation
              ↓         ↓
          Handlers → Utils
```

Key import rule: **Higher layers depend on lower layers, never reverse**.
- CLI can import Manager, but Manager should not import CLI
- Handlers should not import from each other (use types.py for shared data)
- Utils should have no internal dependencies (only external libraries)

## Phase-Specific Notes

**Current Status**: Phase 2 in progress (~70% complete)
- Phase 1: Planning & Foundation ✅ Complete
- Phase 2: Core Engineering 🔄 70% complete (functional but undertested)
- Phase 3: Integration & Release ⏳ Pending

**Priority for Phase 2 Completion:**
1. Increase test coverage from 25% to 80%+ (critical modules: manager.py, config.py, gtk_handler.py, qt_handler.py, color.py)
2. Test CLI commands (currently 0% coverage)
3. Integration tests for full theme application workflow

When modifying the codebase:
1. Read the relevant specification in `docs/` first
2. Maintain type safety (run mypy before committing)
3. **Always add tests** - coverage target is 80%+
4. Follow existing patterns (especially in handlers/)
5. Update documentation if changing architecture

## Configuration Locations

User-modifiable configs:
- GTK4/libadwaita CSS: `~/.config/gtk-4.0/gtk.css`
- Qt kdeglobals: `~/.config/kdeglobals`
- Kvantum themes: `~/.config/Kvantum/`
- Flatpak overrides: `~/.local/share/flatpak/overrides/`
- Backups: `~/.config/unified-theming/backups/`
- Logs: `~/.local/state/unified-theming/unified-theming.log`

Theme directories scanned:
- `~/.themes` (user themes)
- `~/.local/share/themes` (XDG user themes)
- `/usr/share/themes` (system themes)
- `/usr/local/share/themes` (locally installed themes)

## Current Implementation Status

### What Works
- ✅ Theme discovery: Successfully scans and discovers 59+ system themes
- ✅ Theme parsing: Extracts metadata and color variables from GTK themes
- ✅ Core architecture: All 4 layers implemented and functional
- ✅ All 6 existing tests pass
- ✅ Type system: Fully type-hinted, mypy passes with strict settings

### What Needs Work
- ❌ **Test coverage**: Only 25% (need 80%+)
  - Critical gaps: manager.py (24%), config.py (15%), gtk_handler.py (25%), qt_handler.py (19%), color.py (0%)
- ❌ **CLI testing**: Commands implemented but untested (0% coverage)
- ❌ **Integration tests**: No end-to-end theme application tests
- ⚠️ **Backup/restore**: Implemented but untested (15% coverage)
- ⚠️ **Container support**: Flatpak/Snap handlers implemented but minimally tested

### Test Coverage by Module (from coverage.xml)
```
unified_theming/core/parser.py:        87% ✅
unified_theming/core/types.py:         89% ✅
unified_theming/handlers/base.py:      83% ✅
unified_theming/handlers/snap_handler.py: 50%
unified_theming/utils/validation.py:   43%
unified_theming/handlers/flatpak_handler.py: 39%
unified_theming/utils/logging_config.py: 37%
unified_theming/handlers/qt_handler.py: 19% ❌
unified_theming/core/config.py:        15% ❌
unified_theming/core/manager.py:       24% ❌
unified_theming/handlers/gtk_handler.py: 25% ❌
unified_theming/utils/color.py:         0% ❌ CRITICAL
unified_theming/cli/commands.py:        0% ❌
```

## Documentation References

For comprehensive information, see:
- `docs/requirements_specification.md` - What the system does (35 pages)
- `docs/architecture.md` - How the system is designed (40 pages)
- `docs/developer_guide.md` - How to develop for the system (30 pages)
- `PHASE1_COMPLETE.md` - Phase 1 completion summary
- `PROJECT_STATE_MEMORY.md` - Complete project state and history
- `docs/HANDOFF_TO_QWEN_CODER.md` - Phase 2 implementation guide
