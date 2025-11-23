# Unified Theming System

[![Tests](https://img.shields.io/badge/tests-144%20passing-brightgreen)](https://github.com/phlthy88/unified-theming)
[![Coverage](https://img.shields.io/badge/coverage-48%25-yellow)](https://github.com/phlthy88/unified-theming)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/badge/release-v0.5.0-green)](https://github.com/phlthy88/unified-theming/releases)

## Project Overview

Unified Theming is a comprehensive Linux desktop application that applies consistent themes across GTK, Qt, and containerized applications. It simplifies the complex task of theming Linux desktops by providing a unified interface to theme multiple GUI toolkits (GTK2/3/4, libadwaita, Qt5/6) and container formats (Flatpak, Snap).

## Features

### Toolkit Support
- **GTK 2/3/4 & Libadwaita:** Native theming via GSettings and CSS injection
- **Enhanced Libadwaita:** Automatic detection of LibAdapta (Linux Mint) and Zorin OS patches for 95% theming coverage
- **Qt 5/6:** kdeglobals generation with semantic color translation + Kvantum support
- **Containerized Apps:** Full support for Flatpak applications, basic Snap support

### Interfaces
- **CLI Interface:** Full-featured command-line interface with Click
- **GUI Interface:** Modern GTK4/Libadwaita native GNOME-style interface

### Safety Features
- Automatic backup before theme changes
- Rollback to previous configurations
- Theme validation and compatibility checking
- Graceful degradation when toolkits are unavailable

## Screenshots

*GUI interface screenshots coming soon*

## Installation

### System Dependencies (Required First)

**Important:** You must install system dependencies BEFORE running `pip install` with the GUI option, as PyGObject requires native libraries to build.

**Ubuntu/Debian (22.04+):**
```bash
sudo apt install -y \
  libgtk-4-dev \
  libadwaita-1-dev \
  libgirepository1.0-dev \
  gir1.2-gtk-4.0 \
  python3-gi \
  python3-gi-cairo \
  pkg-config \
  python3-dev
```

**Debian 13+ / Ubuntu 24.04+ (with GObject Introspection 2.0):**
```bash
sudo apt install -y \
  libgtk-4-dev \
  libadwaita-1-dev \
  libgirepository-1.0-dev \
  gir1.2-gtk-4.0 \
  python3-gi \
  python3-gi-cairo \
  pkg-config \
  python3-dev
```

**Fedora/RHEL:**
```bash
sudo dnf install -y \
  gtk4-devel \
  libadwaita-devel \
  gobject-introspection-devel \
  python3-gobject \
  python3-cairo \
  pkg-config \
  python3-devel
```

**Arch Linux:**
```bash
sudo pacman -S \
  gtk4 \
  libadwaita \
  gobject-introspection \
  python-gobject \
  python-cairo \
  pkgconf
```

### From Source

```bash
# Clone the repository
git clone https://github.com/phlthy88/unified-theming.git
cd unified-theming

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install CLI only (no GUI dependencies)
pip install -e ".[dev]"

# OR install with GUI support (requires system dependencies above)
pip install -e ".[dev,gui]"
```

**Note:** If you only need the CLI interface, you can skip the system dependencies and use `pip install -e ".[dev]"` instead.

## Usage

### CLI Commands

```bash
# List available themes
unified-theming list

# Apply a theme to all toolkits
unified-theming apply_theme Adwaita-dark

# Preview changes without applying
unified-theming apply_theme Adwaita-dark --dry-run

# Apply to specific targets
unified-theming apply_theme Nord --targets gtk4 --targets flatpak

# Show currently applied themes
unified-theming current

# Validate a theme's compatibility
unified-theming validate Dracula

# Rollback to previous configuration
unified-theming rollback

# List available backups
unified-theming rollback --list-backups
```

### GUI Application

```bash
# Launch the GUI (requires GTK4/Libadwaita dependencies)
unified-theming-gui

# Or via Python module
python -m unified_theming.gui.launcher
```

The GUI provides:
- Visual theme browser with preview
- One-click theme application
- Settings management
- Backup/restore interface
- Real-time progress indicators

## Architecture

Unified Theming uses a **4-layer architecture**:

```
┌─────────────────────────────────────────────┐
│           User Interface Layer              │
│     CLI (Click) │ GUI (GTK4/Libadwaita)     │
├─────────────────────────────────────────────┤
│          Application Core Layer             │
│  Manager │ Parser │ Config │ Types          │
├─────────────────────────────────────────────┤
│          Toolkit Handler Layer              │
│  GTK │ Qt │ Flatpak │ Snap Handlers         │
├─────────────────────────────────────────────┤
│        System Integration Layer             │
│  Color Utils │ File Ops │ Validation        │
└─────────────────────────────────────────────┘
```

## Development

### Prerequisites
- Linux distribution (Ubuntu 22.04+, Fedora 37+, or equivalent)
- Python 3.10 or higher
- GTK 4.10+ development files (for GUI)
- Git

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=unified_theming --cov-report=html

# Run specific test file
pytest tests/test_parser.py

# Run without slow tests
pytest -m "not slow"
```

### Code Quality

```bash
# Format code (required before commits)
black unified_theming/

# Type check
mypy unified_theming/

# Lint code
flake8 unified_theming/

# Sort imports
isort unified_theming/
```

## Project Status

### Current Phase: Phase 2 - Core Engineering (~75% Complete)

| Component | Coverage | Status |
|-----------|----------|--------|
| color.py | 86% | Excellent |
| manager.py | 93% | Excellent |
| config.py | 75% | Good |
| flatpak_handler.py | 100% | Excellent |
| parser.py | 87% | Excellent |
| **Overall** | **48%** | In Progress |

### Test Suite
- **144 tests** passing (99.3% pass rate)
- Comprehensive unit tests for core modules
- Integration tests available

### What's Working
- Theme discovery across all standard locations
- GTK2/3/4 theme application
- Libadwaita CSS injection (70% coverage)
- Qt kdeglobals generation
- Flatpak theme overrides
- Backup/restore functionality
- CLI commands (all functional)
- GUI interface (GTK4/Libadwaita)

### Known Limitations
- Libadwaita: 70% coverage (colors only, no widget structure changes)
- Qt translation: Approximate (GTK and Qt have different color models)
- Snap: Basic support (76% coverage, limited by Snap permissions)

## Roadmap

- **v0.5.0** (Current): CLI alpha release with basic GUI
- **v0.9.0**: GUI beta with full feature parity
- **v1.0.0**: Production release with packaging (Flatpak/AppImage)

## Contributing

Contributions are welcome! This project uses a multi-agent development workflow.

```bash
# Setup development environment
git clone https://github.com/phlthy88/unified-theming.git
cd unified-theming
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev,gui]"

# Run tests before submitting
pytest
black --check unified_theming/
mypy unified_theming/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Documentation

- [Requirements Specification](docs/requirements_specification.md) - What the system does
- [Architecture Guide](docs/architecture.md) - How the system is designed
- [Developer Guide](docs/developer_guide.md) - How to develop for the system
- [CLAUDE.md](CLAUDE.md) - Claude Code integration guide
- [GUI Setup](docs/GUI_SETUP_AND_TROUBLESHOOTING.md) - GUI installation help

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| GUI Framework | GTK4 + Libadwaita |
| CLI Framework | Click |
| Testing | pytest |
| Type Checking | mypy (strict mode) |
| Formatting | Black, isort |
| Linting | flake8 |

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with multi-agent collaboration:
- **Claude Code:** Architecture, design, documentation
- **Qwen Coder:** Implementation, testing
- **Opencode AI:** QA validation, packaging
