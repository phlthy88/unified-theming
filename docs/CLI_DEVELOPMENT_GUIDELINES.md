# CLI Development Guidelines

**Purpose:** Prevent name shadowing and CLI-related bugs  
**Related:** [CLI_TEST_FAILURES_RCA.md](./CLI_TEST_FAILURES_RCA.md)  
**Last Updated:** 2025-01-27  

## Quick Reference

### ❌ Don't Do This
```python
# Generic command names that shadow built-ins
@cli.command()
def list(...):  # Shadows built-in list()
    pass

@cli.command() 
def dict(...):  # Shadows built-in dict()
    pass

# Using shadowed built-ins
def some_function():
    items = {'a', 'b', 'c'}
    return list(items)  # ❌ Calls Click command, not built-in!
```

### ✅ Do This Instead
```python
# Descriptive command names
@cli.command()
def list_themes(...):  # Clear, specific name
    pass

@cli.command()
def show_config(...):  # Descriptive name
    pass

# Safe built-in usage
def some_function():
    items = {'a', 'b', 'c'}
    return [*items]  # ✅ Unpacking syntax, no collision
    # OR
    from builtins import list as builtin_list
    return builtin_list(items)  # ✅ Explicit built-in
```

## Name Collision Prevention

### 1. Command Naming Convention

**Pattern:** `<verb>_<noun>` or `<verb>_<noun>_<modifier>`

```python
# Good examples
@cli.command()
def apply_theme(...): pass

@cli.command() 
def list_themes(...): pass

@cli.command()
def show_current_theme(...): pass

@cli.command()
def validate_theme_structure(...): pass

# Bad examples  
@cli.command()
def apply(...): pass  # Too generic

@cli.command()
def list(...): pass   # Shadows built-in

@cli.command()
def get(...): pass    # Too generic
```

### 2. Built-in Function Usage

**When you need built-in functions in Click modules:**

```python
# Option 1: Unpacking (preferred for simple cases)
my_set = {'a', 'b', 'c'}
my_list = [*my_set]  # Clean, no collision

# Option 2: Explicit import (for complex cases)
from builtins import list as builtin_list, dict as builtin_dict
my_list = builtin_list(my_set)
my_dict = builtin_dict(pairs)

# Option 3: Constructor syntax (rarely needed)
my_list = list.__new__(list, my_set)
```

### 3. Testing Built-in Access

```python
def test_builtin_functions_accessible():
    """Ensure built-ins aren't shadowed by Click commands."""
    import builtins
    
    # Test that built-ins are still callable
    assert callable(builtins.list)
    assert callable(builtins.dict)
    assert callable(builtins.str)
    
    # Test that they work correctly
    result = builtins.list({'a', 'b'})
    assert isinstance(result, list)
    assert len(result) == 2
```

## Click-Specific Best Practices

### 1. Command Organization

```python
# Group related commands
@cli.group()
def theme():
    """Theme management commands."""
    pass

@theme.command()
def apply(name: str):
    """Apply a theme."""
    pass

@theme.command() 
def list_available():
    """List available themes."""
    pass

# Usage: unified-theming theme apply Nord
#        unified-theming theme list-available
```

### 2. Option Naming

```python
# Consistent option names across commands
@click.option('--targets', multiple=True, help='Target toolkits')
@click.option('--format', type=click.Choice(['table', 'json', 'list']))
@click.option('--config', type=click.Path(), help='Config file path')

# Not: --toolkit in one command, --targets in another
```

### 3. Parameter Validation

```python
@cli.command()
@click.argument('theme_name')
@click.option('--targets', multiple=True)
def apply_theme(theme_name: str, targets: Tuple[str, ...]):
    """Apply theme with validation."""
    
    # Validate early
    if not theme_name.strip():
        raise click.BadParameter('Theme name cannot be empty')
    
    # Map and validate targets
    handler_names, unknown = map_toolkits_to_handlers(targets)
    if unknown:
        raise click.BadParameter(f'Unknown targets: {", ".join(unknown)}')
    
    # Proceed with validated data
    # ...
```

## Testing Guidelines

### 1. Test Command Registration

```python
def test_commands_registered():
    """Verify all expected commands are registered."""
    from unified_theming.cli.commands import cli
    
    # Get all registered commands
    commands = cli.list_commands(None)
    
    # Verify expected commands exist
    expected = ['apply_theme', 'list_themes', 'current_theme', 'rollback', 'validate']
    for cmd in expected:
        assert cmd in commands, f'Command {cmd} not registered'
```

### 2. Test Parameter Mapping

```python
def test_toolkit_to_handler_mapping():
    """Test that toolkit names map correctly to handlers."""
    from unified_theming.cli.commands import map_toolkits_to_handlers
    
    # Test individual mappings
    handlers, unknown = map_toolkits_to_handlers(('gtk4',))
    assert handlers == ['gtk']
    assert unknown == []
    
    # Test multiple mappings
    handlers, unknown = map_toolkits_to_handlers(('gtk4', 'qt5'))
    assert set(handlers) == {'gtk', 'qt'}
    assert unknown == []
    
    # Test 'all' mapping
    handlers, unknown = map_toolkits_to_handlers(('all',))
    assert set(handlers) == {'gtk', 'qt', 'flatpak', 'snap'}
    assert unknown == []
```

### 3. Test CLI Integration

```python
def test_cli_end_to_end():
    """Test complete CLI workflow."""
    from click.testing import CliRunner
    from unified_theming.cli.commands import cli
    
    runner = CliRunner()
    
    # Test help works
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'apply_theme' in result.output
    
    # Test command help works
    result = runner.invoke(cli, ['apply_theme', '--help'])
    assert result.exit_code == 0
    assert '--targets' in result.output
    
    # Test dry-run works (with mocking)
    with patch('unified_theming.cli.commands.UnifiedThemeManager'):
        result = runner.invoke(cli, ['apply_theme', 'TestTheme', '--dry-run'])
        assert result.exit_code == 0
```

## Debugging Techniques

### 1. Isolate Name Resolution Issues

```python
# Check what 'list' resolves to in your module
def debug_name_resolution():
    print(f"list = {list}")
    print(f"list type = {type(list)}")
    print(f"list callable = {callable(list)}")
    
    # Compare with built-in
    import builtins
    print(f"builtins.list = {builtins.list}")
    print(f"Same object? {list is builtins.list}")

# Run this in your CLI module to see what's happening
```

### 2. Test Click Command Invocation

```python
# Test if a function is accidentally calling a Click command
def test_function_behavior():
    try:
        result = map_toolkits_to_handlers(('gtk4',))
        print(f"Success: {result}")
    except SystemExit as e:
        print(f"SystemExit (Click command called): {e}")
    except Exception as e:
        print(f"Other error: {e}")
        import traceback
        traceback.print_exc()
```

### 3. Verify Command Registration

```python
# Check what commands are actually registered
from unified_theming.cli.commands import cli

print("Registered commands:")
for cmd_name in cli.list_commands(None):
    cmd = cli.get_command(None, cmd_name)
    print(f"  {cmd_name}: {cmd}")
    print(f"    Callback: {cmd.callback}")
    print(f"    Params: {[p.name for p in cmd.params]}")
```

## Code Review Checklist

### Before Merging CLI Changes

- [ ] **Command names are descriptive** (not generic like 'list', 'get', 'set')
- [ ] **No built-in function shadowing** in the same module
- [ ] **Tests cover command registration** and parameter parsing
- [ ] **Integration tests verify end-to-end CLI workflow**
- [ ] **Help text is clear and consistent** across commands
- [ ] **Error messages are user-friendly** and actionable
- [ ] **Option names are consistent** across related commands

### Red Flags to Watch For

- ❌ Generic function names in Click modules
- ❌ `SystemExit` exceptions in unit tests (indicates Click command called)
- ❌ "Got unexpected extra argument" errors
- ❌ Exit code 2 in CLI tests (parsing failure)
- ❌ Mock assertions failing with "Called 0 times"

## Emergency Debugging

If you encounter similar issues:

### 1. Quick Diagnosis
```bash
# Test command recognition
python -m your_module.cli.commands your_command --help

# Test with minimal args
python -m your_module.cli.commands your_command arg1 --option value
```

### 2. Check Name Resolution
```python
# In your CLI module
print(f"Built-in list: {__builtins__['list']}")
print(f"Module list: {globals().get('list', 'Not found')}")
```

### 3. Isolate the Problem
```python
# Test the specific function that's failing
from your_module.cli.commands import problematic_function
result = problematic_function(test_args)
```

---

**Remember:** When in doubt, use explicit imports or alternative syntax to avoid name collisions entirely.
