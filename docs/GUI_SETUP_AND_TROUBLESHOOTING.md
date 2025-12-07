# GUI Setup and Troubleshooting

**Status:** GUI requires system dependencies for GTK4/Libadwaita  
**Issue:** PyGObject installation fails without system GTK libraries  
**Solutions:** Multiple approaches provided below  

## Current GUI Issues

### 1. Missing System Dependencies
The GUI requires GTK4 and Libadwaita system libraries that are not available in all environments.

**Error:** `ModuleNotFoundError: No module named 'gi'`

### 2. PyGObject Installation Failure
PyGObject (Python GTK bindings) requires system development headers and libraries.

**Error:** `Python dependency not found` during pycairo/PyGObject build

## Solutions

### Option 1: Install System Dependencies (Recommended)

#### Ubuntu/Debian:
```bash
# Install GTK4 and development libraries
sudo apt update
sudo apt install -y \
    libgtk-4-dev \
    libadwaita-1-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0 \
    gir1.2-adw-1

# Then install GUI dependencies
pip install -e ".[gui]"
```

#### Fedora/RHEL:
```bash
# Install GTK4 and development libraries
sudo dnf install -y \
    gtk4-devel \
    libadwaita-devel \
    gobject-introspection-devel \
    cairo-devel \
    pkgconfig \
    python3-devel \
    python3-gobject \
    python3-cairo

# Then install GUI dependencies
pip install -e ".[gui]"
```

#### Arch Linux:
```bash
# Install GTK4 and development libraries
sudo pacman -S \
    gtk4 \
    libadwaita \
    gobject-introspection \
    cairo \
    pkgconf \
    python-gobject \
    python-cairo

# Then install GUI dependencies
pip install -e ".[gui]"
```

### Option 2: Use System Python with GTK (Alternative)

If pip installation fails, use system Python with pre-installed GTK bindings:

```bash
# Use system Python instead of venv
/usr/bin/python3 -m unified_theming.gui.application

# Or create symlinks in venv
ln -s /usr/lib/python3/dist-packages/gi venv/lib/python3.*/site-packages/
```

### Option 3: CLI-Only Usage (Fallback)

If GUI cannot be installed, use the fully functional CLI:

```bash
# List available themes
unified-theming list

# Apply a theme with dry-run preview
unified-theming apply_theme Adwaita-dark --dry-run

# Apply a theme to specific toolkits
unified-theming apply_theme Adwaita-dark --targets gtk4 --targets qt5

# Show current theme
unified-theming current

# Rollback to previous theme
unified-theming rollback
```

## GUI Entry Points

### Add GUI Entry Point to pyproject.toml

The GUI currently lacks a proper entry point. Add this to `pyproject.toml`:

```toml
[project.scripts]
unified-theming = "unified_theming.cli.commands:main"
unified-theming-gui = "unified_theming.gui.application:main"  # Add this line
```

### Manual GUI Launch

Until the entry point is added, launch GUI manually:

```bash
# From project root
python -m unified_theming.gui.application

# Or with full path
python /path/to/unified-theming/unified_theming/gui/application.py
```

## Troubleshooting Common Issues

### Issue 0: Snap fails on Ubuntu 25.10+ (snapd 2.72+)

**Error:** `snap "unified-theming" has "configure" hook change "core.experimental.desktop-support"`

**Cause:** Ubuntu 25.10 ships snapd 2.72 which removed the `core.experimental.desktop-support` option. The unified-theming snap's configure hook still references this deprecated option, causing installation/run failure.

**Solution:** Use the pip/source installation instead:

```bash
# 1. Uninstall the snap (if installed)
sudo snap remove unified-theming

# 2. Install system GTK dependencies
sudo apt update && sudo apt install -y \
    libgtk-4-dev libadwaita-1-dev libgirepository1.0-dev \
    gir1.2-gtk-4.0 python3-gi python3-gi-cairo pkg-config python3-dev

# 3. Install from source with GUI support
cd ~/unified-theming
source venv/bin/activate
pip install -e ".[dev,gui]"

# 4. Launch GUI directly
python -m unified_theming.gui.application
```

**Alternative:** Run on Ubuntu 22.04/24.04 with older snapd, or wait for snap package update.

### Issue 1: "No module named 'gi'"
**Cause:** PyGObject not installed  
**Solution:** Install system GTK libraries first, then `pip install PyGObject`

### Issue 2: "Python dependency not found" during build
**Cause:** Missing python3-dev headers  
**Solution:** Install `python3-dev` or `python3-devel` package

### Issue 3: "cairo not found"
**Cause:** Missing Cairo development libraries  
**Solution:** Install `libcairo2-dev` or `cairo-devel` package

### Issue 4: Blank window or no functionality
**Cause:** GUI not properly connected to backend  
**Solution:** Check that `UnifiedThemeManager` is properly initialized

### Issue 5: Permission errors
**Cause:** GUI trying to write to system directories  
**Solution:** Ensure GUI uses user config directories (`~/.config/`)

## GUI Architecture Overview

The GUI consists of several components:

### Main Components
- **`ThemeApp`**: Main GTK4 application class
- **`MainWindow`**: Primary application window
- **`ThemeListBox`**: Widget for displaying available themes
- **`ThemePreviewWidget`**: Theme preview functionality
- **`ProgressDialog`**: Progress indication for theme operations
- **`SettingsDialog`**: Application settings

### Backend Integration
- **`UnifiedThemeManager`**: Core theme management
- **Theme Discovery**: Automatic theme detection
- **Progress Callbacks**: Real-time operation feedback
- **Error Handling**: User-friendly error messages

## Development Setup

### For GUI Development:

```bash
# 1. Install system dependencies (see Option 1 above)

# 2. Create development environment
python3 -m venv venv
source venv/bin/activate

# 3. Install with GUI dependencies
pip install -e ".[dev,gui]"

# 4. Test GUI launch
python -m unified_theming.gui.application

# 5. Run GUI-related tests
pytest tests/test_gui.py  # When available
```

### GUI Testing

Currently, GUI tests are not implemented due to GTK testing complexity. Consider:

1. **Manual testing** with real themes
2. **Backend unit tests** for core functionality
3. **Integration tests** for theme operations
4. **Mock GUI tests** for widget behavior

## Future Improvements

### Planned Enhancements
1. **Proper entry point** in pyproject.toml
2. **Fallback to CLI** when GUI unavailable
3. **Better error messages** for missing dependencies
4. **Containerized GUI** using Flatpak
5. **Web-based interface** as alternative

### Alternative Interfaces
1. **TUI (Terminal UI)** using Rich/Textual
2. **Web interface** using Flask/FastAPI
3. **Desktop integration** via D-Bus
4. **System tray** application

## Quick Fix Implementation

To immediately resolve the GUI issues:

1. **Add GUI entry point**
2. **Improve error handling** for missing dependencies
3. **Provide clear setup instructions**
4. **Test on multiple distributions**

---

**Current Status:** GUI functional but requires system dependencies  
**Recommended:** Use CLI for immediate functionality, install GTK4 for GUI  
**Priority:** Add proper entry point and dependency checking
