# Unified Theming Application - Development Context

## Project Overview

Unified Theming is a comprehensive solution for applying consistent themes across GTK, Qt, and containerized applications on Linux. The project is designed to simplify the complex task of theming Linux desktop applications by providing a unified interface to theme multiple GUI toolkits and application packaging formats (Flatpak, Snap).

### Project Status
- **Current Phase:** Phase 1 - Planning & Foundation (Complete)
- **Development Stage:** Architecture & Specification (Complete)
- **Next Phase:** Phase 2 - Core Engineering (Starting)

### Features (Planned)
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

## System Requirements

- Python 3.10+
- GTK 4.10+
- Qt 5.15+ or Qt 6.2+ (optional)
- Flatpak 1.12+ (optional)
- Snapd (optional)

## Architecture Overview

The application follows a 4-layer architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────┐              ┌──────────────┐            │
│  │   CLI Tool   │              │  GUI (GTK4)  │            │
│  │   (Click)    │              │ (Libadwaita) │            │
│  └──────┬───────┘              └──────┬───────┘            │
│         │                             │                     │
│         └─────────────┬───────────────┘                     │
└───────────────────────┼─────────────────────────────────────┘
                        │
┌───────────────────────┼─────────────────────────────────────┐
│              Application Core Layer                          │
│                        │                                     │
│         ┌──────────────▼──────────────┐                     │
│         │  UnifiedThemeManager        │                     │
│         │  - Orchestrate operations   │                     │
│         │  - Handle state/transactions│                     │
│         │  - Coordinate handlers      │                     │
│         │  - Error aggregation        │                     │
│         └──────────────┬──────────────┘                     │
│                        │                                     │
│         ┌──────────────┴──────────────┐                     │
│         │                              │                     │
│    ┌────▼─────┐                  ┌────▼────┐               │
│    │  Theme   │                  │ Config  │               │
│    │  Parser  │                  │ Manager │               │
│    │          │                  │         │               │
│    │ - Scan   │                  │ - Backup│               │
│    │ - Parse  │                  │ - State │               │
│    │ - Extract│                  │ - Restore│              │
│    │ - Validate                  │         │               │
│    └────┬─────┘                  └────┬────┘               │
└─────────┼──────────────────────────────┼───────────────────┘
          │                              │
┌─────────┼──────────────────────────────┼───────────────────┐
│    Toolkit Handler Layer               │                    │
│         │                              │                    │
│    ┌────▼──────────┐  ┌───────────────▼──────┐            │
│    │ GTK Handler   │  │  Qt Handler           │            │
│    │               │  │                       │            │
│    │ ├─ GTK2/3     │  │  ├─ kdeglobals        │            │
│    │ │  (GSettings)│  │  ├─ Kvantum           │            │
│    │ ├─ GTK4       │  │  ├─ qt5ct/qt6ct       │            │
│    │ │  (CSS link) │  │  └─ Color translation │            │
│    │ └─ libadwaita │  │                       │            │
│    │    (CSS inject│  │                       │            │
│    └───────────────┘  └──────────────────────┘            │
│                                                             │
│    ┌─────────────────────────────────────────┐            │
│    │       Container Handler                  │            │
│    │                                          │            │
│    │  ├─ Flatpak Handler                     │            │
│    │  │  ├─ Portal configuration             │            │
│    │  │  ├─ Filesystem overrides             │            │
│    │  │  └─ Environment variables            │            │
│    │  │                                      │            │
│    │  └─ Snap Handler                        │            │
│    │     ├─ Interface connections            │            │
│    │     ├─ Portal integration               │            │
│    │     └─ Theme access configuration       │            │
│    └─────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
          │                              │
┌─────────┼──────────────────────────────┼───────────────────┐
│    System Integration Layer            │                    │
│         │                              │                    │
│    ┌────▼─────┐  ┌─────────┐    ┌─────▼────┐              │
│    │ GSettings│  │  File   │    │Subprocess│              │
│    │  / dconf │  │ System  │    │  Manager │              │
│    │          │  │ Monitor │    │          │              │
│    │ - Read   │  │         │    │ - Launch │              │
│    │ - Write  │  │ - Watch │    │ - Monitor│              │
│    │ - Listen │  │ - Events│    │ - Control│              │
│    └──────────┘  └─────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Unified Theme Manager
- Central orchestrator for all theme operations
- Transaction-like behavior (all-or-nothing with rollback)
- Error aggregation and reporting
- State management
- Handler coordination

### 2. Theme Parser
- Theme discovery across directories
- Metadata extraction
- Color palette parsing
- Theme validation

### 3. Config Manager
- Configuration backup
- State persistence
- Backup management (pruning old backups)
- State restoration

### 4. Toolkit Handlers
- **GTK Handler:** GTK2/3/4 and libadwaita theming
- **Qt Handler:** Qt5/6 theming via kdeglobals and Kvantum
- **Flatpak Handler:** Flatpak application theming
- **Snap Handler:** Snap application theming

## Data Structures

The project uses comprehensive data classes defined in `unified_theming/core/types.py`, including:
- `ThemeInfo`: Complete information about a discovered theme
- `ThemeData`: Theme data prepared for application to a specific toolkit
- `ValidationResult`: Result of theme validation
- `ApplicationResult`: Aggregated result of theme application
- `Backup`: Configuration backup representation
- `HandlerResult`: Result of a single handler's theme application

## Exception Hierarchy

All exceptions inherit from `UnifiedThemingError` and include:
- Theme discovery and parsing errors
- Theme application errors
- Configuration and backup errors
- File system errors
- Validation errors
- System integration errors

## Development Setup

### Prerequisites
- Linux distribution (Ubuntu 22.04+, Fedora 37+, or equivalent)
- Python 3.10 or higher
- GTK 4.10+ development files
- Git

### Quick Start
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

## Code Quality Standards

- **Type Hints:** Complete type hints with mypy validation
- **Code Style:** Black for formatting, isort for imports
- **Documentation:** Google-style docstrings
- **Testing:** Minimum 80% test coverage (90%+ for core modules)

## Current Implementation Status

Phase 1 (Planning & Foundation) is complete:
- ✅ Complete requirements specification
- ✅ System architecture design
- ✅ Type system implemented
- ✅ Exception hierarchy implemented
- ✅ Logging configuration implemented
- ✅ CLI interface specification
- ✅ Project structure created

Phase 2 (Core Engineering) implementation priorities:
1. **UnifiedThemeParser** (CRITICAL PATH)
2. **LibadwaitaHandler** (HIGH PRIORITY)
3. **QtThemeHandler** (HIGH PRIORITY)
4. **Integration Testing**

## Performance Requirements

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Theme discovery (100 themes) | <5s | Time to complete `discover_themes()` |
| Single theme parsing | <50ms | Time to complete `parse_theme()` |
| Color extraction | <20ms | Time to complete `extract_colors()` |
| Theme application | <2s | Time from `apply_theme()` call to completion |
| CSS generation | <100ms | Time to generate libadwaita CSS |
| kdeglobals generation | <100ms | Time to generate Qt config |

## Key Files and Locations

- **Requirements:** `docs/requirements_specification.md`
- **Architecture:** `docs/architecture.md`
- **Developer Guide:** `docs/developer_guide.md`
- **Type System:** `unified_theming/core/types.py`
- **Exceptions:** `unified_theming/core/exceptions.py`
- **Logging:** `unified_theming/utils/logging_config.py`
- **CLI Spec:** `unified_theming/cli/commands.py`

## Next Steps for Development

Phase 2 implementation priorities:
1. Implement UnifiedThemeParser
2. Implement GTKHandler (with libadwaita CSS injection)
3. Implement QtHandler (kdeglobals + Kvantum)
4. Implement UnifiedThemeManager
5. Implement ConfigManager
6. Write comprehensive tests
7. Performance optimization