"""GTK renderer - converts universal tokens to GTK CSS."""

from pathlib import Path

from ..color.spaces import Color
from ..tokens.schema import UniversalTokenSchema
from .base import BaseRenderer, RenderedTheme


class GTKRenderer(BaseRenderer):
    """Render universal tokens to GTK CSS format."""

    def render(self, tokens: UniversalTokenSchema) -> RenderedTheme:
        """Generate GTK CSS from universal tokens."""
        css = self._generate_css(tokens)

        return RenderedTheme(
            toolkit="gtk",
            files={
                Path("gtk-4.0/gtk.css"): css,
                Path("gtk-3.0/gtk.css"): css,
            },
            settings={
                "gtk-theme-name": tokens.name,
                "color-scheme": (
                    "prefer-dark" if tokens.variant == "dark" else "default"
                ),
            },
        )

    def _generate_css(self, tokens: UniversalTokenSchema) -> str:
        """Generate GTK CSS with @define-color statements."""
        lines = [
            f"/* Generated from {tokens.name} ({tokens.variant}) */",
            "",
            "/* Surface colors */",
            self._color_def("theme_bg_color", tokens.surfaces.primary),
            self._color_def("theme_base_color", tokens.surfaces.secondary),
            self._color_def("window_bg_color", tokens.surfaces.primary),
            self._color_def("view_bg_color", tokens.surfaces.secondary),
            self._color_def("card_bg_color", tokens.surfaces.secondary),
            self._color_def("popover_bg_color", tokens.surfaces.elevated),
            self._color_def("dialog_bg_color", tokens.surfaces.elevated),
            self._color_def("headerbar_bg_color", tokens.surfaces.secondary),
            "",
            "/* Content colors */",
            self._color_def("theme_fg_color", tokens.content.primary),
            self._color_def("theme_text_color", tokens.content.primary),
            self._color_def("window_fg_color", tokens.content.primary),
            self._color_def("view_fg_color", tokens.content.primary),
            self._color_def("insensitive_fg_color", tokens.content.tertiary),
            self._color_def("link_color", tokens.content.link),
            self._color_def("visited_link_color", tokens.content.link_visited),
            "",
            "/* Accent colors */",
            self._color_def("theme_selected_bg_color", tokens.accents.primary),
            self._color_def("accent_bg_color", tokens.accents.primary),
            self._color_def("accent_color", tokens.accents.primary),
            self._color_def("accent_fg_color", tokens.content.inverse),
            "",
            "/* Semantic colors */",
            self._color_def("success_color", tokens.accents.success),
            self._color_def("success_bg_color", tokens.accents.success),
            self._color_def("warning_color", tokens.accents.warning),
            self._color_def("warning_bg_color", tokens.accents.warning),
            self._color_def("error_color", tokens.accents.error),
            self._color_def("error_bg_color", tokens.accents.error),
            self._color_def("destructive_bg_color", tokens.accents.error),
            "",
            "/* Border colors */",
            self._color_def("borders", tokens.borders.default),
            self._color_def("unfocused_borders", tokens.borders.subtle),
            "",
        ]
        return "\n".join(lines)

    def _color_def(self, name: str, color: Color) -> str:
        """Generate @define-color statement."""
        if color.a < 1.0:
            return f"@define-color {name} rgba({color.r}, {color.g}, {color.b}, {color.a:.2f});"
        return f"@define-color {name} {color.to_hex()};"
