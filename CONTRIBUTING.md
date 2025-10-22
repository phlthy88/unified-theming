# Contributing to Unified Theming

Thank you for your interest in contributing to Unified Theming! This guide will help you set up your development environment, understand our testing strategy, and submit high-quality contributions.

## Table of Contents

- [Development Setup](#development-setup)
- [Testing](#testing)
- [CLI Usage](#cli-usage)
- [Issue Triage Templates](#issue-triage-templates)
- [Contribution Process](#contribution-process)
- [Code Style Standards](#code-style-standards)
- [Integration Testing Notes](#integration-testing-notes)

## Development Setup

### Prerequisites

- Linux distribution (Ubuntu 22.04+, Fedora 37+, or equivalent)
- Python 3.10 or higher
- Git
- GTK 4.10+ development files (optional, for GUI development)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/phlthy88/unified-theming.git
cd unified-theming

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e ".[dev,gui]"
```

### Verify Installation

```bash
# Run tests to verify setup
pytest

# Run linting checks
black --check unified_theming/
flake8 unified_theming/
mypy unified_theming/

# Test CLI availability
unified-theming --help
```

## Testing

### Running Tests

```bash
# Run all tests (from project root, venv activated)
pytest

# Run with coverage report
pytest --cov=unified_theming --cov-report=html

# Run specific test file
pytest tests/test_parser.py

# Run specific test function
pytest tests/test_parser.py::test_discover_themes

# Run without slow tests
pytest -m "not slow"
```

### Coverage Requirements

- Core modules (parser, manager, config): 90%+
- Handlers: 85%+
- Utilities: 80%+
- Overall: 80% minimum

### Writing Tests

All test files should be placed in the `tests/` directory and follow the naming convention `test_*.py`. Use the fixtures defined in `tests/conftest.py` for common test scenarios.

Example test structure:

```python
import pytest
from unified_theming.core.parser import UnifiedThemeParser

def test_discover_themes(parser, tmp_theme_dir):
    """Test theme discovery with valid themes."""
    themes = parser.discover_themes()
    assert len(themes) > 0
    assert "ValidTheme" in themes
```

## CLI Usage

### Basic Commands

```bash
# List available themes
unified-theming list

# Preview theme changes without applying (safe, non-destructive)
unified-theming apply Adwaita-dark --dry-run

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

### Dry-Run Mode

The `--dry-run` flag allows you to preview all proposed system changes before applying them. This is the recommended way to test theme compatibility:

```bash
# Preview what would be changed
unified-theming apply Nord --dry-run

# Output shows:
# - Which configuration files would be modified
# - What values would be changed
# - Which handlers would be invoked
# - No actual changes are made to your system
```

### Verbosity Levels

```bash
# Normal output
unified-theming apply Nord

# Verbose output (useful for debugging)
unified-theming -v apply Nord

# Very verbose (diagnostic details)
unified-theming -vv apply Nord

# Maximum verbosity
unified-theming -vvv apply Nord
```

## Issue Triage Templates

### Bug Report Template

When reporting bugs, please include:

```markdown
## Bug Description
[Clear, concise description of the bug]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [Etc.]

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Environment
- OS: [e.g., Ubuntu 24.04]
- Python Version: [e.g., 3.10.12]
- Unified Theming Version: [e.g., 0.5.0]
- Installed Toolkits: [e.g., GTK 4.12, Qt 6.5]

## Logs
[Paste relevant logs from ~/.local/state/unified-theming/unified-theming.log]

## Dry-Run Output
[If applicable, include output from --dry-run]
```

### Feature Request Template

```markdown
## Feature Description
[Clear description of the proposed feature]

## Use Case
[Why is this feature needed? What problem does it solve?]

## Proposed Solution
[If you have an idea of how to implement this]

## Alternatives Considered
[Other approaches you've thought about]

## Additional Context
[Any other relevant information]
```

### Theme Compatibility Issue Template

```markdown
## Theme Name
[Name of the theme]

## Theme Source
[Where the theme is from - system package, manual install, etc.]

## Toolkit(s) Affected
[GTK2, GTK3, GTK4, Libadwaita, Qt5, Qt6, Flatpak, Snap]

## Validation Output
[Output from `unified-theming validate ThemeName`]

## Dry-Run Output
[Output from `unified-theming apply ThemeName --dry-run`]

## Expected Result
[What should happen]

## Actual Result
[What actually happens]
```

## Contribution Process

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/unified-theming.git
cd unified-theming
git remote add upstream https://github.com/phlthy88/unified-theming.git
```

### 2. Create a Feature Branch

```bash
# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 3. Make Your Changes

- Write clear, documented code following our style guide
- Add tests for new functionality
- Update documentation as needed
- Run tests and linting before committing

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add feature: brief description

Detailed explanation of what changed and why.
Fixes #123 (if applicable)"
```

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create a pull request on GitHub
```

### Pull Request Guidelines

- **Title**: Clear, concise description (e.g., "Add --dry-run flag to apply command")
- **Description**: Explain what changed, why, and any relevant context
- **Tests**: Ensure all tests pass and coverage meets requirements
- **Documentation**: Update relevant docs (README, CLAUDE.md, etc.)
- **Commits**: Keep commits logical and well-messaged

### Code Review Process

1. Automated CI checks will run (linting, tests, coverage)
2. Maintainers will review your code
3. Address any feedback or requested changes
4. Once approved, your PR will be merged

## Code Style Standards

### Python Style

- **Line length**: 88 characters (Black default)
- **Docstrings**: Google style with type information
- **Imports**: Organized with isort (stdlib, third-party, local)
- **Type hints**: Required on all public functions/methods
- **String quotes**: Double quotes preferred

### Example Function

```python
def apply_theme(
    self,
    theme_name: str,
    targets: Optional[List[str]] = None,
    dry_run: bool = False
) -> ApplicationResult:
    """
    Apply a theme to specified targets.

    Args:
        theme_name: Name of theme to apply
        targets: List of toolkit targets (None = all)
        dry_run: If True, preview changes without applying

    Returns:
        ApplicationResult with per-handler results

    Raises:
        ThemeNotFoundError: If theme doesn't exist
        ThemeApplicationError: If application fails critically
    """
    # Implementation here
```

### Formatting Tools

```bash
# Auto-format code
black unified_theming/

# Sort imports
isort unified_theming/

# Check type hints
mypy unified_theming/

# Lint code
flake8 unified_theming/
```

### Logging Guidelines

```python
from unified_theming.utils.logging_config import get_logger
logger = get_logger(__name__)

# Use appropriate log levels
logger.debug("Parsing theme file: %s", theme_path)  # Diagnostic details
logger.info("Applying theme '%s'", theme_name)      # Major operations
logger.warning("Kvantum not installed")             # Non-critical issues
logger.error("Failed to apply Qt theme: %s", e)     # Errors preventing operation
logger.critical("Backup restoration failed")        # System-breaking errors
```

## Integration Testing Notes

### Integration Test Structure

Integration tests validate end-to-end workflows and are located in `tests/test_integration.py`. They test:

1. Complete theme application workflows
2. Backup and restore operations
3. Handler coordination
4. Error handling and recovery
5. CLI command integration

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/test_integration.py

# Run specific integration test
pytest tests/test_integration.py::test_complete_theme_application

# Run integration tests with verbose output
pytest tests/test_integration.py -v
```

### Writing Integration Tests

Integration tests should:

- Use realistic test data with proper theme structures
- Properly isolate tests using mocks and fixtures
- Test error handling and recovery scenarios
- Include comprehensive documentation
- Clean up after themselves (no leftover files/state)

Example:

```python
def test_complete_theme_application(manager, valid_theme, monkeypatch):
    """Test complete theme application workflow (IT-001)."""
    # Arrange
    theme_name = "ValidTheme"

    # Mock handler operations
    def mock_apply(theme_data):
        return True

    # Act
    result = manager.apply_theme(theme_name)

    # Assert
    assert result.overall_success
    assert result.backup_id is not None
```

### Integration Test Scenarios

The test suite covers these core scenarios:

- **IT-001**: Complete theme application workflow
- **IT-002**: Theme application with partial handler failures
- **IT-003**: Backup and rollback operations
- **IT-004**: Theme validation and compatibility checking
- **IT-005**: Handler coordination with unavailable toolkits

### Testing Containerized Applications

When testing Flatpak and Snap handlers:

- Use test applications installed in user scope
- Mock portal/interface operations where needed
- Verify configuration file generation without requiring containers
- Test permission handling and override files

### CI/CD Integration

All pull requests automatically run:

1. Code formatting checks (Black, isort)
2. Type checking (mypy)
3. Linting (flake8)
4. Unit tests with coverage reporting
5. Integration tests
6. CLI smoke tests
7. GUI prototype syntax validation (if applicable)

The CI must pass before merging. Check the GitHub Actions tab for detailed logs.

## Getting Help

- **Documentation**: See `docs/` directory for detailed specs
- **Issues**: Check existing issues on GitHub
- **Questions**: Open a discussion on GitHub
- **Chat**: Join the project's communication channel (if available)

## License

By contributing to Unified Theming, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Unified Theming!** Your efforts help make Linux desktop theming more accessible and reliable for everyone.
