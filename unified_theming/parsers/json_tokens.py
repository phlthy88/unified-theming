import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..color.spaces import Color
from ..tokens.schema import (
    AccentTokens,
    BorderTokens,
    ContentTokens,
    StateTokens,
    SurfaceTokens,
    UniversalTokenSchema,
)
from .base import ThemeParseError, ThemeParser


class JSONTokenParser(ThemeParser):
    """
    Parses W3C Design Tokens Community Group format JSON files
    into a UniversalTokenSchema.
    """

    def can_parse(self, source: Path) -> bool:
        """
        Checks if the parser can handle the given source.
        It can parse files with a '.json' extension that exist.
        """
        return source.is_file() and source.suffix == ".json"

    def parse(self, source: Path) -> UniversalTokenSchema:
        """
        Parses a W3C Design Token JSON file into a UniversalTokenSchema.
        """
        if not self.can_parse(source):
            raise ThemeParseError(
                f"JSONTokenParser cannot parse source: {source}", source=source
            )

        try:
            data = json.loads(source.read_text())
        except json.JSONDecodeError as e:
            raise ThemeParseError(
                f"Invalid JSON format in {source}: {e}", source=source
            ) from e

        resolved_data = self._resolve_references(data)
        return self._map_to_universal_schema(resolved_data, source.stem)

    def _resolve_references(self, data: Dict) -> Dict:
        """
        Recursively resolves references within the design token data.
        References are in the format '{path.to.token}'.
        """
        # This is a simplified reference resolver. A more robust one might
        # handle circular dependencies or more complex expressions.
        resolved_data = json.loads(json.dumps(data))  # Deep copy

        def get_value(obj: Dict, path: str) -> Any:
            keys = path.split(".")
            current = obj
            for key in keys:
                if key in current:
                    current = current[key]
                else:
                    return None  # Reference not found
            # If the current value is a dict and has a $value key, return it.
            # Otherwise, return the current value itself.
            return (
                current.get("$value")
                if isinstance(current, dict) and "$value" in current
                else current
            )

        def replace_refs(obj: Any) -> Any:
            if isinstance(obj, dict):
                # Check for $value key in the current dict
                if (
                    "$value" in obj
                    and isinstance(obj["$value"], str)
                    and obj["$value"].startswith("{")
                    and obj["$value"].endswith("}")
                ):
                    ref_path = obj["$value"][1:-1]
                    resolved_value = get_value(resolved_data, ref_path)
                    if resolved_value is not None:
                        obj["$value"] = resolved_value
                # Recursively apply to other dict items
                for key, value in obj.items():
                    obj[key] = replace_refs(value)
            elif isinstance(obj, list):
                obj = [replace_refs(item) for item in obj]
            return obj

        # Perform multiple passes to ensure all references are resolved,
        # especially for nested references.
        # A more advanced solution might build a dependency graph.
        for _ in range(5):  # Max 5 passes to resolve nested references
            old_data_str = json.dumps(
                resolved_data, sort_keys=True
            )  # sort_keys for consistent comparison
            resolved_data = replace_refs(resolved_data)
            if old_data_str == json.dumps(resolved_data, sort_keys=True):
                break  # No more changes, all references resolved or unresolvable

        return resolved_data

    def _map_to_universal_schema(
        self, data: Dict, theme_name: str
    ) -> UniversalTokenSchema:
        """
        Maps the resolved W3C Design Tokens to the UniversalTokenSchema.
        """

        # Helper to extract color values from token structure
        def get_color_value(token_group: Dict, path: str) -> Optional[Color]:
            keys = path.split(".")
            current = token_group
            for key in keys:
                if key not in current or not isinstance(current, dict):
                    return None
                current = current[key]

            # If the resolved value is a string, assume it's a color hex and convert
            if isinstance(current, dict) and "$value" in current:
                value = current["$value"]
                if isinstance(value, str):
                    try:
                        return Color.from_hex(value)
                    except ValueError:
                        return None  # Invalid color format
                # If value is already a Color object (from a previous resolution step)
                elif isinstance(value, Color):
                    return value
            elif isinstance(current, str):  # Direct string reference
                try:
                    return Color.from_hex(current)
                except ValueError:
                    return None
            return None

        # Default colors for mandatory fields that might be missing
        # TODO: Refine default color strategy (e.g., transparent, raise error)
        default_color = Color.from_hex("#000000")
        default_inverse_color = Color.from_hex("#ffffff")

        # Map 'surface' tokens
        surface_tokens_data = data.get("surface", {})
        surfaces = SurfaceTokens(
            primary=get_color_value(surface_tokens_data, "primary") or default_color,
            secondary=get_color_value(surface_tokens_data, "secondary")
            or get_color_value(surface_tokens_data, "primary")
            or default_color,
            tertiary=get_color_value(surface_tokens_data, "tertiary")
            or get_color_value(surface_tokens_data, "secondary")
            or default_color,
            elevated=get_color_value(surface_tokens_data, "elevated")
            or get_color_value(surface_tokens_data, "primary")
            or default_color,
            inverse=get_color_value(surface_tokens_data, "inverse")
            or default_inverse_color,
        )

        # Map 'content' tokens
        content_tokens_data = data.get("content", {})
        content = ContentTokens(
            primary=get_color_value(content_tokens_data, "primary")
            or default_inverse_color,
            secondary=get_color_value(content_tokens_data, "secondary")
            or get_color_value(content_tokens_data, "primary")
            or default_inverse_color,
            tertiary=get_color_value(content_tokens_data, "tertiary")
            or get_color_value(content_tokens_data, "secondary")
            or default_inverse_color,
            inverse=get_color_value(content_tokens_data, "inverse") or default_color,
            link=get_color_value(content_tokens_data, "link")
            or Color.from_hex("#3584e4"),  # Default link color
            link_visited=get_color_value(content_tokens_data, "link_visited")
            or Color.from_hex("#8035e4"),  # Default visited link color
        )

        # Map 'accent' tokens
        accent_tokens_data = data.get("accent", {})
        accents = AccentTokens(
            primary=get_color_value(accent_tokens_data, "primary")
            or Color.from_hex("#3584e4"),
            primary_container=get_color_value(accent_tokens_data, "primary_container")
            or Color.from_hex("#d3e5f9"),
            secondary=get_color_value(accent_tokens_data, "secondary")
            or Color.from_hex("#729fcf"),
            success=get_color_value(accent_tokens_data, "success")
            or Color.from_hex("#2ec27e"),
            warning=get_color_value(accent_tokens_data, "warning")
            or Color.from_hex("#f5c211"),
            error=get_color_value(accent_tokens_data, "error")
            or Color.from_hex("#e01b24"),
        )

        # Map 'state' tokens (StateTokens has default values)
        state_tokens_data = data.get("state", {})
        states = StateTokens(
            hover_overlay=state_tokens_data.get(
                "hover_overlay", StateTokens.hover_overlay
            ),
            pressed_overlay=state_tokens_data.get(
                "pressed_overlay", StateTokens.pressed_overlay
            ),
            focus_ring=get_color_value(state_tokens_data, "focus_ring"),  # Optional
            disabled_opacity=state_tokens_data.get(
                "disabled_opacity", StateTokens.disabled_opacity
            ),
        )

        # Map 'border' tokens
        border_tokens_data = data.get("border", {})
        borders = BorderTokens(
            subtle=get_color_value(border_tokens_data, "subtle")
            or Color.from_hex("#d3d7cf"),
            default=get_color_value(border_tokens_data, "default")
            or Color.from_hex("#babdb6"),
            strong=get_color_value(border_tokens_data, "strong")
            or Color.from_hex("#888888"),
        )

        # Determine theme variant (light/dark)
        # For simplicity, default to "light". A more sophisticated approach
        # would involve analyzing background colors.
        theme_variant = "light"

        return UniversalTokenSchema(
            name=theme_name,
            variant=theme_variant,
            surfaces=surfaces,
            content=content,
            accents=accents,
            states=states,
            borders=borders,
            source="json_tokens",
        )
