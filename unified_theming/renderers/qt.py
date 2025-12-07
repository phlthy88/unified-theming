"""Qt renderer - converts universal tokens to kdeglobals format."""

from pathlib import Path

from ..color.spaces import Color
from ..tokens.schema import UniversalTokenSchema
from .base import BaseRenderer, RenderedTheme


class QtRenderer(BaseRenderer):
    """Render universal tokens to Qt's kdeglobals configuration."""

    def render(self, tokens: UniversalTokenSchema) -> RenderedTheme:
        """Generate kdeglobals content from universal tokens."""
        kdeglobals = self._generate_kdeglobals(tokens)

        return RenderedTheme(
            toolkit="qt",
            files={Path("kdeglobals"): kdeglobals},
            settings={"color-scheme": tokens.name},
        )

    def _generate_kdeglobals(self, tokens: UniversalTokenSchema) -> str:
        """Build kdeglobals INI content."""
        lines = [
            f"# Generated from {tokens.name} ({tokens.variant})",
            "[General]",
            f"ColorScheme={tokens.name}",
            "",
            "[Colors:Window]",
            f"BackgroundNormal={self._rgb(tokens.surfaces.primary)}",
            f"BackgroundAlternate={self._rgb(tokens.surfaces.secondary)}",
            f"ForegroundNormal={self._rgb(tokens.content.primary)}",
            f"ForegroundInactive={self._rgb(tokens.content.secondary)}",
            f"ForegroundActive={self._rgb(tokens.content.primary)}",
            f"ForegroundLink={self._rgb(tokens.content.link)}",
            f"ForegroundVisited={self._rgb(tokens.content.link_visited)}",
            f"ForegroundNegative={self._rgb(tokens.accents.error)}",
            f"ForegroundNeutral={self._rgb(tokens.accents.warning)}",
            f"ForegroundPositive={self._rgb(tokens.accents.success)}",
            f"DecorationFocus={self._rgb(tokens.accents.primary)}",
            f"DecorationHover={self._rgb(tokens.accents.primary_container)}",
            "",
            "[Colors:View]",
            f"BackgroundNormal={self._rgb(tokens.surfaces.secondary)}",
            f"BackgroundAlternate={self._rgb(tokens.surfaces.tertiary)}",
            f"ForegroundNormal={self._rgb(tokens.content.primary)}",
            "",
            "[Colors:Button]",
            f"BackgroundNormal={self._rgb(tokens.surfaces.secondary)}",
            f"BackgroundAlternate={self._rgb(tokens.surfaces.tertiary)}",
            f"ForegroundNormal={self._rgb(tokens.content.primary)}",
            f"ForegroundInactive={self._rgb(tokens.content.tertiary)}",
            f"ForegroundActive={self._rgb(tokens.content.primary)}",
            "",
            "[Colors:Selection]",
            f"BackgroundNormal={self._rgb(tokens.accents.primary)}",
            f"ForegroundNormal={self._rgb(tokens.content.inverse)}",
            "",
            "[Colors:Tooltip]",
            f"BackgroundNormal={self._rgb(tokens.surfaces.elevated)}",
            f"ForegroundNormal={self._rgb(tokens.content.primary)}",
        ]
        return "\n".join(lines)

    def _rgb(self, color: Color) -> str:
        """Return Qt rgb triple (ignores alpha channel)."""
        return f"{color.r},{color.g},{color.b}"
