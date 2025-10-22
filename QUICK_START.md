# Quick Start Guide - Week 1 Testing

**Status:** ✅ Installation Complete
**Ready for:** Week 1, Day 1 Testing
**Target:** color.py 80% coverage by Day 2

---

## Daily Workflow

### 1. Activate Environment
```bash
cd /home/joshu/unified-theming
source venv/bin/activate
```

### 2. Run Tests
```bash
# All tests
pytest tests/ -v

# Specific module (color.py)
pytest tests/test_color_utils.py -v

# With coverage
pytest tests/test_color_utils.py --cov=unified_theming/utils/color.py --cov-report=term
```

### 3. Check Coverage
```bash
# Quick check
coverage report --include="unified_theming/utils/color.py"

# Full report
pytest --cov=unified_theming --cov-report=html
# View: htmlcov/index.html
```

### 4. Code Quality
```bash
# Format
black unified_theming/

# Type check
mypy unified_theming/

# Lint
flake8 unified_theming/
```

---

## Week 1 Targets

| Day | Module | Current | Target | Test File |
|-----|--------|---------|--------|-----------|
| 1-2 | color.py | 72% | 80% | tests/test_color_utils.py |
| 2-3 | manager.py | 24% | 85% | tests/test_manager_integration.py |
| 3-4 | config.py | 15% | 70% | tests/test_config_backup.py |
| 4-5 | gtk_handler.py | 25% | 70% | tests/test_gtk_handler.py |

---

## Quick Commands

```bash
# Create new test file
touch tests/test_manager_integration.py

# Run with debugging
pytest tests/test_color_utils.py -vv --tb=short

# Check one module
coverage report --include="unified_theming/core/manager.py"

# Generate HTML report
pytest --cov=unified_theming --cov-report=html && open htmlcov/index.html
```

---

## References

- **Test Plan:** `docs/test_plan_week1.md` (130+ test cases)
- **Handoff Protocol:** `docs/HANDOFF_PROTOCOL.md` (collaboration workflow)
- **Troubleshooting:** `docs/INSTALLATION_TROUBLESHOOTING.md`
- **Project Guide:** `CLAUDE.md`

---

## Current Status (Post-Installation)

✅ Python 3.12.3 active
✅ pytest 7.4.4 installed
✅ PyGObject 3.48.2 available (system)
✅ 41 tests passing
✅ Coverage tracking works
✅ Development tools ready

**Next:** Fix color.py failing tests, implement remaining test cases (TC-C-001 to TC-C-030)

---

**Activate:** `source venv/bin/activate`
**Test:** `pytest tests/ -v`
**Coverage:** `pytest --cov=unified_theming --cov-report=term`
