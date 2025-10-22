# Phase 1 → Phase 2 Handoff Document

**From:** Claude Code (Sonnet 4.5) - Phase 1
**To:** Qwen Coder - Phase 2
**Date:** 2025-10-20
**Status:** Phase 1 Complete - Ready for Implementation

---

## Executive Summary

Phase 1 (Planning & Foundation) is complete. This document provides everything needed to begin Phase 2 (Core Engineering). All specifications, architecture, and foundational code are ready for implementation.

**What's Done:**
- ✅ Complete requirements specification
- ✅ System architecture design
- ✅ Module structure defined
- ✅ Type system implemented
- ✅ Exception hierarchy implemented
- ✅ Logging configuration implemented
- ✅ CLI interface specification
- ✅ Developer documentation
- ✅ Project structure created

**What's Next (Your Tasks):**
- Implement UnifiedThemeParser
- Implement GTKHandler (with libadwaita CSS injection)
- Implement QtHandler (kdeglobals + Kvantum)
- Implement UnifiedThemeManager
- Implement ConfigManager
- Write comprehensive tests
- Performance optimization

---

## Delivered Artifacts

### 1. Requirements Specification
**Location:** `docs/requirements_specification.md`

**Key Sections:**
- Functional Requirements (FR-1 through FR-4)
- Non-Functional Requirements (NFR-1 through NFR-4)
- Success Criteria
- Acceptance Testing

**Target Coverage:**
- GTK2/3: 95%
- GTK4: 85%
- Libadwaita: 70% (CSS injection)
- Qt5/6: 75%
- Flatpak: 70%
- Snap: 65%

### 2. System Architecture
**Location:** `docs/architecture.md`

**Key Components:**
- 4-layer architecture (UI, Core, Handler, System Integration)
- Data flow diagrams
- Module structure
- Design patterns (Facade, Strategy, Memento)
- Performance considerations

### 3. Type System
**Location:** `unified_theming/core/types.py`

**Defined Types:**
- `ThemeInfo`: Complete theme metadata
- `ThemeData`: Processed theme for handlers
- `ValidationResult`: Validation outcomes
- `HandlerResult`: Per-handler results
- `ApplicationResult`: Aggregated results
- `Backup`: Backup metadata
- Enums: `Toolkit`, `ValidationLevel`, `ColorFormat`

### 4. Exception Hierarchy
**Location:** `unified_theming/core/exceptions.py`

**Exception Categories:**
- Theme Discovery & Parsing
- Theme Application
- Configuration & Backup
- File System
- Validation
- System Integration

### 5. Logging Configuration
**Location:** `unified_theming/utils/logging_config.py`

**Features:**
- Colored console output
- Rotating file logs
- Configurable verbosity
- Helper functions

### 6. CLI Specification
**Location:** `unified_theming/cli/commands.py`

**Commands:**
- `list`: List available themes
- `apply`: Apply theme
- `preview`: Preview theme
- `rollback`: Restore previous theme
- `current`: Show current themes
- `validate`: Validate theme

### 7. Project Structure
```
unified-theming/
├── docs/
│   ├── requirements_specification.md
│   ├── architecture.md
│   ├── developer_guide.md
│   └── HANDOFF_TO_QWEN_CODER.md (this file)
├── unified_theming/
│   ├── core/
│   │   ├── types.py          ✅ Implemented
│   │   ├── exceptions.py     ✅ Implemented
│   │   ├── manager.py        ⏳ Stub (implement in Phase 2)
│   │   ├── parser.py         ⏳ Stub (implement in Phase 2)
│   │   └── config.py         ⏳ Stub (implement in Phase 2)
│   ├── handlers/
│   │   ├── base.py           ⏳ Stub (implement in Phase 2)
│   │   ├── gtk_handler.py    ⏳ Stub (implement in Phase 2)
│   │   ├── qt_handler.py     ⏳ Stub (implement in Phase 2)
│   │   ├── flatpak_handler.py ⏳ Stub (implement in Phase 2)
│   │   └── snap_handler.py    ⏳ Stub (implement in Phase 2)
│   ├── utils/
│   │   ├── logging_config.py ✅ Implemented
│   │   ├── color.py          ⏳ Stub (implement in Phase 2)
│   │   ├── file.py           ⏳ Stub (implement in Phase 2)
│   │   └── validation.py     ⏳ Stub (implement in Phase 2)
│   ├── cli/
│   │   └── commands.py       ✅ Specification complete
│   └── gui/
│       └── (defer to Phase 3)
├── tests/
│   └── fixtures/             ⏳ Create test themes
├── pyproject.toml            ✅ Complete
└── README.md                 ✅ Complete
```

---

## Implementation Priorities

### CRITICAL PATH (Weeks 1-2)

#### Priority 1: UnifiedThemeParser
**File:** `unified_theming/core/parser.py`

**Must Implement:**
```python
class UnifiedThemeParser:
    def discover_themes(self) -> Dict[str, ThemeInfo]:
        """Scan theme directories and return all themes."""
        pass

    def parse_theme(self, theme_path: Path) -> ThemeInfo:
        """Parse single theme and extract metadata."""
        pass

    def extract_colors(self, theme_path: Path, toolkit: str) -> Dict[str, str]:
        """Extract color palette from theme CSS."""
        pass

    def validate_theme(self, theme_path: Path) -> ValidationResult:
        """Validate theme structure and completeness."""
        pass
```

**Key Requirements:**
- Scan `~/.themes`, `~/.local/share/themes`, `/usr/share/themes`
- Parse `@define-color` statements from CSS
- Handle both GTK3 and GTK4 CSS formats
- Complete in <5 seconds for 100+ themes
- 90%+ test coverage

**Test Fixtures Needed:**
Create in `tests/fixtures/`:
1. `ValidTheme/` - Complete GTK2/3/4 theme
2. `IncompleteTheme/` - Missing GTK4 support
3. `MalformedTheme/` - Syntax errors in CSS
4. `MinimalTheme/` - Minimal valid theme

### HIGH PRIORITY (Weeks 3-4)

#### Priority 2: GTKHandler
**File:** `unified_theming/handlers/gtk_handler.py`

**Must Implement:**
```python
class GTKHandler(BaseHandler):
    def apply_theme(self, theme_data: ThemeData) -> bool:
        """Apply theme to GTK2/3/4/libadwaita."""
        # 1. Apply GTK2/3 via GSettings
        # 2. Generate libadwaita CSS
        # 3. Write to ~/.config/gtk-4.0/gtk.css
        # 4. Backup previous configuration
        pass
```

**Color Mapping:**
Use mapping table from architecture doc:
- `theme_bg_color` → `window_bg_color`
- `theme_fg_color` → `window_fg_color`
- `theme_selected_bg_color` → `accent_bg_color`
- etc.

**CSS Generation Template:**
```css
/* Generated by Unified Theming App */
/* Theme: {theme_name} */

@define-color window_bg_color {value};
@define-color window_fg_color {value};
/* ... all libadwaita colors ... */
```

#### Priority 3: QtHandler
**File:** `unified_theming/handlers/qt_handler.py`

**Must Implement:**
```python
class QtHandler(BaseHandler):
    def apply_theme(self, theme_data: ThemeData) -> bool:
        """Apply theme to Qt5/6."""
        # 1. Translate GTK colors to Qt
        # 2. Generate kdeglobals file
        # 3. Optionally generate Kvantum theme
        pass

    def _translate_colors(self, gtk_colors: Dict[str, str]) -> Dict[str, str]:
        """Translate GTK color variables to Qt equivalents."""
        pass
```

**Color Translation:**
- GTK `theme_bg_color` → Qt `BackgroundNormal`
- GTK `theme_fg_color` → Qt `ForegroundNormal`
- GTK `theme_selected_bg_color` → Qt `Highlight`
- etc.

### MEDIUM PRIORITY (Weeks 5-6)

#### Priority 4: UnifiedThemeManager
**File:** `unified_theming/core/manager.py`

**Must Implement:**
```python
class UnifiedThemeManager:
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize manager with handlers."""
        self.parser = UnifiedThemeParser()
        self.config_manager = ConfigManager(config_path)
        self.handlers = {
            'gtk': GTKHandler(),
            'qt': QtHandler(),
            'flatpak': FlatpakHandler(),
            'snap': SnapHandler(),
        }

    def apply_theme(
        self,
        theme_name: str,
        targets: Optional[List[str]] = None
    ) -> ApplicationResult:
        """Apply theme to specified targets."""
        # 1. Discover and validate theme
        # 2. Backup current configuration
        # 3. Apply to each handler
        # 4. Aggregate results
        # 5. Rollback on critical failure
        pass
```

#### Priority 5: ConfigManager
**File:** `unified_theming/core/config.py`

**Must Implement:**
```python
class ConfigManager:
    def backup_current_state(self) -> str:
        """Create backup of current configuration."""
        # Backup:
        # - ~/.config/gtk-4.0/gtk.css
        # - ~/.config/kdeglobals
        # - Flatpak/Snap settings
        pass

    def restore_backup(self, backup_id: str) -> bool:
        """Restore previous configuration."""
        pass

    def get_backups(self) -> List[Backup]:
        """List available backups."""
        pass
```

### LOWER PRIORITY (Weeks 7-8)

#### Priority 6: Container Handlers
**Files:** `unified_theming/handlers/flatpak_handler.py`, `snap_handler.py`

Basic implementation:
- Flatpak: Use `flatpak override` for filesystem access
- Snap: Use `snap connect` for interface connections

#### Priority 7: Utility Modules
**Files:** `unified_theming/utils/color.py`, `file.py`, `validation.py`

Implement helper functions:
- Color format normalization
- Color validation
- File operations with error handling
- CSS syntax validation

---

## Testing Requirements

### Minimum Coverage: 80%

**Coverage Breakdown:**
- Core modules (parser, manager, config): 90%+
- Handlers: 85%+
- Utilities: 80%+
- CLI: 70%+ (CLI testing is challenging)

### Test Structure

```python
# tests/conftest.py - Shared fixtures

import pytest
from pathlib import Path
from unified_theming.core.parser import UnifiedThemeParser

@pytest.fixture
def tmp_theme_dir(tmp_path):
    """Create temporary theme directory."""
    theme_dir = tmp_path / ".themes"
    theme_dir.mkdir()
    return theme_dir

@pytest.fixture
def valid_theme(tmp_theme_dir):
    """Create a complete valid theme."""
    theme = tmp_theme_dir / "ValidTheme"
    theme.mkdir()

    # GTK4 support
    gtk4 = theme / "gtk-4.0"
    gtk4.mkdir()
    (gtk4 / "gtk.css").write_text("""
@define-color theme_bg_color #ffffff;
@define-color theme_fg_color #000000;
@define-color theme_selected_bg_color #3584e4;
@define-color theme_selected_fg_color #ffffff;
    """)

    # GTK3 support
    gtk3 = theme / "gtk-3.0"
    gtk3.mkdir()
    (gtk3 / "gtk.css").write_text("""
@define-color theme_bg_color #ffffff;
@define-color theme_fg_color #000000;
    """)

    return theme

@pytest.fixture
def parser():
    """Create ThemeParser instance."""
    return UnifiedThemeParser()
```

### Example Test Cases

```python
# tests/test_parser.py

def test_discover_themes(parser, tmp_theme_dir, valid_theme):
    """Test theme discovery."""
    themes = parser.discover_themes()

    assert "ValidTheme" in themes
    assert isinstance(themes["ValidTheme"], ThemeInfo)

def test_parse_theme(parser, valid_theme):
    """Test parsing a valid theme."""
    theme_info = parser.parse_theme(valid_theme)

    assert theme_info.name == "ValidTheme"
    assert Toolkit.GTK3 in theme_info.supported_toolkits
    assert Toolkit.GTK4 in theme_info.supported_toolkits

def test_extract_colors(parser, valid_theme):
    """Test color extraction."""
    colors = parser.extract_colors(valid_theme, "gtk4")

    assert "theme_bg_color" in colors
    assert colors["theme_bg_color"] == "#ffffff"
    assert len(colors) >= 4

def test_validate_theme(parser, valid_theme):
    """Test theme validation."""
    result = parser.validate_theme(valid_theme)

    assert result.valid is True
    assert not result.has_errors()
```

---

## Performance Requirements

### Benchmarks to Meet

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Theme discovery (100 themes) | <5s | Time to complete `discover_themes()` |
| Single theme parsing | <50ms | Time to complete `parse_theme()` |
| Color extraction | <20ms | Time to complete `extract_colors()` |
| Theme application | <2s | Time from `apply_theme()` call to completion |
| CSS generation | <100ms | Time to generate libadwaita CSS |
| kdeglobals generation | <100ms | Time to generate Qt config |

### Performance Tips

1. **Parallel Scanning:**
   ```python
   from concurrent.futures import ThreadPoolExecutor

   with ThreadPoolExecutor() as executor:
       themes = list(executor.map(parse_theme, theme_paths))
   ```

2. **Lazy Loading:**
   ```python
   @property
   def colors(self):
       """Lazy load colors on first access."""
       if self._colors is None:
           self._colors = self._extract_colors()
       return self._colors
   ```

3. **Caching:**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def get_theme_info(theme_path: str) -> ThemeInfo:
       return parse_theme(Path(theme_path))
   ```

---

## Integration with CLI

Once core components are implemented, connect to CLI:

```python
# cli/commands.py

@cli.command()
def list(ctx, toolkit, format):
    """List available themes."""
    manager = UnifiedThemeManager(config_path=ctx.obj.get('config'))
    themes = manager.discover_themes()

    # Display themes based on format
    # (Implementation examples are in cli/commands.py)
```

---

## Design Decisions & Rationale

### Decision 1: CSS Injection for Libadwaita (MVP)
**Why:**
- Low maintenance burden
- Safe (no system modifications)
- Proven by Gradience project
- 70% coverage acceptable for v1.0

**Alternative:** Library patching (deferred to post-1.0)

### Decision 2: Synchronous Operations
**Why:**
- Simpler code
- Operations complete in <2s
- Desktop application context

**Alternative:** async/await (unnecessary complexity)

### Decision 3: kdeglobals + Kvantum for Qt
**Why:**
- kdeglobals: Universal Qt color scheme
- Kvantum: Enhanced styling (optional)
- Covers 75% of Qt apps

**Alternative:** qt5ct/qt6ct only (lower coverage)

### Decision 4: Backup Before Every Change
**Why:**
- Safety first
- Easy rollback
- User confidence

**Trade-off:** Disk space (mitigated by pruning old backups)

---

## Known Limitations & Constraints

### Technical Constraints

1. **No Root Access Required**
   - Only modify user files (`~/.config`, `~/.themes`)
   - Cannot modify system themes

2. **Libadwaita Coverage Limit**
   - CSS injection: 70% coverage (colors only)
   - Cannot modify widget structure
   - Full coverage requires patching (post-1.0)

3. **Qt Translation Imperfect**
   - GTK and Qt color semantics differ
   - Some colors require manual derivation
   - Target: 75% coverage

4. **Container App Limitations**
   - Flatpak: Depends on app permissions (70% coverage)
   - Snap: Limited by confinement (65% coverage)
   - AppImage: Very limited (20% coverage, deferred)

### Non-Goals for Phase 2

- ❌ GUI implementation (deferred to Phase 3)
- ❌ libAdapta integration (evaluate in Phase 3)
- ❌ Library patching (post-1.0)
- ❌ Theme creation tools (post-1.0)
- ❌ Remote theme repository (post-2.0)

---

## Questions & Clarifications

### If You Need Clarification

**Process:**
1. Review this document thoroughly
2. Check architecture.md and requirements_specification.md
3. Review code comments and docstrings
4. If still unclear, create a feedback request:

**Feedback Format:**
```
FEEDBACK REQUEST: Qwen Coder → Claude Code

Context: [What you're working on]

Question/Issue:
[Specific question or unclear requirement]

Current Approach:
[How you plan to solve it]

Request:
[ ] Clarification on specification
[ ] Design review
[ ] Alternative approach suggestion
[ ] Other: ___________

Priority: [LOW / MEDIUM / HIGH / URGENT]
```

### Common Anticipated Questions

**Q:** How should I handle CSS parsing errors?
**A:** Use `CSSParseError` exception. Log the error, add to validation warnings, but continue parsing other colors. See exceptions.py.

**Q:** What if a theme has only GTK3 but user applies to GTK4?
**A:** Extract colors from GTK3 and generate GTK4 CSS. Add validation warning about missing native GTK4 support.

**Q:** How to test without system modifications?
**A:** Use `tmp_path` fixture to create temporary config directories. Never write to actual `~/.config` in tests.

**Q:** What if Kvantum is not installed?
**A:** Check in `is_available()`. If not available, use kdeglobals only. Log info message, not error.

---

## Success Criteria for Phase 2

### Must Have (Blocking for Phase 3)

- ✅ All core modules implemented
- ✅ 80%+ test coverage
- ✅ All integration tests passing
- ✅ Performance benchmarks met
- ✅ No critical bugs
- ✅ Code passes linting (black, flake8, mypy)

### Should Have (Fix before handoff)

- ✅ 85%+ test coverage
- ✅ All known issues documented
- ✅ Code reviewed and refactored
- ✅ Optimization opportunities identified

### Nice to Have (Can defer)

- Advanced error recovery
- Extensive logging
- Performance profiling
- Additional utility functions

---

## Timeline Expectations

**Phase 2 Duration:** 8-10 weeks

**Milestone Breakdown:**
- Weeks 1-2: ThemeParser implementation
- Weeks 3-4: GTKHandler + QtHandler implementation
- Weeks 5-6: UnifiedThemeManager + ConfigManager implementation
- Weeks 7-8: Container handlers, utilities, integration testing
- Weeks 9-10: Code review, optimization, documentation

**Critical Path:** ThemeParser → Handlers → Manager → Integration

---

## Handoff Checklist

Phase 1 Deliverables:
- [x] Requirements specification complete
- [x] Architecture documented
- [x] API specifications defined with type hints
- [x] Exception hierarchy implemented
- [x] Logging configuration implemented
- [x] CLI specification complete
- [x] Developer guide written
- [x] Project structure created
- [x] pyproject.toml configured
- [x] Type system implemented (types.py)
- [x] Test structure defined

Phase 2 Expectations:
- [ ] ThemeParser implemented
- [ ] GTKHandler implemented
- [ ] QtHandler implemented
- [ ] UnifiedThemeManager implemented
- [ ] ConfigManager implemented
- [ ] Container handlers implemented
- [ ] Utility modules implemented
- [ ] 80%+ test coverage achieved
- [ ] All benchmarks met
- [ ] Code review completed

---

## Communication Protocol

### Regular Updates (Recommended)

- **Weekly:** Progress summary
  - What's completed
  - What's in progress
  - Blockers/questions
  - Next week's goals

### Handoff to Phase 3 (Opencode AI)

When Phase 2 is complete, create similar handoff document:
- Implementation summary
- Test coverage report
- Performance benchmark results
- Known issues
- Integration instructions for GUI
- Packaging requirements

---

## Final Notes

**Remember:**
1. **Follow the specifications** - They're carefully designed
2. **Write tests first** - TDD ensures quality
3. **Performance matters** - Users expect fast operations
4. **Error handling is critical** - Graceful degradation
5. **Document as you go** - Future maintainers will thank you

**You have everything you need** to implement a solid, well-tested core application. The architecture is sound, the specifications are complete, and the expectations are clear.

**Good luck!** 🚀

---

**End of Handoff Document**

---

## Appendix: Quick Reference

### File Locations
- Requirements: `docs/requirements_specification.md`
- Architecture: `docs/architecture.md`
- Developer Guide: `docs/developer_guide.md`
- Type System: `unified_theming/core/types.py`
- Exceptions: `unified_theming/core/exceptions.py`
- Logging: `unified_theming/utils/logging_config.py`
- CLI Spec: `unified_theming/cli/commands.py`

### Key Imports
```python
from unified_theming.core.types import (
    ThemeInfo, ThemeData, ValidationResult,
    ApplicationResult, Toolkit
)
from unified_theming.core.exceptions import (
    ThemeNotFoundError, ThemeApplicationError,
    ValidationError
)
from unified_theming.utils.logging_config import get_logger

logger = get_logger(__name__)
```

### Color Variable References
- GTK: `GTK_COLOR_VARIABLES` in types.py
- Libadwaita: `LIBADWAITA_COLOR_VARIABLES` in types.py
- Qt: `QT_COLOR_VARIABLES` in types.py
