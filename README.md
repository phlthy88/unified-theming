# Unified Theming System

## Project Overview

Unified Theming is a comprehensive solution for applying consistent themes across GTK, Qt, and containerized applications on Linux. The project simplifies the complex task of theming Linux desktop applications by providing a unified interface to theme multiple GUI toolkits and application packaging formats (Flatpak, Snap).

## Features (Planned)
- **GTK 2/3/4 & Libadwaita:** Native theming via GSettings and CSS injection
- **Qt 5/6:** kdeglobals + Kvantum integration
- **Containerized Apps:** Support for Flatpak and Snap applications
- **Both CLI and GUI:** Full-featured command-line and modern GTK4/Libadwaita interfaces
- **Safety Features:** Automatic backup, rollback, validation, and graceful degradation

## Technology Stack

- **Language:** Python 3.10+
- **GUI Framework:** GTK4 + Libadwaita (for future GUI implementation)
- **CLI Framework:** Click
- **Testing:** pytest
- **Type Checking:** mypy
- **Linting:** flake8, black
- **Build System:** setuptools

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/unified-theming.git
cd unified-theming

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e ".[dev,gui]"
```

## Usage

```bash
# List available themes
unified-theme list

# Apply a theme
unified-theme apply <theme-name>

# Show current theme
unified-theme current

# Validate a theme
unified-theme validate <theme-name>

# Create backup
unified-theme backup create

# List backups
unified-theme backup list

# Restore from backup
unified-theme backup restore <backup-id>
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
git clone https://github.com/yourusername/unified-theming.git
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
- **Current Phase:** Phase 1 - Planning & Foundation (Complete)
- **Development Stage:** Architecture & Specification (Complete)
- **Next Phase:** Phase 2 - Core Engineering (Starting)

## License

[License information should be added here]