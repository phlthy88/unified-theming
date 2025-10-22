# Qwen Coder: Week 2 Day 5 - Flatpak Handler Testing + v0.5 Release

**DIRECT ORDERS - NO DEVIATIONS**

---

## MISSION

**Primary:** Test `unified_theming/handlers/flatpak_handler.py` to achieve **75% coverage** (current: 42%)
**Secondary:** Prepare v0.5.0 CLI-only release
**Deadline:** End of Day 5
**Handoff Tag:** `handoff/week2-day5`

---

## CURRENT STATUS

### Project Coverage
```
Week 1:     28% (color.py complete)
Week 2 D3:  40% (manager.py complete)
Week 2 D4:  44% (config.py complete)
Week 2 D5:  50%+ target (Flatpak + v0.5)
```

### Module Status
```
✅ color.py:     86% (Week 1)
✅ manager.py:   93% (Week 2 Day 3)
✅ config.py:    75% (Week 2 Day 4)
⏳ flatpak_handler.py: 42% → 75% target (Week 2 Day 5)
```

### Test Suite
```
Current: 109 passed, 1 skipped (99.1% pass rate)
Target:  130+ passed, 1 skipped (after Flatpak tests)
```

---

## PART 1: FLATPAK HANDLER TESTING (6-8 hours)

### STEP 1: READ IMPLEMENTATION (15 minutes)

```bash
cd /home/joshu/unified-theming
source venv/bin/activate
cat unified_theming/handlers/flatpak_handler.py
```

**Identify:**
- Public methods to test
- Flatpak system interactions
- Override file paths
- Portal detection logic
- Error handling paths

**DO NOT PROCEED until you understand the Flatpak handler API.**

---

### STEP 2: CREATE TEST FILE (20 minutes)

Create `tests/test_flatpak_handler.py`:

```python
"""Tests for unified_theming.handlers.flatpak_handler module."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import subprocess

from unified_theming.handlers.flatpak_handler import FlatpakHandler
from unified_theming.core.types import ThemeData, Toolkit, ValidationResult
from unified_theming.core.exceptions import HandlerNotAvailableError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def flatpak_handler():
    """FlatpakHandler instance for testing."""
    return FlatpakHandler()


@pytest.fixture
def sample_theme_data():
    """Sample theme data for testing."""
    return ThemeData(
        name="Adwaita-dark",
        toolkit=Toolkit.FLATPAK,
        colors={
            "theme_bg_color": "#2e3436",
            "theme_fg_color": "#eeeeec",
            "theme_selected_bg_color": "#3584e4"
        },
        additional_data={}
    )


@pytest.fixture
def mock_flatpak_list():
    """Mock Flatpak application list."""
    return """
org.gnome.Calculator
org.mozilla.firefox
com.spotify.Client
"""


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

def test_flatpak_handler_init(flatpak_handler):
    """Test TC-FP-001: Initialize FlatpakHandler."""
    assert flatpak_handler is not None
    assert flatpak_handler.toolkit == Toolkit.FLATPAK


@patch('shutil.which', return_value='/usr/bin/flatpak')
def test_flatpak_handler_available(mock_which, flatpak_handler):
    """Test TC-FP-002: Check Flatpak is available."""
    assert flatpak_handler.is_available() is True
    mock_which.assert_called_once_with('flatpak')


@patch('shutil.which', return_value=None)
def test_flatpak_handler_not_available(mock_which, flatpak_handler):
    """Test TC-FP-003: Check Flatpak not available."""
    assert flatpak_handler.is_available() is False


# ============================================================================
# OVERRIDE CREATION TESTS
# ============================================================================

def test_apply_theme_success(flatpak_handler, sample_theme_data):
    """Test TC-FP-004: Apply theme successfully."""
    # TODO: Mock file operations and Flatpak commands
    pass


def test_create_global_override(flatpak_handler, sample_theme_data):
    """Test TC-FP-005: Create global Flatpak override."""
    # TODO: Verify override file created at ~/.local/share/flatpak/overrides/global
    pass


def test_create_per_app_override(flatpak_handler, sample_theme_data):
    """Test TC-FP-006: Create per-app override."""
    # TODO: Verify override for specific app (e.g., org.gnome.Calculator)
    pass


def test_override_file_format(flatpak_handler, sample_theme_data):
    """Test TC-FP-007: Verify override file format."""
    # TODO: Check [Context], [Environment] sections
    pass


# ============================================================================
# THEME VARIABLE MAPPING TESTS
# ============================================================================

def test_gtk_to_flatpak_color_mapping(flatpak_handler, sample_theme_data):
    """Test TC-FP-008: Map GTK colors to Flatpak environment variables."""
    # TODO: Verify GTK_THEME, GTK3_THEME, etc. are set correctly
    pass


def test_theme_variable_escaping(flatpak_handler):
    """Test TC-FP-009: Special characters in theme names are escaped."""
    # TODO: Test theme name with spaces, special chars
    pass


# ============================================================================
# PORTAL DETECTION TESTS
# ============================================================================

@patch('subprocess.run')
def test_detect_portal_available(mock_run, flatpak_handler):
    """Test TC-FP-010: Detect xdg-desktop-portal is available."""
    mock_run.return_value = Mock(returncode=0)
    # TODO: Verify portal detection logic
    pass


@patch('subprocess.run')
def test_detect_portal_not_available(mock_run, flatpak_handler):
    """Test TC-FP-011: Handle missing xdg-desktop-portal."""
    mock_run.return_value = Mock(returncode=1)
    # TODO: Verify graceful handling when portal missing
    pass


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_apply_theme_permission_denied(flatpak_handler, sample_theme_data):
    """Test TC-FP-012: Handle permission denied when writing overrides."""
    with patch('pathlib.Path.write_text', side_effect=PermissionError("Access denied")):
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is False


def test_apply_theme_flatpak_not_installed(flatpak_handler, sample_theme_data):
    """Test TC-FP-013: Handle Flatpak not installed."""
    with patch.object(flatpak_handler, 'is_available', return_value=False):
        result = flatpak_handler.apply_theme(sample_theme_data)
        assert result is False


def test_list_apps_command_fails(flatpak_handler):
    """Test TC-FP-014: Handle 'flatpak list' command failure."""
    with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'flatpak')):
        # TODO: Verify error handling when listing apps fails
        pass


# ============================================================================
# ACCESSIBILITY TESTS
# ============================================================================

def test_high_contrast_theme(flatpak_handler):
    """Test TC-FP-015: Apply high contrast theme."""
    theme_data = ThemeData(
        name="HighContrast",
        toolkit=Toolkit.FLATPAK,
        colors={"theme_bg_color": "#ffffff", "theme_fg_color": "#000000"},
        additional_data={"high_contrast": True}
    )
    # TODO: Verify high contrast settings applied
    pass


def test_font_scaling(flatpak_handler):
    """Test TC-FP-016: Apply custom font scaling."""
    theme_data = ThemeData(
        name="Adwaita",
        toolkit=Toolkit.FLATPAK,
        colors={},
        additional_data={"font_scale": 1.5}
    )
    # TODO: Verify font scale environment variable set
    pass


# ============================================================================
# VALIDATION TESTS
# ============================================================================

def test_validate_compatibility_success(flatpak_handler, sample_theme_data):
    """Test TC-FP-017: Validate theme compatibility."""
    result = flatpak_handler.validate_compatibility(sample_theme_data)
    assert isinstance(result, ValidationResult)


def test_get_current_theme(flatpak_handler):
    """Test TC-FP-018: Get currently applied Flatpak theme."""
    # TODO: Mock reading override file, return theme name
    pass


# Add more tests as needed to reach 75% coverage
```

**SAVE THIS FILE. Run baseline tests:**

```bash
pytest tests/test_flatpak_handler.py -v -o addopts=""
```

---

### STEP 3: IMPLEMENT TESTS INCREMENTALLY (5-6 hours)

**Phase 1: Initialization (30 min)**
- Implement TC-FP-001, TC-FP-002, TC-FP-003
- **Check coverage:** Should reach ~10%

**Phase 2: Override Creation (2 hours)**
- Implement TC-FP-004 to TC-FP-007
- Mock `Path.write_text()` for file operations
- Mock `subprocess.run()` for Flatpak commands
- **Check coverage:** Should reach ~40%

**Phase 3: Variable Mapping (1 hour)**
- Implement TC-FP-008, TC-FP-009
- **Check coverage:** Should reach ~55%

**Phase 4: Portal Detection (1 hour)**
- Implement TC-FP-010, TC-FP-011
- **Check coverage:** Should reach ~65%

**Phase 5: Error Handling (1 hour)**
- Implement TC-FP-012 to TC-FP-014
- **Check coverage:** Should reach ~75%

**Phase 6: Accessibility (30 min)**
- Implement TC-FP-015, TC-FP-016
- **Check coverage:** Should reach ~80%+ (stretch goal)

**After each phase, run:**
```bash
pytest tests/test_flatpak_handler.py --cov=unified_theming/handlers/flatpak_handler.py --cov-report=term
```

**DO NOT PROCEED TO NEXT PHASE IF TESTS FAIL.**

---

### STEP 4: VERIFY COVERAGE (15 minutes)

```bash
pytest tests/test_flatpak_handler.py --cov=unified_theming/handlers/flatpak_handler.py --cov-report=term-missing
```

**Required:** flatpak_handler.py coverage ≥ 75%

**If coverage < 75%:**
1. Check `htmlcov/flatpak_handler_py.html` for uncovered lines
2. Add tests for critical uncovered paths
3. Re-run coverage check

**DO NOT PROCEED UNTIL COVERAGE ≥ 75%.**

---

### STEP 5: FULL SUITE VERIFICATION (10 minutes)

```bash
pytest -v --cov=unified_theming --cov-report=term
```

**Required Results:**
- Flatpak tests passing (≥20 tests)
- No regressions (109 previous tests still passing)
- Project coverage ≥ 48%

---

## PART 2: v0.5.0 RELEASE PREPARATION (2-3 hours)

### STEP 6: ADD BASIC CLI TESTS (1 hour)

Create `tests/test_cli_basic.py`:

```python
"""Basic CLI command tests for v0.5.0 release."""
import pytest
from click.testing import CliRunner
from unified_theming.cli.commands import main, list_themes, apply


@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    return CliRunner()


def test_cli_main_help(cli_runner):
    """Test main CLI help message."""
    result = cli_runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'unified-theming' in result.output.lower()


def test_cli_list_themes(cli_runner):
    """Test 'list' command."""
    result = cli_runner.invoke(list_themes)
    # Should not crash, exit code 0 or 1 acceptable
    assert result.exit_code in [0, 1]


def test_cli_apply_theme_missing_name(cli_runner):
    """Test 'apply' command without theme name."""
    result = cli_runner.invoke(apply)
    assert result.exit_code != 0  # Should fail without theme name


def test_cli_apply_theme_nonexistent(cli_runner):
    """Test 'apply' command with non-existent theme."""
    result = cli_runner.invoke(apply, ['NonExistentTheme'])
    assert result.exit_code != 0


def test_cli_version(cli_runner):
    """Test --version flag."""
    result = cli_runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert '1.0.0' in result.output or '0.5.0' in result.output
```

**Run CLI tests:**
```bash
pytest tests/test_cli_basic.py -v
```

**Expected:** 4-5 tests passing, CLI coverage +5-10%

---

### STEP 7: CREATE RELEASE NOTES (30 minutes)

Create `RELEASE_NOTES_v0.5.0.md`:

```markdown
# Unified Theming v0.5.0 - CLI Alpha Release

**Release Date:** October 21, 2025
**Type:** Alpha Release (CLI-only)
**Status:** Feature Complete, Testing In Progress

---

## 🎉 What's New

### CLI Commands Available
- `unified-theming list` - List all available themes
- `unified-theming apply <theme>` - Apply a theme across toolkits
- `unified-theming current` - Show currently applied themes
- `unified-theming rollback` - Rollback to previous theme
- `unified-theming validate <theme>` - Validate theme compatibility

### Supported Toolkits
- ✅ GTK2/3/4 themes
- ✅ Libadwaita applications (70% coverage via CSS injection)
- ✅ Qt5/6 applications (kdeglobals + Kvantum)
- ✅ Flatpak containerized apps (global + per-app overrides)
- ✅ Snap applications (basic support)

### Core Features
- **Theme Discovery:** Automatically finds themes in ~/.themes, /usr/share/themes
- **Cross-Toolkit Application:** Applies themes to all supported toolkits at once
- **Color Translation:** Converts GTK color variables to Qt format
- **Backup/Restore:** Automatic backup before theme changes, rollback on failure
- **Graceful Degradation:** Continues if one toolkit unavailable

---

## 📊 Test Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| color.py | 86% | ✅ Excellent |
| manager.py | 93% | ✅ Excellent |
| config.py | 75% | ✅ Good |
| flatpak_handler.py | XX% | ✅ Good |
| **Overall** | **XX%** | ⚠️ **In Progress (target: 80%)** |

**Test Suite:**
- XXX tests passing (YY% pass rate)
- Comprehensive unit tests for core modules
- Integration tests in progress (Week 3)

---

## 🚀 Installation

### From Source (Recommended for v0.5.0)
```bash
git clone https://github.com/yourusername/unified-theming
cd unified-theming
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### System Dependencies (Ubuntu/Debian)
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
```

---

## 🎯 Quick Start

```bash
# List available themes
unified-theming list

# Apply a theme
unified-theming apply Adwaita-dark

# Check current themes
unified-theming current

# Rollback if something goes wrong
unified-theming rollback
```

---

## ⚠️ Known Limitations (v0.5.0)

### Not Yet Implemented
- ❌ **GUI application** (planned for Week 4-6)
- ❌ **Percentage RGB colors** (TC-C-030, deferred to post-v0.5)
- ❌ **Theme preview** (planned for v1.0)
- ❌ **Packaging** (Flatpak/AppImage/PPA planned for Weeks 7-9)

### Partial Support
- ⚠️ **Libadwaita:** 70% coverage (colors only, no widget structure changes)
- ⚠️ **Qt translation:** Approximate (GTK and Qt have different color models)
- ⚠️ **Snap:** Basic support (76% coverage, but limited by Snap permissions)

### Testing Status
- ⚠️ **Integration tests:** In progress (Week 3 planned)
- ⚠️ **Performance tests:** Not yet implemented (Week 3 planned)
- ⚠️ **Stress tests:** Not yet implemented (Week 3 planned)

---

## 🐛 Known Issues

1. **Backup timestamp collisions** - Fixed in v0.5.0 (added microsecond precision)
2. **CLI commands untested** - Basic tests added in v0.5.0 (full coverage Week 3)
3. **Handler coordination** - Tested individually, integration tests pending

---

## 📚 Documentation

- [Requirements Specification](docs/requirements_specification.md)
- [Architecture Guide](docs/architecture.md)
- [Developer Guide](docs/developer_guide.md)
- [Test Plan](docs/test_plan_week1.md)
- [CLAUDE.md](CLAUDE.md) - Claude Code integration guide

---

## 🤝 Contributing

This project is in **active development** (Phase 2, ~70% complete).

**Current Focus:** Testing and integration (Weeks 2-3)
**Next Phase:** GUI development (Weeks 4-6)

See [HANDOFF_PROTOCOL.md](docs/HANDOFF_PROTOCOL.md) for multi-agent development workflow.

---

## 📅 Roadmap

- **v0.5.0 (Week 2):** ✅ CLI-only alpha release
- **v0.9.0 (Week 6):** GUI beta release
- **v1.0.0 (Week 9-11):** Production release with packaging

---

## 🙏 Acknowledgments

Built with multi-agent collaboration:
- **Claude Code:** Architecture, design, documentation
- **Qwen Coder:** Implementation, testing
- **Opencode AI:** QA validation, packaging

---

## 📄 License

MIT License (see LICENSE file)

---

**This is an alpha release. Expect bugs and missing features. Report issues at:**
https://github.com/yourusername/unified-theming/issues

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**SAVE THIS FILE.**

---

### STEP 8: UPDATE PROJECT COVERAGE (10 minutes)

Run full coverage report:

```bash
pytest --cov=unified_theming --cov-report=html --cov-report=term
```

**Update RELEASE_NOTES_v0.5.0.md with actual coverage numbers.**

---

### STEP 9: CREATE COMPLETION DOCUMENT (20 minutes)

Create `WEEK2_DAY5_COMPLETE.md`:

```markdown
# Week 2 Day 5 Complete ✅

**Date:** October 21, 2025
**Status:** [COMPLETE/INCOMPLETE]
**Release:** v0.5.0 published

## Achievement Summary

### Flatpak Handler Testing
- **Target:** 75% coverage
- **Achieved:** XX% coverage
- **Tests:** YY/YY passing (ZZ% pass rate)
- **Status:** ✅/❌

### v0.5.0 Release
- **CLI Tests:** 5 tests added
- **Release Notes:** Created
- **Git Tag:** `release/v0.5.0` created
- **Status:** ✅/❌

### Overall Project
- **Project Coverage:** XX% (was 44%)
- **Total Tests:** XXX tests passing
- **Pass Rate:** YY%

## Coverage by Module

| Module | Coverage | Status |
|--------|----------|--------|
| color.py | 86% | ✅ Week 1 |
| manager.py | 93% | ✅ Week 2 Day 3 |
| config.py | 75% | ✅ Week 2 Day 4 |
| flatpak_handler.py | XX% | ✅/❌ Week 2 Day 5 |

## Tests Created

### Flatpak Handler Tests
[List all test functions]

### CLI Tests
[List all CLI test functions]

## Issues Found

[List any issues discovered]

## Next Steps

**Week 3 Focus:**
- Integration testing (full workflow tests)
- Performance benchmarking
- Handler coordination tests
- Target: 80% overall coverage
```

---

### STEP 10: GIT COMMIT AND TAG (15 minutes)

```bash
# Add all changes
git add tests/test_flatpak_handler.py
git add tests/test_cli_basic.py
git add RELEASE_NOTES_v0.5.0.md
git add WEEK2_DAY5_COMPLETE.md
git add unified_theming/handlers/flatpak_handler.py  # if modified
git add coverage.xml htmlcov/

# Commit
git commit -m "Week 2 Day 5 Complete: Flatpak XX% coverage, v0.5.0 release

✅ Flatpak handler: 42% → XX% coverage
✅ CLI tests added: 5 basic command tests
✅ v0.5.0 release prepared and tagged
✅ Project coverage: 44% → XX%

Week 2 Summary:
- Day 3: manager.py 93% coverage (27 tests)
- Day 4: config.py 75% coverage (17 tests)
- Day 5: flatpak_handler.py XX% coverage (YY tests)

v0.5.0 Release:
- CLI-only alpha release
- Core functionality tested and working
- Known limitations documented
- Ready for community testing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Create tags
git tag -a milestone/week2-complete -m "Week 2 complete: Core modules tested"
git tag -a handoff/week2-day5 -m "Week 2 Day 5 complete, ready for QA"
git tag -a release/v0.5.0 -m "v0.5.0 CLI alpha release"
```

---

## SUCCESS CRITERIA

### MINIMUM (GO to Week 3)
- [ ] flatpak_handler.py coverage ≥ 75%
- [ ] Flatpak tests pass rate ≥ 95%
- [ ] No regressions (109+ previous tests pass)
- [ ] v0.5.0 release notes created
- [ ] Git tags created

### STRETCH (EXCELLENT)
- [ ] flatpak_handler.py coverage ≥ 80%
- [ ] CLI tests added (5+ tests)
- [ ] Project coverage ≥ 50%
- [ ] All test pass rate = 100%

---

## DELIVERABLES CHECKLIST

Before completing Day 5:

- [ ] `tests/test_flatpak_handler.py` created (≥20 tests)
- [ ] `tests/test_cli_basic.py` created (5 tests)
- [ ] `RELEASE_NOTES_v0.5.0.md` created
- [ ] `WEEK2_DAY5_COMPLETE.md` created
- [ ] All tests passing
- [ ] Coverage reports generated
- [ ] Git commit with proper message
- [ ] Git tags: `milestone/week2-complete`, `handoff/week2-day5`, `release/v0.5.0`

---

## RULES - NO EXCEPTIONS

1. **DO NOT skip Flatpak handler testing** - Primary objective
2. **DO NOT proceed if Flatpak coverage < 75%**
3. **DO NOT skip CLI tests** - Required for v0.5.0 validation
4. **DO NOT skip release notes** - Required for community release
5. **DO NOT commit without tags** - Triggers handoff to Opencode AI
6. **DO NOT modify existing tests** unless fixing regressions
7. **DO NOT use real Flatpak commands** - Mock all subprocess calls
8. **DO NOT skip full suite verification** - Ensure no regressions
9. **DO NOT proceed without completion document**
10. **DO NOT deviate from this sequence**

---

## TIME ALLOCATION

| Phase | Task | Time |
|-------|------|------|
| 1 | Read Flatpak handler | 15 min |
| 2 | Create test file structure | 20 min |
| 3 | Implement Flatpak tests | 5-6 hours |
| 4 | Verify coverage ≥75% | 15 min |
| 5 | Full suite verification | 10 min |
| 6 | Add CLI tests | 1 hour |
| 7 | Create release notes | 30 min |
| 8 | Update coverage numbers | 10 min |
| 9 | Create completion doc | 20 min |
| 10 | Git commit and tag | 15 min |

**Total:** 8-9 hours

**Deadline:** End of Week 2 Day 5

---

## IF YOU GET STUCK

**Flatpak coverage not reaching 75%?**
- Focus on override creation tests (highest impact)
- Add tests for error handling (permission denied, missing Flatpak)
- Test portal detection (adds ~10% coverage)

**Flatpak tests failing?**
- Check if mocking `subprocess.run()` correctly
- Verify `Path.write_text()` mocked for file operations
- Use `pytest -v -s` for verbose output

**Don't understand Flatpak overrides?**
- Read: https://docs.flatpak.org/en/latest/flatpak-command-reference.html#flatpak-override
- Override format: INI-style with [Context] and [Environment] sections
- Example: `GTK_THEME=Adwaita-dark`

---

## HANDOFF TRIGGER

**When complete, create handoff tag:**

```bash
git tag -a handoff/week2-day5 -m "Week 2 Day 5 complete: Flatpak XX% coverage, v0.5.0 ready for QA validation"
git push --tags
```

**This triggers Opencode AI to:**
1. Validate Flatpak tests (coverage ≥75%, pass rate ≥95%)
2. Validate v0.5.0 release readiness
3. Create QA report (`qa_report_week2_day5.md`)
4. Make GO/NO-GO decision for Week 3
5. Package v0.5.0 release if GO

---

## BEGIN NOW

**Start with PART 1, STEP 1. Follow the steps exactly. Report back when complete.**

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
