# Week 3 Vibe Session Workflow
## Handler Integration & CLI Enhancement

**Duration:** 5 sessions (~2-3 hours each)  
**Goal:** Integrate new parser/renderer architecture with existing handlers and CLI  
**Branch:** `feature/handler-integration`

---

## Week 2 Recap ✅

| Component | Status | Tests |
|-----------|--------|-------|
| ThemeParser interface | ✅ | 19 |
| GTKThemeParser | ✅ | - |
| JSONTokenParser | ✅ | 8 |
| BaseRenderer interface | ✅ | 18 |
| GTKRenderer | ✅ | - |
| QtRenderer | ✅ | 8 |
| Integration tests | ✅ | 8 |
| **Total** | **362 passing** | **53% coverage** |

---

## Week 3 Focus: Integration

The new architecture is built but not connected:
```
OLD: Theme Dir → Handler → Config Files
NEW: Theme Dir → Parser → Tokens → Renderer → Config Files
```

Week 3 connects these systems.

---

## Agent Delegation Strategy

| Day | Agent | Focus |
|-----|-------|-------|
| **Day 1** | **Claude Opus 4.5** | Refactor GTKHandler to use GTKRenderer |
| **Day 2** | **Gemini 3 Pro** | Refactor QtHandler to use QtRenderer |
| **Day 3** | **ChatGPT 5.1 Codex** | Update CLI commands for new architecture |
| **Day 4** | **Claude Opus 4.5** | Add token-based theme creation command |
| **Day 5** | **ChatGPT 5.1 Codex** | End-to-end tests, documentation, polish |

---

## Day 1: GTKHandler Integration
**Agent:** Claude Opus 4.5  
**Theme:** "Bridging old and new"

### Tasks
1. Update `GTKHandler.apply_theme()` to optionally use tokens
2. Add `apply_from_tokens(tokens: UniversalTokenSchema)` method
3. Use `GTKRenderer` internally for CSS generation
4. Maintain backward compatibility with existing API

### Key Changes
```python
class GTKHandler(BaseHandler):
    def __init__(self):
        self.renderer = GTKRenderer()
    
    def apply_from_tokens(self, tokens: UniversalTokenSchema) -> bool:
        rendered = self.renderer.render(tokens)
        # Write files, apply settings
        ...
    
    def apply_theme(self, theme_data: ThemeData) -> bool:
        # Existing behavior preserved
        ...
```

---

## Day 2: QtHandler Integration
**Agent:** Gemini 3 Pro  
**Theme:** "Qt meets tokens"

### Tasks
1. Update `QtHandler` to use `QtRenderer`
2. Add `apply_from_tokens()` method
3. Handle kdeglobals writing
4. Test with real Qt applications

### Key Changes
```python
class QtHandler(BaseHandler):
    def __init__(self):
        self.renderer = QtRenderer()
    
    def apply_from_tokens(self, tokens: UniversalTokenSchema) -> bool:
        rendered = self.renderer.render(tokens)
        self._write_kdeglobals(rendered.files[...])
        ...
```

---

## Day 3: CLI Enhancement
**Agent:** ChatGPT 5.1 Codex  
**Theme:** "Power to the user"

### Tasks
1. Add `--from-tokens` flag to `apply_theme` command
2. Add `unified-theming convert` command (theme → tokens)
3. Add `unified-theming render` command (tokens → config)
4. Update help text and examples

### New Commands
```bash
# Convert GTK theme to JSON tokens
unified-theming convert Adwaita-dark --output tokens.json

# Apply theme from token file
unified-theming apply_theme --from-tokens tokens.json

# Render tokens to specific toolkit
unified-theming render tokens.json --target gtk --output ./output/
```

---

## Day 4: Token Creation Command
**Agent:** Claude Opus 4.5  
**Theme:** "Create from scratch"

### Tasks
1. Add `unified-theming create` command
2. Interactive token creation wizard
3. Generate from accent color
4. Validate and save tokens

### New Command
```bash
# Create new theme tokens interactively
unified-theming create MyTheme

# Create from accent color
unified-theming create MyTheme --accent "#ff5500" --variant dark

# Create and apply immediately
unified-theming create MyTheme --accent "#3584e4" --apply
```

---

## Day 5: Polish & Documentation
**Agent:** ChatGPT 5.1 Codex  
**Theme:** "Ship it"

### Tasks
1. End-to-end integration tests
2. Update README with new commands
3. Add CLI usage examples
4. Final quality checks
5. Merge PR

### Tests to Add
```python
def test_full_workflow():
    """Test complete theme workflow."""
    # 1. Parse existing theme
    # 2. Convert to tokens
    # 3. Modify tokens
    # 4. Render to all toolkits
    # 5. Apply via handlers
```

---

## Week 3 Success Metrics

| Metric | Target |
|--------|--------|
| Handler integration | GTK + Qt |
| New CLI commands | 3+ |
| New tests | 30+ |
| Total tests | 400+ |
| Coverage | 55%+ |
| Documentation | Updated |

---

## Architecture After Week 3

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI                                  │
│  apply_theme │ convert │ render │ create │ validate         │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Parser    │   │   Tokens    │   │  Renderer   │
│  GTK/JSON   │──▶│   Schema    │──▶│  GTK/Qt     │
└─────────────┘   └─────────────┘   └─────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       HANDLERS                               │
│  GTKHandler │ QtHandler │ FlatpakHandler │ SnapHandler      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM CONFIG                             │
│  gtk.css │ kdeglobals │ flatpak overrides │ snap config     │
└─────────────────────────────────────────────────────────────┘
```

---

## Session Prompts

### Day 1 → Claude Opus 4.5
```
Integrate GTKRenderer into GTKHandler.

1. Import GTKRenderer in handlers/gtk_handler.py
2. Add apply_from_tokens(tokens: UniversalTokenSchema) method
3. Use renderer.render() to generate CSS
4. Write CSS to appropriate locations
5. Apply GSettings for theme name
6. Maintain backward compatibility with apply_theme()
7. Add tests for new method
```

### Day 2 → Gemini 3 Pro
```
Integrate QtRenderer into QtHandler.

1. Import QtRenderer in handlers/qt_handler.py
2. Add apply_from_tokens(tokens: UniversalTokenSchema) method
3. Use renderer.render() to generate kdeglobals
4. Write to ~/.config/kdeglobals
5. Maintain backward compatibility
6. Test with actual Qt applications if possible
```

### Day 3 → ChatGPT 5.1 Codex
```
Add new CLI commands for token workflow.

1. Add --from-tokens flag to apply_theme command
2. Add 'convert' command: theme dir → JSON tokens
3. Add 'render' command: JSON tokens → config files
4. Update cli/commands.py
5. Add comprehensive tests for new commands
6. Update --help text
```

### Day 4 → Claude Opus 4.5
```
Add theme creation command.

1. Add 'create' command to CLI
2. Accept --accent color and --variant (light/dark)
3. Use create_light_tokens/create_dark_tokens from tokens module
4. Validate created tokens
5. Save to JSON file
6. Optional --apply flag to apply immediately
```

### Day 5 → ChatGPT 5.1 Codex
```
Final integration and polish.

1. Write end-to-end integration tests
2. Update README.md with new commands
3. Add examples to docs/
4. Run full quality checks
5. Create PR summary
6. Merge to main
```

---

## Quick Reference

```bash
# Setup
cd ~/unified-theming
source venv/bin/activate
git checkout -b feature/handler-integration

# Test specific module
pytest tests/test_gtk_handler.py -v

# Full suite
pytest -q

# Quality
black unified_theming/ && flake8 unified_theming/
```

---

*Week 3: Integration is everything.*
