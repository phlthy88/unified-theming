# Unified Theming Project: Three-Agent Workflow

## Overview

This document details the orchestrated workflow between three AI agents, each leveraging their specific strengths to build a production-ready unified theming application.

**Agent Roles:**
- **Claude (Sonnet 4.5)**: Planning, Architecture, Documentation
- **Qwen Coder**: Core Implementation, Engineering
- **Opencode AI**: Integration, Packaging, Release

---

## Phase 1: Planning & Foundation (Claude Code)

**Duration**: 4-6 weeks  
**Agent**: Claude (Sonnet 4.5)  
**Focus**: Strategic planning, system design, specifications

### Week 1-2: Requirements & Architecture

#### Deliverable 1.1: Project Requirements Document

```markdown
# Unified Theming Application - Requirements Specification

## Functional Requirements

### FR-1: Theme Discovery & Parsing
- **FR-1.1**: Scan standard theme directories (~/.themes, /usr/share/themes)
- **FR-1.2**: Parse GTK2, GTK3, GTK4 theme metadata
- **FR-1.3**: Extract color palettes from CSS files
- **FR-1.4**: Validate theme structure and completeness

### FR-2: Cross-Toolkit Theming
- **FR-2.1**: Apply themes to GTK2/GTK3 applications
- **FR-2.2**: Apply themes to GTK4/libadwaita via CSS injection
- **FR-2.3**: Translate and apply themes to Qt5/Qt6 applications
- **FR-2.4**: Handle Flatpak application theming
- **FR-2.5**: Handle Snap application theming

### FR-3: Theme Application
- **FR-3.1**: Apply themes system-wide
- **FR-3.2**: Apply themes per-application (overrides)
- **FR-3.3**: Preview themes before application
- **FR-3.4**: Rollback to previous theme configuration

### FR-4: Error Handling & Recovery
- **FR-4.1**: Backup existing configurations
- **FR-4.2**: Detect and report incompatible themes
- **FR-4.3**: Graceful degradation when toolkit unavailable
- **FR-4.4**: Restore previous state on failure

## Non-Functional Requirements

### NFR-1: Performance
- Theme switching < 2 seconds
- Discovery scan < 5 seconds
- Memory usage < 100MB

### NFR-2: Compatibility
- GTK 4.10+ support
- Qt 5.15+ or Qt 6.2+ support
- Python 3.10+ runtime
- Wayland and X11 session support

### NFR-3: Usability
- CLI for power users
- GUI for general users
- Clear error messages
- Comprehensive documentation

### NFR-4: Maintainability
- Modular architecture
- 80%+ test coverage
- Type hints throughout
- API documentation
```

#### Deliverable 1.2: System Architecture Diagram

```python
"""
System Architecture for Unified Theming Application

┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                          │
│  ┌──────────────┐              ┌──────────────┐            │
│  │   CLI Tool   │              │  GUI (GTK4)  │            │
│  └──────┬───────┘              └──────┬───────┘            │
│         │                             │                     │
│         └─────────────┬───────────────┘                     │
└───────────────────────┼─────────────────────────────────────┘
                        │
┌───────────────────────┼─────────────────────────────────────┐
│               Core Application Layer                         │
│                        │                                     │
│         ┌──────────────▼──────────────┐                     │
│         │  UnifiedThemeManager        │                     │
│         │  - Orchestrate operations   │                     │
│         │  - Handle state            │                     │
│         │  - Coordinate handlers     │                     │
│         └──────────────┬──────────────┘                     │
│                        │                                     │
│         ┌──────────────┴──────────────┐                     │
│         │                              │                     │
│    ┌────▼─────┐                  ┌────▼────┐               │
│    │  Theme   │                  │ Config  │               │
│    │  Parser  │                  │ Manager │               │
│    └────┬─────┘                  └────┬────┘               │
└─────────┼──────────────────────────────┼───────────────────┘
          │                              │
┌─────────┼──────────────────────────────┼───────────────────┐
│    Toolkit Handler Layer               │                    │
│         │                              │                    │
│    ┌────▼──────────┐  ┌───────────────▼──────┐            │
│    │ GTK Handler   │  │  Qt Handler           │            │
│    │ ├─ GTK2/3     │  │  ├─ kdeglobals        │            │
│    │ ├─ GTK4       │  │  ├─ Kvantum           │            │
│    │ └─ libadwaita │  │  └─ qt5ct/qt6ct       │            │
│    └───────────────┘  └──────────────────────┘            │
│                                                             │
│    ┌─────────────────────────────────────────┐            │
│    │       Container Handler                  │            │
│    │  ├─ Flatpak (portals, overrides)        │            │
│    │  └─ Snap (interfaces, portals)          │            │
│    └─────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
          │                              │
┌─────────┼──────────────────────────────┼───────────────────┐
│    System Integration Layer            │                    │
│         │                              │                    │
│    ┌────▼─────┐  ┌─────────┐    ┌─────▼────┐              │
│    │ GSettings│  │FileSystem│    │ Subprocess│              │
│    │ / dconf  │  │ Monitor  │    │  Manager │              │
│    └──────────┘  └─────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────┘

Data Flow:
1. User selects theme → UnifiedThemeManager
2. ThemeParser extracts theme data
3. ConfigManager backs up current state
4. Toolkit handlers apply theme to respective toolkits
5. Container handlers configure sandboxed apps
6. System integration commits changes
7. Feedback provided to user
"""
```

#### Deliverable 1.3: Module Structure & API Specifications

```
unified_theming/
├── __init__.py
├── __main__.py                 # Entry point
├── core/
│   ├── __init__.py
│   ├── manager.py              # UnifiedThemeManager
│   ├── parser.py               # ThemeParser
│   ├── config.py               # ConfigManager
│   └── exceptions.py           # Custom exceptions
├── handlers/
│   ├── __init__.py
│   ├── gtk_handler.py          # GTK2/3/4/libadwaita
│   ├── qt_handler.py           # Qt5/6 + Kvantum
│   ├── flatpak_handler.py      # Flatpak theming
│   └── snap_handler.py         # Snap theming
├── utils/
│   ├── __init__.py
│   ├── color.py                # Color utilities
│   ├── file.py                 # File operations
│   └── validation.py           # Theme validation
├── cli/
│   ├── __init__.py
│   └── commands.py             # CLI interface
├── gui/
│   ├── __init__.py
│   ├── window.py               # Main window
│   ├── widgets.py              # Custom widgets
│   └── dialogs.py              # Dialogs
└── tests/
    ├── __init__.py
    ├── test_parser.py
    ├── test_handlers.py
    └── fixtures/                # Test themes
```

**API Specifications:**

```python
# core/manager.py API Specification

from typing import Dict, List, Optional
from pathlib import Path

class UnifiedThemeManager:
    """
    Central orchestrator for unified theming operations.
    
    Responsibilities:
    - Coordinate theme operations across toolkits
    - Manage application state
    - Handle errors and rollback
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        enable_backup: bool = True
    ):
        """
        Initialize theme manager.
        
        Args:
            config_path: Path to configuration directory
            enable_backup: Whether to backup configurations
        """
        pass
    
    def discover_themes(self) -> Dict[str, 'ThemeInfo']:
        """
        Discover all available themes.
        
        Returns:
            Dictionary mapping theme names to ThemeInfo objects
            
        Raises:
            ThemeDiscoveryError: If theme scanning fails
        """
        pass
    
    def apply_theme(
        self,
        theme_name: str,
        targets: Optional[List[str]] = None
    ) -> 'ApplicationResult':
        """
        Apply theme to specified targets.
        
        Args:
            theme_name: Name of theme to apply
            targets: List of toolkit targets (None = all)
                    Options: ['gtk2', 'gtk3', 'gtk4', 'libadwaita', 
                             'qt5', 'qt6', 'flatpak', 'snap']
        
        Returns:
            ApplicationResult with success status per target
            
        Raises:
            ThemeNotFoundError: If theme doesn't exist
            ThemeApplicationError: If application fails
        """
        pass
    
    def preview_theme(
        self,
        theme_name: str,
        apps: Optional[List[str]] = None
    ) -> None:
        """
        Launch preview applications with theme.
        
        Args:
            theme_name: Theme to preview
            apps: Applications to launch for preview
        """
        pass
    
    def rollback(self) -> bool:
        """
        Rollback to previous theme configuration.
        
        Returns:
            True if rollback successful
        """
        pass
    
    def get_current_themes(self) -> Dict[str, str]:
        """
        Get currently applied themes per toolkit.
        
        Returns:
            Dictionary mapping toolkit to theme name
        """
        pass
```

```python
# core/parser.py API Specification

class ThemeParser:
    """
    Parse and extract information from theme directories.
    """
    
    def parse_theme(self, theme_path: Path) -> 'ThemeInfo':
        """
        Parse theme and extract metadata.
        
        Args:
            theme_path: Path to theme directory
            
        Returns:
            ThemeInfo object with theme data
            
        Raises:
            InvalidThemeError: If theme structure invalid
        """
        pass
    
    def extract_colors(
        self,
        theme_path: Path,
        toolkit: str
    ) -> Dict[str, str]:
        """
        Extract color palette from theme.
        
        Args:
            theme_path: Path to theme directory
            toolkit: Toolkit to extract colors for
            
        Returns:
            Dictionary of color variable names to values
        """
        pass
    
    def validate_theme(
        self,
        theme_path: Path
    ) -> 'ValidationResult':
        """
        Validate theme structure and completeness.
        
        Args:
            theme_path: Path to theme directory
            
        Returns:
            ValidationResult with warnings and errors
        """
        pass
```

### Week 3-4: Error Handling & Logging Design

#### Deliverable 1.4: Exception Hierarchy

```python
# core/exceptions.py

class UnifiedThemingError(Exception):
    """Base exception for all unified theming errors."""
    pass

class ThemeDiscoveryError(UnifiedThemingError):
    """Raised when theme discovery fails."""
    pass

class ThemeNotFoundError(UnifiedThemingError):
    """Raised when requested theme doesn't exist."""
    pass

class InvalidThemeError(UnifiedThemingError):
    """Raised when theme structure is invalid."""
    pass

class ThemeApplicationError(UnifiedThemingError):
    """Raised when theme application fails."""
    
    def __init__(
        self,
        message: str,
        toolkit: str,
        recoverable: bool = True
    ):
        super().__init__(message)
        self.toolkit = toolkit
        self.recoverable = recoverable

class BackupError(UnifiedThemingError):
    """Raised when configuration backup fails."""
    pass

class RollbackError(UnifiedThemingError):
    """Raised when rollback operation fails."""
    pass

class ConfigurationError(UnifiedThemingError):
    """Raised when configuration is invalid."""
    pass
```

#### Deliverable 1.5: Logging Strategy

```python
# utils/logging_config.py

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> None:
    """
    Configure application-wide logging.
    
    Log Levels by Component:
    - DEBUG: Detailed diagnostic information
    - INFO: General informational messages
    - WARNING: Non-critical issues (theme compatibility)
    - ERROR: Errors that prevent operations
    - CRITICAL: System-breaking errors
    
    Log Format:
    [TIMESTAMP] [LEVEL] [MODULE:FUNCTION] Message
    
    Example:
    [2025-10-20 10:30:45] [INFO] [manager:apply_theme] Applying theme 'Nord'
    [2025-10-20 10:30:45] [DEBUG] [gtk_handler:apply] Writing GTK CSS to ~/.config/gtk-4.0/gtk.css
    [2025-10-20 10:30:46] [WARNING] [qt_handler:apply] Kvantum not installed, using kdeglobals only
    [2025-10-20 10:30:46] [INFO] [manager:apply_theme] Theme applied successfully
    """
    
    logger = logging.getLogger('unified_theming')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
```

### Week 5-6: CLI Prototype & Documentation

#### Deliverable 1.6: CLI Specification

```python
# cli/commands.py

import click
from typing import Optional, List

@click.group()
@click.option('--verbose', '-v', count=True, help='Increase verbosity')
@click.option('--config', type=click.Path(), help='Config file path')
@click.pass_context
def cli(ctx, verbose: int, config: Optional[str]):
    """Unified Theming Application - Apply themes across toolkits."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config

@cli.command()
@click.option('--toolkit', '-t', multiple=True,
              type=click.Choice(['gtk2', 'gtk3', 'gtk4', 'libadwaita', 'qt5', 'qt6', 'all']),
              help='Filter by toolkit')
def list(toolkit: tuple):
    """List all available themes."""
    pass

@cli.command()
@click.argument('theme_name')
@click.option('--targets', '-t', multiple=True,
              type=click.Choice(['gtk2', 'gtk3', 'gtk4', 'libadwaita', 
                               'qt5', 'qt6', 'flatpak', 'snap', 'all']),
              default=['all'],
              help='Target toolkits')
@click.option('--preview', '-p', is_flag=True, help='Preview before applying')
@click.option('--backup/--no-backup', default=True, help='Backup current config')
def apply(theme_name: str, targets: tuple, preview: bool, backup: bool):
    """Apply THEME_NAME to specified targets."""
    pass

@cli.command()
@click.argument('theme_name')
@click.option('--apps', '-a', multiple=True, help='Apps to launch for preview')
def preview(theme_name: str, apps: tuple):
    """Preview THEME_NAME without applying."""
    pass

@cli.command()
def rollback():
    """Rollback to previous theme configuration."""
    pass

@cli.command()
def current():
    """Show currently applied themes."""
    pass

@cli.command()
@click.argument('theme_name')
def validate(theme_name: str):
    """Validate THEME_NAME structure and compatibility."""
    pass

# Example Usage:
# $ unified-theming list
# $ unified-theming list --toolkit gtk4
# $ unified-theming apply Nord --targets gtk4 --targets libadwaita
# $ unified-theming preview Nord --apps gnome-calculator --apps nautilus
# $ unified-theming current
# $ unified-theming rollback
# $ unified-theming validate Nord
```

#### Deliverable 1.7: Initial Developer Documentation

```markdown
# Developer Guide - Unified Theming Application

## Getting Started

### Prerequisites
- Python 3.10+
- GTK 4.10+
- Qt 5.15+ or Qt 6.2+
- Git

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/unified-theming.git
cd unified-theming

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 unified_theming/
mypy unified_theming/
```

## Architecture Overview

[Include architecture diagram from Deliverable 1.2]

## Module Guidelines

### Adding a New Handler

1. Create handler class in `handlers/`
2. Inherit from `BaseHandler`
3. Implement required methods:
   - `apply_theme(theme_data: ThemeData) -> bool`
   - `get_current_theme() -> str`
   - `validate_compatibility(theme_data: ThemeData) -> ValidationResult`

Example:

```python
from handlers.base import BaseHandler
from core.types import ThemeData, ValidationResult

class NewToolkitHandler(BaseHandler):
    """Handler for NewToolkit applications."""
    
    def apply_theme(self, theme_data: ThemeData) -> bool:
        """Apply theme to NewToolkit apps."""
        # Implementation
        pass
    
    def get_current_theme(self) -> str:
        """Get currently applied theme name."""
        # Implementation
        pass
    
    def validate_compatibility(
        self,
        theme_data: ThemeData
    ) -> ValidationResult:
        """Check if theme is compatible with NewToolkit."""
        # Implementation
        pass
```

4. Register handler in `core/manager.py`
5. Add tests in `tests/test_new_handler.py`
6. Update documentation

### Color Translation

When translating colors between toolkits, use `utils/color.py`:

```python
from utils.color import ColorTranslator

translator = ColorTranslator()

# GTK to Qt
qt_colors = translator.gtk_to_qt(gtk_colors)

# Normalize color format
normalized = translator.normalize('#rgb', output_format='hex')
```

## Testing Guidelines

### Unit Tests

Test each handler independently:

```python
# tests/test_gtk_handler.py

import pytest
from handlers.gtk_handler import GTKHandler
from core.types import ThemeData

def test_gtk_handler_apply(tmp_path):
    """Test GTK theme application."""
    handler = GTKHandler(config_dir=tmp_path)
    
    theme_data = ThemeData(
        name='TestTheme',
        colors={'theme_bg_color': '#ffffff'}
    )
    
    result = handler.apply_theme(theme_data)
    assert result is True
    
    # Verify files created
    assert (tmp_path / 'gtk-4.0' / 'gtk.css').exists()
```

### Integration Tests

Test cross-handler interactions:

```python
# tests/test_integration.py

def test_full_theme_application(manager, test_theme):
    """Test applying theme across all handlers."""
    result = manager.apply_theme('TestTheme')
    
    assert result.gtk_success is True
    assert result.qt_success is True
    assert result.libadwaita_success is True
```

## Code Style

- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters (Black formatter)
- Docstrings: Google style

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is empty
    """
    pass
```
```

### Phase 1 Handoff Package

**Files to deliver to Qwen Coder:**

1. `requirements_specification.md` - Complete requirements
2. `architecture_diagram.py` - System architecture with ASCII diagrams
3. `api_specifications.py` - All API interfaces with type hints
4. `exception_hierarchy.py` - Complete exception classes
5. `logging_config.py` - Logging setup and guidelines
6. `cli_specification.py` - CLI interface with Click decorators
7. `developer_guide.md` - Development setup and guidelines
8. `module_structure.txt` - File/directory layout

**Handoff Checklist:**
- [ ] All specifications reviewed and approved
- [ ] API contracts clearly defined
- [ ] Error handling strategy documented
- [ ] Logging strategy implemented
- [ ] CLI prototype tested manually
- [ ] Developer guide comprehensive
- [ ] Test fixtures prepared

**Communication to Qwen Coder:**

```
HANDOFF: Phase 1 → Phase 2

Status: Planning & Foundation Complete

Delivered Artifacts:
- Complete requirements specification (functional & non-functional)
- System architecture with clear module boundaries
- API specifications for all core components
- Exception hierarchy and error handling strategy
- Logging configuration and guidelines
- CLI interface prototype
- Developer documentation

Implementation Priorities for Phase 2:
1. UnifiedThemeParser (core/parser.py) - CRITICAL PATH
2. LibadwaitaHandler (handlers/gtk_handler.py) - HIGH PRIORITY
3. QtThemeHandler (handlers/qt_handler.py) - HIGH PRIORITY
4. ThemeTester (tests/) - MEDIUM PRIORITY
5. Flatpak/Snap handlers - LOWER PRIORITY (defer if time-constrained)

Key Design Decisions:
- CSS injection for libadwaita (not patching in MVP)
- kdeglobals + Kvantum for Qt theming
- Backup-first strategy for all operations
- Graceful degradation when toolkit unavailable

Testing Requirements:
- 80%+ code coverage minimum
- Integration tests for cross-handler interactions
- Test fixtures for multiple theme formats

Questions/Clarifications:
[Space for Qwen Coder to ask questions before starting]

Expected Phase 2 Duration: 8-10 weeks
```

---

## Phase 2: Core Engineering (Qwen Coder)

**Duration**: 8-10 weeks  
**Agent**: Qwen Coder  
**Focus**: Implementation, testing, performance optimization

### Week 1-2: Core Theme Parser

#### Implementation Tasks

1. **UnifiedThemeParser Implementation**
   - Theme discovery across standard directories
   - CSS parsing for GTK themes
   - INI parsing for Qt themes
   - Color extraction with fallbacks
   - Metadata validation

2. **ThemeInfo Data Structure**
   ```python
   @dataclass
   class ThemeInfo:
       name: str
       path: Path
       supported_toolkits: List[str]
       colors: Dict[str, str]
       metadata: Dict[str, Any]
       validation_result: ValidationResult
   ```

3. **Test Suite**
   - Unit tests for each parsing function
   - Test fixtures with real theme samples
   - Edge case handling tests
   - Performance benchmarks

**Expected Output:**
- Fully functional parser with 90%+ test coverage
- Performance: <5s for scanning 100+ themes
- Comprehensive error messages for invalid themes

### Week 3-4: GTK/Libadwaita Handler

#### Implementation Tasks

1. **GTK2/3 Support**
   - GSettings integration
   - Theme symlink management
   - Icon theme coordination

2. **GTK4/Libadwaita CSS Injection**
   - CSS generation from color palette
   - Backup and restoration logic
   - App notification mechanism
   - Validation of generated CSS

3. **Testing**
   - Test with GNOME applications
   - Verify CSS syntax
   - Test backup/restore cycle

**Expected Output:**
- Complete GTK handler with CSS injection
- Automatic backup before changes
- Rollback capability tested
- Documentation of color mappings

### Week 5-6: Qt Handler & Color Translation

#### Implementation Tasks

1. **Qt Handler Implementation**
   - kdeglobals file generation
   - Kvantum theme creation
   - qt5ct/qt6ct configuration
   - Environment variable setup

2. **Color Translation Engine**
   - GTK → Qt color mapping
   - Color format normalization
   - Derived color generation
   - Semantic color translation

3. **Testing**
   - Test with KDE applications
   - Test with Qt5 and Qt6 apps separately
   - Verify color accuracy
   - Test Kvantum theme loading

**Expected Output:**
- Functional Qt handler
- Accurate color translation (>90% visual match)
- Support for both Qt5 and Qt6
- Performance: <500ms theme generation

### Week 7-8: Container Handlers & Testing Framework

#### Implementation Tasks

1. **Flatpak Handler**
   - Portal configuration
   - Filesystem overrides
   - Environment variables
   - Per-app theming support

2. **Snap Handler**
   - Interface connections
   - Portal integration
   - Theme access configuration

3. **ThemeTester Framework**
   - Automated app launching
   - Screenshot comparison (optional)
   - Error detection
   - Compatibility reporting

**Expected Output:**
- Flatpak handler with 70% success rate
- Snap handler with 65% success rate
- Automated testing suite
- Test reports in JSON/HTML format

### Week 9-10: Integration & Documentation

#### Implementation Tasks

1. **UnifiedThemeManager Integration**
   - Coordinate all handlers
   - Implement transaction-like operations
   - Error aggregation and reporting
   - State management

2. **Performance Optimization**
   - Profile critical paths
   - Optimize file I/O
   - Cache theme data
   - Parallel handler execution (if safe)

3. **Engineering Documentation**
   - Code comments and docstrings
   - Implementation notes
   - Performance characteristics
   - Known limitations

**Expected Output:**
- Integrated system with all components working
- Performance meets specifications
- Complete code documentation
- Known issues documented

### Phase 2 Handoff Package

**Files to deliver to Opencode AI:**

1. Complete source code (`unified_theming/`)
2. Test suite with 80%+ coverage (`tests/`)
3. Performance benchmarks and profiling results
4. Engineering notes on implementation decisions
5. Known issues and workarounds
6. API documentation (generated from docstrings)

**Handoff Checklist:**
- [ ] All core modules implemented and tested
- [ ] Integration tests passing
- [ ] Performance requirements met
- [ ] Code reviewed and documented
- [ ] Known limitations documented
- [ ] Build/install process tested locally

**Communication to Opencode AI:**

```
HANDOFF: Phase 2 → Phase 3

Status: Core Engineering Complete

Implemented Components:
✅ UnifiedThemeParser - Theme discovery and parsing
✅ LibadwaitaHandler - GTK4/libadwaita CSS injection
✅ QtThemeHandler - Qt5/6 theming with kdeglobals/Kvantum
✅ FlatpakHandler - Flatpak portal configuration
✅ SnapHandler - Snap interface management
✅ ThemeTester - Automated testing framework
✅ UnifiedThemeManager - Central coordinator

Test Coverage: 82%
Performance: All benchmarks met
Known Issues: 3 minor (documented in KNOWN_ISSUES.md)

Integration Needs for Phase 3:
1. CLI integration - Connect commands to UnifiedThemeManager
2. GUI development - Build on implemented backend
3. Packaging - Create installable formats
4. CI/CD - Automated testing and builds
5. Documentation - User guides and tutorials

Build Instructions:
```bash
pip install -e .
pytest  # All tests should pass
```

Deployment Considerations:
- Requires GTK 4.10+ and Qt 5.15+/6.2+
- Optional dependencies: Kvantum, Flatpak, Snapd
- Config location: ~/.config/unified-theming/

Suggested GUI Framework: GTK4 + Libadwaita (dogfooding)

Next Steps:
1. Review codebase and test locally
2. Develop GUI interface
3. Create packaging for Flatpak, PPA, AUR
4. Write user documentation
5. Set up CI/CD pipeline

Questions/Feedback:
[Space for Opencode AI to provide feedback]

Estimated Phase 3 Duration: 6-8 weeks
```

---

## Phase 3: Integration & Release (Opencode AI)

**Duration**: 6-8 weeks  
**Agent**: Opencode AI  
**Focus**: Integration, packaging, release engineering

### Week 1-2: GUI Development

#### Implementation Tasks

1. **Main Window (GTK4/Libadwaita)**
   - Navigation sidebar with theme list
   - Theme details pane with preview
   - Settings and preferences
   - About dialog

2. **Theme Browser**
   - Thumbnail previews
   - Filter by toolkit support
   - Search functionality
   - Theme metadata display

3. **Application Dialog**
   - Theme application progress
   - Per-toolkit status
   - Error reporting with recovery options
   - Rollback option

4. **Preview System**
   - Live color swatches
   - Sample UI elements
   - Optional app launching

**Expected Output:**
- Functional GTK4 GUI
- Intuitive user experience
- Progress feedback during operations
- Error handling with user-friendly messages

### Week 3-4: Packaging & Distribution

#### Implementation Tasks

1. **Flatpak Packaging**
   - Create Flatpak manifest
   - Bundle all dependencies
   - Test sandbox restrictions
   - Submit to Flathub (if approved)

2. **Debian/Ubuntu PPA**
   - Create debian/ directory
   - Write maintainer scripts
   - Build source package
   - Set up Launchpad PPA

3. **Arch AUR**
   - Write PKGBUILD
   - Test on clean Arch system
   - Submit to AUR

4. **AppImage (optional)**
   - Create AppImage recipe
   - Test portability
   - Publish to AppImageHub

**Expected Output:**
- Flatpak package tested and working
- Ubuntu PPA with installable package
- AUR package available
- Installation instructions for each format

### Week 5-6: CI/CD & Documentation

#### Implementation Tasks

1. **GitHub Actions Pipeline**
   ```yaml
   # .github/workflows/ci.yml
   name: CI
   
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
           with:
             python-version: '3.10'
         - run: pip install -e ".[dev]"
         - run: pytest --cov
         - run: flake8 unified_theming/
         - run: mypy unified_theming/
     
     build-flatpak:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: flatpak/flatpak-github-actions/flatpak-builder@v4
           with:
             bundle: unified-theming.flatpak
             manifest-path: com.example.UnifiedTheming.json
   ```

2. **User Documentation**
   - Installation guide for each platform
   - Quick start tutorial
   - Theme creation guide
   - FAQ and troubleshooting

3. **Contributor Documentation**
   - Contributing guidelines
   - Code of conduct
   - Issue templates
   - Pull request template

4. **Release Process**
   - Automated versioning
   - Changelog generation
   - GitHub releases
   - Distribution updates

**Expected Output:**
- Automated CI/CD pipeline
- Complete user documentation
- Contributor-friendly repository
- Streamlined release process

### Week 7-8: Release & Community Setup

#### Implementation Tasks

1. **Initial Release (v1.0)**
   - Tag release in Git
   - Build all distribution formats
   - Publish to repositories
   - Announce on forums/social media

2. **Community Infrastructure**
   - GitHub Discussions enabled
   - Matrix/Discord channel created
   - Open Collective page set up
   - GitHub Sponsors configured

3. **Marketing Materials**
   - Screenshots and demos
   - Feature comparison table
   - Blog post/article
   - Submit to OMG!Ubuntu, Phoronix, etc.

4. **Support System**
   - Issue templates for bug reports
   - Feature request template
   - Support channels documented
   - Response time commitments

**Expected Output:**
- Production v1.0 release published
- Community channels active
- Funding mechanisms in place
- Initial user feedback collected

### Phase 3 Handoff Package (Optional - Back to Claude)

**Files to deliver if handing back to Claude:**

1. Released v1.0 package
2. Community metrics and feedback
3. Bug reports and feature requests
4. Documentation site analytics
5. Packaging automation scripts

**Communication to Claude Code:**

```
HANDOFF: Phase 3 → Post-Release (Optional)

Status: Production Release Complete

Release Highlights:
✅ v1.0 Released on [DATE]
✅ Flatpak published to Flathub
✅ Ubuntu PPA available at ppa:username/unified-theming
✅ AUR package: unified-theming
✅ CI/CD pipeline operational
✅ Documentation site live
✅ Community channels active

User Metrics (First Week):
- Downloads: [NUMBER]
- GitHub Stars: [NUMBER]
- Issues Opened: [NUMBER]
- Community Members: [NUMBER]

Top User Feedback:
1. [Positive feedback example]
2. [Feature request example]
3. [Bug report example]

Suggested Post-Release Activities:
1. Community engagement - Respond to issues/discussions
2. Marketing - Write blog posts, create videos
3. Feature prioritization - Based on user feedback
4. Documentation improvements - Address common questions
5. Partnership outreach - Contact theme developers

Community Health:
- Average issue response time: [TIME]
- Average PR review time: [TIME]
- Active contributors: [NUMBER]
- Funding: $[AMOUNT]/month

Next Version Planning (v1.1):
Priority features based on community feedback:
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]

Maintenance Status:
- Requires [X] hours/week for current user base
- Scaling needs: [ESTIMATE] hours/week per 1000 users

Claude's Role Going Forward:
- Community management and communication
- Feature planning and roadmap
- Documentation updates
- Marketing and announcements
- Feedback incorporation into next cycle

Sustainability Plan:
[Summary of funding, contributor recruitment, etc.]
```

---

## Continuous Feedback Loops

### Feedback Protocol

At any phase, agents can request feedback from prior agents:

**Format:**
```
FEEDBACK REQUEST: [Current Agent] → [Target Agent]

Context: [What's being worked on]

Question/Issue:
[Specific question or problem]

Current Approach:
[How you're currently solving it]

Request:
[ ] Clarification on specification
[ ] Design review
[ ] Alternative approach suggestion
[ ] Performance optimization advice
[ ] Other: [specify]

Expected Turnaround: [URGENT / 24hrs / 48hrs / 1 week]
```

**Example:**

```
FEEDBACK REQUEST: Qwen Coder → Claude Code

Context: Implementing QtThemeHandler color translation

Question/Issue:
The GTK color variable @theme_bg_color needs to map to Qt's
BackgroundNormal, but some themes use rgba() format while Qt
expects #RRGGBB. The color normalization logic is getting complex.

Current Approach:
Created ColorTranslator class with regex parsing for rgba() and
hex conversion. Works but feels fragile.

Request:
[X] Design review
[ ] Alternative approach suggestion

Should this be part of the color utilities, or should Qt handler
handle its own color format conversion?

Expected Turnaround: 48hrs
```

### Handoff Meeting Template

Before each phase transition, conduct a handoff meeting:

**Agenda:**
1. **Review of completed work** (15 min)
   - Deliverables walkthrough
   - Test results
   - Known issues

2. **Q&A** (20 min)
   - Clarifications on implementation
   - Design decisions explained
   - Technical debt discussed

3. **Next phase planning** (15 min)
   - Priorities confirmation
   - Timeline adjustment if needed
   - Resource requirements

4. **Documentation review** (10 min)
   - Ensure handoff package is complete
   - Verify all files delivered
   - Confirm access to repositories

**Total: 60 minutes**

---

## Maintenance Loop

After initial release, enter maintenance mode:

```
┌─────────────────────────────────────────────────────────┐
│                    Maintenance Cycle                     │
│                                                          │
│  ┌──────────────┐                                       │
│  │User Feedback │                                       │
│  │Bug Reports   │                                       │
│  │Feature Req.  │                                       │
│  └──────┬───────┘                                       │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐     ┌──────────────┐                │
│  │Claude Code   │────▶│Prioritization│                │
│  │- Triage      │     │- Roadmap     │                │
│  │- Communicate │     │- Specs       │                │
│  └──────┬───────┘     └──────────────┘                │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐     ┌──────────────┐                │
│  │Qwen Coder    │────▶│Implement &   │                │
│  │- Bug fixes   │     │Test          │                │
│  │- Features    │     └──────────────┘                │
│  └──────┬───────┘                                       │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐     ┌──────────────┐                │
│  │Opencode AI   │────▶│Release v1.X  │                │
│  │- Integration │     │              │                │
│  │- Release     │     └──────────────┘                │
│  └──────────────┘                                       │
│         │                                               │
│         └───────────────────┐                          │
│                             ▼                          │
│                      ┌──────────────┐                  │
│                      │User Feedback │                  │
│                      └──────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

**Cycle Duration:** 4-6 weeks per release

---

## Success Metrics

### Phase 1 Success
- [ ] Complete specifications approved
- [ ] Architecture documented and clear
- [ ] API contracts defined with type hints
- [ ] CLI prototype functional
- [ ] Developer guide comprehensive
- [ ] Qwen Coder has no clarification questions

### Phase 2 Success
- [ ] 80%+ test coverage achieved
- [ ] All core components implemented
- [ ] Performance benchmarks met
- [ ] Integration tests passing
- [ ] Code documented with docstrings
- [ ] Opencode AI successfully builds locally

### Phase 3 Success
- [ ] GUI functional and intuitive
- [ ] Packaged for 3+ distributions
- [ ] CI/CD pipeline operational
- [ ] User documentation complete
- [ ] v1.0 released publicly
- [ ] Community infrastructure active

### Overall Project Success
- [ ] 70%+ desktop app theming coverage
- [ ] 1000+ active users in 6 months
- [ ] 4+ star average rating
- [ ] Active community (10+ contributors)
- [ ] Sustainable funding ($500+/month)
- [ ] Monthly release cadence

---

## Risk Mitigation

### Risk: Agent Unavailability

**Scenario:** One agent becomes unavailable mid-phase

**Mitigation:**
- Comprehensive handoff documentation at each phase
- Another agent can pick up work with documentation
- Modular architecture allows parallel development
- Regular commits to Git ensure no work lost

### Risk: Scope Creep

**Scenario:** Features added beyond specification

**Mitigation:**
- Claude Code acts as gatekeeper in Phase 1
- Clear requirements prevent deviation
- Feature requests logged for v2.0
- "Defer to next version" mindset

### Risk: Technical Blockers

**Scenario:** Fundamental technical issue discovered

**Mitigation:**
- Immediate feedback loop to Claude Code
- Architecture review and redesign if needed
- Fallback approaches specified upfront
- Graceful degradation acceptable

### Risk: Integration Issues

**Scenario:** Phase 2 and 3 components don't integrate

**Mitigation:**
- Clear API contracts from Phase 1
- Integration tests in Phase 2
- Opencode AI tests build immediately upon handoff
- Communication channel always open

---

## Conclusion

This three-agent workflow maximizes each AI's strengths:

- **Claude Code**: Strategic thinking, documentation, architecture
- **Qwen Coder**: Implementation excellence, testing, optimization
- **Opencode AI**: Integration mastery, packaging, release engineering

Success depends on:
1. **Clear handoffs** with complete documentation
2. **Open communication** through feedback loops
3. **Modular architecture** allowing independent work
4. **Realistic timelines** accounting for complexity
5. **Quality gates** at each phase transition

**Total Timeline: 18-24 weeks from start to v1.0 release**

With this workflow, the unified theming project will be built efficiently, maintainably, and sustainably.
