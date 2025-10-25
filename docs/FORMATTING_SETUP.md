# Code Formatting Setup

**Purpose:** Ensure consistent code formatting across the project  
**Tools:** Black, isort, flake8, mypy  
**Status:** ✅ Configured and enforced in CI  

## Quick Setup for Contributors

### 1. Install Development Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install project with dev dependencies
pip install -e ".[dev]"
```

### 2. Install Pre-commit Hooks (Recommended)
```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Run on all files (first time)
pre-commit run --all-files
```

### 3. Manual Formatting Commands
```bash
# Format code with Black
black unified_theming tests examples/

# Sort imports with isort
isort unified_theming tests examples/

# Check style with flake8
flake8 unified_theming tests examples/

# Type check with mypy (optional, currently disabled in CI)
mypy unified_theming
```

## Formatting Standards

### Black Configuration
- **Line length:** 88 characters
- **Target Python:** 3.10+
- **String quotes:** Double quotes preferred
- **Configuration:** `pyproject.toml` `[tool.black]` section

### isort Configuration
- **Profile:** Black-compatible
- **Multi-line output:** Mode 3 (vertical hanging indent)
- **Configuration:** `pyproject.toml` `[tool.isort]` section

### flake8 Configuration
- **Configuration file:** `.flake8`
- **Line length:** 88 characters (matches Black)
- **Ignored rules:** E203, W503 (Black compatibility)

## CI Integration

### Formatting Check Job
The CI workflow (`.github/workflows/ci.yml`) includes:

```yaml
- name: Code Style Check
  run: |
    black --check unified_theming tests examples/
    flake8 unified_theming tests examples/
```

### Failure Resolution
If CI fails due to formatting:

1. **Run Black locally:**
   ```bash
   black unified_theming tests examples/
   ```

2. **Check what changed:**
   ```bash
   git diff
   ```

3. **Commit the changes:**
   ```bash
   git add .
   git commit -m "fix: apply Black formatting"
   git push
   ```

## Pre-commit Hooks

### Configuration File: `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 25.9.0  # Pinned to match CI
    hooks:
      - id: black
        
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]
        
  - repo: https://github.com/pycqa/flake8
    rev: 7.3.0
    hooks:
      - id: flake8
```

### Benefits of Pre-commit Hooks
- ✅ **Automatic formatting** before each commit
- ✅ **Prevents CI failures** due to formatting issues
- ✅ **Consistent code style** across all contributors
- ✅ **Faster development** workflow

## IDE Integration

### VS Code
Add to `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true
}
```

### PyCharm
1. Install Black plugin
2. Configure Black as external tool
3. Set up file watchers for automatic formatting
4. Configure flake8 and mypy inspections

## Troubleshooting

### Common Issues

#### 1. Black and flake8 Conflicts
**Problem:** flake8 complains about Black-formatted code  
**Solution:** Use Black-compatible flake8 configuration (already set up)

#### 2. Import Order Issues
**Problem:** isort and Black disagree on import formatting  
**Solution:** Use `--profile black` for isort (already configured)

#### 3. Line Length Disagreements
**Problem:** Different tools use different line lengths  
**Solution:** All tools configured for 88 characters (Black default)

#### 4. Pre-commit Hook Failures
**Problem:** Pre-commit hooks fail on commit  
**Solution:** 
```bash
# Fix formatting issues
black .
isort .

# Or skip hooks temporarily (not recommended)
git commit --no-verify
```

### Debugging Commands

```bash
# Check what Black would change (without applying)
black --diff --color unified_theming/

# Check specific file
black --check tests/test_cli_dry_run.py

# See detailed flake8 output
flake8 --statistics unified_theming/

# Run pre-commit on specific files
pre-commit run black --files unified_theming/cli/commands.py
```

## Version Compatibility

### Tool Versions (Pinned)
- **Black:** 25.9.0
- **isort:** 5.13.2  
- **flake8:** 7.3.0
- **mypy:** 1.13.0 (when enabled)

### Python Compatibility
- **Minimum:** Python 3.10
- **Tested:** Python 3.10, 3.11, 3.12
- **Target:** Python 3.12 (development)

## Best Practices

### For Contributors
1. ✅ **Install pre-commit hooks** on first setup
2. ✅ **Run formatting tools** before committing
3. ✅ **Check CI status** after pushing
4. ✅ **Fix formatting issues** promptly

### For Maintainers
1. ✅ **Keep tool versions pinned** in CI and pre-commit
2. ✅ **Update versions together** to avoid conflicts
3. ✅ **Document formatting changes** in release notes
4. ✅ **Review formatting in PRs** before merging

### Code Style Guidelines
1. ✅ **Let Black handle formatting** - don't fight it
2. ✅ **Use descriptive variable names** even if longer
3. ✅ **Break long lines logically** at function calls
4. ✅ **Group imports** by standard library, third-party, local
5. ✅ **Add docstrings** to public functions and classes

## Recent Fixes

### CLI Test Formatting Issue (2025-01-27)
- **Problem:** `tests/test_cli_dry_run.py` failed Black formatting check
- **Cause:** Long function calls exceeded line length
- **Solution:** Applied Black formatting to break lines appropriately
- **Prevention:** Pre-commit hooks now prevent similar issues

---

**Next Steps:**
1. Install pre-commit hooks in your local development environment
2. Run `pre-commit run --all-files` to ensure all files are properly formatted
3. Commit any formatting changes that result from the initial run
