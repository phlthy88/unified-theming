# Day 3 Handoff: GnomeShellHandler Integration

## Day 2 Complete ✅

### What Was Done
- Integrated `QtRenderer` into `QtHandler`
- Added `apply_from_tokens(tokens: UniversalTokenSchema)` method to `QtHandler`
- Handler now has `self.renderer = QtRenderer()` instance
- 6 new tests added in `tests/test_qt_handler_tokens.py`, all passing
- Verified backward compatibility

### Key Files Modified
- `unified_theming/handlers/qt_handler.py` - Added renderer integration
- `tests/test_qt_handler_tokens.py` - New test file

### Known Issues
- `tests/test_flatpak_handler.py` has 3 failures unrelated to recent changes (`test_apply_theme_permission_denied`, `test_apply_theme_partial_failure`, `test_apply_theme_all_dirs_fail`). These seem to be pre-existing.

---

## Day 3 Tasks: GnomeShellHandler Integration

**Agent:** Day 3 Agent
**Theme:** "Shell meets tokens"

### Objective
Replicate the Renderer/Handler pattern for `GnomeShellHandler`. Currently, `GnomeShellHandler` has internal logic (`_generate_shell_css`) that should be extracted into a dedicated renderer.

### Tasks
1. **Create Renderer:** Create `unified_theming/renderers/gnome_shell.py` implementing `BaseRenderer`.
    - Extract logic from `GnomeShellHandler._generate_shell_css` and `_generate_shell_css` (internal method) to the new renderer.
    - Map `UniversalTokenSchema` to shell CSS variables.
2. **Update Handler:** Modify `unified_theming/handlers/gnome_shell_handler.py`.
    - Import `GnomeShellRenderer`.
    - Initialize `self.renderer = GnomeShellRenderer()` in `__init__`.
    - Implement `apply_from_tokens(tokens: UniversalTokenSchema)`.
3. **Add Tests:** Create `tests/test_gnome_shell_handler_tokens.py`.
    - Verify token application writes correct CSS files.

### Reference Implementation (from QtHandler)

```python
# In __init__:
from ..renderers.gnome_shell import GnomeShellRenderer
self.renderer = GnomeShellRenderer()

# New method:
def apply_from_tokens(self, tokens: UniversalTokenSchema) -> bool:
    """Apply theme from universal tokens using GnomeShellRenderer."""
    logger.info(f"Applying theme '{tokens.name}' from tokens to GNOME Shell")
    
    try:
        rendered = self.renderer.render(tokens)
        
        # Write files
        for rel_path, content in rendered.files.items():
            target = self.config_dir / rel_path # Note: Check path logic for shell
            target.parent.mkdir(parents=True, exist_ok=True)
            if not write_file_with_backup(target, content):
                return False
        
        return True
    except Exception as e:
        logger.error(...)
        raise ...
```

### Success Criteria
- [ ] `unified_theming/renderers/gnome_shell.py` created
- [ ] `GnomeShellHandler` uses the new renderer
- [ ] `apply_from_tokens` implemented
- [ ] New tests passing
