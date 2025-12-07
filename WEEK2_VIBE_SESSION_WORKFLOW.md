# Week 2 Vibe Session Workflow
## Parser Enhancement & Token Integration

**Duration:** 5 sessions (~2-3 hours each)  
**Goal:** Enable parsing from multiple theme sources and integrate tokens with handlers  
**Branch:** `feature/parser-enhancement`

---

## Week 1 Recap ✅

| Deliverable | Status |
|-------------|--------|
| Color class with OKLCH | ✅ Complete |
| WCAG contrast functions | ✅ Complete |
| PerceptualColorEngine | ✅ Complete |
| UniversalTokenSchema | ✅ Complete |
| Token defaults & validation | ✅ Complete |
| 309 tests passing | ✅ Complete |
| 100% coverage on color/tokens | ✅ Complete |

---

## Agent Delegation Strategy

| Day | Agent | Focus |
|-----|-------|-------|
| **Day 1** | **Claude Opus 4.5** | Abstract parser interface, refactor GTK parser |
| **Day 2** | **Gemini 3 Pro** | JSON token parser (W3C Design Tokens format) |
| **Day 3** | **ChatGPT 5.1 Codex** | Qt theme parser, exhaustive tests |
| **Day 4** | **Claude Opus 4.5** | GTK renderer (tokens → CSS), handler integration |
| **Day 5** | **ChatGPT 5.1 Codex** | Qt renderer, integration tests, polish |

---

## Day 1: Abstract Parser Interface
**Agent:** Claude Opus 4.5  
**Theme:** "The foundation of flexibility"

### Tasks
1. Create `unified_theming/parsers/` module
2. Define abstract `ThemeParser` interface
3. Refactor existing `core/parser.py` → `parsers/gtk.py`
4. GTK parser now produces `UniversalTokenSchema`

### Deliverables
```
unified_theming/parsers/
├── __init__.py
├── base.py          # Abstract ThemeParser
└── gtk.py           # GTKThemeParser (refactored)
```

### Key Interface
```python
class ThemeParser(ABC):
    @abstractmethod
    def can_parse(self, source: Path) -> bool: ...
    
    @abstractmethod
    def parse(self, source: Path) -> UniversalTokenSchema: ...
```

---

## Day 2: JSON Token Parser
**Agent:** Gemini 3 Pro  
**Theme:** "Speaking the universal language"

### Tasks
1. Implement W3C Design Tokens format parser
2. Support token references (`{color.primary}`)
3. Support OKLCH extensions for derived colors
4. Create sample token files

### Deliverables
```
unified_theming/parsers/
└── json_tokens.py   # JSONTokenParser

examples/
└── tokens/
    ├── adwaita-light.json
    └── adwaita-dark.json
```

### Token Format Example
```json
{
  "color": {
    "primary": { "$value": "#3584e4", "$type": "color" },
    "surface": { "$value": "#ffffff", "$type": "color" }
  }
}
```

---

## Day 3: Qt Theme Parser
**Agent:** ChatGPT 5.1 Codex  
**Theme:** "Bridging the divide"

### Tasks
1. Parse kdeglobals color schemes
2. Parse Kvantum theme configs
3. Map Qt color roles to universal tokens
4. Comprehensive test coverage

### Deliverables
```
unified_theming/parsers/
└── qt.py            # QtThemeParser

tests/
└── test_parsers.py  # All parser tests
```

### Qt Color Mapping
```python
QT_TO_SEMANTIC = {
    "BackgroundNormal": "surface.primary",
    "ForegroundNormal": "content.primary",
    "Highlight": "accent.primary",
    # ...
}
```

---

## Day 4: GTK Renderer
**Agent:** Claude Opus 4.5  
**Theme:** "Tokens to reality"

### Tasks
1. Create `unified_theming/renderers/` module
2. Implement GTK renderer (tokens → CSS)
3. Integrate with existing GTKHandler
4. Maintain backward compatibility

### Deliverables
```
unified_theming/renderers/
├── __init__.py
├── base.py          # Abstract BaseRenderer
└── gtk.py           # GTKRenderer
```

### Key Interface
```python
class BaseRenderer(ABC):
    @abstractmethod
    def render(self, tokens: UniversalTokenSchema) -> RenderedTheme: ...
```

---

## Day 5: Qt Renderer & Integration
**Agent:** ChatGPT 5.1 Codex  
**Theme:** "Bringing it all together"

### Tasks
1. Implement Qt renderer (tokens → kdeglobals)
2. Integration tests for full pipeline
3. Update CLI to use new architecture
4. Documentation and cleanup

### Deliverables
```
unified_theming/renderers/
└── qt.py            # QtRenderer

tests/
├── test_renderers.py
└── test_integration_pipeline.py
```

### Full Pipeline Test
```python
def test_full_pipeline():
    # Parse GTK theme
    parser = GTKThemeParser()
    tokens = parser.parse(Path("/usr/share/themes/Adwaita"))
    
    # Validate
    result = validate_tokens(tokens)
    assert result.valid
    
    # Render to Qt
    renderer = QtRenderer()
    output = renderer.render(tokens)
    assert "BackgroundNormal" in output.kdeglobals
```

---

## Week 2 Success Metrics

| Metric | Target |
|--------|--------|
| New parsers | 3 (GTK, JSON, Qt) |
| New renderers | 2 (GTK, Qt) |
| New tests | 40+ |
| Total tests | 350+ |
| Coverage (parsers/) | 85%+ |
| Coverage (renderers/) | 85%+ |
| Backward compatibility | ✅ Maintained |

---

## Architecture After Week 2

```
┌─────────────────────────────────────────────────────────────┐
│                    THEME SOURCES                             │
│  GTK Theme │ Qt Theme │ JSON Tokens                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    PARSERS (NEW)                             │
│  GTKThemeParser │ QtThemeParser │ JSONTokenParser           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              UNIVERSAL TOKEN SCHEMA (Week 1)                 │
│  SurfaceTokens │ ContentTokens │ AccentTokens │ ...         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   RENDERERS (NEW)                            │
│  GTKRenderer │ QtRenderer                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  CONFIG FILES                                │
│  gtk.css │ kdeglobals │ Kvantum                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Session Prompts

### Day 1 → Claude Opus 4.5
```
Create the parser abstraction layer for unified-theming.

1. Create unified_theming/parsers/ module
2. Define abstract ThemeParser in base.py:
   - can_parse(source: Path) -> bool
   - parse(source: Path) -> UniversalTokenSchema
3. Refactor core/parser.py into parsers/gtk.py
4. GTKThemeParser.parse() should return UniversalTokenSchema
5. Map GTK @define-color variables to semantic tokens
6. Maintain backward compatibility with existing code

Use the token schema from unified_theming.tokens.
```

### Day 2 → Gemini 3 Pro
```
Implement JSON Design Token parser following W3C format.

1. Create parsers/json_tokens.py with JSONTokenParser
2. Parse W3C Design Tokens Community Group format
3. Support $value, $type, $description fields
4. Support token references: {color.primary}
5. Create example token files in examples/tokens/

Reference: https://design-tokens.github.io/community-group/format/
```

### Day 3 → ChatGPT 5.1 Codex
```
Implement Qt theme parser for kdeglobals and Kvantum.

1. Create parsers/qt.py with QtThemeParser
2. Parse ~/.config/kdeglobals [Colors:*] sections
3. Parse Kvantum theme.kvconfig files
4. Map Qt color roles to UniversalTokenSchema
5. Write exhaustive tests in tests/test_parsers.py

Cover edge cases: missing files, malformed configs, partial themes.
```

### Day 4 → Claude Opus 4.5
```
Create the renderer layer to output toolkit-specific configs.

1. Create unified_theming/renderers/ module
2. Define abstract BaseRenderer in base.py
3. Implement GTKRenderer that outputs:
   - gtk.css with @define-color statements
   - GSettings values for theme name
4. Integrate with existing GTKHandler
5. Ensure backward compatibility
```

### Day 5 → ChatGPT 5.1 Codex
```
Complete Week 2 with Qt renderer and integration.

1. Implement QtRenderer outputting kdeglobals format
2. Write integration tests for full parse→render pipeline
3. Update CLI commands to use new architecture (optional)
4. Final quality checks: black, flake8, mypy, pytest
5. Update HANDOFF_TO_NEXT_AGENT.md
```

---

## Quick Reference

```bash
# Setup
cd ~/unified-theming
source venv/bin/activate
git checkout -b feature/parser-enhancement

# Test specific module
pytest tests/test_parsers.py -v

# Coverage
pytest --cov=unified_theming/parsers --cov=unified_theming/renderers

# Quality
black unified_theming/ && flake8 unified_theming/ && mypy unified_theming/parsers unified_theming/renderers
```

---

*Week 2: From tokens to reality.*
