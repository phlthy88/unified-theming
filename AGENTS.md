# Agent Guidelines for Unified Theming

## Build/Lint/Test Commands
- **Install dev deps**: `pip install -e ".[dev]"`
- **Run all tests**: `pytest`
- **Run single test**: `pytest tests/test_file.py::test_function_name`
- **Run with coverage**: `pytest --cov=unified_theming`
- **Format code**: `black unified_theming tests`
- **Sort imports**: `isort unified_theming tests`
- **Type check**: `mypy unified_theming`
- **Lint**: `flake8 unified_theming tests`
- **Full check**: `black --check unified_theming tests && isort --check-only unified_theming tests && mypy unified_theming && flake8 unified_theming tests && pytest`

## Code Style Guidelines
- **Formatting**: Black (88 char line length)
- **Imports**: isort with black profile (grouped, trailing commas, parentheses)
- **Types**: Strict mypy (required type hints for public functions)
- **Docstrings**: Google style with Args/Returns/Raises sections
- **Quotes**: Double quotes preferred
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error handling**: Custom exceptions in core/exceptions.py, log errors with context
- **Logging**: Use unified_theming.utils.logging_config.get_logger(__name__)