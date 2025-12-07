"""GTK theme parser producing universal tokens."""

import re
from pathlib import Path
from typing import Dict, Optional

from ..color.spaces import Color
from ..color.wcag import ensure_contrast
from ..tokens.schema import (
    AccentTokens,
    BorderTokens,
    ContentTokens,
    StateTokens,
    SurfaceTokens,
    UniversalTokenSchema,
)
from .base import ThemeParseError, ThemeParser

# GTK color variables to semantic token mapping
GTK_TO_SEMANTIC = {
    # Surfaces
    "theme_bg_color": "surface.primary",
    "theme_base_color": "surface.secondary",
    "window_bg_color": "surface.primary",
    "view_bg_color": "surface.secondary",
    "card_bg_color": "surface.secondary",
    "popover_bg_color": "surface.elevated",
    "dialog_bg_color": "surface.elevated",
    "headerbar_bg_color": "surface.secondary",
    # Content
    "theme_fg_color": "content.primary",
    "theme_text_color": "content.primary",
    "window_fg_color": "content.primary",
    "view_fg_color": "content.primary",
    "insensitive_fg_color": "content.tertiary",
    "link_color": "content.link",
    "visited_link_color": "content.link_visited",
    # Accents
    "theme_selected_bg_color": "accent.primary",
    "accent_bg_color": "accent.primary",
    "accent_color": "accent.primary",
    "success_color": "accent.success",
    "success_bg_color": "accent.success",
    "warning_color": "accent.warning",
    "warning_bg_color": "accent.warning",
    "error_color": "accent.error",
    "error_bg_color": "accent.error",
    "destructive_bg_color": "accent.error",
    # Borders
    "borders": "border.default",
    "unfocused_borders": "border.subtle",
}


class GTKThemeParser(ThemeParser):
    """Parse GTK themes into universal token schema."""

    def __init__(self):
        self._color_regex = re.compile(
            r"@define-color\s+([\w-]+)\s+([^;]+);", re.IGNORECASE
        )

    def can_parse(self, source: Path) -> bool:
        """Check if source is a GTK theme directory."""
        if not source.is_dir():
            return False
        return (source / "gtk-4.0" / "gtk.css").exists() or (
            source / "gtk-3.0" / "gtk.css"
        ).exists()

    def parse(self, source: Path) -> UniversalTokenSchema:
        """Parse GTK theme into universal tokens."""
        if not source.exists():
            raise ThemeParseError("Theme directory not found", source)

        raw_colors = self._extract_colors(source)
        if not raw_colors:
            raise ThemeParseError("No color definitions found", source)

        semantic = self._map_to_semantic(raw_colors)
        return self._build_schema(semantic, source.name)

    def _extract_colors(self, theme_path: Path) -> Dict[str, str]:
        """Extract @define-color statements from CSS files."""
        colors: Dict[str, str] = {}

        css_files = [
            theme_path / "gtk-4.0" / "gtk.css",
            theme_path / "gtk-3.0" / "gtk.css",
        ]

        for css_file in css_files:
            if css_file.exists():
                try:
                    content = css_file.read_text(encoding="utf-8")
                    for match in self._color_regex.finditer(content):
                        var_name = match.group(1).strip()
                        color_value = match.group(2).strip()
                        colors[var_name] = color_value
                except Exception:
                    continue

        return colors

    def _map_to_semantic(self, raw_colors: Dict[str, str]) -> Dict[str, Color]:
        """Map GTK color variables to semantic token paths."""
        semantic: Dict[str, Color] = {}

        for gtk_var, token_path in GTK_TO_SEMANTIC.items():
            if gtk_var in raw_colors:
                color = self._parse_color(raw_colors[gtk_var])
                if color:
                    semantic[token_path] = color

        return semantic

    def _parse_color(self, value: str) -> Optional[Color]:
        """Parse color value string to Color object."""
        value = value.strip()

        if value.startswith("#"):
            try:
                return Color.from_hex(value)
            except Exception:
                return None

        rgb_match = re.match(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", value)
        if rgb_match:
            return Color(int(rgb_match[1]), int(rgb_match[2]), int(rgb_match[3]))

        rgba_match = re.match(
            r"rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)", value
        )
        if rgba_match:
            return Color(
                int(rgba_match[1]),
                int(rgba_match[2]),
                int(rgba_match[3]),
                float(rgba_match[4]),
            )

        return None

    def _build_schema(
        self, semantic: Dict[str, Color], name: str
    ) -> UniversalTokenSchema:
        """Build complete token schema, deriving missing values."""
        # Get or derive surface colors
        surface_primary = semantic.get("surface.primary", Color(255, 255, 255))
        is_dark = surface_primary.luminance() < 0.5

        # Derive missing surfaces
        surface_secondary = semantic.get("surface.secondary") or self._derive_surface(
            surface_primary, 0.03 if not is_dark else -0.03
        )
        surface_tertiary = self._derive_surface(
            surface_primary, 0.06 if not is_dark else -0.06
        )
        surface_elevated = semantic.get("surface.elevated", surface_primary)

        # Content colors
        content_primary = semantic.get(
            "content.primary", Color(255, 255, 255) if is_dark else Color(26, 26, 26)
        )
        content_primary = ensure_contrast(content_primary, surface_primary, 7.0)

        # Accent
        accent = semantic.get("accent.primary", Color.from_hex("#3584e4"))

        return UniversalTokenSchema(
            name=name,
            variant="dark" if is_dark else "light",
            surfaces=SurfaceTokens(
                primary=surface_primary,
                secondary=surface_secondary,
                tertiary=surface_tertiary,
                elevated=surface_elevated,
                inverse=Color(26, 26, 26) if not is_dark else Color(255, 255, 255),
            ),
            content=ContentTokens(
                primary=content_primary,
                secondary=self._with_opacity(content_primary, 0.7),
                tertiary=semantic.get("content.tertiary")
                or self._with_opacity(content_primary, 0.5),
                inverse=Color(255, 255, 255) if not is_dark else Color(26, 26, 26),
                link=semantic.get("content.link", accent),
                link_visited=semantic.get(
                    "content.link_visited", Color.from_hex("#8035e4")
                ),
            ),
            accents=AccentTokens(
                primary=accent,
                primary_container=self._derive_container(accent, is_dark),
                secondary=semantic.get("accent.secondary", Color(128, 128, 128)),
                success=semantic.get("accent.success", Color.from_hex("#2ec27e")),
                warning=semantic.get("accent.warning", Color.from_hex("#f5c211")),
                error=semantic.get("accent.error", Color.from_hex("#e01b24")),
            ),
            states=StateTokens(
                hover_overlay=0.08 if not is_dark else 0.12,
                pressed_overlay=0.12 if not is_dark else 0.16,
                focus_ring=accent,
                disabled_opacity=0.38,
            ),
            borders=BorderTokens(
                subtle=(
                    semantic.get("border.subtle") or Color(230, 230, 230)
                    if not is_dark
                    else Color(60, 60, 60)
                ),
                default=(
                    semantic.get("border.default") or Color(200, 200, 200)
                    if not is_dark
                    else Color(80, 80, 80)
                ),
                strong=Color(160, 160, 160) if not is_dark else Color(110, 110, 110),
            ),
            source="gtk",
        )

    def _derive_surface(self, base: Color, lightness_delta: float) -> Color:
        """Derive surface color by adjusting lightness."""
        oklch = base.to_oklch()
        return oklch.with_lightness(oklch.lightness + lightness_delta).to_rgb()

    def _with_opacity(self, color: Color, opacity: float) -> Color:
        """Return color with adjusted alpha."""
        return Color(color.r, color.g, color.b, opacity)

    def _derive_container(self, accent: Color, is_dark: bool) -> Color:
        """Derive container color from accent."""
        oklch = accent.to_oklch()
        if is_dark:
            return oklch.with_lightness(0.25).with_chroma(oklch.chroma * 0.5).to_rgb()
        return oklch.with_lightness(0.9).with_chroma(oklch.chroma * 0.3).to_rgb()
