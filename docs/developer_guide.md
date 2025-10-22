# Developer Guide - Unified Theming Application

**Version:** 1.0
**Last Updated:** 2025-10-20
**Phase:** 1 - Planning & Foundation

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Architecture Overview](#architecture-overview)
4. [Module Guidelines](#module-guidelines)
5. [Testing Guidelines](#testing-guidelines)
6. [Code Style](#code-style)
7. [Documentation Standards](#documentation-standards)
8. [Common Development Tasks](#common-development-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

**System Requirements:**
- Linux distribution (Ubuntu 22.04+, Fedora 37+, or equivalent)
- Python 3.10 or higher
- GTK 4.10+ development files
- Git

**Optional Dependencies (for full functionality):**
- Qt 5.15+ or Qt 6.2+ development files
- Flatpak
- Snapd
- Kvantum theme engine

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

---

## Development Setup

### Environment Setup

1. **Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   ```

2. **Install Dependencies**:
   ```bash
   # Development dependencies
   pip install -e ".[dev]"

   # GUI dependencies (optional for CLI-only development)
   pip install -e ".[gui]"
   ```

3. **System Dependencies** (Ubuntu/Debian):
   ```bash
   sudo apt install \
       python3-dev \
       python3-gi \
       python3-gi-cairo \
       gir1.2-gtk-4.0 \
       gir1.2-adw-1 \
       libgirepository1.0-dev \
       libcairo2-dev \
       pkg-config
   ```

4. **System Dependencies** (Fedora):
   ```bash
   sudo dnf install \
       python3-devel \
       python3-gobject \
       gtk4-devel \
       libadwaita-devel \
       cairo-gobject-devel \
       pkg-config
   ```

### IDE Configuration

#### VS Code

Recommended extensions:
- Python (Microsoft)
- Pylance
- Black Formatter
- MyPy Type Checker

`.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false
}
```

#### PyCharm

- Enable type checking (Settings → Editor → Inspections → Python → Type hints)
- Set code style to Black (Settings → Tools → Black)
- Enable pytest as test runner (Settings → Tools → Python Integrated Tools)

---

## Architecture Overview

### Layer Structure

```
User Interface Layer
    ↓
Application Core Layer
    ↓
Toolkit Handler Layer
    ↓
System Integration Layer
```

See [architecture.md](architecture.md) for complete details.

### Key Components

1. **UnifiedThemeManager** (`core/manager.py`)
   - Central orchestrator
   - Coordinates all operations
   - Manages state and transactions

2. **ThemeParser** (`core/parser.py`)
   - Theme discovery
   - Metadata extraction
   - Color palette parsing

3. **Handlers** (`handlers/`)
   - GTKHandler: GTK2/3/4/libadwaita theming
   - QtHandler: Qt5/6 theming
   - FlatpakHandler: Flatpak application theming
   - SnapHandler: Snap application theming

4. **ConfigManager** (`core/config.py`)
   - Configuration backup
   - State persistence
   - Rollback functionality

---

## Module Guidelines

### Adding a New Handler

Handlers are the core of toolkit-specific theming. Here's how to add one:

1. **Create Handler File**:
   ```python
   # handlers/new_toolkit_handler.py

   from pathlib import Path
   from typing import Dict, Optional
   from unified_theming.handlers.base import BaseHandler
   from unified_theming.core.types import ThemeData, ValidationResult, Toolkit
   from unified_theming.utils.logging_config import get_logger

   logger = get_logger(__name__)

   class NewToolkitHandler(BaseHandler):
       """Handler for NewToolkit applications."""

       def __init__(self, config_dir: Optional[Path] = None):
           """Initialize handler."""
           super().__init__(Toolkit.NEW_TOOLKIT)
           self.config_dir = config_dir or (Path.home() / ".config")

       def apply_theme(self, theme_data: ThemeData) -> bool:
           """Apply theme to NewToolkit apps."""
           logger.info(f"Applying theme to NewToolkit: {theme_data.name}")

           try:
               # Implementation here
               # 1. Prepare configuration
               # 2. Write configuration files
               # 3. Trigger toolkit updates
               return True

           except Exception as e:
               logger.error(f"Failed to apply theme: {e}")
               return False

       def get_current_theme(self) -> str:
           """Get currently applied theme name."""
           # Implementation here
           pass

       def validate_compatibility(
           self,
           theme_data: ThemeData
       ) -> ValidationResult:
           """Check if theme is compatible with NewToolkit."""
           result = ValidationResult(valid=True)

           # Check for required files, colors, etc.
           # Add errors/warnings as needed

           return result

       def is_available(self) -> bool:
           """Check if NewToolkit is installed."""
           # Check for toolkit presence
           # e.g., look for command in PATH, check for library
           return True
   ```

2. **Create Base Handler Interface** (if not exists):
   ```python
   # handlers/base.py

   from abc import ABC, abstractmethod
   from unified_theming.core.types import ThemeData, ValidationResult, Toolkit

   class BaseHandler(ABC):
       """Base class for all toolkit handlers."""

       def __init__(self, toolkit: Toolkit):
           """Initialize handler with toolkit type."""
           self.toolkit = toolkit

       @abstractmethod
       def apply_theme(self, theme_data: ThemeData) -> bool:
           """
           Apply theme to this toolkit.

           Args:
               theme_data: Prepared theme data for this toolkit

           Returns:
               True if successful, False otherwise
           """
           pass

       @abstractmethod
       def get_current_theme(self) -> str:
           """
           Get currently applied theme name.

           Returns:
               Name of currently applied theme
           """
           pass

       @abstractmethod
       def validate_compatibility(
           self,
           theme_data: ThemeData
       ) -> ValidationResult:
           """
           Check if theme is compatible with this toolkit.

           Args:
               theme_data: Theme data to validate

           Returns:
               ValidationResult with any errors/warnings
           """
           pass

       @abstractmethod
       def is_available(self) -> bool:
           """
           Check if this toolkit is available on the system.

           Returns:
               True if toolkit is installed and usable
           """
           pass
   ```

3. **Register Handler**:
   ```python
   # core/manager.py

   from unified_theming.handlers.new_toolkit_handler import NewToolkitHandler

   class UnifiedThemeManager:
       def __init__(self):
           self.handlers = {
               'gtk': GTKHandler(),
               'qt': QtHandler(),
               'flatpak': FlatpakHandler(),
               'snap': SnapHandler(),
               'new_toolkit': NewToolkitHandler(),  # Add here
           }
   ```

4. **Add Tests**:
   ```python
   # tests/test_new_toolkit_handler.py

   import pytest
   from pathlib import Path
   from unified_theming.handlers.new_toolkit_handler import NewToolkitHandler
   from unified_theming.core.types import ThemeData, Toolkit

   @pytest.fixture
   def handler(tmp_path):
       """Create handler with temporary config directory."""
       return NewToolkitHandler(config_dir=tmp_path)

   @pytest.fixture
   def sample_theme_data():
       """Create sample theme data for testing."""
       return ThemeData(
           name="TestTheme",
           toolkit=Toolkit.NEW_TOOLKIT,
           colors={
               "bg_color": "#ffffff",
               "fg_color": "#000000",
           }
       )

   def test_handler_apply(handler, sample_theme_data):
       """Test theme application."""
       result = handler.apply_theme(sample_theme_data)
       assert result is True

   def test_handler_get_current(handler):
       """Test getting current theme."""
       theme = handler.get_current_theme()
       assert isinstance(theme, str)

   def test_handler_is_available(handler):
       """Test toolkit availability check."""
       available = handler.is_available()
       assert isinstance(available, bool)
   ```

### Color Translation

Use `utils/color.py` for color format conversions:

```python
from unified_theming.utils.color import ColorTranslator

translator = ColorTranslator()

# GTK to Qt color translation
gtk_colors = {
    "theme_bg_color": "#ffffff",
    "theme_fg_color": "#000000",
}

qt_colors = translator.gtk_to_qt(gtk_colors)
# Returns: {"BackgroundNormal": "#ffffff", "ForegroundNormal": "#000000", ...}

# Normalize color format
normalized = translator.normalize("rgb(255, 0, 0)", output_format="hex")
# Returns: "#ff0000"

# Validate color
is_valid = translator.validate("#ff0000")
# Returns: True
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_manager.py          # Core manager tests
├── test_parser.py           # Theme parser tests
├── test_gtk_handler.py      # GTK handler tests
├── test_qt_handler.py       # Qt handler tests
├── test_integration.py      # Integration tests
└── fixtures/                # Test themes
    ├── ValidTheme/
    ├── IncompleteTheme/
    └── MalformedTheme/
```

### Writing Unit Tests

```python
import pytest
from pathlib import Path
from unified_theming.core.parser import ThemeParser
from unified_theming.core.types import ThemeInfo

@pytest.fixture
def parser():
    """Create ThemeParser instance."""
    return ThemeParser()

@pytest.fixture
def valid_theme_path(tmp_path):
    """Create a valid test theme."""
    theme_dir = tmp_path / "TestTheme"
    theme_dir.mkdir()

    # Create GTK4 support
    gtk4_dir = theme_dir / "gtk-4.0"
    gtk4_dir.mkdir()

    # Create CSS file
    css_file = gtk4_dir / "gtk.css"
    css_file.write_text("""
@define-color theme_bg_color #ffffff;
@define-color theme_fg_color #000000;
    """)

    return theme_dir

def test_parse_valid_theme(parser, valid_theme_path):
    """Test parsing a valid theme."""
    theme_info = parser.parse_theme(valid_theme_path)

    assert theme_info.name == "TestTheme"
    assert theme_info.path == valid_theme_path
    assert len(theme_info.colors) >= 2
    assert "theme_bg_color" in theme_info.colors

def test_parse_nonexistent_theme(parser, tmp_path):
    """Test parsing a theme that doesn't exist."""
    from unified_theming.core.exceptions import ThemeNotFoundError

    with pytest.raises(ThemeNotFoundError):
        parser.parse_theme(tmp_path / "NonExistent")
```

### Integration Tests

```python
# tests/test_integration.py

import pytest
from unified_theming.core.manager import UnifiedThemeManager

@pytest.fixture
def manager(tmp_path):
    """Create manager with temporary config."""
    return UnifiedThemeManager(config_path=tmp_path)

def test_full_theme_application(manager, valid_theme_path):
    """Test applying theme across all handlers."""
    # Discover themes
    themes = manager.discover_themes()
    assert "TestTheme" in themes

    # Apply theme
    result = manager.apply_theme("TestTheme")

    # Verify results
    assert result.overall_success is True
    assert len(result.get_failed_handlers()) == 0

    # Verify current theme
    current = manager.get_current_themes()
    assert "gtk4" in current
    assert current["gtk4"] == "TestTheme"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=unified_theming --cov-report=html

# Run specific test file
pytest tests/test_parser.py

# Run specific test
pytest tests/test_parser.py::test_parse_valid_theme

# Run tests matching pattern
pytest -k "theme_application"

# Run without slow tests
pytest -m "not slow"

# Verbose output
pytest -v

# Show print statements
pytest -s
```

---

## Code Style

### PEP 8 Compliance

Follow [PEP 8](https://peps.python.org/pep-0008/) with these specifics:

- Line length: 88 characters (Black default)
- Indentation: 4 spaces (no tabs)
- Imports: Organized with `isort`
- String quotes: Double quotes preferred

### Type Hints

**All public functions must have type hints:**

```python
from pathlib import Path
from typing import Dict, List, Optional

def parse_colors(
    css_file: Path,
    fallback: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Parse color definitions from CSS file.

    Args:
        css_file: Path to CSS file
        fallback: Optional fallback colors

    Returns:
        Dictionary of color_name → color_value

    Raises:
        FileNotFoundError: If CSS file doesn't exist
        CSSParseError: If CSS syntax is invalid
    """
    colors: Dict[str, str] = {}
    # Implementation...
    return colors
```

### Docstring Format (Google Style)

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief one-line description.

    Longer description that explains what the function does in more
    detail. Can span multiple lines and includes implementation notes.

    Args:
        param1: Description of first parameter. Should explain what
            values are valid and what they mean.
        param2: Description of second parameter. Can span multiple
            lines if needed.

    Returns:
        Description of the return value. Explain what True/False means,
        or what the returned object contains.

    Raises:
        ValueError: When param1 is empty
        FileNotFoundError: When referenced file doesn't exist

    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True

    Note:
        Any additional notes or warnings about usage.
    """
    pass
```

### Code Formatting

**Use Black for automatic formatting:**

```bash
# Format all files
black unified_theming/

# Check without modifying
black --check unified_theming/

# Format specific file
black unified_theming/core/parser.py
```

**Import Organization (isort):**

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import click
from gi.repository import Gtk

# Local application imports
from unified_theming.core.types import ThemeInfo
from unified_theming.core.exceptions import ThemeNotFoundError
from unified_theming.utils.logging_config import get_logger
```

---

## Documentation Standards

### Code Comments

```python
# Good: Explain WHY, not WHAT
def calculate_derived_colors(base_colors: Dict[str, str]) -> Dict[str, str]:
    """Generate derived colors from base palette."""
    derived = {}

    # Darken background for hover state
    # This improves visual feedback and matches GNOME HIG guidelines
    if "theme_bg_color" in base_colors:
        derived["theme_bg_hover"] = darken(base_colors["theme_bg_color"], 0.9)

    return derived

# Bad: Repeating what code does
def calculate_derived_colors(base_colors: Dict[str, str]) -> Dict[str, str]:
    """Generate derived colors from base palette."""
    # Create empty dictionary
    derived = {}

    # Check if theme_bg_color exists in base_colors
    if "theme_bg_color" in base_colors:
        # Call darken function with base color and 0.9
        derived["theme_bg_hover"] = darken(base_colors["theme_bg_color"], 0.9)

    # Return derived colors
    return derived
```

### README Files

Each major module should have a README explaining its purpose:

```markdown
# Module Name

## Purpose
What this module does and why it exists.

## Key Components
- Component1: Brief description
- Component2: Brief description

## Usage
```python
from module import Component
component = Component()
component.do_thing()
```

## Dependencies
- List of dependencies specific to this module

## Notes
- Any important implementation details
- Known limitations
- Future improvements
```

---

## Common Development Tasks

### Adding a New Color Variable

1. **Add to types.py**:
   ```python
   LIBADWAITA_COLOR_VARIABLES = [
       # ... existing variables ...
       "new_custom_color",  # Add here
   ]
   ```

2. **Update color mapping**:
   ```python
   # handlers/gtk_handler.py

   GTK_TO_LIBADWAITA_MAPPING = {
       # ... existing mappings ...
       "gtk_custom_color": "new_custom_color",
   }
   ```

3. **Add tests**:
   ```python
   def test_new_color_translation():
       """Test new color variable translation."""
       gtk_colors = {"gtk_custom_color": "#ff0000"}
       adw_colors = translate_colors(gtk_colors)
       assert "new_custom_color" in adw_colors
   ```

### Adding a New CLI Command

See the CLI section in `cli/commands.py`. Follow this pattern:

```python
@cli.command()
@click.argument('arg1')
@click.option('--option1', '-o', help='Option description')
@click.pass_context
def new_command(ctx, arg1: str, option1: Optional[str]):
    """
    Brief command description.

    Detailed description and examples.
    """
    # Implementation
    pass
```

### Adding a New Exception

1. **Add to exceptions.py**:
   ```python
   class NewSpecificError(UnifiedThemingError):
       """Raised when specific condition occurs."""

       def __init__(self, message: str, context: Optional[str] = None):
           super().__init__(message)
           self.context = context
   ```

2. **Use in code**:
   ```python
   from unified_theming.core.exceptions import NewSpecificError

   if error_condition:
       raise NewSpecificError(
           "Operation failed",
           context="Additional context"
       )
   ```

---

## Troubleshooting

### Common Issues

**Problem**: Import errors when running tests
```bash
# Solution: Install package in editable mode
pip install -e .
```

**Problem**: GTK import errors
```bash
# Solution: Install system dependencies
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1
```

**Problem**: Type checking errors with PyGObject
```python
# Solution: Add type: ignore comments for PyGObject
from gi.repository import Gtk  # type: ignore
```

**Problem**: Tests failing due to missing test themes
```bash
# Solution: Ensure test fixtures exist
pytest --collect-only  # Check test collection
```

### Debug Logging

Enable debug logging during development:

```python
from unified_theming.utils.logging_config import setup_logging

# Enable debug logging
setup_logging(log_level="DEBUG", console_output=True)
```

Or via CLI:

```bash
# Increase verbosity
unified-theming -vvv list  # Maximum verbosity
```

---

## Contributing Workflow

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make Changes**:
   - Write code following style guidelines
   - Add/update tests
   - Update documentation

3. **Run Quality Checks**:
   ```bash
   # Format code
   black unified_theming/
   isort unified_theming/

   # Run linters
   flake8 unified_theming/
   pylint unified_theming/
   mypy unified_theming/

   # Run tests
   pytest --cov
   ```

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat: Add new feature description

   - Detailed change 1
   - Detailed change 2

   Closes #123"
   ```

5. **Push and Create PR**:
   ```bash
   git push origin feature/my-new-feature
   # Create pull request on GitHub
   ```

---

## Next Steps for Phase 2 (Qwen Coder)

Phase 2 implementation priorities:

1. **UnifiedThemeParser** (CRITICAL PATH)
   - Implement theme discovery
   - Implement CSS parsing
   - Implement color extraction
   - Add comprehensive tests

2. **LibadwaitaHandler** (HIGH PRIORITY)
   - Implement CSS generation
   - Implement color mapping
   - Add backup functionality
   - Test with real themes

3. **QtThemeHandler** (HIGH PRIORITY)
   - Implement kdeglobals generation
   - Implement color translation
   - Add Kvantum support
   - Test with Qt applications

4. **Integration Testing**
   - Test full theme application workflow
   - Test error handling and rollback
   - Performance testing

See [handoff document](handoff_to_qwen_coder.md) for detailed instructions.

---

**End of Developer Guide**
