# Unified Theming: Refactoring Feasibility Report
## Transforming into a True Theme Unification Engine

**Date:** December 7, 2025  
**Version:** 1.0  
**Status:** Strategic Analysis

---

## Executive Summary

This report analyzes the current Unified Theming codebase and provides a roadmap for refactoring it into a **true theme unification engine** - a system that doesn't just apply themes across toolkits, but provides a semantic abstraction layer that enables genuine cross-toolkit theme consistency.

### Key Findings

| Aspect | Current State | Target State | Gap |
|--------|--------------|--------------|-----|
| Architecture | Handler-per-toolkit | Semantic token engine | Major |
| Color Translation | Direct mapping | Perceptual + semantic | Moderate |
| Theme Format | GTK-centric parsing | Universal token format | Major |
| Libadwaita Support | CSS injection (70%) | Full theming (95%) | Moderate |
| Qt Integration | kdeglobals generation | Native Qt style engine | Major |
| Container Support | Override-based | Portal-native | Minor |

### Recommendation

**Feasibility: HIGH** - The existing codebase provides a solid foundation. Refactoring is achievable in 3-4 months with the proposed phased approach.

---

## 1. Current Architecture Analysis

### 1.1 Strengths

The current implementation has several well-designed components:

```
✅ Clean 4-layer architecture (UI → Core → Handlers → System)
✅ Solid handler abstraction (BaseHandler pattern)
✅ Comprehensive type system (ThemeInfo, ThemeData, ValidationResult)
✅ Robust backup/rollback mechanism
✅ Good test coverage on core modules (manager: 93%, parser: 87%)
✅ Well-structured exception hierarchy
```

### 1.2 Architectural Limitations

```
❌ GTK-centric design - themes are parsed assuming GTK structure
❌ Direct color mapping - loses semantic meaning in translation
❌ No intermediate representation - each handler re-interprets raw data
❌ Toolkit-specific handlers are isolated - no shared color intelligence
❌ Missing perceptual color science - translations are mechanical, not visual
❌ No design token abstraction layer
```

### 1.3 Current Data Flow

```
Theme Directory → Parser → ThemeInfo → Manager → Handler → Config Files
                    ↓
              GTK Colors Dict
                    ↓
         Direct Mapping to Qt/Flatpak
```

**Problem:** The `ThemeData.colors` dictionary contains raw GTK variable names. Each handler must independently interpret these, leading to:
- Inconsistent translations
- Lost semantic meaning
- No perceptual color matching

---

## 2. Vision: True Theme Unification Engine

### 2.1 Core Concept: Design Token Architecture

A true unification engine requires an **intermediate semantic layer** that abstracts theme concepts away from toolkit-specific implementations.

```
┌─────────────────────────────────────────────────────────────────┐
│                    THEME SOURCES                                 │
│  GTK Theme │ Qt Theme │ JSON Tokens │ Wallpaper │ Brand Guide   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              SEMANTIC TOKEN ENGINE (NEW)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Universal Token Schema                      │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │   │
│  │  │ Surface │  │ Content │  │ Accent  │  │ State   │    │   │
│  │  │ Tokens  │  │ Tokens  │  │ Tokens  │  │ Tokens  │    │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Perceptual Color Engine                        │   │
│  │  • OKLCH color space operations                          │   │
│  │  • Contrast ratio calculations (WCAG)                    │   │
│  │  • Derived color generation                              │   │
│  │  • Dark/light mode transformations                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TOOLKIT RENDERERS                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   GTK    │  │    Qt    │  │ Flatpak  │  │  Shell   │        │
│  │ Renderer │  │ Renderer │  │ Renderer │  │ Renderer │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Universal Token Schema

Instead of toolkit-specific color variables, define semantic tokens:

```python
@dataclass
class UniversalTokenSchema:
    """Platform-agnostic design tokens."""
    
    # Surface tokens (backgrounds)
    surface_primary: Color      # Main window background
    surface_secondary: Color    # Cards, sidebars
    surface_tertiary: Color     # Nested containers
    surface_elevated: Color     # Popovers, dialogs
    
    # Content tokens (foregrounds)
    content_primary: Color      # Main text
    content_secondary: Color    # Secondary text
    content_tertiary: Color     # Disabled/placeholder
    content_inverse: Color      # Text on accent
    
    # Accent tokens
    accent_primary: Color       # Primary brand/action color
    accent_secondary: Color     # Secondary actions
    accent_success: Color       # Success states
    accent_warning: Color       # Warning states
    accent_error: Color         # Error states
    
    # Interactive state tokens
    state_hover: float          # Hover overlay opacity
    state_pressed: float        # Pressed overlay opacity
    state_focus: Color          # Focus ring color
    state_disabled: float       # Disabled opacity
    
    # Border tokens
    border_subtle: Color        # Subtle separators
    border_default: Color       # Default borders
    border_strong: Color        # Emphasized borders
    
    # Shadow tokens
    shadow_small: Shadow        # Subtle elevation
    shadow_medium: Shadow       # Cards, buttons
    shadow_large: Shadow        # Dialogs, popovers
```

### 2.3 Perceptual Color Engine

The key innovation: **perceptual color science** for accurate cross-toolkit translation.

```python
class PerceptualColorEngine:
    """
    Color operations in perceptually uniform color spaces.
    Uses OKLCH for accurate lightness/chroma manipulation.
    """
    
    def derive_hover_color(self, base: Color) -> Color:
        """Generate hover state using perceptual lightness shift."""
        oklch = base.to_oklch()
        if oklch.lightness > 0.5:
            # Dark overlay for light colors
            return oklch.with_lightness(oklch.lightness - 0.08).to_rgb()
        else:
            # Light overlay for dark colors
            return oklch.with_lightness(oklch.lightness + 0.08).to_rgb()
    
    def ensure_contrast(self, fg: Color, bg: Color, min_ratio: float = 4.5) -> Color:
        """Adjust foreground to meet WCAG contrast requirements."""
        current_ratio = self.contrast_ratio(fg, bg)
        if current_ratio >= min_ratio:
            return fg
        
        # Iteratively adjust lightness until contrast is met
        oklch = fg.to_oklch()
        direction = 1 if bg.luminance() < 0.5 else -1
        
        while current_ratio < min_ratio:
            oklch = oklch.with_lightness(oklch.lightness + (0.05 * direction))
            current_ratio = self.contrast_ratio(oklch.to_rgb(), bg)
        
        return oklch.to_rgb()
    
    def generate_palette(self, accent: Color, mode: str = "light") -> Dict[str, Color]:
        """Generate complete color palette from single accent color."""
        oklch = accent.to_oklch()
        
        if mode == "light":
            return {
                "surface_primary": Color("#FFFFFF"),
                "surface_secondary": oklch.with_lightness(0.97).with_chroma(0.01).to_rgb(),
                "content_primary": Color("#1A1A1A"),
                "accent_primary": accent,
                "accent_hover": self.derive_hover_color(accent),
                # ... more derived colors
            }
        # ... dark mode generation
```

---

## 3. Gap Analysis: Current vs Target

### 3.1 Parser Module (`parser.py`)

**Current:** Extracts `@define-color` statements from GTK CSS files.

**Gap:** Cannot parse Qt themes, JSON token files, or extract colors from images.

**Refactoring Required:**
```python
# Current
class UnifiedThemeParser:
    def extract_colors(self, theme_path: Path, toolkit: str = "gtk") -> ColorPalette:
        # Only handles GTK CSS

# Target
class UniversalThemeParser:
    def parse(self, source: ThemeSource) -> UniversalTokenSchema:
        """Parse any theme source into universal tokens."""
        if source.type == "gtk":
            return self._parse_gtk(source)
        elif source.type == "qt":
            return self._parse_qt(source)
        elif source.type == "json":
            return self._parse_json_tokens(source)
        elif source.type == "image":
            return self._extract_from_image(source)
```

### 3.2 Color Utilities (`color.py`)

**Current:** Format conversion (hex ↔ rgb ↔ hsl) and basic GTK→Qt mapping.

**Gap:** No perceptual color operations, no OKLCH support, no contrast calculations.

**Refactoring Required:**
```python
# Current
def gtk_to_qt_colors(gtk_colors: Dict[str, str]) -> Dict[str, str]:
    # Direct variable name mapping

# Target  
class Color:
    """Perceptually-aware color class."""
    
    def to_oklch(self) -> OKLCHColor: ...
    def luminance(self) -> float: ...
    def contrast_ratio(self, other: 'Color') -> float: ...
    def blend(self, other: 'Color', amount: float) -> 'Color': ...
    def adjust_lightness(self, delta: float) -> 'Color': ...
```

### 3.3 Handler Architecture

**Current:** Each handler independently interprets `ThemeData.colors`.

**Gap:** No shared semantic understanding, duplicated translation logic.

**Refactoring Required:**
```python
# Current
class GTKHandler(BaseHandler):
    def apply_theme(self, theme_data: ThemeData) -> bool:
        # Uses theme_data.colors directly

# Target
class GTKRenderer(BaseRenderer):
    def render(self, tokens: UniversalTokenSchema) -> RenderedTheme:
        """Transform universal tokens to GTK-specific output."""
        return RenderedTheme(
            css=self._generate_css(tokens),
            gsettings=self._generate_gsettings(tokens),
        )
```

### 3.4 Type System (`types.py`)

**Current:** `ThemeData` contains toolkit-specific color dict.

**Gap:** No universal token representation.

**Refactoring Required:**
```python
# Add new types
@dataclass
class UniversalTokenSchema:
    """Platform-agnostic design tokens."""
    surfaces: SurfaceTokens
    content: ContentTokens
    accents: AccentTokens
    states: StateTokens
    borders: BorderTokens
    shadows: ShadowTokens
    
@dataclass
class RenderedTheme:
    """Toolkit-specific rendered output."""
    toolkit: Toolkit
    files: Dict[Path, str]  # file path → content
    settings: Dict[str, Any]  # runtime settings
```

---

## 4. Refactoring Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Goal:** Introduce perceptual color engine without breaking existing functionality.

#### Week 1-2: Color Science Module
```
unified_theming/
└── color/
    ├── __init__.py
    ├── spaces.py      # Color space implementations (sRGB, OKLCH, etc.)
    ├── operations.py  # Perceptual operations (blend, contrast, derive)
    └── wcag.py        # Accessibility calculations
```

**Key Deliverables:**
- `Color` class with perceptual operations
- OKLCH color space support
- WCAG contrast ratio calculations
- Unit tests with 90%+ coverage

#### Week 3-4: Universal Token Schema
```
unified_theming/
└── tokens/
    ├── __init__.py
    ├── schema.py      # Token dataclasses
    ├── defaults.py    # Default token values
    └── validation.py  # Token validation
```

**Key Deliverables:**
- `UniversalTokenSchema` dataclass
- Default light/dark token sets
- Token validation utilities

### Phase 2: Parser Enhancement (Weeks 5-8)

**Goal:** Enable parsing from multiple theme sources.

#### Week 5-6: Multi-Source Parser
```
unified_theming/
└── parsers/
    ├── __init__.py
    ├── base.py        # Abstract parser interface
    ├── gtk.py         # GTK CSS parser (refactored from current)
    ├── qt.py          # Qt theme parser (NEW)
    ├── json.py        # JSON token parser (NEW)
    └── image.py       # Image color extraction (NEW)
```

**Key Deliverables:**
- Abstract `ThemeParser` interface
- Refactored GTK parser producing `UniversalTokenSchema`
- New Qt theme parser
- JSON design token parser (W3C Design Tokens format)

#### Week 7-8: Color Extraction Engine
```python
class ImageColorExtractor:
    """Extract dominant colors from images (wallpapers, brand assets)."""
    
    def extract(self, image_path: Path, num_colors: int = 5) -> List[Color]:
        """Extract dominant colors using k-means clustering."""
        ...
    
    def generate_palette(self, image_path: Path) -> UniversalTokenSchema:
        """Generate complete token schema from image."""
        colors = self.extract(image_path)
        accent = self._select_accent(colors)
        return self.color_engine.generate_palette(accent)
```

### Phase 3: Renderer Architecture (Weeks 9-12)

**Goal:** Replace handlers with semantic renderers.

#### Week 9-10: Renderer Framework
```
unified_theming/
└── renderers/
    ├── __init__.py
    ├── base.py        # Abstract renderer interface
    ├── gtk.py         # GTK renderer (CSS generation)
    ├── qt.py          # Qt renderer (kdeglobals, Kvantum)
    ├── flatpak.py     # Flatpak renderer
    └── shell.py       # GNOME Shell renderer
```

**Key Deliverables:**
- `BaseRenderer` abstract class
- GTK renderer producing CSS from tokens
- Qt renderer with semantic color mapping

#### Week 11-12: Integration & Migration
- Update `UnifiedThemeManager` to use new architecture
- Maintain backward compatibility with existing CLI/GUI
- Migration path for existing configurations

### Phase 4: Advanced Features (Weeks 13-16)

**Goal:** Implement advanced unification features.

#### Week 13-14: Libadwaita Deep Integration
- Implement marker file system (Zorin-style)
- Full widget theming support
- Automatic fallback handling

#### Week 15-16: Qt Style Engine
- Native Qt style plugin (optional)
- Kvantum theme generation
- Qt6 color scheme support

---

## 5. Technical Deep Dives

### 5.1 Perceptual Color Translation

The current direct mapping approach fails because GTK and Qt have different color semantics:

| GTK Variable | Qt Variable | Semantic Meaning |
|--------------|-------------|------------------|
| `theme_bg_color` | `BackgroundNormal` | Primary surface |
| `theme_selected_bg_color` | `Highlight` | Selection/accent |
| `insensitive_fg_color` | `ForegroundInactive` | Disabled text |

**Problem:** Direct mapping ignores that Qt expects specific contrast relationships.

**Solution:** Semantic token intermediary with perceptual derivation:

```python
def translate_to_qt(tokens: UniversalTokenSchema) -> QtColorScheme:
    """Translate universal tokens to Qt color scheme."""
    engine = PerceptualColorEngine()
    
    return QtColorScheme(
        # Window colors
        BackgroundNormal=tokens.surface_primary,
        ForegroundNormal=engine.ensure_contrast(
            tokens.content_primary, 
            tokens.surface_primary,
            min_ratio=4.5  # WCAG AA
        ),
        
        # Selection colors - Qt expects specific contrast
        Highlight=tokens.accent_primary,
        HighlightedText=engine.ensure_contrast(
            tokens.content_inverse,
            tokens.accent_primary,
            min_ratio=4.5
        ),
        
        # Derived states
        BackgroundAlternate=engine.derive_alternate(tokens.surface_primary),
        ForegroundInactive=engine.with_opacity(tokens.content_primary, 0.6),
    )
```

### 5.2 OKLCH Color Space

OKLCH (Oklab Lightness-Chroma-Hue) is the recommended color space for perceptual operations:

```python
@dataclass
class OKLCHColor:
    """Color in OKLCH perceptual color space."""
    lightness: float  # 0-1, perceptually uniform
    chroma: float     # 0-0.4, colorfulness
    hue: float        # 0-360, color angle
    
    def with_lightness(self, l: float) -> 'OKLCHColor':
        return OKLCHColor(l, self.chroma, self.hue)
    
    def with_chroma(self, c: float) -> 'OKLCHColor':
        return OKLCHColor(self.lightness, c, self.hue)
    
    def rotate_hue(self, degrees: float) -> 'OKLCHColor':
        return OKLCHColor(self.lightness, self.chroma, (self.hue + degrees) % 360)
```

**Why OKLCH?**
- Perceptually uniform lightness (unlike HSL)
- Predictable chroma behavior
- Hue stability during lightness changes
- Better for generating accessible color palettes

### 5.3 Design Token Format

Adopt W3C Design Tokens Community Group format for interoperability:

```json
{
  "$schema": "https://design-tokens.github.io/community-group/format/",
  "surface": {
    "primary": {
      "$value": "#ffffff",
      "$type": "color",
      "$description": "Primary background surface"
    },
    "secondary": {
      "$value": "{surface.primary}",
      "$type": "color",
      "$extensions": {
        "oklch": { "lightness": -0.03 }
      }
    }
  },
  "content": {
    "primary": {
      "$value": "#1a1a1a",
      "$type": "color",
      "$extensions": {
        "contrast": {
          "against": "{surface.primary}",
          "minRatio": 7.0
        }
      }
    }
  }
}
```

---

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing functionality | Medium | High | Comprehensive test suite, feature flags |
| Performance regression | Low | Medium | Benchmark critical paths, lazy evaluation |
| Color accuracy issues | Medium | Medium | Visual regression tests, user feedback |
| Qt integration complexity | High | Medium | Start with kdeglobals, defer style engine |

### 6.2 Maintenance Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Libadwaita API changes | High | High | Abstract libadwaita interactions, version pinning |
| Qt6 evolution | Medium | Medium | Modular Qt renderer, version detection |
| New toolkit emergence | Low | Low | Extensible renderer architecture |

### 6.3 Adoption Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| User confusion with new concepts | Medium | Medium | Clear documentation, migration guides |
| Theme author adoption | Medium | High | Provide conversion tools, maintain GTK compatibility |

---

## 7. Success Metrics

### 7.1 Technical Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Test coverage | 48% | 80% |
| Color translation accuracy | ~70% | 95% |
| Libadwaita coverage | 70% | 95% |
| Qt application consistency | ~60% | 90% |
| Theme parsing formats | 1 (GTK) | 4 (GTK, Qt, JSON, Image) |

### 7.2 User Experience Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Theme application time | ~2s | <1s |
| Cross-toolkit visual consistency | Moderate | High |
| Accessibility compliance | Partial | WCAG AA |

---

## 8. Resource Requirements

### 8.1 Development Effort

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Foundation | 4 weeks | 1 developer |
| Phase 2: Parser Enhancement | 4 weeks | 1 developer |
| Phase 3: Renderer Architecture | 4 weeks | 1-2 developers |
| Phase 4: Advanced Features | 4 weeks | 1-2 developers |
| **Total** | **16 weeks** | **~20 person-weeks** |

### 8.2 Dependencies

**New Python Dependencies:**
- `colour-science` or custom OKLCH implementation
- `Pillow` for image color extraction
- `numpy` for color clustering (optional)

**No New System Dependencies** - maintains current GTK4/Qt compatibility.

---

## 9. Conclusion

### 9.1 Feasibility Assessment

**Overall Feasibility: HIGH**

The current codebase provides an excellent foundation for transformation into a true theme unification engine. The key architectural changes are:

1. **Semantic Token Layer** - Introduces platform-agnostic design tokens
2. **Perceptual Color Engine** - Enables accurate cross-toolkit translation
3. **Multi-Source Parsing** - Supports diverse theme formats
4. **Renderer Architecture** - Clean separation of concerns

### 9.2 Recommended Approach

1. **Start with Phase 1** - The color science module provides immediate value and low risk
2. **Maintain backward compatibility** - Existing CLI/GUI should continue working
3. **Iterate based on feedback** - Release early, gather user feedback
4. **Collaborate with community** - Engage with Gradience, Linux Mint teams

### 9.3 Expected Outcomes

After refactoring:
- **True visual consistency** across GTK, Qt, Flatpak, and Shell
- **Accessibility by default** with WCAG-compliant color generation
- **Extensible architecture** ready for future toolkits
- **Industry-standard token format** for theme interoperability

---

## Appendix A: File-by-File Refactoring Guide

### Core Module Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `core/types.py` | Extend | Add `UniversalTokenSchema`, `RenderedTheme` |
| `core/manager.py` | Refactor | Use token engine, maintain API compatibility |
| `core/parser.py` | Replace | Move to `parsers/` module |

### New Modules

| Module | Purpose |
|--------|---------|
| `color/` | Perceptual color operations |
| `tokens/` | Universal token schema |
| `parsers/` | Multi-source theme parsing |
| `renderers/` | Toolkit-specific rendering |

### Handler Migration

| Current Handler | Target Renderer | Notes |
|-----------------|-----------------|-------|
| `gtk_handler.py` | `renderers/gtk.py` | CSS generation from tokens |
| `qt_handler.py` | `renderers/qt.py` | kdeglobals + Kvantum |
| `flatpak_handler.py` | `renderers/flatpak.py` | Portal configuration |
| `snap_handler.py` | `renderers/snap.py` | Minimal changes |
| `gnome_shell_handler.py` | `renderers/shell.py` | Shell CSS generation |

---

## Appendix B: Token Schema Reference

```python
# Complete Universal Token Schema

@dataclass
class SurfaceTokens:
    primary: Color          # Main background
    secondary: Color        # Cards, sidebars
    tertiary: Color         # Nested containers
    elevated: Color         # Popovers, dialogs
    inverse: Color          # Inverse surfaces

@dataclass
class ContentTokens:
    primary: Color          # Main text
    secondary: Color        # Secondary text
    tertiary: Color         # Hints, placeholders
    inverse: Color          # Text on accent
    link: Color             # Link text
    link_visited: Color     # Visited links

@dataclass
class AccentTokens:
    primary: Color          # Primary brand color
    primary_container: Color # Primary container
    secondary: Color        # Secondary actions
    success: Color          # Success states
    warning: Color          # Warning states
    error: Color            # Error states

@dataclass
class StateTokens:
    hover_overlay: float    # Hover opacity (0-1)
    pressed_overlay: float  # Pressed opacity
    focus_ring: Color       # Focus indicator
    disabled_opacity: float # Disabled state

@dataclass
class BorderTokens:
    subtle: Color           # Subtle separators
    default: Color          # Default borders
    strong: Color           # Emphasized borders
    focus: Color            # Focus borders

@dataclass
class ShadowTokens:
    small: Shadow           # Subtle elevation
    medium: Shadow          # Cards, buttons
    large: Shadow           # Dialogs, popovers

@dataclass
class UniversalTokenSchema:
    surfaces: SurfaceTokens
    content: ContentTokens
    accents: AccentTokens
    states: StateTokens
    borders: BorderTokens
    shadows: ShadowTokens
    
    # Metadata
    name: str
    variant: str  # "light" | "dark"
    source: Optional[str]  # Original theme source
```

---

**End of Report**

*This document should be reviewed and updated as implementation progresses.*


---

## Appendix C: Implementation Examples

### C.1 Perceptual Color Class Implementation

```python
"""
color/spaces.py - Color space implementations
"""
import math
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Color:
    """
    Perceptually-aware color class.
    Internal representation: sRGB (0-255)
    """
    r: int
    g: int
    b: int
    a: float = 1.0
    
    @classmethod
    def from_hex(cls, hex_str: str) -> 'Color':
        """Parse hex color string."""
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 3:
            hex_str = ''.join(c*2 for c in hex_str)
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        a = int(hex_str[6:8], 16) / 255 if len(hex_str) == 8 else 1.0
        return cls(r, g, b, a)
    
    def to_hex(self) -> str:
        """Convert to hex string."""
        if self.a < 1.0:
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}{int(self.a*255):02x}"
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    def to_linear_rgb(self) -> Tuple[float, float, float]:
        """Convert sRGB to linear RGB."""
        def linearize(c: int) -> float:
            c_norm = c / 255
            if c_norm <= 0.04045:
                return c_norm / 12.92
            return ((c_norm + 0.055) / 1.055) ** 2.4
        return (linearize(self.r), linearize(self.g), linearize(self.b))
    
    def luminance(self) -> float:
        """Calculate relative luminance (WCAG definition)."""
        lr, lg, lb = self.to_linear_rgb()
        return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb
    
    def to_oklch(self) -> 'OKLCHColor':
        """Convert to OKLCH color space."""
        # sRGB -> Linear RGB -> Oklab -> OKLCH
        lr, lg, lb = self.to_linear_rgb()
        
        # Linear RGB to Oklab
        l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
        m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
        s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb
        
        l_ = l ** (1/3) if l >= 0 else -((-l) ** (1/3))
        m_ = m ** (1/3) if m >= 0 else -((-m) ** (1/3))
        s_ = s ** (1/3) if s >= 0 else -((-s) ** (1/3))
        
        L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
        a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
        b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
        
        # Oklab to OKLCH
        C = math.sqrt(a*a + b*b)
        H = math.degrees(math.atan2(b, a)) % 360
        
        return OKLCHColor(L, C, H)
    
    def contrast_ratio(self, other: 'Color') -> float:
        """Calculate WCAG contrast ratio."""
        l1 = self.luminance()
        l2 = other.luminance()
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)


@dataclass  
class OKLCHColor:
    """Color in OKLCH perceptual color space."""
    lightness: float  # 0-1
    chroma: float     # 0-0.4 typical
    hue: float        # 0-360
    
    def with_lightness(self, l: float) -> 'OKLCHColor':
        return OKLCHColor(max(0, min(1, l)), self.chroma, self.hue)
    
    def with_chroma(self, c: float) -> 'OKLCHColor':
        return OKLCHColor(self.lightness, max(0, c), self.hue)
    
    def rotate_hue(self, degrees: float) -> 'OKLCHColor':
        return OKLCHColor(self.lightness, self.chroma, (self.hue + degrees) % 360)
    
    def to_rgb(self) -> Color:
        """Convert OKLCH back to sRGB."""
        # OKLCH -> Oklab
        a = self.chroma * math.cos(math.radians(self.hue))
        b = self.chroma * math.sin(math.radians(self.hue))
        L = self.lightness
        
        # Oklab -> Linear RGB
        l_ = L + 0.3963377774 * a + 0.2158037573 * b
        m_ = L - 0.1055613458 * a - 0.0638541728 * b
        s_ = L - 0.0894841775 * a - 1.2914855480 * b
        
        l = l_ ** 3
        m = m_ ** 3
        s = s_ ** 3
        
        lr = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
        lg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
        lb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
        
        # Linear RGB -> sRGB
        def gamma(c: float) -> int:
            if c <= 0.0031308:
                c_srgb = 12.92 * c
            else:
                c_srgb = 1.055 * (c ** (1/2.4)) - 0.055
            return max(0, min(255, int(c_srgb * 255 + 0.5)))
        
        return Color(gamma(lr), gamma(lg), gamma(lb))
```

### C.2 Universal Token Parser Example

```python
"""
parsers/gtk.py - GTK theme parser producing universal tokens
"""
from pathlib import Path
from typing import Dict, Optional
import re

from ..color.spaces import Color
from ..tokens.schema import UniversalTokenSchema, SurfaceTokens, ContentTokens, AccentTokens

class GTKThemeParser:
    """Parse GTK themes into universal token schema."""
    
    # Mapping from GTK variables to semantic tokens
    GTK_TO_SEMANTIC = {
        # Surfaces
        'theme_bg_color': 'surface.primary',
        'theme_base_color': 'surface.secondary',
        'window_bg_color': 'surface.primary',
        'view_bg_color': 'surface.secondary',
        'card_bg_color': 'surface.secondary',
        'popover_bg_color': 'surface.elevated',
        'dialog_bg_color': 'surface.elevated',
        
        # Content
        'theme_fg_color': 'content.primary',
        'theme_text_color': 'content.primary',
        'window_fg_color': 'content.primary',
        'view_fg_color': 'content.primary',
        'insensitive_fg_color': 'content.tertiary',
        'link_color': 'content.link',
        'visited_link_color': 'content.link_visited',
        
        # Accents
        'theme_selected_bg_color': 'accent.primary',
        'accent_bg_color': 'accent.primary',
        'accent_color': 'accent.primary',
        'success_color': 'accent.success',
        'success_bg_color': 'accent.success',
        'warning_color': 'accent.warning',
        'warning_bg_color': 'accent.warning',
        'error_color': 'accent.error',
        'error_bg_color': 'accent.error',
        'destructive_bg_color': 'accent.error',
        
        # Borders
        'borders': 'border.default',
    }
    
    def __init__(self):
        self._color_regex = re.compile(
            r'@define-color\s+([\w-]+)\s+([^;]+);', re.IGNORECASE
        )
    
    def parse(self, theme_path: Path) -> UniversalTokenSchema:
        """Parse GTK theme directory into universal tokens."""
        # Extract raw colors from CSS files
        raw_colors = self._extract_colors(theme_path)
        
        # Map to semantic tokens
        semantic = self._map_to_semantic(raw_colors)
        
        # Build token schema with derivations
        return self._build_schema(semantic, theme_path.name)
    
    def _extract_colors(self, theme_path: Path) -> Dict[str, str]:
        """Extract @define-color statements from CSS files."""
        colors = {}
        
        css_files = [
            theme_path / 'gtk-4.0' / 'gtk.css',
            theme_path / 'gtk-3.0' / 'gtk.css',
        ]
        
        for css_file in css_files:
            if css_file.exists():
                content = css_file.read_text()
                for match in self._color_regex.finditer(content):
                    var_name = match.group(1).strip()
                    color_value = match.group(2).strip()
                    colors[var_name] = color_value
        
        return colors
    
    def _map_to_semantic(self, raw_colors: Dict[str, str]) -> Dict[str, Color]:
        """Map GTK color variables to semantic token paths."""
        semantic = {}
        
        for gtk_var, token_path in self.GTK_TO_SEMANTIC.items():
            if gtk_var in raw_colors:
                try:
                    color = self._parse_color(raw_colors[gtk_var])
                    semantic[token_path] = color
                except ValueError:
                    pass  # Skip unparseable colors
        
        return semantic
    
    def _parse_color(self, value: str) -> Color:
        """Parse color value string to Color object."""
        value = value.strip()
        
        if value.startswith('#'):
            return Color.from_hex(value)
        
        if value.startswith('rgb('):
            match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', value)
            if match:
                return Color(int(match[1]), int(match[2]), int(match[3]))
        
        if value.startswith('rgba('):
            match = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)', value)
            if match:
                return Color(int(match[1]), int(match[2]), int(match[3]), float(match[4]))
        
        raise ValueError(f"Cannot parse color: {value}")
    
    def _build_schema(self, semantic: Dict[str, Color], name: str) -> UniversalTokenSchema:
        """Build complete token schema, deriving missing values."""
        from ..color.operations import PerceptualColorEngine
        engine = PerceptualColorEngine()
        
        # Get or derive surface colors
        surface_primary = semantic.get('surface.primary', Color(255, 255, 255))
        surface_secondary = semantic.get('surface.secondary') or \
            engine.derive_secondary_surface(surface_primary)
        
        # Determine if dark mode based on surface luminance
        is_dark = surface_primary.luminance() < 0.5
        
        # Get or derive content colors
        content_primary = semantic.get('content.primary') or \
            (Color(255, 255, 255) if is_dark else Color(26, 26, 26))
        
        # Ensure contrast
        content_primary = engine.ensure_contrast(content_primary, surface_primary, 7.0)
        
        # Build schema
        return UniversalTokenSchema(
            name=name,
            variant='dark' if is_dark else 'light',
            surfaces=SurfaceTokens(
                primary=surface_primary,
                secondary=surface_secondary,
                tertiary=semantic.get('surface.tertiary') or \
                    engine.derive_tertiary_surface(surface_primary),
                elevated=semantic.get('surface.elevated') or surface_primary,
                inverse=Color(26, 26, 26) if not is_dark else Color(255, 255, 255),
            ),
            content=ContentTokens(
                primary=content_primary,
                secondary=engine.with_opacity(content_primary, 0.7),
                tertiary=engine.with_opacity(content_primary, 0.5),
                inverse=Color(255, 255, 255) if not is_dark else Color(26, 26, 26),
                link=semantic.get('content.link') or Color(53, 132, 228),
                link_visited=semantic.get('content.link_visited') or Color(128, 53, 228),
            ),
            accents=AccentTokens(
                primary=semantic.get('accent.primary') or Color(53, 132, 228),
                primary_container=engine.derive_container(
                    semantic.get('accent.primary') or Color(53, 132, 228)
                ),
                secondary=semantic.get('accent.secondary') or Color(128, 128, 128),
                success=semantic.get('accent.success') or Color(46, 194, 126),
                warning=semantic.get('accent.warning') or Color(245, 194, 17),
                error=semantic.get('accent.error') or Color(224, 27, 36),
            ),
            # ... states, borders, shadows
        )
```

### C.3 Qt Renderer Example

```python
"""
renderers/qt.py - Qt theme renderer from universal tokens
"""
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

from ..tokens.schema import UniversalTokenSchema
from ..color.spaces import Color
from ..color.operations import PerceptualColorEngine

@dataclass
class QtColorScheme:
    """Qt color scheme data."""
    colors: Dict[str, Dict[str, str]]  # section -> {key: value}

class QtRenderer:
    """Render universal tokens to Qt configuration files."""
    
    def __init__(self):
        self.engine = PerceptualColorEngine()
    
    def render(self, tokens: UniversalTokenSchema) -> Dict[Path, str]:
        """Render tokens to Qt configuration files."""
        return {
            Path.home() / '.config' / 'kdeglobals': self._render_kdeglobals(tokens),
        }
    
    def _render_kdeglobals(self, tokens: UniversalTokenSchema) -> str:
        """Generate kdeglobals content from tokens."""
        scheme = self._build_color_scheme(tokens)
        
        lines = [
            f"# Generated by Unified Theming Engine",
            f"# Theme: {tokens.name}",
            f"# Variant: {tokens.variant}",
            "",
        ]
        
        for section, values in scheme.colors.items():
            lines.append(f"[{section}]")
            for key, value in values.items():
                lines.append(f"{key}={value}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _build_color_scheme(self, tokens: UniversalTokenSchema) -> QtColorScheme:
        """Build Qt color scheme from universal tokens."""
        
        def to_qt(color: Color) -> str:
            """Convert Color to Qt RGB format."""
            return f"{color.r},{color.g},{color.b}"
        
        # Derive Qt-specific colors with proper contrast
        window_bg = tokens.surfaces.primary
        window_fg = self.engine.ensure_contrast(
            tokens.content.primary, window_bg, 4.5
        )
        
        view_bg = tokens.surfaces.secondary
        view_fg = self.engine.ensure_contrast(
            tokens.content.primary, view_bg, 4.5
        )
        
        selection_bg = tokens.accents.primary
        selection_fg = self.engine.ensure_contrast(
            tokens.content.inverse, selection_bg, 4.5
        )
        
        return QtColorScheme(colors={
            "Colors:Window": {
                "BackgroundNormal": to_qt(window_bg),
                "BackgroundAlternate": to_qt(self.engine.derive_alternate(window_bg)),
                "ForegroundNormal": to_qt(window_fg),
                "ForegroundInactive": to_qt(self.engine.with_opacity(window_fg, 0.6)),
                "ForegroundActive": to_qt(tokens.accents.primary),
                "ForegroundLink": to_qt(tokens.content.link),
                "ForegroundVisited": to_qt(tokens.content.link_visited),
                "ForegroundNegative": to_qt(tokens.accents.error),
                "ForegroundNeutral": to_qt(tokens.accents.warning),
                "ForegroundPositive": to_qt(tokens.accents.success),
            },
            "Colors:View": {
                "BackgroundNormal": to_qt(view_bg),
                "BackgroundAlternate": to_qt(self.engine.derive_alternate(view_bg)),
                "ForegroundNormal": to_qt(view_fg),
                "ForegroundInactive": to_qt(self.engine.with_opacity(view_fg, 0.6)),
            },
            "Colors:Selection": {
                "BackgroundNormal": to_qt(selection_bg),
                "BackgroundAlternate": to_qt(self.engine.derive_alternate(selection_bg)),
                "ForegroundNormal": to_qt(selection_fg),
                "ForegroundInactive": to_qt(self.engine.with_opacity(selection_fg, 0.8)),
            },
            "Colors:Button": {
                "BackgroundNormal": to_qt(tokens.surfaces.secondary),
                "BackgroundAlternate": to_qt(self.engine.derive_alternate(tokens.surfaces.secondary)),
                "ForegroundNormal": to_qt(tokens.content.primary),
                "ForegroundInactive": to_qt(tokens.content.tertiary),
            },
            "Colors:Tooltip": {
                "BackgroundNormal": to_qt(tokens.surfaces.elevated),
                "ForegroundNormal": to_qt(tokens.content.primary),
            },
        })
```

---

## Appendix D: Migration Checklist

### Pre-Migration

- [ ] Backup current codebase
- [ ] Document current API surface
- [ ] Create comprehensive test suite for existing behavior
- [ ] Set up feature flags for gradual rollout

### Phase 1 Migration

- [ ] Implement `Color` class with OKLCH support
- [ ] Add perceptual color operations
- [ ] Create `UniversalTokenSchema` dataclass
- [ ] Write unit tests for color operations
- [ ] Verify no regression in existing functionality

### Phase 2 Migration

- [ ] Refactor `parser.py` to `parsers/gtk.py`
- [ ] Implement abstract `ThemeParser` interface
- [ ] Add JSON token parser
- [ ] Add Qt theme parser
- [ ] Update `UnifiedThemeManager` to use new parsers

### Phase 3 Migration

- [ ] Create `BaseRenderer` abstract class
- [ ] Implement `GTKRenderer`
- [ ] Implement `QtRenderer`
- [ ] Migrate handlers to renderers
- [ ] Update CLI commands
- [ ] Update GUI components

### Phase 4 Migration

- [ ] Implement Libadwaita marker file support
- [ ] Add image color extraction
- [ ] Implement Kvantum theme generation
- [ ] Performance optimization
- [ ] Documentation update

### Post-Migration

- [ ] Remove deprecated code
- [ ] Update all documentation
- [ ] Create migration guide for users
- [ ] Release notes

---

*Report generated by Kiro CLI analysis*
