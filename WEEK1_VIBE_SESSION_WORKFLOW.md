# Week 1 Vibe Session Workflow
## Perceptual Color Engine Foundation

**Duration:** 5 sessions (~2-3 hours each)  
**Goal:** Implement the perceptual color engine without breaking existing functionality  
**Vibe:** Flow state coding with music, minimal context switching

---

## Agent Delegation Strategy

| Day | Agent | Rationale |
|-----|-------|-----------|
| **Day 1** | **Claude Opus 4.5** | Foundational architecture, precise math implementations, clean abstractions |
| **Day 2** | **ChatGPT 5.1 Codex** | Test-heavy work, edge case coverage, systematic validation logic |
| **Day 3** | **Gemini 3 Pro** | Creative color derivation, experimental algorithms, visual intuition |
| **Day 4** | **Claude Opus 4.5** | Type system design, dataclass architecture, schema coherence |
| **Day 5** | **ChatGPT 5.1 Codex** | Integration testing, documentation, cleanup, CI/CD readiness |

### Agent Strengths Applied

**Claude Opus 4.5** (Days 1 & 4)
- Excels at: Architectural decisions, type safety, mathematical precision
- Best for: Core `Color` class, OKLCH transforms, `UniversalTokenSchema` design
- Style: Thoughtful, gets abstractions right the first time

**ChatGPT 5.1 Codex** (Days 2 & 5)
- Excels at: Exhaustive test coverage, edge cases, documentation
- Best for: WCAG compliance tests, integration, docstrings, final polish
- Style: Thorough, systematic, catches corner cases

**Gemini 3 Pro** (Day 3)
- Excels at: Creative problem-solving, multimodal reasoning, rapid iteration
- Best for: Palette generation algorithms, perceptual color operations, visual preview
- Style: Experimental, fast prototyping, good visual intuition

---

## Pre-Session Setup (15 min before Day 1)

```bash
cd ~/unified-theming
source venv/bin/activate
git checkout -b feature/perceptual-color-engine
pytest -q  # Verify baseline: 144 tests passing
```

**Environment:**
- Terminal with split panes (code left, tests right)
- Music: Lo-fi beats or ambient (no lyrics)
- Notifications OFF
- Water bottle filled

---

## Day 1: Color Class Foundation
**Theme:** "Building the atom"  
**Duration:** 2-3 hours  
**Energy:** High focus, foundational work

### Session Flow

#### Warmup (10 min)
```bash
# Review current color.py to understand what exists
cat unified_theming/utils/color.py | head -100
```

#### Block 1: Create Module Structure (20 min)
```bash
mkdir -p unified_theming/color
touch unified_theming/color/__init__.py
touch unified_theming/color/spaces.py
touch unified_theming/color/operations.py
touch unified_theming/color/wcag.py
```

#### Block 2: Core Color Class (60 min)

**File:** `unified_theming/color/spaces.py`

Implement in this order:
1. `Color` dataclass with r, g, b, a
2. `from_hex()` classmethod
3. `to_hex()` method
4. `to_linear_rgb()` for gamma correction
5. `luminance()` for WCAG calculations

**Checkpoint:** Write tests as you go
```python
# tests/test_color_spaces.py
def test_color_from_hex():
    c = Color.from_hex("#ff5500")
    assert c.r == 255
    assert c.g == 85
    assert c.b == 0

def test_color_roundtrip():
    original = "#3584e4"
    c = Color.from_hex(original)
    assert c.to_hex() == original
```

#### Block 3: OKLCH Conversion (45 min)

Add to `spaces.py`:
1. `OKLCHColor` dataclass
2. `Color.to_oklch()` method
3. `OKLCHColor.to_rgb()` method

**Math reference (keep open):**
- sRGB → Linear RGB → Oklab → OKLCH
- Use the matrix transforms from Appendix C.1

#### Cooldown (15 min)
```bash
# Run tests, commit progress
pytest tests/test_color_spaces.py -v
git add unified_theming/color/ tests/test_color_spaces.py
git commit -m "feat(color): Add Color class with OKLCH support"
```

### Day 1 Deliverables
- [ ] `Color` class with hex parsing
- [ ] Linear RGB conversion
- [ ] Luminance calculation
- [ ] `OKLCHColor` class
- [ ] Bidirectional OKLCH conversion
- [ ] 10+ unit tests passing

---

## Day 2: WCAG & Contrast Engine
**Theme:** "Accessibility is not optional"  
**Duration:** 2-3 hours  
**Energy:** Methodical, precision work

### Session Flow

#### Warmup (10 min)
```bash
pytest tests/test_color_spaces.py -v  # Verify Day 1 work
```

#### Block 1: WCAG Module (45 min)

**File:** `unified_theming/color/wcag.py`

```python
"""WCAG accessibility calculations."""

def contrast_ratio(fg: Color, bg: Color) -> float:
    """Calculate WCAG 2.1 contrast ratio."""
    ...

def meets_aa(fg: Color, bg: Color, large_text: bool = False) -> bool:
    """Check WCAG AA compliance (4.5:1 normal, 3:1 large)."""
    ...

def meets_aaa(fg: Color, bg: Color, large_text: bool = False) -> bool:
    """Check WCAG AAA compliance (7:1 normal, 4.5:1 large)."""
    ...
```

**Test cases to write:**
```python
def test_contrast_white_black():
    white = Color.from_hex("#ffffff")
    black = Color.from_hex("#000000")
    assert contrast_ratio(white, black) == pytest.approx(21.0, rel=0.01)

def test_meets_aa_pass():
    fg = Color.from_hex("#1a1a1a")
    bg = Color.from_hex("#ffffff")
    assert meets_aa(fg, bg) is True

def test_meets_aa_fail():
    fg = Color.from_hex("#767676")  # Gray that barely fails
    bg = Color.from_hex("#ffffff")
    assert meets_aa(fg, bg) is False
```

#### Block 2: Contrast Adjustment (60 min)

**File:** `unified_theming/color/operations.py`

```python
def ensure_contrast(fg: Color, bg: Color, min_ratio: float = 4.5) -> Color:
    """Adjust foreground color to meet minimum contrast ratio."""
    ...
```

**Algorithm:**
1. Check current contrast
2. If passing, return unchanged
3. Convert to OKLCH
4. Iteratively adjust lightness toward white/black
5. Return when contrast met

**Edge cases to test:**
- Already compliant colors (no change)
- Near-black on black (must lighten significantly)
- Near-white on white (must darken significantly)
- Preserve hue when possible

#### Block 3: Integration Test (30 min)

Create integration test with real theme colors:
```python
def test_adwaita_dark_contrast():
    """Verify Adwaita-dark colors meet accessibility."""
    bg = Color.from_hex("#1e1e1e")  # Adwaita dark bg
    fg = Color.from_hex("#ffffff")  # Adwaita dark fg
    assert meets_aa(fg, bg) is True
```

#### Cooldown (15 min)
```bash
pytest tests/test_color_*.py -v
git add -A
git commit -m "feat(color): Add WCAG contrast calculations and adjustment"
```

### Day 2 Deliverables
- [ ] `contrast_ratio()` function
- [ ] `meets_aa()` / `meets_aaa()` functions
- [ ] `ensure_contrast()` with OKLCH adjustment
- [ ] 15+ tests for accessibility functions
- [ ] Integration test with real theme colors

---

## Day 3: Perceptual Color Operations
**Theme:** "Colors that feel right"  
**Duration:** 2-3 hours  
**Energy:** Creative, experimental

### Session Flow

#### Warmup (10 min)
```bash
pytest -v --tb=short  # Full test suite check
```

#### Block 1: Color Derivation Functions (60 min)

**File:** `unified_theming/color/operations.py`

```python
class PerceptualColorEngine:
    """Perceptual color operations using OKLCH."""
    
    def derive_hover(self, base: Color) -> Color:
        """Generate hover state (8% lightness shift)."""
        ...
    
    def derive_pressed(self, base: Color) -> Color:
        """Generate pressed state (12% lightness shift)."""
        ...
    
    def derive_secondary_surface(self, primary: Color) -> Color:
        """Derive secondary surface from primary."""
        ...
    
    def derive_alternate(self, base: Color) -> Color:
        """Derive alternating row color."""
        ...
    
    def with_opacity(self, color: Color, opacity: float) -> Color:
        """Return color with adjusted alpha."""
        ...
```

**Key insight:** Light themes darken on hover, dark themes lighten.

#### Block 2: Palette Generation (45 min)

```python
def generate_palette(self, accent: Color, mode: str = "light") -> Dict[str, Color]:
    """Generate complete palette from single accent color."""
    ...
```

**Palette structure:**
- Surface colors (derived from mode)
- Content colors (contrast-adjusted)
- Accent variations (same hue, different lightness)
- State colors (success/warning/error with consistent saturation)

#### Block 3: Visual Verification Script (30 min)

Create a quick visual test:
```python
# scripts/preview_palette.py
"""Generate HTML preview of derived palette."""
from unified_theming.color import PerceptualColorEngine, Color

engine = PerceptualColorEngine()
accent = Color.from_hex("#3584e4")  # GNOME blue
palette = engine.generate_palette(accent, "light")

# Output HTML with color swatches
html = "<html><body style='font-family: sans-serif;'>"
for name, color in palette.items():
    html += f"<div style='background:{color.to_hex()};padding:20px;margin:5px;'>{name}: {color.to_hex()}</div>"
html += "</body></html>"

Path("palette_preview.html").write_text(html)
print("Open palette_preview.html in browser")
```

#### Cooldown (15 min)
```bash
pytest tests/test_color_*.py -v
python scripts/preview_palette.py  # Visual check
git add -A
git commit -m "feat(color): Add PerceptualColorEngine with palette generation"
```

### Day 3 Deliverables
- [ ] `PerceptualColorEngine` class
- [ ] Hover/pressed state derivation
- [ ] Surface color derivation
- [ ] `generate_palette()` from accent
- [ ] Visual preview script
- [ ] 20+ tests for operations

---

## Day 4: Universal Token Schema
**Theme:** "The Rosetta Stone"  
**Duration:** 2-3 hours  
**Energy:** Architectural thinking

### Session Flow

#### Warmup (10 min)
```bash
# Review existing types.py
cat unified_theming/core/types.py | head -80
```

#### Block 1: Token Dataclasses (45 min)

**File:** `unified_theming/tokens/schema.py`

```python
"""Universal design token schema."""
from dataclasses import dataclass, field
from typing import Optional
from ..color.spaces import Color

@dataclass
class SurfaceTokens:
    primary: Color
    secondary: Color
    tertiary: Color
    elevated: Color
    inverse: Color

@dataclass
class ContentTokens:
    primary: Color
    secondary: Color
    tertiary: Color
    inverse: Color
    link: Color
    link_visited: Color

@dataclass
class AccentTokens:
    primary: Color
    primary_container: Color
    secondary: Color
    success: Color
    warning: Color
    error: Color

@dataclass
class StateTokens:
    hover_overlay: float = 0.08
    pressed_overlay: float = 0.12
    focus_ring: Optional[Color] = None
    disabled_opacity: float = 0.38

@dataclass
class BorderTokens:
    subtle: Color
    default: Color
    strong: Color

@dataclass
class UniversalTokenSchema:
    name: str
    variant: str  # "light" | "dark"
    surfaces: SurfaceTokens
    content: ContentTokens
    accents: AccentTokens
    states: StateTokens
    borders: BorderTokens
    source: Optional[str] = None
```

#### Block 2: Default Token Sets (45 min)

**File:** `unified_theming/tokens/defaults.py`

```python
"""Default token values for light and dark modes."""

def create_light_defaults(accent: Color) -> UniversalTokenSchema:
    """Create default light mode tokens."""
    ...

def create_dark_defaults(accent: Color) -> UniversalTokenSchema:
    """Create default dark mode tokens."""
    ...

# Pre-built defaults
ADWAITA_LIGHT = create_light_defaults(Color.from_hex("#3584e4"))
ADWAITA_DARK = create_dark_defaults(Color.from_hex("#3584e4"))
```

#### Block 3: Token Validation (45 min)

**File:** `unified_theming/tokens/validation.py`

```python
"""Token schema validation."""
from dataclasses import dataclass
from typing import List

@dataclass
class TokenValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]

def validate_tokens(schema: UniversalTokenSchema) -> TokenValidationResult:
    """Validate token schema for completeness and accessibility."""
    errors = []
    warnings = []
    
    # Check contrast ratios
    content_bg_ratio = contrast_ratio(schema.content.primary, schema.surfaces.primary)
    if content_bg_ratio < 4.5:
        errors.append(f"Content/surface contrast {content_bg_ratio:.1f} below WCAG AA (4.5)")
    
    # Check accent visibility
    ...
    
    return TokenValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
```

#### Cooldown (15 min)
```bash
pytest tests/test_tokens*.py -v
git add -A
git commit -m "feat(tokens): Add UniversalTokenSchema with defaults and validation"
```

### Day 4 Deliverables
- [ ] `UniversalTokenSchema` dataclass
- [ ] All sub-token dataclasses
- [ ] Light/dark default generators
- [ ] Token validation with accessibility checks
- [ ] 15+ tests for token system

---

## Day 5: Integration & Polish
**Theme:** "Bringing it together"  
**Duration:** 2-3 hours  
**Energy:** Integration, cleanup

### Session Flow

#### Warmup (10 min)
```bash
# Full test suite
pytest -v
# Check coverage
pytest --cov=unified_theming/color --cov=unified_theming/tokens --cov-report=term-missing
```

#### Block 1: Module Exports (30 min)

**File:** `unified_theming/color/__init__.py`
```python
"""Perceptual color engine."""
from .spaces import Color, OKLCHColor
from .operations import PerceptualColorEngine
from .wcag import contrast_ratio, meets_aa, meets_aaa, ensure_contrast

__all__ = [
    "Color",
    "OKLCHColor", 
    "PerceptualColorEngine",
    "contrast_ratio",
    "meets_aa",
    "meets_aaa",
    "ensure_contrast",
]
```

**File:** `unified_theming/tokens/__init__.py`
```python
"""Universal design tokens."""
from .schema import (
    UniversalTokenSchema,
    SurfaceTokens,
    ContentTokens,
    AccentTokens,
    StateTokens,
    BorderTokens,
)
from .defaults import ADWAITA_LIGHT, ADWAITA_DARK, create_light_defaults, create_dark_defaults
from .validation import validate_tokens, TokenValidationResult

__all__ = [
    "UniversalTokenSchema",
    "SurfaceTokens",
    "ContentTokens",
    "AccentTokens",
    "StateTokens",
    "BorderTokens",
    "ADWAITA_LIGHT",
    "ADWAITA_DARK",
    "create_light_defaults",
    "create_dark_defaults",
    "validate_tokens",
    "TokenValidationResult",
]
```

#### Block 2: Backward Compatibility Bridge (45 min)

Create bridge to existing `color.py`:
```python
# unified_theming/utils/color.py - Add at bottom

# Bridge to new color engine (backward compatible)
def _new_color_to_dict(color: 'Color') -> Dict[str, int]:
    """Convert new Color to legacy dict format."""
    return {"r": color.r, "g": color.g, "b": color.b}

# Future: Deprecation warnings for old functions
```

#### Block 3: Documentation & Type Hints (45 min)

Add docstrings to all public functions:
```python
def ensure_contrast(fg: Color, bg: Color, min_ratio: float = 4.5) -> Color:
    """
    Adjust foreground color to meet minimum contrast ratio.
    
    Uses OKLCH color space for perceptually uniform adjustments.
    Preserves hue and chroma when possible, only adjusting lightness.
    
    Args:
        fg: Foreground color to adjust
        bg: Background color (unchanged)
        min_ratio: Minimum WCAG contrast ratio (default 4.5 for AA)
    
    Returns:
        Adjusted foreground color meeting contrast requirement
    
    Example:
        >>> bg = Color.from_hex("#1e1e1e")
        >>> fg = Color.from_hex("#666666")  # Low contrast gray
        >>> adjusted = ensure_contrast(fg, bg, 4.5)
        >>> contrast_ratio(adjusted, bg) >= 4.5
        True
    """
```

#### Block 4: Final Quality Checks (30 min)

```bash
# Format
black unified_theming/color unified_theming/tokens tests/test_color*.py tests/test_tokens*.py

# Type check
mypy unified_theming/color unified_theming/tokens

# Lint
flake8 unified_theming/color unified_theming/tokens

# Full test with coverage
pytest --cov=unified_theming --cov-report=html
```

#### Cooldown (15 min)
```bash
git add -A
git commit -m "feat(color): Complete Week 1 - Perceptual Color Engine foundation"

# Create PR or merge
git checkout main
git merge feature/perceptual-color-engine
git push
```

### Day 5 Deliverables
- [ ] Clean module exports
- [ ] Backward compatibility bridge
- [ ] Complete docstrings
- [ ] Type hints passing mypy
- [ ] 90%+ coverage on new modules
- [ ] All tests passing
- [ ] Code merged to main

---

## Week 1 Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| New tests | 50+ | `pytest --collect-only \| grep test_ \| wc -l` |
| Coverage (color/) | 90%+ | `pytest --cov=unified_theming/color` |
| Coverage (tokens/) | 90%+ | `pytest --cov=unified_theming/tokens` |
| Type errors | 0 | `mypy unified_theming/color unified_theming/tokens` |
| Lint errors | 0 | `flake8 unified_theming/color unified_theming/tokens` |
| Existing tests | Still passing | `pytest tests/` |

---

## Vibe Session Tips

### Flow State Triggers
- **Start ritual:** Same music playlist, same drink, same spot
- **Pomodoro variant:** 45 min code / 10 min break / 5 min review
- **End ritual:** Commit, write tomorrow's first task, close laptop

### When Stuck
1. Write the test first (TDD unsticks)
2. Rubber duck to the terminal
3. Take a walk, come back fresh
4. Check Appendix C in feasibility report for reference implementations

### Energy Management
- Day 1-2: High complexity (foundational)
- Day 3: Creative (palette generation)
- Day 4: Architectural (schemas)
- Day 5: Integration (lower cognitive load)

---

## Quick Reference Commands

```bash
# Run specific test file
pytest tests/test_color_spaces.py -v

# Run tests matching pattern
pytest -k "contrast" -v

# Coverage for specific module
pytest --cov=unified_theming/color --cov-report=term-missing

# Type check single file
mypy unified_theming/color/spaces.py

# Format single file
black unified_theming/color/spaces.py

# Interactive Python with imports
python -c "from unified_theming.color import Color; c = Color.from_hex('#ff0000'); print(c)"
```

---

---

## Agent Session Prompts

### Day 1 Prompt → Claude Opus 4.5

```
Context: I'm building a perceptual color engine for a Linux theming app. 
See REFACTORING_FEASIBILITY_REPORT.md for full architecture vision.

Task: Implement the foundational Color class in unified_theming/color/spaces.py

Requirements:
1. Color dataclass with r, g, b, a (sRGB 0-255, alpha 0-1)
2. from_hex() classmethod supporting #RGB, #RRGGBB, #RRGGBBAA
3. to_hex() method
4. to_linear_rgb() with proper gamma correction (sRGB transfer function)
5. luminance() using WCAG relative luminance formula
6. OKLCHColor dataclass with lightness (0-1), chroma (0-0.4), hue (0-360)
7. Color.to_oklch() and OKLCHColor.to_rgb() bidirectional conversion

Use the matrix transforms from Björn Ottosson's Oklab specification.
Write tests in tests/test_color_spaces.py as you implement.
Prioritize mathematical correctness over performance.
```

### Day 2 Prompt → ChatGPT 5.1 Codex

```
Context: Day 1 created Color and OKLCHColor classes in unified_theming/color/spaces.py.
Now we need WCAG accessibility calculations.

Task: Implement WCAG module in unified_theming/color/wcag.py

Requirements:
1. contrast_ratio(fg, bg) → float (WCAG 2.1 formula)
2. meets_aa(fg, bg, large_text=False) → bool (4.5:1 normal, 3:1 large)
3. meets_aaa(fg, bg, large_text=False) → bool (7:1 normal, 4.5:1 large)
4. ensure_contrast(fg, bg, min_ratio=4.5) → Color
   - Adjust fg lightness in OKLCH until contrast met
   - Preserve hue/chroma, only modify lightness
   - Handle edge cases: already compliant, impossible to achieve

Write exhaustive tests including:
- White on black (21:1)
- Known failing pairs (gray on white)
- Edge cases at exact thresholds
- Colors that need significant adjustment
- Verify hue preservation after adjustment
```

### Day 3 Prompt → Gemini 3 Pro

```
Context: We have Color, OKLCHColor, and WCAG functions. Now the creative part.

Task: Implement PerceptualColorEngine in unified_theming/color/operations.py

Requirements:
1. derive_hover(base) - 8% lightness shift (darken light colors, lighten dark)
2. derive_pressed(base) - 12% lightness shift
3. derive_secondary_surface(primary) - subtle variation for cards/sidebars
4. derive_alternate(base) - alternating row backgrounds
5. with_opacity(color, opacity) - alpha adjustment
6. generate_palette(accent, mode="light"|"dark") → Dict[str, Color]
   - From single accent, derive complete UI palette
   - Surface colors, content colors, accent variations, semantic colors

Be creative with the palette generation - consider:
- Complementary colors for success/warning/error
- Consistent saturation across semantic colors
- Proper contrast relationships built-in

Also create scripts/preview_palette.py that outputs HTML color swatches
for visual verification.
```

### Day 4 Prompt → Claude Opus 4.5

```
Context: Color engine is complete. Now we need the universal token schema
that bridges all toolkit-specific implementations.

Task: Create token system in unified_theming/tokens/

Files needed:
1. schema.py - Token dataclasses
2. defaults.py - Default light/dark token sets  
3. validation.py - Token validation with accessibility checks

Requirements for schema.py:
- SurfaceTokens: primary, secondary, tertiary, elevated, inverse
- ContentTokens: primary, secondary, tertiary, inverse, link, link_visited
- AccentTokens: primary, primary_container, secondary, success, warning, error
- StateTokens: hover_overlay, pressed_overlay, focus_ring, disabled_opacity
- BorderTokens: subtle, default, strong
- UniversalTokenSchema: combines all above + name, variant, source

Requirements for validation.py:
- validate_tokens() returns TokenValidationResult
- Check all content/surface pairs meet WCAG AA
- Check accent colors are distinguishable
- Return errors (blocking) and warnings (advisory)

Design for extensibility - future toolkits may need additional tokens.
```

### Day 5 Prompt → ChatGPT 5.1 Codex

```
Context: All components built. Final integration and polish day.

Tasks:
1. Create clean __init__.py exports for color/ and tokens/ modules
2. Add backward compatibility bridge in utils/color.py
3. Complete docstrings for all public functions (Google style)
4. Ensure mypy passes with strict mode
5. Run full test suite, fix any regressions
6. Generate coverage report, identify gaps
7. Final commit and merge to main

Quality checklist:
- [ ] All 144 original tests still pass
- [ ] 50+ new tests added
- [ ] 90%+ coverage on new modules
- [ ] 0 mypy errors
- [ ] 0 flake8 errors
- [ ] All public functions have docstrings with examples
- [ ] Module __all__ exports are complete

Document any decisions or trade-offs in commit messages.
```

---

## Handoff Protocol Between Agents

After each session, create a brief handoff note:

```markdown
## Day N Complete - Handoff to [Next Agent]

### Completed
- [x] Task 1
- [x] Task 2

### Files Modified
- unified_theming/color/spaces.py (new)
- tests/test_color_spaces.py (new)

### Test Status
- New tests: 12 passing
- Total suite: 156 passing

### Notes for Next Agent
- [Any context needed]
- [Decisions made and why]
- [Known issues to address]
```

---

*Let the vibe flow. Ship it.*
