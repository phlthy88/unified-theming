# Unified Theming System

[![Tests](https://img.shields.io/badge/tests-181%20passing-brightgreen)](https://github.com/phlthy88/unified-theming)
[![Coverage](https://img.shields.io/badge/coverage-56%25-yellow)](https://github.com/phlthy88/unified-theming)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Project Overview

Unified Theming is a comprehensive solution for applying consistent themes across GTK, Qt, and containerized applications on Linux. The project simplifies the complex task of theming Linux desktop applications by providing a unified interface to theme multiple GUI toolkits and application packaging formats (Flatpak, Snap).

## Features
- ✅ **GTK 2/3/4 & Libadwaita:** Native theming via GSettings and CSS injection
- ✅ **Enhanced Libadwaita:** Automatic detection of LibAdapta (Linux Mint) and Zorin OS patches for 95% theming coverage
- ✅ **Qt 5/6:** kdeglobals generation with semantic color translation
- ✅ **Containerized Apps:** Full support for Flatpak applications
- ✅ **CLI Interface:** Full-featured command-line interface with Click
- ✅ **Safety Features:** Automatic backup, rollback, validation, and graceful degradation
- 🚧 **GUI Interface:** Modern GTK4/Libadwaita interface is under development.

## Technology Stack

- **Language:** Python 3.10+
- **GUI Framework:** GTK4 + Libadwaita (for future GUI implementation)
- **CLI Framework:** Click
- **Testing:** pytest
- **Type Checking:** mypy
- **Linting:** flake8, black
- **Build System:** setuptools

## Installation

### From Source (Recommended for v0.5.0)
```bash
git clone https://github.com/phlthy88/unified-theming.git
cd unified-theming

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e ".[dev,gui]"
```

### System Dependencies (Ubuntu/Debian)
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
```

## Usage

```bash
# List available themes
unified-theming list

# Apply a theme to all toolkits
unified-theming apply Adwaita-dark

# Apply to specific targets
unified-theming apply Nord --targets gtk4 --targets flatpak

# Show currently applied themes
unified-theming current

# Validate a theme's compatibility
unified-theming validate Dracula

# Rollback to previous configuration
unified-theming rollback

# List available backups
unified-theming rollback --list-backups
```

## Development

### Prerequisites
- Linux distribution (Ubuntu 22.04+, Fedora 37+, or equivalent)
- Python 3.10 or higher
- GTK 4.10+ development files
- Git

### Quick Start for Development
```bash
# Clone the repository
git clone https://github.com/phlthy88/unified-theming.git
cd unified-theming

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e ".[dev,gui]"

# Run tests to verify setup
pytest

# Run linting checks
black --check unified_theming/
flake8 unified_theming/
mypy unified_theming/
```

## Project Status

The project is currently in alpha. The CLI is feature-complete and stable, while the GUI is under active development.

### Next Milestones
- **GUI Development:** Implementation of the GTK4/Libadwaita interface.
- **v1.0 Release:** Official stable release with GUI and packaging.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

MIT License - See [LICENSE](LICENSE) file for details.