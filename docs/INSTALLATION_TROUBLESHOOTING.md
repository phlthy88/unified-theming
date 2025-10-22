# Installation Troubleshooting Guide

**Issue:** PyGObject dependency installation failures
**Date:** October 21, 2025
**Platform:** Ubuntu 24.04 (WSL)

---

## Problem Analysis

The project has `PyGObject>=3.42` as a **required dependency** in `pyproject.toml` (line 43), but PyGObject requires system-level libraries that cannot be installed via pip alone.

### Root Causes

1. **System Libraries Missing:** PyGObject needs:
   - `libcairo2-dev` (Cairo graphics library)
   - `libgirepository1.0-dev` (GObject Introspection)
   - `pkg-config` (for finding libraries)
   - `python3-dev` (Python headers)
   - `gir1.2-gtk-4.0` (GTK4 introspection bindings)

2. **Dependency Structure Issue:** PyGObject is listed as both:
   - **Required dependency** (line 43) - Always installed
   - **Optional GUI dependency** (line 58) - Should be optional

3. **Virtual Environment Confusion:** Multiple venvs exist (`venv`, `venv_new`)

---

## Solution Strategy

### Option 1: Install System Dependencies (Recommended for GUI Development)

If you plan to work on the GUI or run the full application:

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y \
    python3-dev \
    python3-venv \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-4.0 \
    gobject-introspection \
    libgtk-4-dev

# 2. Remove old virtual environments
cd /home/joshu/unified-theming
rm -rf venv venv_new

# 3. Create fresh virtual environment
python3 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Upgrade pip
pip install --upgrade pip setuptools wheel

# 6. Install project with GUI support
pip install -e ".[dev,gui]"
```

**Expected Result:** Full installation with PyGObject, ready for GUI development.

---

### Option 2: Install Without GUI (For Testing/CLI-Only Work)

If you only need CLI functionality or are working on Week 1 testing (no GUI needed yet):

```bash
# 1. Fix pyproject.toml to make PyGObject truly optional
# (We'll do this below)

# 2. Remove old virtual environments
cd /home/joshu/unified-theming
rm -rf venv venv_new

# 3. Create fresh virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip setuptools wheel

# 5. Install without GUI (PyGObject skipped)
pip install -e ".[dev]"
```

**Expected Result:** CLI and testing tools installed, GUI dependencies skipped.

---

### Option 3: Use System Python3-PyGObject (Easiest for WSL)

Ubuntu provides pre-built PyGObject packages:

```bash
# 1. Install system PyGObject (no compilation needed)
sudo apt update
sudo apt install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0

# 2. Create venv with --system-site-packages (allows access to system PyGObject)
cd /home/joshu/unified-theming
rm -rf venv venv_new
python3 -m venv --system-site-packages venv
source venv/bin/activate

# 3. Install dev dependencies only (PyGObject comes from system)
pip install -e ".[dev]"
```

**Expected Result:** Uses system-provided PyGObject, avoids compilation issues.

---

## Fix pyproject.toml (Required for Option 2)

The current `pyproject.toml` has PyGObject as a **required** dependency. For CLI-only work (Week 1-3), it should be optional.

### Current (Problematic):
```toml
dependencies = [
    "click>=8.0",
    "PyGObject>=3.42",  # ← Always required
]

[project.optional-dependencies]
gui = [
    "PyGObject>=3.42",  # ← Redundant
]
```

### Fixed (PyGObject Optional):
```toml
dependencies = [
    "click>=8.0",
    # PyGObject moved to optional dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    # ... existing dev deps
]
gui = [
    "PyGObject>=3.42",  # ← Only installed with [gui]
]
```

---

## Verification Steps

After installation, verify everything works:

```bash
# 1. Check Python version
python --version
# Expected: Python 3.10+ (Ubuntu 24.04 has 3.12)

# 2. Check virtual environment active
which python
# Expected: /home/joshu/unified-theming/venv/bin/python

# 3. Check installed packages
pip list | grep -E '(click|pytest|PyGObject)'
# Expected: click, pytest, pytest-cov (PyGObject only if GUI installed)

# 4. Test imports (CLI-only)
python -c "import click; print('click OK')"
python -c "import pytest; print('pytest OK')"

# 5. Test imports (GUI - only if installed)
python -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print('PyGObject OK')"

# 6. Run tests (should work even without GUI)
pytest tests/test_parser.py -v
```

---

## Recommended Approach for Week 1 (Testing Phase)

Since Week 1 focuses on **testing CLI functionality** (no GUI needed), use **Option 3** (system PyGObject with --system-site-packages) or **Option 2** (skip GUI entirely).

### Step-by-Step (Option 3 - Easiest):

```bash
# 1. Install system dependencies (one-time)
sudo apt update && sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0

# 2. Clean environment
cd /home/joshu/unified-theming
rm -rf venv venv_new

# 3. Create venv with system packages
python3 -m venv --system-site-packages venv
source venv/bin/activate

# 4. Install dev dependencies
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"

# 5. Verify
pytest --version
python -c "import click; print('Ready for Week 1 testing!')"
```

**This avoids PyGObject compilation issues while keeping it available if needed later.**

---

## Common Errors & Solutions

### Error: "Run-time dependency cairo found: NO"
**Cause:** libcairo2-dev not installed
**Solution:** `sudo apt install libcairo2-dev pkg-config`

### Error: "Pkg-config for machine host machine not found"
**Cause:** pkg-config not installed
**Solution:** `sudo apt install pkg-config`

### Error: "No module named 'gi'"
**Cause:** PyGObject not installed
**Solution:** Either install system package (`python3-gi`) or compile from pip after installing system deps

### Error: "Could not find a version that satisfies the requirement PyGObject"
**Cause:** PyGObject compilation failed silently
**Solution:** Install system dependencies first, then retry pip install

### Error: Virtual environment points to wrong path
**Cause:** venv created elsewhere then moved
**Solution:** Delete venv and recreate in correct location

---

## Platform-Specific Notes

### Ubuntu 24.04 (Current System)
- Python 3.12 default
- GTK4 available via `gir1.2-gtk-4.0`
- PyGObject available via `python3-gi`
- **Recommended:** Option 3 (system-site-packages)

### Ubuntu 22.04
- Python 3.10 default
- Same package names as 24.04
- Fully supported

### Fedora 40
- Python 3.12
- Use `dnf install python3-gobject gtk4 cairo-devel`
- Otherwise same approach

### Arch Linux
- Rolling release, latest Python
- Use `pacman -S python-gobject gtk4`
- AUR may have newer PyGObject

---

## Next Steps After Installation

Once installation succeeds:

1. **Verify test infrastructure:**
   ```bash
   pytest --version
   coverage --version
   black --version
   mypy --version
   ```

2. **Run existing tests:**
   ```bash
   pytest tests/ -v
   ```

3. **Check coverage:**
   ```bash
   pytest --cov=unified_theming --cov-report=term
   ```

4. **Begin Week 1 testing** (per test_plan_week1.md):
   ```bash
   # Create color.py test file
   touch tests/test_color_utils.py

   # Start implementing TC-C-001 to TC-C-030
   # Target: 80% coverage by Day 2
   ```

---

## Contact & Escalation

If issues persist after trying all options:

1. **Check system info:**
   ```bash
   cat /etc/os-release
   python3 --version
   dpkg -l | grep -E '(cairo|girepository|gtk)'
   ```

2. **Save error output:**
   ```bash
   pip install -e ".[dev,gui]" 2>&1 | tee install_error.log
   ```

3. **Report with:**
   - OS version
   - Python version
   - Full error log
   - Output of `dpkg -l | grep -E '(cairo|girepository)'`

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-21 | Initial troubleshooting guide | Claude Code |

---

**TL;DR:** For Week 1 testing (CLI-only), use Option 3 (system PyGObject with --system-site-packages). It's the fastest and most reliable on Ubuntu 24.04.
