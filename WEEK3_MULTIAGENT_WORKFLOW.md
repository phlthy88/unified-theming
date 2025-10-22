# Week 3 Multi-Agent Workflow: Integration & Testing Sprint

**Timeline:** 5 Days (October 22-26, 2025)
**Goal:** Achieve 72-75% test coverage with validated integration workflows
**Current Baseline:** 48% coverage, 149 tests passing
**Success Threshold:** 70%+ coverage to unlock Phase 3 (GUI)

## 🆕 Week 3 Enhancement: LibAdwaita/Zorin Integration

**Added on October 22, 2025** - Based on examination of libAdapta (Linux Mint) and Zorin OS libadwaita patch codebases.

### Strategic Addition (Day 3 Morning)
- **Claude Code** will refactor `GTKHandler` to detect and adapt to:
  1. **LibAdapta** (Linux Mint) - full structural theming via `libadapta-1.5/` directories
  2. **Zorin Patch** - full structural theming via `.libadwaita` marker files
  3. **CSS Injection** (default) - color-only theming (existing implementation)

### Implementation Approach
- **Detection-based adaptation** (NOT library replacement)
- **Automatic optimization** - Uses best method available on system
- **Graceful degradation** - Always falls back to CSS injection
- **Zero system modifications** - Works in user space only
- **Progressive enhancement** - 70% → 95% coverage when patches available

### Impact on Coverage Targets
- Day 3 GTK handler target: 42% → **70%** (increased from 65%)
- New tests required: **25+ libadwaita detection/adaptation tests**
- Total Day 3 tests: **45+** (20 existing + 25 new)
- Claude Code morning work: **3 hours** (refactoring + documentation)
- Qwen Coder afternoon work: **6 hours** (testing implementation)

### Deliverables
- `unified_theming/handlers/gtk_handler.py` (refactored with 3-mode system)
- `docs/libadwaita_detection_spec.md` (technical specification)
- `tests/test_gtk_handler_libadwaita.py` (NEW test file with 25+ tests)
- `HANDOFF_DAY3_CLAUDE_TO_QWEN.md` (detailed testing instructions)

---

## 🎯 Week 3 Overview

### Coverage Targets by Module

| Module | Current | Target | Agent | Day |
|--------|---------|--------|-------|-----|
| Integration (new) | 0% | 100% | Claude Code + Qwen | Days 1-2 |
| CLI commands.py | 0% | 60%+ | Qwen Coder | Day 2 |
| gtk_handler.py | 42% | 70%+ | Qwen Coder | Day 3 |
| **gtk_handler.py (refactor)** | **-** | **LibAdapta/Zorin** | **Claude Code** | **Day 3 Morning** |
| qt_handler.py | 24% | 60%+ | Qwen Coder | Day 4-5 |
| utils/validation.py | 43% | 60%+ | Qwen Coder | Day 5 |
| **Overall Project** | **48%** | **72-75%** | **All Agents** | **EOW** |

### Agent Specializations (Optimized for Week 3)

**🧠 Claude Code (Strategic Architect)**
- Design integration test scenarios
- Create handoff documents
- Write test specifications
- Generate comprehensive documentation
- Perform final week analysis

**⚙️ Qwen Coder (Implementation Specialist)**
- Write pytest test implementations
- Execute test runs and fix failures
- Implement missing test coverage
- Optimize test performance
- Handle all coding tasks

**🔍 Opencode AI (QA & Integration Validator)**
- Run coverage analysis after each day
- Validate test quality and completeness
- Create coverage reports
- Identify gaps and missing tests
- Perform cross-module integration validation
- Generate handoff readiness reports

---

## 📢 Daily Stand-Up Protocol

### Purpose
Ensure transparency, alignment, and early detection of issues across all agents.

### Schedule
**Every morning: 08:00 - 08:15 (15 minutes)**

### Format (Three Questions)

Each day's stand-up addresses:

1. **What did we accomplish yesterday?**
   - Coverage gains
   - Tests added
   - Issues resolved
   - Code reviews completed

2. **What are we doing today?**
   - Agent assignments
   - Specific objectives
   - Deliverables
   - Success criteria

3. **What blockers or risks do we face?**
   - Technical blockers
   - Resource constraints
   - Timeline concerns
   - Dependency issues

### Stand-Up Outputs

Each stand-up produces:
- Written summary (markdown)
- Coverage trajectory update
- Risk assessment
- GO/NO-GO status for the day

### Transparency Benefits

Daily stand-ups ensure:
- ✅ All agents aligned on progress
- ✅ Issues surfaced early
- ✅ Realistic planning adjustments
- ✅ Clear accountability
- ✅ Momentum tracking

**Stand-up reports are stored in:** `reports/daily_standup_dayX.md`

---

## 🔍 Code Review Protocol

### Purpose
Maintain code quality and catch issues before they compound.

### When Code Reviews Happen

**Day 1:** Claude reviews Qwen (Integration tests - complex)
**Day 2:** Claude reviews Qwen (CLI tests - user-facing)
**Day 3:** Qwen self-review (GTK tests - mid-week time pressure)
**Day 4:** Claude reviews Qwen (Qt tests - complex color translation)
**Day 5:** Qwen self-review (Gap closure - final push)

### Code Review Standards

**Review Scope:**
- Code quality (readability, maintainability)
- Test coverage (completeness, edge cases)
- Test isolation (no interdependencies)
- Documentation (docstrings, comments)
- Best practices (fixtures, mocks, assertions)

**Review Timeline:**
- Request review: Tag commit `dayX-implementation-ready`
- Review duration: 30 minutes
- Feedback provided: `CODE_REVIEW_DAYX.md`
- Fixes applied: 15-30 minutes
- Final approval: Tag commit `dayX-complete`

**Review Categories:**
- **Critical:** Must fix before merge
- **Minor:** Should fix, can defer if time-constrained
- **Suggestion:** Nice to have

### Self-Review Checklist (Days 3 & 5)

When self-reviewing, Qwen uses:

```markdown
# Self-Review Checklist

## Code Quality
- [ ] All functions have docstrings
- [ ] No print statements (use logging)
- [ ] No hardcoded paths
- [ ] Proper error handling

## Test Quality
- [ ] Tests are isolated
- [ ] Fixtures used properly
- [ ] Assertions are specific
- [ ] Edge cases covered

## Documentation
- [ ] Test names descriptive
- [ ] Complex logic commented
- [ ] Fixture purposes documented

**Issues Found:** [X]
**Issues Fixed:** [X]
**Approval:** [YES/NO - proceed to Opencode validation]
```

---

## 📅 Day-by-Day Execution Plan

---

# DAY 1 (October 22, 2025)

## Agent: Claude Code (Morning Shift)
**Duration:** 4 hours  
**Role:** Integration Test Architect

### Objectives
1. Design 5 core integration test scenarios
2. Define test data fixtures and mocks
3. Create detailed test specifications for Qwen Coder
4. Document expected behaviors and edge cases

### Deliverables
- [x] `docs/integration_test_specification.md` - Complete test scenarios
- [x] `tests/fixtures/integration_fixtures.py` - Test data structures
- [x] `HANDOFF_DAY1_CLAUDE_TO_QWEN.md` - Implementation instructions

### Tasks Breakdown

#### Task 1.1: Design Core Integration Scenarios (90 min)
**Output:** `docs/integration_test_specification.md`

```markdown
# Integration Test Scenarios - Week 3 Day 1

## Scenario 1: Happy Path - Full Theme Application
**Test ID:** IT-001
**Priority:** P0 (Critical)
**Description:** Complete workflow from theme discovery to successful application

**Test Steps:**
1. Initialize UnifiedThemeManager
2. Discover available themes (expect 59+ themes)
3. Select "Adwaita-dark" theme
4. Apply theme with handlers=['gtk', 'flatpak']
5. Verify files written:
   - ~/.gtkrc-2.0
   - ~/.config/gtk-3.0/settings.ini
   - ~/.config/gtk-4.0/gtk.css
   - Flatpak overrides

**Expected Results:**
- result.success == True
- result.applied_handlers == ['gtk', 'flatpak']
- result.failed_handlers == []
- Backup created automatically
- All theme files contain correct color values

**Edge Cases:**
- Theme with missing color definitions
- Partial theme (GTK3 only, no GTK2)
- Theme with invalid CSS syntax

**Mock Requirements:**
- Mock file system writes (use tmpdir)
- Mock subprocess calls for flatpak commands

---

## Scenario 2: Error Recovery - Handler Failure with Rollback
**Test ID:** IT-002
**Priority:** P0 (Critical)
**Description:** System recovers gracefully when handler fails

**Test Steps:**
1. Apply theme "Test-Theme"
2. Inject failure in GTK handler (simulate permission denied)
3. Trigger rollback
4. Verify system restored to previous state

**Expected Results:**
- result.success == False
- result.failed_handlers == ['gtk']
- Rollback executed automatically
- Backup restored
- User receives clear error message

**Failure Injection Points:**
- Permission denied on file write
- Disk full error
- Invalid theme data

---

## Scenario 3: Multi-Handler Coordination
**Test ID:** IT-003
**Priority:** P0 (Critical)
**Description:** All handlers receive correct theme data simultaneously

**Test Steps:**
1. Apply theme with handlers=['gtk', 'qt', 'flatpak']
2. Verify each handler receives properly formatted data
3. Check no data corruption between handlers
4. Validate color translations (GTK → Qt)

**Expected Results:**
- All 3 handlers apply successfully
- GTK colors: @theme_bg_color, @theme_fg_color
- Qt colors: window.bg, window.fg (translated)
- No color drift (hex values match semantically)

---

## Scenario 4: Backup and Restore Workflow
**Test ID:** IT-004
**Priority:** P1 (High)
**Description:** Manual backup/restore via CLI

**Test Steps:**
1. Apply "Theme-A"
2. Create manual backup (backup_id_1)
3. Apply "Theme-B"
4. Restore backup_id_1
5. Verify "Theme-A" restored

**Expected Results:**
- Backup contains all theme files
- Restore overwrites current theme
- No data loss
- Backup list shows both backups

---

## Scenario 5: Theme Validation and Compatibility Check
**Test ID:** IT-005
**Priority:** P1 (High)
**Description:** Validate theme before application

**Test Steps:**
1. Load theme "Incomplete-Theme" (missing required files)
2. Run validation check
3. Receive compatibility report
4. Attempt to apply (should warn user)

**Expected Results:**
- validation.is_valid == False
- validation.missing_components == ['gtk2', 'libadwaita']
- validation.supported_handlers == ['gtk3', 'flatpak']
- User warned before application
```

#### Task 1.2: Create Test Fixtures (60 min)
**Output:** `tests/fixtures/integration_fixtures.py`

```python
"""
Integration test fixtures and mock data
Week 3 Day 1 - Claude Code
"""

import pytest
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, MagicMock
from src.core.types import Theme, ThemeMetadata, ThemeColors, ThemeFiles

@pytest.fixture
def mock_theme_adwaita_dark():
    """Complete mock theme for happy path testing."""
    return Theme(
        name="Adwaita-dark",
        path=Path("/tmp/test-themes/Adwaita-dark"),
        metadata=ThemeMetadata(
            display_name="Adwaita Dark",
            author="GNOME Project",
            version="42.0",
            description="Default GNOME dark theme"
        ),
        colors={
            'theme_bg_color': '#303030',
            'theme_fg_color': '#ffffff',
            'theme_selected_bg_color': '#3584e4',
            'theme_selected_fg_color': '#ffffff',
            'borders': '#1c1c1c',
            'headerbar_bg_color': '#2a2a2a',
            'headerbar_fg_color': '#ffffff'
        },
        files=ThemeFiles(
            gtk2=Path("/tmp/test-themes/Adwaita-dark/gtk-2.0/gtkrc"),
            gtk3=Path("/tmp/test-themes/Adwaita-dark/gtk-3.0/gtk.css"),
            gtk4=Path("/tmp/test-themes/Adwaita-dark/gtk-4.0/gtk.css")
        )
    )

@pytest.fixture
def mock_theme_incomplete():
    """Incomplete theme for validation testing."""
    return Theme(
        name="Incomplete-Theme",
        path=Path("/tmp/test-themes/Incomplete-Theme"),
        metadata=ThemeMetadata(
            display_name="Incomplete Theme",
            author="Test",
            version="1.0"
        ),
        colors={
            'theme_bg_color': '#ffffff',
            'theme_fg_color': '#000000'
            # Missing selected colors, borders, etc.
        },
        files=ThemeFiles(
            gtk2=None,  # Missing GTK2
            gtk3=Path("/tmp/test-themes/Incomplete-Theme/gtk-3.0/gtk.css"),
            gtk4=None   # Missing GTK4
        )
    )

@pytest.fixture
def mock_file_system(tmp_path, monkeypatch):
    """Mock file system with proper directory structure."""
    # Create mock home directory
    home = tmp_path / "home" / "testuser"
    home.mkdir(parents=True)
    
    # Create config directories
    config = home / ".config"
    config.mkdir()
    (config / "gtk-3.0").mkdir()
    (config / "gtk-4.0").mkdir()
    
    # Create themes directory
    themes = home / ".themes"
    themes.mkdir()
    
    # Mock Path.home() to return our test home
    monkeypatch.setattr(Path, "home", lambda: home)
    
    return {
        'home': home,
        'config': config,
        'themes': themes
    }

@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """Mock subprocess.run for flatpak/snap commands."""
    mock_run = Mock()
    mock_run.return_value = Mock(
        returncode=0,
        stdout="Success",
        stderr=""
    )
    monkeypatch.setattr('subprocess.run', mock_run)
    return mock_run

@pytest.fixture
def mock_manager(mock_file_system, mock_subprocess_run):
    """Fully mocked UnifiedThemeManager for integration tests."""
    from src.core.manager import UnifiedThemeManager
    
    manager = UnifiedThemeManager()
    
    # Inject mocked handlers
    manager.handlers['gtk'].available = True
    manager.handlers['qt'].available = False  # Qt not on test system
    manager.handlers['flatpak'].available = True
    manager.handlers['snap'].available = False
    
    return manager

@pytest.fixture
def integration_test_theme_repository(tmp_path):
    """Create a temporary theme repository with multiple themes."""
    repo = tmp_path / "test-themes"
    repo.mkdir()
    
    themes = ['Adwaita', 'Adwaita-dark', 'Arc', 'Arc-Dark', 'Test-Incomplete']
    
    for theme in themes:
        theme_dir = repo / theme
        theme_dir.mkdir()
        
        # Create basic structure
        (theme_dir / "gtk-2.0").mkdir()
        (theme_dir / "gtk-3.0").mkdir()
        
        # Create index.theme
        index = theme_dir / "index.theme"
        index.write_text(f"""
[Desktop Entry]
Type=X-GNOME-Metatheme
Name={theme}
Comment=Test theme
[X-GNOME-Metatheme]
GtkTheme={theme}
""")
        
        # Create basic gtk-3.0 CSS
        css = theme_dir / "gtk-3.0" / "gtk.css"
        css.write_text("""
@define-color theme_bg_color #ffffff;
@define-color theme_fg_color #000000;
""")
    
    return repo
```

#### Task 1.3: Write Handoff Document (90 min)
**Output:** `HANDOFF_DAY1_CLAUDE_TO_QWEN.md`

```markdown
# Handoff: Claude Code → Qwen Coder
**Date:** October 22, 2025 - Day 1 Afternoon  
**From:** Claude Code (Strategic Architect)  
**To:** Qwen Coder (Implementation Specialist)  
**Status:** Integration test architecture COMPLETE ✅

---

## 📦 What I've Delivered

### 1. Integration Test Specification
**Location:** `docs/integration_test_specification.md`

I've designed 5 core integration test scenarios (IT-001 through IT-005):
- IT-001: Happy path (full theme application)
- IT-002: Error recovery with rollback
- IT-003: Multi-handler coordination
- IT-004: Backup/restore workflow
- IT-005: Theme validation

Each scenario includes:
- Test steps
- Expected results
- Edge cases
- Mock requirements

### 2. Test Fixtures
**Location:** `tests/fixtures/integration_fixtures.py`

Created comprehensive fixtures:
- `mock_theme_adwaita_dark` - Complete theme for happy path
- `mock_theme_incomplete` - Incomplete theme for validation
- `mock_file_system` - Mocked filesystem (tmpdir based)
- `mock_subprocess_run` - Mocked subprocess for flatpak/snap
- `mock_manager` - Fully configured test manager
- `integration_test_theme_repository` - Multi-theme test repo

All fixtures use pytest best practices and are fully isolated.

### 3. This Handoff Document
You're reading it! 📖

---

## 🎯 Your Mission (Day 1 Afternoon)

**Objective:** Implement 5 integration tests (IT-001 through IT-005)  
**Target:** All tests passing, 100% integration test coverage  
**Time:** 4 hours  
**EOD Goal:** Working integration test suite, commit with tag `week3-day1-complete`

---

## 📋 Implementation Checklist

### Step 1: Create Integration Test File (15 min)
**File:** `tests/test_integration.py`

```python
"""
Integration tests for unified theming application
Week 3 Day 1 - Qwen Coder implementation
"""

import pytest
from pathlib import Path
from src.core.manager import UnifiedThemeManager
from tests.fixtures.integration_fixtures import (
    mock_theme_adwaita_dark,
    mock_theme_incomplete,
    mock_file_system,
    mock_subprocess_run,
    mock_manager,
    integration_test_theme_repository
)

# Your tests go here - implement IT-001 through IT-005
```

### Step 2: Implement IT-001 - Happy Path (45 min)
**Priority:** P0 - CRITICAL

```python
def test_integration_happy_path_full_theme_application(
    mock_manager,
    mock_theme_adwaita_dark,
    mock_file_system
):
    """
    IT-001: Complete workflow from discovery to successful application
    
    Test validates:
    1. Theme discovery works
    2. Theme parsing succeeds
    3. Theme applies to multiple handlers
    4. Files written correctly
    5. Backup created automatically
    """
    # TODO: Implement this test
    # Use mock_manager to apply mock_theme_adwaita_dark
    # Verify result.success == True
    # Check result.applied_handlers contains 'gtk' and 'flatpak'
    # Verify files exist in mock_file_system['config']
    # Confirm backup created
    
    pass  # Replace with implementation
```

**Hints:**
- Use `mock_manager.apply_theme(theme.name, handlers=['gtk', 'flatpak'])`
- Check return value: `assert result.success`
- Verify files: `assert (mock_file_system['config'] / 'gtk-3.0' / 'settings.ini').exists()`
- Check backup: `backups = mock_manager.config.list_backups(); assert len(backups) > 0`

### Step 3: Implement IT-002 - Error Recovery (60 min)
**Priority:** P0 - CRITICAL

```python
def test_integration_error_recovery_rollback(
    mock_manager,
    mock_theme_adwaita_dark,
    mock_file_system,
    monkeypatch
):
    """
    IT-002: System recovers gracefully when handler fails
    
    Test validates:
    1. Handler failure detected
    2. Rollback triggered automatically
    3. Previous state restored
    4. Error message clear
    """
    # TODO: Implement this test
    # Apply a theme successfully first (baseline)
    # Then inject failure into gtk_handler.apply() using monkeypatch
    # Attempt to apply different theme
    # Verify rollback occurred
    # Check original theme still active
    
    pass  # Replace with implementation
```

**Hints:**
- Use `monkeypatch.setattr` to inject failure: 
  ```python
  def mock_apply_with_failure(theme):
      raise PermissionError("Permission denied")
  monkeypatch.setattr(mock_manager.handlers['gtk'], 'apply', mock_apply_with_failure)
  ```
- Verify `result.success == False`
- Check `result.failed_handlers == ['gtk']`
- Confirm rollback restored previous theme files

### Step 4: Implement IT-003 - Multi-Handler Coordination (60 min)
**Priority:** P0 - CRITICAL

```python
def test_integration_multi_handler_coordination(
    mock_manager,
    mock_theme_adwaita_dark,
    mock_file_system
):
    """
    IT-003: All handlers receive correct theme data simultaneously
    
    Test validates:
    1. Multiple handlers apply in parallel
    2. Each handler receives correct data
    3. Color translations accurate (GTK → Qt)
    4. No data corruption
    """
    # TODO: Implement this test
    # Enable multiple handlers: ['gtk', 'flatpak']
    # Apply theme
    # Verify each handler's output files
    # Check color consistency
    
    pass  # Replace with implementation
```

**Hints:**
- Apply with `handlers=['gtk', 'flatpak']`
- Read written files and parse color values
- Verify GTK colors: `@define-color theme_bg_color #303030`
- If Qt available, check kdeglobals color translations

### Step 5: Implement IT-004 - Backup/Restore (45 min)
**Priority:** P1 - HIGH

```python
def test_integration_backup_restore_workflow(
    mock_manager,
    mock_theme_adwaita_dark,
    mock_file_system
):
    """
    IT-004: Manual backup and restore via manager
    
    Test validates:
    1. Backup creation
    2. Theme switching
    3. Restore from backup
    4. No data loss
    """
    # TODO: Implement this test
    # Apply Theme-A
    # Create manual backup
    # Apply Theme-B
    # Restore backup
    # Verify Theme-A active again
    
    pass  # Replace with implementation
```

**Hints:**
- Use `backup_id = mock_manager.config.create_backup()`
- Switch themes: `mock_manager.apply_theme('Theme-B')`
- Restore: `mock_manager.config.restore_backup(backup_id)`
- Verify by reading theme files

### Step 6: Implement IT-005 - Theme Validation (30 min)
**Priority:** P1 - HIGH

```python
def test_integration_theme_validation_compatibility(
    mock_manager,
    mock_theme_incomplete,
    mock_file_system
):
    """
    IT-005: Validate theme before application
    
    Test validates:
    1. Incomplete themes detected
    2. Compatibility report generated
    3. User warned appropriately
    4. Partial application possible
    """
    # TODO: Implement this test
    # Validate incomplete theme
    # Check validation.is_valid == False
    # Verify missing_components reported
    # Attempt partial application
    
    pass  # Replace with implementation
```

**Hints:**
- Use `validation = mock_manager.validate_theme(mock_theme_incomplete)`
- Check `validation.is_valid`, `validation.missing_components`
- Try applying anyway: `result = mock_manager.apply_theme(theme.name, force=True)`

### Step 7: Run Tests and Fix Failures (30 min)

```bash
# Run integration tests only
pytest tests/test_integration.py -v

# With coverage
pytest tests/test_integration.py --cov=src --cov-report=term

# Expected output:
# tests/test_integration.py::test_integration_happy_path_full_theme_application PASSED
# tests/test_integration.py::test_integration_error_recovery_rollback PASSED
# tests/test_integration.py::test_integration_multi_handler_coordination PASSED
# tests/test_integration.py::test_integration_backup_restore_workflow PASSED
# tests/test_integration.py::test_integration_theme_validation_compatibility PASSED
#
# 5 passed in 2.34s
```

**If tests fail:**
1. Read error messages carefully
2. Check mock setups in fixtures
3. Verify file paths use `mock_file_system`
4. Ensure subprocess mocks working
5. Add debug prints if needed

### Step 8: Commit and Tag (10 min)

```bash
git add tests/test_integration.py
git add tests/fixtures/integration_fixtures.py
git add docs/integration_test_specification.md
git commit -m "Week 3 Day 1: Integration tests complete (IT-001 to IT-005)"
git tag week3-day1-complete
git push origin main --tags
```

---

## ✅ Definition of Done (EOD Day 1)

You're done when ALL of these are true:

- [x] File `tests/test_integration.py` exists
- [x] All 5 integration tests implemented (IT-001 through IT-005)
- [x] All 5 tests PASSING (`pytest tests/test_integration.py`)
- [x] No regression in existing tests (`pytest` runs all 149 tests still passing)
- [x] Code follows pytest best practices
- [x] Fixtures properly imported and used
- [x] Git commit with tag `week3-day1-complete`
- [x] Handoff document created for Opencode AI

---

## 🚨 Blockers / Issues

If you encounter blockers:

1. **Mock not working correctly**
   - Check fixture imports
   - Verify monkeypatch usage
   - Use `tmp_path` fixture properly

2. **Tests timing out**
   - Ensure subprocess.run is mocked
   - Check for infinite loops
   - Add timeout to pytest: `pytest --timeout=10`

3. **Import errors**
   - Verify src/ in PYTHONPATH
   - Check relative imports
   - Ensure fixtures in conftest.py or imported explicitly

4. **File system issues**
   - Always use mock_file_system fixture
   - Don't write to real ~/.config
   - Use tmp_path for all file operations

**If blocked:** Document issue in handoff, mark test with `@pytest.mark.skip(reason="Blocked by X")`, move to next test.

---

## 📤 Your Handoff Deliverable

**File:** `HANDOFF_DAY1_QWEN_TO_OPENCODE.md`

Create this file at EOD with:

```markdown
# Handoff: Qwen Coder → Opencode AI
**Date:** October 22, 2025 - Day 1 EOD
**From:** Qwen Coder
**To:** Opencode AI

## Status
- [x] Integration tests implemented: 5/5
- [x] Tests passing: X/5
- [x] Commit tagged: week3-day1-complete

## Test Results
[Paste pytest output here]

## Coverage Impact
Before Day 1: 48%
After Day 1: [Run and report: `pytest --cov --cov-report=term`]

## Blockers Encountered
[List any issues, workarounds, or skipped tests]

## Next Steps for Opencode AI
1. Validate test quality
2. Run full coverage analysis
3. Check for integration with existing tests
4. Generate Day 1 completion report
```

---

## 🎯 Success Metrics

**Minimum Viable:**
- 4/5 tests passing (IT-001, IT-002, IT-003, IT-004 critical)
- No regressions in existing 149 tests
- Commit tagged

**Target:**
- 5/5 tests passing
- Coverage increase of +2-3% (integration paths)
- Clean code, no TODOs

**Stretch:**
- Additional edge case tests
- Performance benchmarks for integration workflows
- Documentation of integration patterns

---

## 📚 Reference Materials

**Related Files:**
- `src/core/manager.py` - UnifiedThemeManager implementation
- `src/core/config.py` - Backup and config management
- `tests/test_manager.py` - Existing manager tests (reference)
- `tests/test_config.py` - Existing config tests (reference)

**Pytest Documentation:**
- Fixtures: https://docs.pytest.org/en/stable/fixture.html
- Monkeypatch: https://docs.pytest.org/en/stable/monkeypatch.html
- Parametrize: https://docs.pytest.org/en/stable/parametrize.html

**Our Testing Standards:**
- Use descriptive test names: `test_integration_<scenario>_<expected_behavior>`
- Always include docstrings explaining what test validates
- Use fixtures for test data (no hardcoded paths)
- Mock all external dependencies (filesystem, subprocess, network)
- Assert specific values, not just truthy/falsy
- One logical assertion per test (multiple asserts OK if testing same concept)

---

## 💪 You've Got This!

This is the critical day that validates our entire architecture. These integration tests prove the system works end-to-end. Take your time, write clean tests, and don't hesitate to add debug output if you need to understand what's happening.

Remember: **Working tests > Perfect tests**. Get them passing first, then refactor if needed.

Good luck! 🚀

---

**Signed:** Claude Code  
**Time:** 12:00 PM, Day 1
```

### EOD Deliverables Checklist for Claude Code

- [x] `docs/integration_test_specification.md` - 5 scenarios documented
- [x] `tests/fixtures/integration_fixtures.py` - All fixtures created
- [x] `HANDOFF_DAY1_CLAUDE_TO_QWEN.md` - Complete handoff document
- [x] Commit with message: "Week 3 Day 1 Morning: Integration test architecture"
- [x] Tag: `week3-day1-architecture-complete`
- [x] Code review checklist created for Qwen's implementation

### Code Review Checklist for Qwen's Work

**Before Qwen starts implementation, Claude provides:**

```markdown
# Code Review Checklist - Day 1 Integration Tests
**Reviewer:** Claude Code (will review Qwen's implementation)

## Code Quality Standards
- [ ] All tests have descriptive docstrings
- [ ] Test names follow convention: `test_integration_<scenario>_<behavior>`
- [ ] No hardcoded paths (use fixtures)
- [ ] All external dependencies mocked
- [ ] Proper use of pytest fixtures
- [ ] Assertions are specific, not generic
- [ ] No print statements (use logging if needed)

## Test Coverage Standards
- [ ] Happy path tested
- [ ] Error cases tested
- [ ] Edge cases identified and tested
- [ ] No duplicate test logic
- [ ] Each test focuses on one scenario

## Integration Standards
- [ ] Tests run in isolation
- [ ] No test interdependencies
- [ ] Proper cleanup after each test
- [ ] Mock setup is clear and correct
- [ ] File system operations use tmp_path

## Documentation Standards
- [ ] Inline comments for complex logic
- [ ] Fixtures documented
- [ ] Test IDs (IT-001, etc.) referenced

**Review Trigger:** After Qwen creates pull request or commits with tag `week3-day1-implementation-ready`
```

---

## Agent: Qwen Coder (Afternoon Shift)
**Duration:** 4 hours  
**Role:** Test Implementation Specialist

### Objectives
1. Implement all 5 integration tests (IT-001 to IT-005)
2. Ensure all tests pass
3. Fix any test failures or mock issues
4. Verify no regressions in existing test suite

### Deliverables
- [x] `tests/test_integration.py` - Complete integration test suite
- [x] All 5 tests passing
- [x] `HANDOFF_DAY1_QWEN_TO_OPENCODE.md` - Handoff for validation

### EOD Success Criteria
- ✅ 5/5 integration tests passing
- ✅ No regressions (149 existing tests still pass)
- ✅ Git commit tagged: `week3-day1-implementation-ready` (triggers Claude review)
- ✅ Coverage increase of +2-3%
- ✅ Code review checklist self-assessed
- ✅ Ready for Claude Code review

### Code Review Protocol

**After Qwen completes implementation:**

1. **Self-Review** (15 min)
   - Go through Claude's code review checklist
   - Fix obvious issues
   - Document any intentional deviations

2. **Request Review**
   - Tag commit: `week3-day1-implementation-ready`
   - Create handoff: `HANDOFF_DAY1_QWEN_TO_CLAUDE_REVIEW.md`
   - Include self-review notes

3. **Claude Review** (30 min)
   - Review against checklist
   - Test code quality
   - Verify test isolation
   - Check documentation
   - Provide feedback in: `CODE_REVIEW_DAY1.md`

4. **Address Feedback** (30 min, if needed)
   - Qwen implements review comments
   - Re-tag: `week3-day1-complete`
   - Proceed to Opencode AI validation

**Review Template:** `CODE_REVIEW_DAY1.md`

```markdown
# Code Review: Day 1 Integration Tests
**Reviewer:** Claude Code
**Author:** Qwen Coder
**Date:** October 22, 2025

## Overall Assessment
**Status:** [APPROVED / NEEDS CHANGES / MAJOR REVISION]
**Quality Score:** [X/10]

## Checklist Review
[Go through code review checklist with findings]

## Issues Found
### Critical (Must Fix)
1. [Issue description]
   - **File:** [filename:line]
   - **Problem:** [description]
   - **Fix:** [suggested fix]

### Minor (Should Fix)
[List minor issues]

### Suggestions (Nice to Have)
[List improvements]

## Positive Highlights
[What was done well]

## Approval Status
- [ ] Approved as-is
- [ ] Approved with minor changes
- [ ] Needs revision

**Next Steps:** [Instructions for Qwen]
```

---

## Agent: Opencode AI (Evening Shift)
**Duration:** 2 hours  
**Role:** QA Validator & Coverage Analyst

### Objectives
1. Validate integration test quality
2. Run comprehensive coverage analysis
3. Check for test interactions and regressions
4. Generate Day 1 completion report

### Deliverables
- [x] `reports/week3_day1_coverage_report.md` - Full coverage analysis
- [x] `reports/week3_day1_qa_validation.md` - Test quality assessment
- [x] `HANDOFF_DAY1_COMPLETE.md` - Day 1 summary for Claude Code

### Tasks Breakdown

#### Task 1: Validate Test Quality (30 min)

```bash
# Run integration tests multiple times to check for flakiness
for i in {1..5}; do
    echo "Run $i"
    pytest tests/test_integration.py -v
done

# Check test isolation (run in random order)
pytest tests/test_integration.py --random-order

# Run with verbose output
pytest tests/test_integration.py -vv --tb=long
```

**Quality Checklist:**
- [ ] Tests pass consistently (5/5 runs)
- [ ] Tests are properly isolated (order doesn't matter)
- [ ] Mocks working correctly
- [ ] No hardcoded paths or dependencies
- [ ] Assertions are specific and meaningful
- [ ] Error messages clear

#### Task 2: Generate Coverage Report (30 min)

```bash
# Run full test suite with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Generate coverage report
coverage report -m > reports/coverage_day1_detailed.txt

# Check coverage by module
coverage report --include="src/core/*"
coverage report --include="src/handlers/*"
coverage report --include="src/utils/*"
```

**Output:** `reports/week3_day1_coverage_report.md`

```markdown
# Week 3 Day 1 Coverage Report
**Generated:** October 22, 2025 22:00
**Agent:** Opencode AI

## Overall Coverage

| Metric | Before Day 1 | After Day 1 | Delta |
|--------|--------------|-------------|-------|
| Total Coverage | 48% | [FILL]% | +[FILL]% |
| Total Tests | 149 | [FILL] | +[FILL] |
| Test Pass Rate | 99.3% | [FILL]% | [FILL] |

## Coverage by Module

| Module | Before | After | Delta | Status |
|--------|--------|-------|-------|--------|
| core/manager.py | 93% | [FILL]% | +[FILL]% | ✅ |
| core/config.py | 75% | [FILL]% | +[FILL]% | ✅ |
| core/parser.py | 63% | [FILL]% | +[FILL]% | ⚠️ |
| handlers/gtk_handler.py | 42% | [FILL]% | +[FILL]% | ⚠️ |
| handlers/qt_handler.py | 24% | [FILL]% | +[FILL]% | ❌ |
| handlers/flatpak_handler.py | 100% | [FILL]% | +[FILL]% | ✅ |

## Integration Test Results

| Test ID | Test Name | Status | Duration |
|---------|-----------|--------|----------|
| IT-001 | Happy Path Full Application | [PASS/FAIL] | [TIME]s |
| IT-002 | Error Recovery Rollback | [PASS/FAIL] | [TIME]s |
| IT-003 | Multi-Handler Coordination | [PASS/FAIL] | [TIME]s |
| IT-004 | Backup Restore Workflow | [PASS/FAIL] | [TIME]s |
| IT-005 | Theme Validation | [PASS/FAIL] | [TIME]s |

## New Coverage Areas

Integration tests added coverage for:
- [ ] Manager.apply_theme() error handling paths
- [ ] Config.rollback() workflow
- [ ] Multi-handler coordination logic
- [ ] Backup/restore end-to-end flow
- [ ] Theme validation pipeline

## Gaps Identified

[List any coverage gaps discovered]

## Recommendations for Day 2

[Specific suggestions for tomorrow's work]
```

#### Task 3: QA Validation Report (30 min)

**Output:** `reports/week3_day1_qa_validation.md`

```markdown
# Week 3 Day 1 QA Validation Report
**Date:** October 22, 2025
**QA Agent:** Opencode AI

## Test Quality Assessment

### Integration Tests (tests/test_integration.py)

#### IT-001: Happy Path Full Theme Application
- **Status:** [PASS/FAIL]
- **Quality Score:** [X/10]
- **Issues Found:** [List any issues]
- **Recommendations:** [Improvements]

#### IT-002: Error Recovery Rollback
- **Status:** [PASS/FAIL]
- **Quality Score:** [X/10]
- **Issues Found:** [List any issues]
- **Recommendations:** [Improvements]

[Repeat for IT-003, IT-004, IT-005]

## Regression Analysis

**Existing Test Suite:**
- Total tests run: [FILL]
- Passed: [FILL]
- Failed: [FILL]
- Skipped: [FILL]

**Regressions Detected:** [YES/NO]
[If yes, list affected tests]

## Test Flakiness Check

**Flakiness Test Results:**
- Run 1: [X/5 passed]
- Run 2: [X/5 passed]
- Run 3: [X/5 passed]
- Run 4: [X/5 passed]
- Run 5: [X/5 passed]

**Flaky Tests:** [None/List]

## Code Quality

**Linting Results:**
```bash
black --check tests/test_integration.py
flake8 tests/test_integration.py
mypy tests/test_integration.py
```
[Paste results]

## Performance

**Test Execution Time:**
- Integration suite: [TIME]s
- Full test suite: [TIME]s

**Performance Issues:** [None/List]

## Day 1 Completion Status

- [x] All integration tests implemented
- [x] Tests passing consistently
- [x] No regressions introduced
- [x] Coverage increased by [X]%
- [x] Code quality checks passed

**Overall Grade:** [A/B/C/D/F]

## GO/NO-GO for Day 2

**Decision:** [GO / NO-GO]

**Justification:** [Explain decision]

**Blockers for Day 2:** [None/List]
```

#### Task 4: Create Day 1 Complete Handoff (30 min)

**Output:** `HANDOFF_DAY1_COMPLETE.md`

```markdown
# Day 1 Complete: Integration Testing
**Date:** October 22, 2025 EOD
**Status:** COMPLETE ✅

## Executive Summary

**Objective:** Implement 5 core integration tests
**Result:** [X/5 tests passing]
**Coverage:** 48% → [X]% (+[X]%)
**Status:** [ON TRACK / NEEDS ATTENTION]

## What Was Accomplished

### Morning (Claude Code)
✅ Integration test architecture designed
✅ 5 test scenarios documented
✅ Test fixtures created
✅ Handoff document complete

### Afternoon (Qwen Coder)
✅ All 5 integration tests implemented
✅ [X/5] tests passing
✅ [List any issues resolved]

### Evening (Opencode AI)
✅ Test quality validated
✅ Coverage analysis complete
✅ No regressions detected
✅ Day 1 reports generated

## Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| IT-001 Happy Path | ✅ | [notes] |
| IT-002 Error Recovery | ✅ | [notes] |
| IT-003 Multi-Handler | ✅ | [notes] |
| IT-004 Backup/Restore | ✅ | [notes] |
| IT-005 Validation | ✅ | [notes] |

## Coverage Impact

**By Module:**
- Manager: 93% → [X]%
- Config: 75% → [X]%
- GTK Handler: 42% (unchanged - expected)
- Qt Handler: 24% (unchanged - expected)

**Overall:** 48% → [X]%

## Key Learnings

[What worked well]
[What was challenging]
[Insights for Day 2]

## Handoff to Day 2 (CLI Testing)

### Ready for Day 2: YES/NO

**Prerequisites Met:**
- [x] Integration tests validated
- [x] No blocking regressions
- [x] Coverage baseline established
- [x] Test infrastructure working

### Day 2 Focus: CLI Command Testing
**Agent:** Qwen Coder (full day)
**Target:** cli/commands.py 0% → 60%+
**File:** `tests/test_cli_commands.py`

**Day 2 Priority Commands:**
1. `unified-theme list` (P0)
2. `unified-theme apply <theme>` (P0)
3. `unified-theme current` (P1)
4. `unified-theme backup create` (P1)
5. `unified-theme backup restore <id>` (P1)

### Blockers for Day 2: [None/List]

### Recommended Actions

[Any specific recommendations for Day 2 based on Day 1 experience]

---

**QA Sign-off:** Opencode AI  
**Date:** October 22, 2025 23:00  
**Next Agent:** Claude Code (Day 2 morning)
```

### EOD Deliverables for Opencode AI

- [x] `reports/week3_day1_coverage_report.md`
- [x] `reports/week3_day1_qa_validation.md`
- [x] `HANDOFF_DAY1_COMPLETE.md`
- [x] Git tag: `week3-day1-validated`

---

# DAY 2 (October 23, 2025)

## Daily Stand-Up Summary (All Agents)
**Time:** 08:00 - 08:15 (15 min)
**Purpose:** Alignment and transparency

### Stand-Up Format

Each agent (or coordinator) provides:

1. **Yesterday's Accomplishments**
   - Day 1 results summary
   - Coverage achieved
   - Tests added

2. **Today's Plan**
   - Day 2 objectives
   - Agent assignments
   - Expected deliverables

3. **Blockers/Risks**
   - Any issues from Day 1
   - Concerns for Day 2
   - Resource needs

### Day 2 Stand-Up Report

**Generated by:** Opencode AI (from Day 1 completion report)

```markdown
# Week 3 Day 2 Stand-Up Report
**Date:** October 23, 2025 08:00
**Duration:** 15 minutes

## Yesterday (Day 1) - Integration Testing

### Accomplishments ✅
- Integration test architecture designed (Claude Code)
- 5 integration tests implemented (Qwen Coder)
- Tests passing: [X/5]
- Coverage: 48% → [X]% (+[Y]%)
- Code review completed
- Validation passed (Opencode AI)

### Issues/Blockers 🚨
[List any issues from Day 1]

### Lessons Learned 💡
[Key insights from Day 1]

## Today (Day 2) - CLI Testing

### Objectives 🎯
- Design CLI test architecture (Claude Code - Morning)
- Implement 15+ CLI tests (Qwen Coder - Full Day)
- Target: cli/commands.py 0% → 60%+
- Code review and validation (Claude + Opencode)

### Agent Assignments 👥
- **08:15-10:15:** Claude Code - CLI test specification
- **10:30-17:00:** Qwen Coder - CLI test implementation
- **17:00-17:30:** Claude Code - Code review
- **17:30-19:30:** Opencode AI - Validation and Day 2 report

### Success Criteria ✅
- [ ] CLI coverage ≥ 60%
- [ ] 15+ CLI tests passing
- [ ] No regressions
- [ ] Code review approved
- [ ] Day 2 complete tag

### Risks ⚠️
[Identify any Day 2-specific risks]

### Coverage Trajectory 📈
- Day 1 End: [X]%
- Day 2 Target: [X+8]% (CLI impact)
- Week Target: 72%
- Days 3-5 Buffer: [Y]%

**Status:** [ON TRACK / AT RISK / NEEDS ATTENTION]
```

---

## Agent: Claude Code (Morning Shift)
**Duration:** 2 hours  
**Role:** CLI Test Architect

### Objectives
1. Review Day 1 results
2. Design CLI test architecture
3. Create CLI test specifications
4. Document CLI command behaviors

### Deliverables
- [x] `docs/cli_test_specification.md` - CLI test scenarios
- [x] `HANDOFF_DAY2_CLAUDE_TO_QWEN.md` - Implementation guide

### Tasks Breakdown

#### Task 2.1: Review Day 1 and Plan Day 2 (30 min)

```bash
# Read Day 1 completion report
cat HANDOFF_DAY1_COMPLETE.md

# Check current coverage
pytest --cov=src --cov-report=term | grep TOTAL

# Identify CLI testing scope
ls -la src/cli/
```

**Planning Questions:**
- What's current coverage? (Baseline: 48%)
- Did Day 1 meet targets? (Target: +2-3%)
- Any blockers from Day 1?
- CLI complexity assessment

#### Task 2.2: Design CLI Test Specification (60 min)

**Output:** `docs/cli_test_specification.md`

```markdown
# CLI Test Specification - Week 3 Day 2

## CLI Architecture Overview

The CLI is implemented using Click framework with following commands:

```
unified-theme
├── list [--format=table|json]
├── apply <theme-name> [--handlers=gtk,qt,flatpak]
├── current [--format=table|json]
├── validate <theme-name>
├── backup
│   ├── create [--name=backup-name]
│   ├── list
│   ├── restore <backup-id>
│   └── delete <backup-id>
└── version
```

## Test Scenarios

### TC-CLI-001: List Command (P0)
**Command:** `unified-theme list`
**Priority:** Critical
**Description:** Display all available themes

**Test Cases:**
1. List with default format (table)
2. List with JSON format (`--format=json`)
3. List when no themes available (edge case)
4. List with many themes (performance)

**Expected Output (table format):**
```
Available Themes:
┌────────────────┬─────────┬────────────┐
│ Name           │ Type    │ Compatible │
├────────────────┼─────────┼────────────┤
│ Adwaita        │ GTK3/4  │ Yes        │
│ Adwaita-dark   │ GTK3/4  │ Yes        │
│ Arc            │ GTK2/3  │ Partial    │
└────────────────┴─────────┴────────────┘
```

**Expected Output (JSON format):**
```json
{
  "themes": [
    {
      "name": "Adwaita",
      "type": "GTK3/4",
      "compatible": true,
      "handlers": ["gtk", "flatpak"]
    }
  ]
}
```

**Assertions:**
- Exit code 0
- Table formatted correctly
- JSON is valid and parseable
- All discovered themes listed
- No crashes or exceptions

---

### TC-CLI-002: Apply Command Success (P0)
**Command:** `unified-theme apply Adwaita-dark`
**Priority:** Critical
**Description:** Successfully apply a theme

**Test Cases:**
1. Apply existing theme (happy path)
2. Apply with specific handlers (`--handlers=gtk,flatpak`)
3. Apply with progress output
4. Apply creates backup automatically

**Expected Output:**
```
Applying theme: Adwaita-dark
[####################################] 100%
✓ GTK theme applied
✓ Flatpak theme applied
✓ Backup created: backup_20251023_120000

Theme 'Adwaita-dark' applied successfully!
```

**Assertions:**
- Exit code 0
- Success message displayed
- Backup created
- Theme actually applied (verify files)

---

### TC-CLI-003: Apply Command Failure (P0)
**Command:** `unified-theme apply NonExistentTheme`
**Priority:** Critical
**Description:** Handle non-existent theme gracefully

**Expected Output:**
```
Error: Theme 'NonExistentTheme' not found.

Available themes: Adwaita, Adwaita-dark, Arc, ...

Run 'unified-theme list' to see all themes.
```

**Assertions:**
- Exit code 1
- Clear error message
- Suggests alternatives
- No crash or stack trace

---

### TC-CLI-004: Apply Command Missing Argument (P0)
**Command:** `unified-theme apply`
**Priority:** Critical
**Description:** Handle missing required argument

**Expected Output:**
```
Error: Missing argument 'THEME_NAME'.

Usage: unified-theme apply [OPTIONS] THEME_NAME

Try 'unified-theme apply --help' for more information.
```

**Assertions:**
- Exit code 2 (Click error code)
- Usage information displayed
- Help hint provided

---

### TC-CLI-005: Current Command (P1)
**Command:** `unified-theme current`
**Priority:** High
**Description:** Display currently active theme

**Test Cases:**
1. Show current theme (table format)
2. Show current theme (JSON format)
3. Handle no active theme

**Expected Output:**
```
Current Theme: Adwaita-dark
Applied: 2025-10-23 12:00:00
Handlers: GTK, Flatpak
Backup: backup_20251023_120000
```

**Assertions:**
- Exit code 0
- Shows theme name
- Shows application date/time
- Lists active handlers

---

### TC-CLI-006: Backup Create (P1)
**Command:** `unified-theme backup create --name=before-experiment`
**Priority:** High
**Description:** Create manual backup

**Expected Output:**
```
Creating backup...
✓ Backup created: before-experiment (backup_20251023_120000)

Location: ~/.config/unified-theming/backups/backup_20251023_120000
```

**Assertions:**
- Exit code 0
- Backup created with given name
- Backup ID returned
- Backup directory exists

---

### TC-CLI-007: Backup List (P1)
**Command:** `unified-theme backup list`
**Priority:** High
**Description:** List all available backups

**Expected Output:**
```
Available Backups:
┌──────────────────────────┬─────────────────────┬─────────┐
│ ID                       │ Created             │ Name    │
├──────────────────────────┼─────────────────────┼─────────┤
│ backup_20251023_120000   │ 2025-10-23 12:00:00 │ auto    │
│ backup_20251023_110000   │ 2025-10-23 11:00:00 │ manual  │
└──────────────────────────┴─────────────────────┴─────────┘
```

**Assertions:**
- Exit code 0
- All backups listed
- Sorted by creation date (newest first)
- Formatted correctly

---

### TC-CLI-008: Backup Restore (P1)
**Command:** `unified-theme backup restore backup_20251023_120000`
**Priority:** High
**Description:** Restore from backup

**Test Cases:**
1. Restore valid backup
2. Restore non-existent backup (error)
3. Restore with confirmation prompt

**Expected Output:**
```
Restoring backup: backup_20251023_120000

Warning: This will overwrite your current theme configuration.
Continue? [y/N]: y

Restoring...
✓ GTK configuration restored
✓ Qt configuration restored
✓ Flatpak overrides restored

Backup restored successfully!
```

**Assertions:**
- Exit code 0
- Confirmation prompt shown
- Files actually restored
- Success message

---

### TC-CLI-009: Version Command (P2)
**Command:** `unified-theme version` or `unified-theme --version`
**Priority:** Medium
**Description:** Display version information

**Expected Output:**
```
unified-theme version 0.5.0
Python 3.10.12
```

**Assertions:**
- Exit code 0
- Version number displayed
- Python version shown

---

### TC-CLI-010: Help Command (P2)
**Command:** `unified-theme --help`
**Priority:** Medium
**Description:** Display help information

**Expected Output:**
```
Usage: unified-theme [OPTIONS] COMMAND [ARGS]...

  Unified theme management across GTK, Qt, and containers.

Options:
  --version  Show version and exit.
  --help     Show this message and exit.

Commands:
  list     List available themes
  apply    Apply a theme
  current  Show current theme
  backup   Manage backups
```

**Assertions:**
- Exit code 0
- All commands listed
- Descriptions present
- Properly formatted

---

## Test Implementation Strategy

### Priority Order
1. **P0 Tests (Critical):** TC-CLI-001 through TC-CLI-004
2. **P1 Tests (High):** TC-CLI-005 through TC-CLI-008
3. **P2 Tests (Medium):** TC-CLI-009, TC-CLI-010

### Test Structure
```python
# tests/test_cli_commands.py

from click.testing import CliRunner
import pytest
from src.cli.commands import cli

@pytest.fixture
def cli_runner():
    """Fixture providing Click CLI test runner."""
    return CliRunner()

@pytest.fixture
def mock_theme_environment(tmp_path, monkeypatch):
    """Mock environment with themes and config."""
    # Set up test environment
    pass

def test_cli_list_default_format(cli_runner, mock_theme_environment):
    """TC-CLI-001: List themes in table format."""
    result = cli_runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'Adwaita' in result.output
```

### Mock Requirements
- Mock theme discovery
- Mock file system (~/.config, ~/.themes)
- Mock subprocess (for flatpak/snap)
- Mock backup operations
- Isolated environment (no real theme changes)

### Coverage Target
- `src/cli/commands.py`: 0% → 60%+
- ~15-20 CLI tests
- All major commands covered
- Error paths tested
```

#### Task 2.3: Create Handoff Document (30 min)

**Output:** `HANDOFF_DAY2_CLAUDE_TO_QWEN.md`

[Full handoff document similar to Day 1, with CLI-specific instructions]

---

## Agent: Qwen Coder (Full Day)
**Duration:** 6 hours  
**Role:** CLI Test Implementation

### Objectives
1. Implement all CLI tests (TC-CLI-001 through TC-CLI-010)
2. Achieve 60%+ coverage on cli/commands.py
3. Fix any CLI bugs discovered during testing
4. Ensure all tests pass

### Deliverables
- [x] `tests/test_cli_commands.py` - Complete CLI test suite
- [x] 15+ tests passing
- [x] CLI coverage 0% → 60%+
- [x] `HANDOFF_DAY2_QWEN_TO_OPENCODE.md`

### EOD Success Criteria
- ✅ 15+ CLI tests implemented and passing
- ✅ CLI coverage ≥ 60%
- ✅ No regressions in existing tests
- ✅ Git commit tagged: `week3-day2-complete`

---

## Agent: Opencode AI (Evening)
**Duration:** 2 hours  
**Role:** Coverage Analysis & Day 2 Validation

### Objectives
1. Validate CLI test quality
2. Run coverage analysis
3. Generate Day 2 completion report
4. Assess Week 3 progress (Days 1-2 combined)

### Deliverables
- [x] `reports/week3_day2_coverage_report.md`
- [x] `reports/week3_day2_qa_validation.md`
- [x] `HANDOFF_DAY2_COMPLETE.md`

### EOD Success Criteria
- ✅ CLI coverage validated ≥ 60%
- ✅ Overall project coverage ≥ 50%
- ✅ Day 3 ready to start (GTK handler testing)

---

# DAY 3 (October 24, 2025)

## Daily Stand-Up Summary (All Agents)
**Time:** 08:00 - 08:15 (15 min)

```markdown
# Week 3 Day 3 Stand-Up Report
**Date:** October 24, 2025 08:00

## Yesterday (Day 2) - CLI Testing

### Accomplishments ✅
- CLI test architecture designed (Claude Code)
- [X] CLI tests implemented (Qwen Coder)
- CLI coverage: 0% → [X]%
- Coverage: [X]% → [Y]% (+[Z]%)
- Code review approved

### Issues/Blockers 🚨
[List any issues from Day 2]

## Today (Day 3) - GTK Handler Testing + LibAdapta/Zorin Integration

### Objectives 🎯
- **🔧 Refactor GTK handler** for LibAdapta/Zorin support (Claude Code - Morning)
- **📝 Implement GTK handler tests** (Qwen Coder - Afternoon)
- Target: gtk_handler.py 42% → 70%+
- 25+ GTK-specific tests (includes new detection/adaptation tests)
- Validation (Opencode AI - Evening)

### Mid-Week Checkpoint 🔍
- **After Day 3:** Mid-week assessment
- **Assess trajectory** toward 72% goal
- **Adjust Days 4-5** if needed

### Success Criteria ✅
- [ ] LibAdapta/Zorin detection implemented ✅
- [ ] Adaptive theme application implemented ✅
- [ ] GTK handler ≥ 70% coverage (increased from 65%)
- [ ] 25+ tests passing (includes new detection tests)
- [ ] Mid-week assessment complete

**Coverage Projection:** [X]% after Day 3
**Gap to 72% target:** [Y]%
```

---

## Agent: Claude Code (Morning)
**Duration:** 3 hours
**Role:** GTK Handler Refactor Architect

### Objectives
1. Implement LibAdapta/Zorin OS patch detection system
2. Refactor GTKHandler to support adaptive theme application
3. Create marker files and theme directories for patched environments
4. Document the three-mode system (CSS injection, LibAdapta, Zorin)
5. Create test specifications for new functionality

### Background Context
**Examined Codebases:**
- LibAdapta (Linux Mint soft fork) - uses `libadapta-1.5/` directories
- Zorin OS patch - uses `.libadwaita` marker files
- Current implementation - CSS injection to `~/.config/gtk-4.0/gtk.css`

**Strategic Decision:** Implement **detection and adaptation**, not library replacement

### Deliverables
- [x] `unified_theming/handlers/gtk_handler.py` (refactored)
- [x] `docs/libadwaita_detection_spec.md` - Technical specification
- [x] `HANDOFF_DAY3_CLAUDE_TO_QWEN.md` - Testing instructions
- [x] Test specifications for new detection/adaptation code

### Refactoring Tasks

#### Task 3.1: Detection System Implementation (60 min)

Add detection methods to `GTKHandler.__init__()`:

```python
class GTKHandler(BaseHandler):
    def __init__(self):
        # ... existing code ...
        self.libadwaita_mode = self._detect_libadwaita_mode()
        logger.info(f"LibAdwaita mode detected: {self.libadwaita_mode}")

    def _detect_libadwaita_mode(self) -> str:
        """
        Detect which libadwaita theming mode is available.

        Returns:
            'libadapta' - LibAdapta fork installed
            'zorin-patch' - Zorin-style patch installed
            'css-injection' - Default mode (no patch)
        """
        # Check for LibAdapta via pkg-config
        if self._check_libadapta_installed():
            return 'libadapta'

        # Check for Zorin patch by scanning for .libadwaita markers
        if self._check_zorin_patch_available():
            return 'zorin-patch'

        # Default: CSS injection
        return 'css-injection'

    def _check_libadapta_installed(self) -> bool:
        """Check if libAdapta is installed via pkg-config."""
        try:
            result = subprocess.run(
                ['pkg-config', '--modversion', 'libadapta-1'],
                capture_output=True, text=True, timeout=2
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_zorin_patch_available(self) -> bool:
        """
        Check if Zorin-style patch is available by looking for
        existing .libadwaita markers in system themes.
        """
        search_paths = [
            Path('/usr/share/themes'),
            Path.home() / '.themes',
            Path.home() / '.local/share/themes'
        ]

        for base_path in search_paths:
            if not base_path.exists():
                continue

            for theme_dir in base_path.iterdir():
                if not theme_dir.is_dir():
                    continue

                marker = theme_dir / 'gtk-4.0' / '.libadwaita'
                if marker.exists():
                    logger.debug(f"Found Zorin patch marker in: {theme_dir}")
                    return True

        return False
```

**Testing Requirements:**
- Test detection with libAdapta present/absent
- Test detection with Zorin markers present/absent
- Test fallback to css-injection
- Mock pkg-config and filesystem for isolation

#### Task 3.2: Adaptive Application Implementation (90 min)

Refactor `_apply_libadwaita_theme()` to use detected mode:

```python
def _apply_libadwaita_theme(self, theme_data: ThemeData) -> bool:
    """
    Apply libadwaita theme using best available method.

    Automatically selects:
    - LibAdapta directory creation if libAdapta installed
    - Zorin marker file if Zorin patch detected
    - CSS injection otherwise (default)
    """
    try:
        if self.libadwaita_mode == 'libadapta':
            success = self._apply_via_libadapta(theme_data)
            logger.info(f"Applied via LibAdapta: {success}")
            return success

        elif self.libadwaita_mode == 'zorin-patch':
            success = self._apply_via_zorin_marker(theme_data)
            logger.info(f"Applied via Zorin patch: {success}")
            return success

        else:
            success = self._apply_via_css_injection(theme_data)
            logger.info(f"Applied via CSS injection: {success}")
            return success

    except Exception as e:
        logger.error(f"Error in adaptive libadwaita application: {e}")
        # Fallback to CSS injection
        logger.warning("Falling back to CSS injection")
        return self._apply_via_css_injection(theme_data)

def _apply_via_libadapta(self, theme_data: ThemeData) -> bool:
    """
    Create libadapta-1.5 theme directory structure.

    Directory structure:
        ~/.themes/THEME_NAME/libadapta-1.5/
            ├── base.css
            ├── base-hc.css
            ├── defaults-light.css
            ├── defaults-dark.css
            └── assets/
    """
    theme_base = Path.home() / '.themes' / theme_data.name
    libadapta_dir = theme_base / 'libadapta-1.5'

    # Check if theme already has native libadapta support
    if (libadapta_dir / 'base.css').exists():
        logger.info(f"Theme '{theme_data.name}' has native libAdapta support")
        # Still apply GTK theme setting
        self._apply_gtk3_theme(theme_data.name)
        return True

    # Generate libadapta theme from GTK theme data
    try:
        libadapta_dir.mkdir(parents=True, exist_ok=True)

        # Generate color definition files
        light_css = self._generate_libadapta_colors(theme_data, dark=False)
        dark_css = self._generate_libadapta_colors(theme_data, dark=True)
        base_css = self._generate_libadapta_base(theme_data)

        # Write files
        write_file_with_backup(libadapta_dir / 'defaults-light.css', light_css)
        write_file_with_backup(libadapta_dir / 'defaults-dark.css', dark_css)
        write_file_with_backup(libadapta_dir / 'base.css', base_css)

        # Apply GTK theme via gsettings
        self._apply_gtk3_theme(theme_data.name)

        logger.info(f"Created libAdapta theme at: {libadapta_dir}")
        return True

    except Exception as e:
        logger.error(f"Failed to create libAdapta theme: {e}")
        return False

def _apply_via_zorin_marker(self, theme_data: ThemeData) -> bool:
    """
    Create .libadwaita marker file and theme CSS for Zorin patch.

    Directory structure:
        ~/.themes/THEME_NAME/gtk-4.0/
            ├── .libadwaita (marker file)
            ├── gtk.css
            └── gtk-dark.css (if dark variant exists)
    """
    theme_base = Path.home() / '.themes' / theme_data.name
    gtk4_dir = theme_base / 'gtk-4.0'

    try:
        gtk4_dir.mkdir(parents=True, exist_ok=True)

        # Create .libadwaita marker file (empty file)
        marker = gtk4_dir / '.libadwaita'
        marker.touch()
        logger.debug(f"Created Zorin marker: {marker}")

        # Generate complete GTK4 theme CSS
        css_content = self._generate_complete_gtk4_css(theme_data, dark=False)
        write_file_with_backup(gtk4_dir / 'gtk.css', css_content)

        # Generate dark variant if dark colors available
        if theme_data.dark_colors:
            dark_css = self._generate_complete_gtk4_css(theme_data, dark=True)
            write_file_with_backup(gtk4_dir / 'gtk-dark.css', dark_css)

        # Apply GTK theme via gsettings
        self._apply_gtk3_theme(theme_data.name)

        logger.info(f"Created Zorin-compatible theme at: {gtk4_dir}")
        return True

    except Exception as e:
        logger.error(f"Failed to create Zorin theme: {e}")
        return False

def _apply_via_css_injection(self, theme_data: ThemeData) -> bool:
    """
    Apply libadwaita theme via CSS injection (existing method).

    This is the fallback method and works on all systems.
    Writes to: ~/.config/gtk-4.0/gtk.css
    """
    # This is the existing implementation - rename for clarity
    try:
        css_content = self._generate_libadwaita_css(theme_data)
        self.gtk4_config_dir.mkdir(parents=True, exist_ok=True)
        css_file = self.gtk4_config_dir / "gtk.css"
        success = write_file_with_backup(css_file, css_content)

        if success:
            logger.debug(f"Libadwaita CSS injected to: {css_file}")
        return success

    except Exception as e:
        logger.error(f"CSS injection failed: {e}")
        return False
```

**Testing Requirements:**
- Test each application method independently
- Test fallback from LibAdapta/Zorin to CSS injection
- Test marker file creation
- Test directory structure creation
- Verify file contents match expected format

#### Task 3.3: CSS Generation Helpers (30 min)

Add helper methods for complete theme generation:

```python
def _generate_libadapta_colors(self, theme_data: ThemeData, dark: bool = False) -> str:
    """Generate libAdapta color definitions (defaults-light.css / defaults-dark.css)."""
    colors = theme_data.dark_colors if dark and theme_data.dark_colors else theme_data.colors

    css_lines = [
        f"/* LibAdapta color definitions - {'Dark' if dark else 'Light'} mode */",
        f"/* Generated from theme: {theme_data.name} */",
        ""
    ]

    # Map GTK colors to libadwaita names with @define-color
    for gtk_color, adw_color in self.gtk_to_libadwaita_mapping.items():
        if gtk_color in colors:
            css_lines.append(f"@define-color {adw_color} {colors[gtk_color]};")

    return "\n".join(css_lines)

def _generate_libadapta_base(self, theme_data: ThemeData) -> str:
    """Generate libAdapta base.css (widget styling)."""
    css_lines = [
        f"/* LibAdapta base stylesheet */",
        f"/* Theme: {theme_data.name} */",
        "",
        "/* Import default Adapta base as foundation */",
        "@import url('resource:///org/gnome/Adapta/styles/base.css');",
        "",
        "/* Theme-specific overrides can be added here */",
    ]

    # If theme has custom CSS, append it
    if theme_data.css_content:
        css_lines.extend(["", "/* Custom theme CSS */", theme_data.css_content])

    return "\n".join(css_lines)

def _generate_complete_gtk4_css(self, theme_data: ThemeData, dark: bool = False) -> str:
    """Generate complete GTK4 CSS for Zorin patch (gtk.css / gtk-dark.css)."""
    colors = theme_data.dark_colors if dark and theme_data.dark_colors else theme_data.colors

    css_lines = [
        f"/* GTK4 Theme for Zorin libadwaita patch - {'Dark' if dark else 'Light'} mode */",
        f"/* Theme: {theme_data.name} */",
        f"/* Generated by Unified Theming v0.5.0 */",
        "",
        "/* Color Definitions */",
    ]

    # Add all color definitions
    for gtk_color, adw_color in self.gtk_to_libadwaita_mapping.items():
        if gtk_color in colors:
            css_lines.append(f"@define-color {adw_color} {colors[gtk_color]};")

    # Import base Adwaita styles
    css_lines.extend([
        "",
        "/* Import base libadwaita styles */",
        "@import url('resource:///org/gnome/Adwaita/styles/base.css');",
        ""
    ])

    # Add custom CSS if available
    if theme_data.css_content:
        css_lines.extend(["/* Custom Theme CSS */", theme_data.css_content])

    return "\n".join(css_lines)
```

#### Task 3.4: Information Methods (30 min)

Add methods to expose capabilities to users:

```python
def get_libadwaita_capabilities(self) -> Dict[str, Any]:
    """
    Get information about libadwaita theming capabilities on this system.

    Returns:
        Dictionary with mode, coverage, and upgrade recommendations
    """
    coverage_map = {
        'libadapta': 95,
        'zorin-patch': 95,
        'css-injection': 70
    }

    recommendation_map = {
        'libadapta': "Full theme support enabled via LibAdapta",
        'zorin-patch': "Full theme support enabled via Zorin OS patch",
        'css-injection': (
            "Color theming only (70% coverage). For complete theming:\n"
            "  • Install Zorin OS libadwaita patch (recommended)\n"
            "  • Install LibAdapta (Linux Mint compatible)\n"
            "  See: docs/libadwaita_detection_spec.md"
        )
    }

    return {
        'mode': self.libadwaita_mode,
        'coverage_percent': coverage_map[self.libadwaita_mode],
        'full_structural_theming': self.libadwaita_mode != 'css-injection',
        'recommendation': recommendation_map[self.libadwaita_mode],
        'installation_guides': {
            'libadapta': 'https://github.com/xapp-project/libadapta',
            'zorin_patch': 'See libadwaita-patch-feasibility-research.md'
        }
    }

def get_supported_features(self) -> List[str]:
    """Get list of features supported by this handler."""
    base_features = [
        "gtk2_theming",
        "gtk3_theming",
        "gtk4_theming",
    ]

    # Add libadwaita-specific features based on mode
    if self.libadwaita_mode == 'css-injection':
        base_features.extend([
            "libadwaita_colors",
            "libadwaita_css_injection"
        ])
    elif self.libadwaita_mode == 'libadapta':
        base_features.extend([
            "libadwaita_full_theming",
            "libadapta_directories",
            "structural_widget_theming"
        ])
    elif self.libadwaita_mode == 'zorin-patch':
        base_features.extend([
            "libadwaita_full_theming",
            "zorin_marker_files",
            "structural_widget_theming"
        ])

    return base_features
```

### Documentation Deliverable

Create `docs/libadwaita_detection_spec.md`:

```markdown
# LibAdwaita Detection & Adaptation Specification

## Overview
The GTK handler now automatically detects and adapts to enhanced libadwaita theming when available.

## Detection Modes

### 1. LibAdapta Mode
**Detection:** `pkg-config --modversion libadapta-1` succeeds
**Application:** Creates `~/.themes/THEME/libadapta-1.5/` directory structure
**Coverage:** ~95% (full structural theming)
**Files Created:**
- `defaults-light.css` - Light mode colors
- `defaults-dark.css` - Dark mode colors
- `base.css` - Widget styling
- `base-hc.css` - High contrast variant (optional)

### 2. Zorin Patch Mode
**Detection:** Existing `.libadwaita` markers found in system themes
**Application:** Creates `~/.themes/THEME/gtk-4.0/.libadwaita` marker
**Coverage:** ~95% (full structural theming)
**Files Created:**
- `.libadwaita` - Empty marker file for opt-in
- `gtk.css` - Complete theme CSS
- `gtk-dark.css` - Dark variant (if available)

### 3. CSS Injection Mode (Default)
**Detection:** Neither LibAdapta nor Zorin patch detected
**Application:** Injects CSS to `~/.config/gtk-4.0/gtk.css`
**Coverage:** ~70% (colors only)
**Files Created:**
- `gtk.css` - Color variable definitions

## Implementation Details

### Detection Flow
```
GTKHandler.__init__()
  ├─→ _check_libadapta_installed()
  │    └─→ Returns True → mode = 'libadapta'
  ├─→ _check_zorin_patch_available()
  │    └─→ Returns True → mode = 'zorin-patch'
  └─→ Default → mode = 'css-injection'
```

### Application Flow
```
_apply_libadwaita_theme(theme_data)
  ├─→ mode == 'libadapta'
  │    └─→ _apply_via_libadapta()
  │         ├─→ Create libadapta-1.5/ directory
  │         ├─→ Generate color files
  │         └─→ Set GTK theme via gsettings
  │
  ├─→ mode == 'zorin-patch'
  │    └─→ _apply_via_zorin_marker()
  │         ├─→ Create .libadwaita marker
  │         ├─→ Generate complete CSS files
  │         └─→ Set GTK theme via gsettings
  │
  └─→ mode == 'css-injection'
       └─→ _apply_via_css_injection()
            └─→ Inject colors to ~/.config/gtk-4.0/gtk.css
```

## Testing Requirements

### Detection Tests
1. Test `_check_libadapta_installed()` with mocked pkg-config
2. Test `_check_zorin_patch_available()` with/without markers
3. Test fallback to css-injection when both fail
4. Test mode persistence across handler lifecycle

### Application Tests
5. Test LibAdapta directory creation and file contents
6. Test Zorin marker creation and CSS generation
7. Test CSS injection as fallback
8. Test error handling and automatic fallback
9. Test that gsettings is called appropriately in each mode

### Integration Tests
10. Test mode detection affects `get_libadwaita_capabilities()`
11. Test `get_supported_features()` varies by mode
12. Test theme application end-to-end in each mode

## User-Facing Benefits
- **Automatic optimization:** Uses best method available
- **Progressive enhancement:** 70% → 95% when patches available
- **Zero configuration:** Detection is automatic
- **Graceful degradation:** Always falls back to working method
- **Clear guidance:** Users know their current capabilities and upgrade paths
```

### Handoff to Qwen

Create `HANDOFF_DAY3_CLAUDE_TO_QWEN.md`:

```markdown
# Day 3 Handoff: GTK Handler Refactor Complete

## What Was Done (Claude Code - Morning)

### ✅ Completed Refactoring
1. Implemented LibAdapta/Zorin patch detection in `GTKHandler.__init__()`
2. Added three-mode adaptive application system:
   - `_apply_via_libadapta()` - Creates libadapta-1.5/ directories
   - `_apply_via_zorin_marker()` - Creates .libadwaita markers
   - `_apply_via_css_injection()` - Existing CSS injection (renamed)
3. Added helper methods for complete theme generation
4. Added `get_libadwaita_capabilities()` for user information
5. Updated `get_supported_features()` to reflect detected capabilities

### Files Modified
- `unified_theming/handlers/gtk_handler.py` - Main refactoring
- `docs/libadwaita_detection_spec.md` - New technical specification

## What Needs Testing (Qwen Coder - Afternoon)

### New Test File: `tests/test_gtk_handler_libadwaita.py`

This should be a NEW test file specifically for the libadwaita detection/adaptation features.

### Test Coverage Required (25+ tests total)

#### Detection Tests (5 tests)
```python
def test_detect_libadapta_installed(mock_subprocess):
    """Test detection when libAdapta is installed."""
    # Mock pkg-config to return success

def test_detect_zorin_patch_available(tmp_path, monkeypatch):
    """Test detection when Zorin markers exist."""
    # Create fake .libadwaita markers

def test_detect_css_injection_fallback():
    """Test fallback to css-injection when nothing detected."""

def test_detection_caching():
    """Test that mode is detected once and cached."""

def test_detection_with_both_available():
    """Test that libAdapta takes precedence over Zorin."""
```

#### LibAdapta Application Tests (7 tests)
```python
def test_apply_via_libadapta_creates_directory(tmp_path):
    """Test that libadapta-1.5/ directory is created."""

def test_apply_via_libadapta_generates_colors():
    """Test color files are generated correctly."""

def test_apply_via_libadapta_light_dark_variants():
    """Test both light and dark CSS files."""

def test_apply_via_libadapta_skips_if_native_support():
    """Test detection of existing native libAdapta themes."""

def test_apply_via_libadapta_calls_gsettings():
    """Test that GTK theme is set via gsettings."""

def test_apply_via_libadapta_error_handling():
    """Test graceful failure and fallback."""

def test_generate_libadapta_colors():
    """Test _generate_libadapta_colors() helper."""
```

#### Zorin Patch Application Tests (7 tests)
```python
def test_apply_via_zorin_creates_marker(tmp_path):
    """Test .libadwaita marker file creation."""

def test_apply_via_zorin_generates_css():
    """Test gtk.css and gtk-dark.css generation."""

def test_apply_via_zorin_complete_css_content():
    """Test generated CSS contains all required elements."""

def test_apply_via_zorin_calls_gsettings():
    """Test gsettings is called to set theme."""

def test_apply_via_zorin_error_handling():
    """Test error recovery and fallback."""

def test_apply_via_zorin_without_dark_colors():
    """Test behavior when theme has no dark variant."""

def test_generate_complete_gtk4_css():
    """Test _generate_complete_gtk4_css() helper."""
```

#### CSS Injection Tests (3 tests)
```python
def test_apply_via_css_injection():
    """Test existing CSS injection method still works."""

def test_css_injection_as_fallback():
    """Test automatic fallback to CSS injection on errors."""

def test_css_injection_file_location():
    """Test CSS is written to ~/.config/gtk-4.0/gtk.css."""
```

#### Information Method Tests (3 tests)
```python
def test_get_libadwaita_capabilities_libadapta_mode():
    """Test capabilities dict in libadapta mode."""

def test_get_libadwaita_capabilities_zorin_mode():
    """Test capabilities dict in zorin-patch mode."""

def test_get_libadwaita_capabilities_css_injection_mode():
    """Test capabilities dict in css-injection mode."""
```

### Existing GTK Handler Tests
The existing `tests/test_gtk_handler.py` should still pass. If any tests break due to refactoring, fix them.

### Testing Tips
1. **Use tmp_path fixture** for filesystem operations
2. **Mock subprocess.run** for pkg-config calls
3. **Mock gsettings** calls to avoid system modifications
4. **Parametrize tests** where possible (e.g., light/dark variants)
5. **Test isolation:** Each test should be independent

### Target Coverage
- **New libadwaita code:** 100% coverage (it's all new)
- **Overall gtk_handler.py:** 42% → 70%+ (target now increased)
- **Total new tests:** 25+ (in addition to existing tests)

## Success Criteria
- [ ] All 25+ new libadwaita tests passing
- [ ] Existing GTK handler tests still pass
- [ ] GTK handler coverage ≥ 70%
- [ ] No regression in existing functionality
- [ ] Code tagged: `week3-day3-libadwaita-complete`

## Time Estimate
- Setup: 30 min
- Detection tests: 60 min
- LibAdapta tests: 90 min
- Zorin tests: 90 min
- Info method tests: 30 min
- Fix any breakage: 30 min
- **Total:** 5.5 hours

Good luck! 🚀
```

---

## Agent: Qwen Coder (Afternoon)
**Duration:** 6 hours
**Role:** GTK Handler Testing Specialist

### Objectives
1. Implement tests for NEW libadwaita detection/adaptation code
2. Test existing GTK2/GTK3/GTK4 theme application
3. Achieve 70%+ coverage on gtk_handler.py (increased target)
4. Ensure no regression in existing functionality

### Deliverables
- [x] `tests/test_gtk_handler_libadwaita.py` - NEW test file (25+ tests)
- [x] Updated `tests/test_gtk_handler.py` - Fix any breakage from refactor
- [x] GTK handler coverage: 42% → 70%+
- [x] 45+ total GTK tests passing (20 existing + 25 new)
- [x] `HANDOFF_DAY3_QWEN_TO_OPENCODE.md`

### Test Scenarios

**See `HANDOFF_DAY3_CLAUDE_TO_QWEN.md` for complete test specifications**

#### NEW Priority Areas (LibAdwaita Detection - P0)
1. **Detection System** - 5 tests
   - LibAdapta detection via pkg-config
   - Zorin patch detection via markers
   - Fallback to css-injection
   - Mode caching and precedence

2. **LibAdapta Application** - 7 tests
   - Directory structure creation (~/.themes/THEME/libadapta-1.5/)
   - Color file generation (defaults-light.css, defaults-dark.css)
   - Base CSS generation
   - Native theme detection
   - gsettings integration
   - Error handling

3. **Zorin Patch Application** - 7 tests
   - Marker file creation (~/.themes/THEME/gtk-4.0/.libadwaita)
   - Complete CSS generation (gtk.css, gtk-dark.css)
   - File content validation
   - gsettings integration
   - Error handling

4. **CSS Injection** - 3 tests
   - Existing method validation
   - Fallback behavior
   - File location verification

5. **Information Methods** - 3 tests
   - `get_libadwaita_capabilities()` in each mode
   - `get_supported_features()` variation

#### EXISTING Priority Areas (Ensure no regression - P1)
6. **Theme File Writing**
   - GTK2: ~/.gtkrc-2.0
   - GTK3: ~/.config/gtk-3.0/settings.ini
   - GTK4: ~/.config/gtk-4.0/gtk.css

7. **Existing Libadwaita CSS** (now _apply_via_css_injection)
   - Color extraction from theme
   - CSS variable generation

8. **Color Mapping**
   - GTK to libadwaita color translation
   - All semantic colors covered

### EOD Success Criteria
- ✅ 25+ NEW libadwaita detection/adaptation tests passing
- ✅ 20+ existing GTK handler tests still passing (no regression)
- ✅ GTK handler coverage ≥ 70% (up from 42%)
- ✅ LibAdapta/Zorin integration validated
- ✅ Git commit tagged: `week3-day3-libadwaita-complete`

---

## Agent: Opencode AI (Evening)
**Duration:** 2 hours  
**Role:** Mid-Week Progress Assessment

### Objectives
1. Validate Day 3 GTK handler tests
2. Generate mid-week progress report (Days 1-3)
3. Assess trajectory toward 72-75% goal
4. Identify risks for Days 4-5

### Deliverables
- [x] `reports/week3_day3_coverage_report.md`
- [x] `reports/week3_midweek_assessment.md` - Critical progress check
- [x] `HANDOFF_DAY3_COMPLETE.md`

### Mid-Week Assessment Focus

**Key Questions:**
1. Are we on track for 72-75% by EOW?
2. Current coverage after 3 days?
3. What's the gap to target?
4. Do we need to adjust Day 4-5 plans?

**Deliverable:** `reports/week3_midweek_assessment.md`

```markdown
# Week 3 Mid-Week Assessment (Days 1-3)
**Date:** October 24, 2025
**Agent:** Opencode AI

## Progress Summary

| Metric | Start | Day 1 | Day 2 | Day 3 | Target EOW |
|--------|-------|-------|-------|-------|------------|
| Coverage | 48% | [X]% | [X]% | [X]% | 72-75% |
| Tests | 149 | [X] | [X] | [X] | 200+ |

## Coverage by Focus Area

### Day 1: Integration Testing
- Integration tests: 0% → 100% ✅
- Overall impact: +[X]%

### Day 2: CLI Testing
- CLI commands: 0% → [X]% [✅/⚠️]
- Overall impact: +[X]%

### Day 3: GTK Handler
- GTK handler: 42% → [X]% [✅/⚠️]
- Overall impact: +[X]%

## Trajectory Analysis

**Current Pace:** +[X]% per day
**Required Pace:** +[Y]% per day to reach 72%

**Status:** [ON TRACK / AT RISK / OFF TRACK]

## Days 4-5 Plan Assessment

**Remaining Coverage Needed:** [X]% (from current to 72%)

**Day 4-5 Targets:**
- Qt handler: 24% → 60%+ (need +36%)
- Validation utils: 43% → 60%+ (need +17%)
- Other gaps: [X]%

**Feasibility:** [REALISTIC / AGGRESSIVE / NEED ADJUSTMENT]

## Risks Identified

[List any risks or blockers]

## Recommendations

[Specific actions for Days 4-5]

## GO/NO-GO for Day 4

**Decision:** [GO / ADJUST PLAN]
```

---

# DAY 4 (October 25, 2025)

## Daily Stand-Up Summary (All Agents)
**Time:** 08:00 - 08:15 (15 min)

```markdown
# Week 3 Day 4 Stand-Up Report
**Date:** October 25, 2025 08:00

## Yesterday (Day 3) - GTK Handler Testing

### Accomplishments ✅
- GTK handler tests implemented (Qwen Coder)
- GTK coverage: 42% → [X]%
- [X] tests added
- Coverage: [X]% → [Y]%
- Mid-week assessment completed ✅

### Mid-Week Assessment Results 🔍
- **Current coverage:** [X]%
- **Gap to 72% target:** [Y]%
- **Trajectory:** [ON TRACK / NEEDS ADJUSTMENT]
- **Day 4-5 plan:** [CONFIRMED / ADJUSTED]

## Today (Day 4) - Qt Handler Testing

### Objectives 🎯
- Qt test architecture (Claude Code - Morning)
- Qt handler tests (Qwen Coder - Full Day)
- Target: qt_handler.py 24% → 60%+
- Focus: kdeglobals (priority), Kvantum (if time)
- Code review (Claude Code)
- Validation (Opencode AI - Evening)

### Success Criteria ✅
- [ ] Qt handler ≥ 60% coverage
- [ ] 15+ tests passing
- [ ] kdeglobals generation validated
- [ ] Code review approved

**Coverage Projection:** [X]% after Day 4
**Remaining for Day 5:** [Y]% to reach 72%
```

---

## Agent: Claude Code (Morning)
**Duration:** 2 hours  
**Role:** Qt Test Architect

### Objectives
1. Review Day 3 results and mid-week assessment
2. Design Qt handler test strategy
3. Create test specifications for Qt testing
4. Adjust Day 4-5 plan if needed based on mid-week assessment

### Deliverables
- [x] `docs/qt_test_specification.md`
- [x] `HANDOFF_DAY4_CLAUDE_TO_QWEN.md`
- [x] Adjusted plan if needed

### Qt Testing Complexity Assessment

**Qt Handler has two paths:**
1. **kdeglobals** (simpler) - INI-style config
2. **Kvantum** (complex) - SVG-based theming

**Recommendation:** Prioritize kdeglobals, defer Kvantum if time-constrained

---

## Agent: Qwen Coder (Full Day)
**Duration:** 6 hours  
**Role:** Qt Handler Testing Specialist

### Objectives
1. Implement Qt handler tests
2. Focus on kdeglobals generation and color translation
3. Achieve 60%+ coverage on qt_handler.py
4. Defer Kvantum if necessary to meet time constraints

### Deliverables
- [x] `tests/test_qt_handler.py` - Qt handler tests
- [x] Qt handler coverage: 24% → 60%+
- [x] 15+ Qt-specific tests passing
- [x] `HANDOFF_DAY4_QWEN_TO_OPENCODE.md`

### Test Scenarios

#### Priority Areas
1. **kdeglobals Generation** (P0)
   - Color section [ColorScheme]
   - GTK → Qt color translation
   - File format validation
   - Path: ~/.config/kdeglobals

2. **Color Translation** (P0)
   - theme_bg_color → window_bg_color
   - theme_fg_color → window_fg_color
   - theme_selected_bg_color → highlight_bg_color
   - Hex format consistency

3. **Availability Detection** (P1)
   - Check if Qt installed
   - Check qt5ct/qt6ct availability
   - Graceful degradation

4. **Kvantum Support** (P2 - Stretch)
   - Basic Kvantum directory structure
   - Defer SVG generation if needed

### Realistic Target
- **kdeglobals:** 80%+ coverage
- **Kvantum:** 30% coverage (basic structure)
- **Overall Qt handler:** 60%+ coverage

### EOD Success Criteria
- ✅ 15+ Qt handler tests passing
- ✅ Qt handler coverage ≥ 60%
- ✅ kdeglobals generation validated
- ✅ Git commit tagged: `week3-day4-complete`

---

## Agent: Opencode AI (Evening)
**Duration:** 2 hours  
**Role:** Day 4 Validation & Day 5 Planning

### Objectives
1. Validate Qt handler tests
2. Assess overall Week 3 progress (Days 1-4)
3. Calculate final gap for Day 5
4. Create detailed Day 5 plan

### Deliverables
- [x] `reports/week3_day4_coverage_report.md`
- [x] `reports/week3_day5_plan.md` - Final day tactical plan
- [x] `HANDOFF_DAY4_COMPLETE.md`

### Day 5 Planning Focus

**Output:** `reports/week3_day5_plan.md`

```markdown
# Week 3 Day 5 Tactical Plan
**Date:** October 25, 2025 EOD
**Agent:** Opencode AI
**Purpose:** Final push to 72-75% coverage

## Current Status (After Day 4)

**Coverage:** [X]%
**Gap to 72% target:** [Y]%
**Gap to 75% stretch:** [Z]%

## Coverage Gaps Identified

| Module | Current | Target | Gap | Priority |
|--------|---------|--------|-----|----------|
| utils/validation.py | 43% | 60% | +17% | P1 |
| core/parser.py | 63% | 70% | +7% | P2 |
| handlers/snap_handler.py | 76% | 80% | +4% | P3 |

## Day 5 Strategy

**Agent:** Qwen Coder (full day)

**Option 1: Target 72% (Conservative)**
- Focus on validation.py (+17%)
- Add parser.py edge cases (+7%)
- Quick wins in other modules (+2-3%)

**Option 2: Target 75% (Stretch)**
- Everything in Option 1
- Plus snap handler polish (+4%)
- Plus additional integration test edge cases (+3%)

**Recommendation:** [Option 1 / Option 2]

## Day 5 Test Priorities

### Priority 1: Validation Utils (60 min)
**File:** `tests/test_validation_complete.py`
**Target:** 43% → 60%+

Tests needed:
- [List specific tests]

### Priority 2: Parser Edge Cases (45 min)
**File:** Add to `tests/test_parser.py`
**Target:** 63% → 70%+

Tests needed:
- [List specific tests]

### Priority 3: Quick Wins (60 min)
**Targets:**
- [Identify specific quick win modules]

### Stretch: Additional Coverage (60 min)
**If ahead of schedule:**
- [List stretch goals]

## Success Criteria for Day 5 / Week 3

**Minimum Viable (72%):**
- [x] Validation: ≥60%
- [x] Parser: ≥70%
- [x] Overall: ≥72%

**Target (75%):**
- [x] All minimum criteria
- [x] Snap handler: ≥80%
- [x] Overall: ≥75%

**Stretch (77-78%):**
- [x] All target criteria
- [x] Additional integration edge cases
- [x] Overall: ≥77%

## Risk Mitigation

**If Day 5 falling short:**
1. Prioritize validation.py (highest impact)
2. Accept 70% overall if tests are high quality
3. Document remaining gaps for Week 4

**Quality over Quantity:**
- 72% with robust tests > 75% with flaky tests
- Phase 3 unlocked at 70%+ anyway
```

---

# DAY 5 (October 26, 2025)

## Daily Stand-Up Summary (All Agents)
**Time:** 08:00 - 08:15 (15 min)

```markdown
# Week 3 Day 5 Stand-Up Report
**Date:** October 26, 2025 08:00

## Yesterday (Day 4) - Qt Handler Testing

### Accomplishments ✅
- Qt test architecture designed (Claude Code)
- Qt handler tests implemented (Qwen Coder)
- Qt coverage: 24% → [X]%
- Coverage: [X]% → [Y]%
- Code review approved

## Today (Day 5) - Gap Closure & Week Completion

### Current Status 🔍
- **Current coverage:** [X]%
- **Target:** 72%
- **Gap:** [Y]%
- **Time available:** 6 hours

### Pre-Defined Priorities (Concrete Plan)

Based on realistic Day 4 completion scenarios:

**SCENARIO A: If coverage ≥ 68% after Day 4 (ON TRACK)**
→ Focus on polishing and reaching 72%+

**SCENARIO B: If coverage 64-67% after Day 4 (SLIGHT GAP)**
→ Focus on highest-impact modules to reach 72%

**SCENARIO C: If coverage < 64% after Day 4 (SIGNIFICANT GAP)**
→ Accept 70% as success, focus on quality
```

---

## Day 5 Execution Plan (Pre-Defined)

### SCENARIO A: Coverage ≥ 68% (Need +4% for 72%)

**Agent:** Qwen Coder (Full Day)

#### Priority 1: Validation Utils (90 min) - HIGH IMPACT
**File:** `tests/test_validation_complete.py`
**Target:** validation.py 43% → 60%+ (+17% module coverage)
**Impact:** +1.5-2% overall coverage

**Pre-defined tests:**
1. `test_validate_theme_complete_theme` - Validate fully formed theme
2. `test_validate_theme_missing_gtk2` - Missing GTK2 component
3. `test_validate_theme_missing_colors` - Incomplete color definitions
4. `test_validate_theme_invalid_paths` - Invalid file paths
5. `test_validate_color_hex_formats` - Various hex color formats (#RGB, #RRGGBB, #RRGGBBAA)
6. `test_validate_color_named_colors` - Named colors (red, blue, etc.)
7. `test_validate_color_rgb_format` - RGB format (rgb(255,0,0))
8. `test_validate_compatibility_all_handlers` - Check all handler compatibility
9. `test_validate_compatibility_partial` - Some handlers compatible
10. `test_validate_compatibility_none` - No compatible handlers

#### Priority 2: Parser Edge Cases (60 min) - MEDIUM IMPACT
**File:** `tests/test_parser.py` (extend existing)
**Target:** parser.py 63% → 70%+ (+7% module coverage)
**Impact:** +1% overall coverage

**Pre-defined tests:**
1. `test_parse_theme_with_comments` - CSS with comments
2. `test_parse_theme_malformed_css` - Invalid CSS syntax
3. `test_parse_theme_missing_index` - No index.theme file
4. `test_parse_theme_empty_directory` - Empty theme directory
5. `test_parse_theme_symlinks` - Theme with symlinked files
6. `test_discover_themes_nested` - Themes in subdirectories
7. `test_discover_themes_permissions` - Unreadable theme directories

#### Priority 3: Polish Existing Tests (45 min) - STABILITY
**Focus:** Fix any flaky tests, improve test quality
**Impact:** +0.5% overall coverage

**Tasks:**
- Run tests 10 times, fix any intermittent failures
- Add missing edge cases to existing tests
- Improve test documentation

#### Priority 4: Quick Wins (45 min) - BONUS
**If ahead of schedule:**
- File utils: 23% → 40%+ (add 5-7 tests)
- Logging config: 37% → 50%+ (add 3-5 tests)

**Expected Day 5 Outcome:** 68% → 72-73% ✅

---

### SCENARIO B: Coverage 64-67% (Need +5-8% for 72%)

**Agent:** Qwen Coder (Full Day)

#### Priority 1: Validation Utils (90 min) - CRITICAL
**Same as Scenario A** - Must complete all 10 tests
**Impact:** +1.5-2% overall coverage

#### Priority 2: File Utils (75 min) - HIGH IMPACT
**File:** `tests/test_file_utils_complete.py`
**Target:** file.py 23% → 50%+ (+27% module coverage)
**Impact:** +2% overall coverage

**Pre-defined tests:**
1. `test_ensure_directory_exists` - Create directory if missing
2. `test_ensure_directory_already_exists` - Directory already present
3. `test_ensure_directory_permission_denied` - Cannot create directory
4. `test_copy_file_success` - Copy file successfully
5. `test_copy_file_overwrite` - Overwrite existing file
6. `test_copy_file_source_not_found` - Source file missing
7. `test_read_config_file_ini` - Read INI format config
8. `test_read_config_file_json` - Read JSON format config
9. `test_write_config_file_backup` - Backup before writing
10. `test_atomic_write_success` - Write file atomically

#### Priority 3: Parser Edge Cases (45 min) - MEDIUM IMPACT
**Same as Scenario A** - 7 parser tests
**Impact:** +1% overall coverage

#### Priority 4: Integration Edge Cases (30 min) - STABILITY
**File:** `tests/test_integration.py` (extend)
**Add 2-3 additional integration edge cases**
**Impact:** +0.5% overall coverage

**Expected Day 5 Outcome:** 64-67% → 71-73% ✅ (Accept 71% as success)

---

### SCENARIO C: Coverage < 64% (Need +8%+ for 72%)

**Decision:** Accept 70% as Week 3 success, prioritize quality over quantity

**Agent:** Qwen Coder (Full Day)

#### Priority 1: Critical Path Validation (2 hours) - QUALITY FOCUS
**Focus:** Ensure all critical workflows are tested, even if coverage is lower

**Tasks:**
1. Run all existing tests 10 times - ensure no flakiness
2. Review integration tests - add missing critical edge cases
3. Review CLI tests - ensure all user-facing commands covered
4. Review handler tests - validate error handling paths

**Impact:** +0-1% coverage, but HIGH QUALITY

#### Priority 2: Validation Utils (90 min) - MUST HAVE
**Same as Scenarios A & B** - Complete all 10 validation tests
**Impact:** +1.5-2% overall coverage

#### Priority 3: Highest ROI Tests (90 min) - TARGETED
**Identify highest-impact untested code paths**

Using coverage report, find:
- Largest untested functions
- Critical error handling paths
- User-facing functionality

Add 10-15 targeted tests for maximum impact.
**Impact:** +2-3% overall coverage

**Expected Day 5 Outcome:** <64% → 68-70% ⚠️ (Below target, but ACCEPTABLE for Phase 3)

---

## Day 5 Success Criteria (Scenario-Dependent)

### Minimum Viable (Any Scenario)
- [ ] Validation utils: ≥ 60% coverage
- [ ] All tests passing with no flakiness
- [ ] Overall coverage: ≥ 70%
- [ ] Code quality high (no TODOs, proper docs)

### Target (Scenarios A & B)
- [ ] Overall coverage: ≥ 72%
- [ ] Parser: ≥ 70% coverage
- [ ] File utils: ≥ 40% coverage (Scenario B)

### Stretch (Scenario A only)
- [ ] Overall coverage: ≥ 73%
- [ ] All modules ≥ 60% coverage
- [ ] Additional integration edge cases

---

## Agent: Qwen Coder (Full Day)
**Duration:** 6 hours  
**Role:** Gap Closure Specialist

### Objectives
1. Execute Day 5 tactical plan from Opencode AI
2. Fill identified coverage gaps
3. Achieve 72-75% overall coverage
4. Ensure all tests passing and stable

### Deliverables
- [x] `tests/test_validation_complete.py` - Validation utils tests
- [x] Additional parser tests in `tests/test_parser.py`
- [x] Any other gap-filling tests identified
- [x] Overall coverage: 72-75%
- [x] `HANDOFF_DAY5_QWEN_TO_OPENCODE.md`

### Task Execution

#### Morning (3 hours)
1. **Validation Utils Testing** (90 min)
   - Implement comprehensive validation tests
   - Target: 43% → 60%+

2. **Parser Edge Cases** (60 min)
   - Add missing parser tests
   - Target: 63% → 70%+

3. **Quick Win Modules** (30 min)
   - Identify and add quick tests
   - Target: +2-3% overall

#### Afternoon (3 hours)
4. **Test Stabilization** (60 min)
   - Fix any flaky tests
   - Ensure all tests pass consistently

5. **Stretch Goals** (60 min) - If ahead of schedule
   - Snap handler polish
   - Additional integration edge cases
   - Documentation improvements

6. **Final Validation** (60 min)
   - Run full test suite multiple times
   - Verify coverage reports
   - Prepare comprehensive handoff

### EOD Success Criteria
- ✅ Overall coverage ≥ 72%
- ✅ All priority modules meet targets
- ✅ No flaky tests
- ✅ Test pass rate ≥ 98%
- ✅ Git commit tagged: `week3-complete`

---

## Agent: Opencode AI (Evening)
**Duration:** 3 hours  
**Role:** Week 3 Completion & Phase 3 Readiness Assessment

### Objectives
1. Validate Week 3 final results
2. Generate comprehensive week completion report
3. Assess Phase 3 (GUI) readiness
4. Create Week 4 handoff document

### Deliverables
- [x] `reports/week3_final_coverage_report.md` - Comprehensive analysis
- [x] `reports/week3_completion_assessment.md` - Week summary
- [x] `reports/phase3_readiness_checklist.md` - GO/NO-GO decision
- [x] `WEEK3_COMPLETE_HANDOFF_TO_CLAUDE.md` - Handoff for Week 4

### Tasks Breakdown

#### Task 1: Final Coverage Validation (60 min)

```bash
# Run full test suite
pytest -v --cov=src --cov-report=html --cov-report=term-missing

# Generate detailed reports
pytest --cov=src --cov-report=json
pytest --cov=src --cov-report=xml

# Check for flakiness
for i in {1..10}; do
    pytest --tb=no -q
done

# Performance check
pytest --durations=20
```

**Output:** `reports/week3_final_coverage_report.md`

```markdown
# Week 3 Final Coverage Report
**Date:** October 26, 2025 23:00
**Agent:** Opencode AI
**Status:** Week 3 COMPLETE

## Executive Summary

| Metric | Week Start | Week End | Delta | Target | Status |
|--------|------------|----------|-------|--------|--------|
| Coverage | 48% | [X]% | +[Y]% | 72-75% | [✅/⚠️/❌] |
| Total Tests | 149 | [X] | +[Y] | 200+ | [✅/⚠️] |
| Pass Rate | 99.3% | [X]% | [Y] | ≥98% | [✅/⚠️] |

## Coverage by Module (Final)

| Module | Week Start | Week End | Target | Status |
|--------|------------|----------|--------|--------|
| **Core Modules** |
| manager.py | 93% | [X]% | 93%+ | [✅] |
| config.py | 75% | [X]% | 80% | [✅/⚠️] |
| parser.py | 63% | [X]% | 70% | [✅/⚠️] |
| **Handlers** |
| gtk_handler.py | 42% | [X]% | 65% | [✅/⚠️] |
| qt_handler.py | 24% | [X]% | 60% | [✅/⚠️] |
| flatpak_handler.py | 100% | [X]% | 100% | [✅] |
| snap_handler.py | 76% | [X]% | 80% | [✅/⚠️] |
| **Utilities** |
| color.py | 86% | [X]% | 90% | [✅] |
| validation.py | 43% | [X]% | 60% | [✅/⚠️] |
| file.py | 23% | [X]% | 50% | [⚠️] |
| **CLI** |
| commands.py | 0% | [X]% | 60% | [✅/⚠️] |
| **Integration** |
| test_integration.py | 0% | 100% | 100% | [✅] |

## Test Suite Health

**Total Tests:** [X]
**Passing:** [X]
**Failing:** [X]
**Skipped:** [X]
**Pass Rate:** [X]%

**Flakiness Test Results:**
- 10 consecutive runs: [X/10 passed all tests]
- Flaky tests identified: [None/List]

**Performance:**
- Fastest test: [X]s
- Slowest test: [X]s
- Total suite time: [X]s

## Week 3 Test Additions

### Day 1: Integration Tests
- Tests added: 5
- Coverage impact: +[X]%
- Files: test_integration.py

### Day 2: CLI Tests
- Tests added: [X]
- Coverage impact: +[X]%
- Files: test_cli_commands.py

### Day 3: GTK Handler Tests
- Tests added: [X]
- Coverage impact: +[X]%
- Files: test_gtk_handler.py

### Day 4: Qt Handler Tests
- Tests added: [X]
- Coverage impact: +[X]%
- Files: test_qt_handler.py

### Day 5: Gap Closure
- Tests added: [X]
- Coverage impact: +[X]%
- Files: test_validation_complete.py, others

**Total New Tests:** [X]
**Total Coverage Gain:** +[Y]%

## Coverage Gaps Remaining

[List any modules still below target with justification]

## Quality Metrics

**Code Quality:**
- Black formatting: [PASS/FAIL]
- Flake8 linting: [PASS/FAIL]
- MyPy type checking: [PASS/FAIL]

**Test Quality:**
- All tests have docstrings: [YES/NO]
- Proper use of fixtures: [YES/NO]
- No hardcoded paths: [YES/NO]
- Isolated test environment: [YES/NO]

## Week 3 Achievement Summary

**Goals Met:**
- [x] Integration testing complete
- [x] CLI testing complete
- [x] Handler testing complete
- [x] Overall coverage ≥72%

**Goals Partially Met:**
- [List any partial achievements]

**Goals Not Met:**
- [List any missed goals with explanation]

## Conclusion

Week 3 Status: [SUCCESS / PARTIAL SUCCESS / NEEDS WORK]

Coverage achieved: [X]%
Target was: 72-75%
Result: [EXCEEDED / MET / BELOW]

Phase 3 (GUI) readiness: [READY / NOT READY]
```

#### Task 2: Phase 3 Readiness Assessment (45 min)

**Output:** `reports/phase3_readiness_checklist.md`

```markdown
# Phase 3 (GUI Development) Readiness Checklist
**Date:** October 26, 2025
**Agent:** Opencode AI
**Assessment:** GO / NO-GO

## Minimum Requirements for Phase 3 Start

### Coverage Requirements
- [ ] Overall coverage ≥ 70% (Minimum threshold for Phase 3)
- [ ] Target coverage 72% (Strong recommendation)
- [ ] Core modules ≥ 80% coverage
- [ ] All handlers ≥ 50% coverage
- [ ] Integration tests implemented and passing
- [ ] CLI tests implemented and passing

**Status:** [PASS / FAIL]
**Actual Coverage:** [X]%
**Assessment:** [EXCEEDS / MEETS / BELOW] threshold

**Decision Matrix:**
- ≥72%: Strong GO for Phase 3 ✅
- 70-71%: Conditional GO (acceptable, proceed with caution) ⚠️
- <70%: NO-GO (additional testing needed before Phase 3) ❌

### Test Quality Requirements
- [ ] Test pass rate ≥ 95%
- [ ] No known critical bugs
- [ ] No flaky tests in core functionality
- [ ] All tests properly isolated
- [ ] Comprehensive integration test coverage

**Status:** [PASS / FAIL]

### Functionality Requirements
- [ ] Theme discovery works reliably
- [ ] Theme application works across handlers
- [ ] Backup/restore validated
- [ ] Error handling tested
- [ ] Rollback mechanism validated

**Status:** [PASS / FAIL]

### Infrastructure Requirements
- [ ] Git history clean and tagged
- [ ] Documentation up to date
- [ ] Development environment stable
- [ ] No known build issues
- [ ] CI/CD foundations in place
- [ ] All daily stand-ups completed and documented
- [ ] All code reviews completed
- [ ] All handoffs properly documented

**Status:** [PASS / FAIL]

**Stand-up Completion:** [X/5] days
**Code Reviews Completed:** [X/5] days
**Handoff Quality:** [Excellent / Good / Needs Improvement]

## Overall Assessment

**Total Score:** [X] / 20 requirements met

**GO / NO-GO Decision:** [GO / NO-GO]

### If GO:
**Justification:**
[Explain why ready for Phase 3]

**Recommended Week 4 Actions:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

### If NO-GO:
**Blockers:**
[List critical blockers]

**Remediation Plan:**
[Steps needed before Phase 3]

**Estimated Additional Time:**
[Time needed to reach GO status]

## Week 4 Recommendations

[Specific guidance for starting GUI development]
```

#### Task 3: Week 3 Completion Assessment (45 min)

**Output:** `reports/week3_completion_assessment.md`

```markdown
# Week 3 Completion Assessment
**Date:** October 26, 2025
**Agent:** Opencode AI

## Week 3 Objectives Review

### Planned Objectives
1. Implement integration tests (Day 1-2)
2. Implement CLI tests (Day 2-3)
3. Implement GTK handler tests (Day 3)
4. Implement Qt handler tests (Day 4)
5. Fill coverage gaps (Day 5)
6. Achieve 72-75% overall coverage

### Actual Achievements

[Check off completed items]

## Daily Performance Analysis

### Day 1: Integration Testing
**Target:** Integration tests implemented
**Result:** [EXCEEDED / MET / BELOW]
**Coverage Impact:** +[X]%
**Key Achievements:** [List]
**Challenges:** [List]

### Day 2: CLI Testing
**Target:** CLI 0% → 60%
**Result:** [EXCEEDED / MET / BELOW]
**Coverage Impact:** +[X]%
**Key Achievements:** [List]
**Challenges:** [List]

### Day 3: GTK Handler Testing
**Target:** GTK 42% → 65%
**Result:** [EXCEEDED / MET / BELOW]
**Coverage Impact:** +[X]%
**Key Achievements:** [List]
**Challenges:** [List]

### Day 4: Qt Handler Testing
**Target:** Qt 24% → 60%
**Result:** [EXCEEDED / MET / BELOW]
**Coverage Impact:** +[X]%
**Key Achievements:** [List]
**Challenges:** [List]

### Day 5: Gap Closure
**Target:** Fill remaining gaps to 72%+
**Result:** [EXCEEDED / MET / BELOW]
**Coverage Impact:** +[X]%
**Key Achievements:** [List]
**Challenges:** [List]

## Multi-Agent Workflow Performance

### Claude Code (Architect)
**Tasks:** Test design, specifications, documentation
**Performance:** [Excellent / Good / Needs Improvement]
**Strengths:** [List]
**Areas for Improvement:** [List]

### Qwen Coder (Implementation)
**Tasks:** Test implementation, code writing
**Performance:** [Excellent / Good / Needs Improvement]
**Strengths:** [List]
**Areas for Improvement:** [List]

### Opencode AI (QA & Integration)
**Tasks:** Validation, coverage analysis, reporting
**Performance:** [Excellent / Good / Needs Improvement]
**Strengths:** [List]
**Areas for Improvement:** [List]

## Lessons Learned

### What Worked Well
1. [Lesson 1]
2. [Lesson 2]
3. [Lesson 3]

### What Could Be Improved
1. [Improvement 1]
2. [Improvement 2]
3. [Improvement 3]

### Recommendations for Future Weeks
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## Week 3 Grade

**Coverage Target:** 72-75%
**Coverage Achieved:** [X]%
**Grade:** [A / B / C / D / F]

**Overall Week 3 Status:** [EXCELLENT / GOOD / ACCEPTABLE / NEEDS WORK]
```

#### Task 4: Create Week 4 Handoff (30 min)

**Output:** `WEEK3_COMPLETE_HANDOFF_TO_CLAUDE.md`

```markdown
# Week 3 Complete: Handoff to Week 4 (GUI Development)
**Date:** October 26, 2025 EOD
**From:** Opencode AI (Week 3 Completion)
**To:** Claude Code (Week 4 GUI Planning)
**Status:** Week 3 [COMPLETE / INCOMPLETE]

---

## Executive Summary

**Week 3 Goal:** Achieve 72-75% coverage through integration, CLI, and handler testing
**Result:** [X]% coverage achieved ([EXCEEDED / MET / BELOW] target)

**Phase 3 Readiness:** [READY / NOT READY]
**Recommendation:** [PROCEED TO GUI / ADDITIONAL TESTING NEEDED]

---

## Week 3 Final Metrics

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Coverage | 72-75% | [X]% | [✅/⚠️/❌] |
| Tests Added | 80+ | [X] | [✅/⚠️] |
| Pass Rate | ≥98% | [X]% | [✅/⚠️] |
| Integration | Complete | [✅/⚠️] | [✅/⚠️] |
| CLI | 60%+ | [X]% | [✅/⚠️] |
| GTK | 65%+ | [X]% | [✅/⚠️] |
| Qt | 60%+ | [X]% | [✅/⚠️] |

---

## Test Suite Summary

**Total Tests:** [X] (was 149)
**New Tests Added:** [X]
**All Tests Passing:** [YES/NO]
**Flaky Tests:** [None/List]

**Test Categories:**
- Integration tests: 5 tests (100% coverage)
- CLI tests: [X] tests ([Y]% coverage)
- GTK handler tests: [X] tests ([Y]% coverage)
- Qt handler tests: [X] tests ([Y]% coverage)
- Utility tests: [X] tests ([Y]% coverage)

---

## Coverage by Module (Final State)

### Core Modules (Target: ≥80%)
- manager.py: [X]% [✅/⚠️]
- config.py: [X]% [✅/⚠️]
- parser.py: [X]% [✅/⚠️]
- types.py: [X]% [✅]

### Handlers (Target: ≥60%)
- gtk_handler.py: [X]% [✅/⚠️]
- qt_handler.py: [X]% [✅/⚠️]
- flatpak_handler.py: [X]% [✅]
- snap_handler.py: [X]% [✅/⚠️]

### Utilities (Target: ≥60%)
- color.py: [X]% [✅]
- validation.py: [X]% [✅/⚠️]
- file.py: [X]% [⚠️]

### CLI (Target: ≥60%)
- commands.py: [X]% [✅/⚠️]

---

## Known Issues / Technical Debt

[List any known issues that should be addressed]

---

## Week 4 (GUI Development) Readiness

### Phase 3 Prerequisites
- [x] Coverage ≥ 70%: [YES/NO]
- [x] Core functionality validated: [YES/NO]
- [x] Integration tests passing: [YES/NO]
- [x] No critical bugs: [YES/NO]

**GO/NO-GO for Phase 3:** [GO / NO-GO]

### If GO - Week 4 Plan

**Week 4 Focus:** Qt6 GUI Development (Days 1-5)

**Agent Assignments:**
- **Day 1-2:** Claude Code - GUI architecture and UI/UX design
- **Day 3-4:** Qwen Coder - Main window and theme browser implementation
- **Day 5:** Qwen Coder - Backend integration
- **Evening:** Opencode AI - GUI testing and validation

**Week 4 Deliverables:**
- Qt6 GUI application functional
- Theme browser with preview
- Apply button working
- Backend integration complete

**Week 4 Success Criteria:**
- GUI launches without errors
- User can list and apply themes from GUI
- No regressions in CLI functionality

### If NO-GO - Additional Testing Needed

**Blockers:**
[List critical blockers]

**Required Actions:**
[List actions needed before Phase 3]

---

## Handoff Documents Available

All Week 3 documentation is in place:
- [x] Day 1 completion: HANDOFF_DAY1_COMPLETE.md
- [x] Day 2 completion: HANDOFF_DAY2_COMPLETE.md
- [x] Day 3 completion: HANDOFF_DAY3_COMPLETE.md
- [x] Day 4 completion: HANDOFF_DAY4_COMPLETE.md
- [x] Day 5 completion: HANDOFF_DAY5_QWEN_TO_OPENCODE.md
- [x] Final coverage: reports/week3_final_coverage_report.md
- [x] Completion assessment: reports/week3_completion_assessment.md
- [x] Phase 3 readiness: reports/phase3_readiness_checklist.md

---

## Recommendations for Claude Code (Week 4 Start)

1. **Review Week 3 Results**
   - Read all completion reports
   - Understand current coverage state
   - Note any remaining gaps

2. **GUI Architecture Planning**
   - Design Qt6 application structure
   - Plan component hierarchy
   - Define state management approach

3. **UI/UX Design**
   - Create wireframes for main window
   - Design theme browser layout
   - Plan preview panel

4. **Technology Validation**
   - Verify PySide6 installation
   - Test Qt6 hello world
   - Validate dependencies

5. **Create Week 4 Day 1 Handoff**
   - Detailed GUI specifications
   - Component designs
   - Implementation guide for Qwen Coder

---

## Final Notes

[Any additional context, insights, or recommendations]

---

**Week 3 Status:** [COMPLETE ✅ / INCOMPLETE ⚠️]

**Next Action:** Claude Code reviews Week 3 results and begins Week 4 GUI planning

**Timeline:** On schedule for [9-10] week plan
**Confidence Level:** [High / Medium / Low] for v1.0.0 delivery

---

**Signed:** Opencode AI  
**Date:** October 26, 2025 23:00  
**Next Agent:** Claude Code (Week 4 Day 1 Morning)
```

### EOD Deliverables for Opencode AI

- [x] `reports/week3_final_coverage_report.md`
- [x] `reports/week3_completion_assessment.md`
- [x] `reports/phase3_readiness_checklist.md`
- [x] `WEEK3_COMPLETE_HANDOFF_TO_CLAUDE.md`
- [x] Git tag: `week3-validated`
- [x] Git tag: `phase3-ready` (if GO decision)

---

# 📊 Week 3 Success Metrics Summary

## Coverage Targets (End of Week 3)

| Category | Minimum | Target | Stretch |
|----------|---------|--------|---------|
| Overall Coverage | 70% | 72% | 73-74% |
| Core Modules | 80% | 85% | 90% |
| Handlers | 55% | 60% | 65% |
| CLI | 55% | 60% | 65% |
| Integration | 100% | 100% | 100% |

**Note:** 72% is the primary target. 75% was deemed too aggressive given Qt handler complexity.

## Test Quantity Targets

| Metric | Minimum | Target | Stretch |
|--------|---------|--------|---------|
| Total Tests | 200+ | 210+ | 220+ |
| Integration Tests | 5 | 5 | 7+ |
| CLI Tests | 15 | 18 | 20 |
| Handler Tests | 30 | 35 | 40 |

## Quality Metrics

| Metric | Threshold |
|--------|-----------|
| Test Pass Rate | ≥ 98% |
| Flaky Tests | 0 |
| Code Coverage | ≥ 72% |
| Critical Bugs | 0 |
| Regression Rate | 0% |
| Code Review Approval | Required for all implementations |
| Stand-up Completion | Daily (5 days) |

## Code Review Metrics

| Day | Reviewer | Author | Status | Issues Found |
|-----|----------|--------|--------|--------------|
| 1 | Claude Code | Qwen Coder | [APPROVED/CHANGES] | [X] critical, [Y] minor |
| 2 | Claude Code | Qwen Coder | [APPROVED/CHANGES] | [X] critical, [Y] minor |
| 3 | (Self-review) | Qwen Coder | [PASS] | [X] issues fixed |
| 4 | Claude Code | Qwen Coder | [APPROVED/CHANGES] | [X] critical, [Y] minor |
| 5 | (Self-review) | Qwen Coder | [PASS] | [X] issues fixed |

**Code Review Standards:**
- All critical issues must be fixed before merge
- Minor issues should be addressed but can be deferred
- Self-review required on Days 3 & 5 (tight timeline)
- Claude formal review on Days 1, 2, 4 (complex work)

---

# 🔄 Handoff Protocol Standards

## Daily Handoff Structure

Every handoff document must include:

1. **Status Header**
   - Date and time
   - From/To agents
   - Completion status

2. **Deliverables Checklist**
   - What was completed
   - What was partially completed
   - What was not started

3. **Test Results**
   - Pass/fail counts
   - Coverage metrics
   - Performance data

4. **Issues Encountered**
   - Blockers
   - Workarounds applied
   - Open questions

5. **Next Agent Instructions**
   - Clear objectives
   - Specific tasks
   - Success criteria
   - Reference materials

6. **Handoff Acceptance**
   - Receiving agent acknowledges
   - Confirms understanding
   - Notes any questions

## Handoff Timing

- **Morning shift:** 08:00 - 12:00 (4 hours)
- **Afternoon shift:** 13:00 - 18:00 (5-6 hours)
- **Evening shift:** 19:00 - 21:00 (2-3 hours)

Handoffs occur at shift boundaries with 30-60 min overlap for questions.

---

# 🚨 Escalation Protocol

## When to Escalate

1. **Coverage falling >5% behind target**
   - Mid-week assessment triggers re-planning
   - Adjust Days 4-5 scope

2. **Critical test failures**
   - All agents stop and investigate
   - Root cause analysis required

3. **Blocker lasting >2 hours**
   - Document in handoff
   - Tag as "BLOCKED"
   - Next agent addresses first

4. **Agent unavailable**
   - Handoff document stands as complete instruction
   - Next available agent picks up work

## Escalation Contacts

- **Technical decisions:** Claude Code
- **Implementation issues:** Qwen Coder
- **Quality concerns:** Opencode AI
- **Priority conflicts:** Project lead

---

# 📈 Progress Tracking

## Daily Tracking Metrics

Each day ends with a progress report including:

```markdown
## Day [X] Progress Report

**Date:** [Date]
**Agent:** [Agent Name]

### Metrics
- Coverage start: [X]%
- Coverage end: [X]%
- Coverage delta: +[X]%
- Tests added: [X]
- Tests passing: [X/Y]
- Time spent: [X] hours

### Objectives
- [x] Objective 1
- [x] Objective 2
- [ ] Objective 3 (incomplete)

### Blockers
[None / List]

### Tomorrow's Focus
[Brief description]
```

## Weekly Tracking Dashboard

**Week 3 Dashboard** (Updated Daily)

| Day | Agent | Focus | Coverage Start | Coverage End | Delta | Status |
|-----|-------|-------|----------------|--------------|-------|--------|
| 1 | Claude + Qwen + Opencode | Integration | 48% | [X]% | +[Y]% | [✅/⚠️] |
| 2 | Claude + Qwen + Opencode | CLI | [X]% | [X]% | +[Y]% | [✅/⚠️] |
| 3 | Qwen + Opencode | GTK | [X]% | [X]% | +[Y]% | [✅/⚠️] |
| 4 | Claude + Qwen + Opencode | Qt | [X]% | [X]% | +[Y]% | [✅/⚠️] |
| 5 | Qwen + Opencode | Gaps | [X]% | [X]% | +[Y]% | [✅/⚠️] |
| **Total** | | | **48%** | **[X]%** | **+[Y]%** | **[✅/⚠️]** |

---

# ✅ Week 3 Completion Checklist

## End of Week Deliverables

### Coverage & Testing
- [ ] Overall coverage ≥ 70% (minimum) or ≥ 72% (target)
- [ ] 200+ tests passing
- [ ] Integration tests: 5+ passing
- [ ] CLI tests: 15+ passing
- [ ] GTK handler tests: 20+ passing
- [ ] Qt handler tests: 15+ passing
- [ ] Test pass rate ≥ 98%
- [ ] Zero flaky tests

### Process & Documentation
- [ ] All 5 daily stand-ups completed and documented
- [ ] Code reviews completed (3 formal + 2 self-reviews)
- [ ] All handoff documents created (~18 total)
- [ ] All coverage reports generated (5 daily + 1 final)
- [ ] Phase 3 readiness assessed
- [ ] Git properly tagged (12+ tags)
- [ ] Documentation updated

### Quality Gates
- [ ] No regressions in existing tests
- [ ] No critical bugs introduced
- [ ] Code quality checks passing (black, flake8, mypy)
- [ ] All fixtures properly isolated
- [ ] All mocks appropriate

## Git Tags Created

- [ ] `week3-day1-architecture-complete`
- [ ] `week3-day1-complete`
- [ ] `week3-day1-validated`
- [ ] `week3-day2-complete`
- [ ] `week3-day2-validated`
- [ ] `week3-day3-complete`
- [ ] `week3-day3-validated`
- [ ] `week3-day4-complete`
- [ ] `week3-day4-validated`
- [ ] `week3-complete`
- [ ] `week3-validated`
- [ ] `phase3-ready` (if GO)

## Documentation Complete

- [ ] Day 1 handoffs (3 documents + 1 code review)
- [ ] Day 2 handoffs (3 documents + 1 code review)
- [ ] Day 3 handoffs (2 documents + 1 self-review)
- [ ] Day 4 handoffs (3 documents + 1 code review)
- [ ] Day 5 handoffs (2 documents + 1 self-review)
- [ ] Daily stand-ups (5 documents)
- [ ] Week 3 final reports (4 reports)
- [ ] Phase 3 readiness assessment
- [ ] Week 4 handoff

**Total Documents:** ~27 documents created during Week 3
**(Includes: 13 handoffs, 5 code reviews, 5 stand-ups, 4 reports)**

---

# 🎯 Final Week 3 Objectives Recap

**Primary Goal:** Achieve 72% test coverage (minimum 70% acceptable)

**Secondary Goals:**
- ✅ Integration testing complete (5 scenarios)
- ✅ CLI testing complete (60%+ coverage)
- ✅ Handler testing complete (GTK 65%+, Qt 60%+)
- ✅ Test quality high (98%+ pass rate, 0 flaky tests)
- ✅ Phase 3 readiness validated
- ✅ All daily stand-ups completed and documented
- ✅ All code reviews completed (3 formal, 2 self-reviews)
- ✅ Complete transparency through process documentation

**Success Definition:**
- Coverage ≥ 72% (target) or ≥ 70% (acceptable minimum)
- All critical paths tested
- No regressions
- Clean handoff to Week 4 GUI development
- High-quality, maintainable test suite

**Quality Over Quantity:**
- 70% with robust, well-documented tests > 72% with flaky tests
- Phase 3 unlocked at 70%+ threshold
- 72% represents strong confidence for GUI development
- Process documentation ensures team alignment and transparency

---

**Document Version:** 1.1 (Minor Improvements Applied)
**Created:** October 22, 2025  
**Updated:** October 22, 2025  
**Agent:** Claude Code  
**Purpose:** Week 3 Multi-Agent Execution Workflow

**Improvements Applied:**
- ✅ Added code review checkpoints between Claude/Qwen
- ✅ Made Day 5 concrete with pre-defined scenario-based priorities
- ✅ Reduced coverage expectations to 72% target (70% minimum acceptable)
- ✅ Added daily stand-up summaries for transparency
- ✅ Enhanced process documentation requirements
