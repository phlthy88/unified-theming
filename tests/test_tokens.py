"""Tests for universal token schema, defaults, and validation."""

import pytest

from unified_theming.color.spaces import Color
from unified_theming.tokens import (
    ADWAITA_DARK,
    ADWAITA_LIGHT,
    TokenValidationResult,
    UniversalTokenSchema,
    create_dark_tokens,
    create_light_tokens,
    validate_tokens,
)


class TestTokenDefaults:
    """Test default token creation."""

    def test_create_light_tokens(self):
        tokens = create_light_tokens()
        assert tokens.variant == "light"
        assert tokens.surfaces.primary.r == 255  # White background

    def test_create_dark_tokens(self):
        tokens = create_dark_tokens()
        assert tokens.variant == "dark"
        assert tokens.surfaces.primary.r == 30  # Dark background

    def test_custom_accent(self):
        accent = Color.from_hex("#ff5500")
        tokens = create_light_tokens(accent=accent)
        assert tokens.accents.primary.r == 255
        assert tokens.accents.primary.g == 85

    def test_custom_name(self):
        tokens = create_light_tokens(name="MyTheme")
        assert tokens.name == "MyTheme"

    def test_adwaita_light_preset(self):
        assert ADWAITA_LIGHT.name == "Adwaita"
        assert ADWAITA_LIGHT.variant == "light"

    def test_adwaita_dark_preset(self):
        assert ADWAITA_DARK.name == "Adwaita-dark"
        assert ADWAITA_DARK.variant == "dark"


class TestTokenValidation:
    """Test token validation."""

    def test_valid_light_tokens(self):
        tokens = create_light_tokens()
        result = validate_tokens(tokens)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_valid_dark_tokens(self):
        tokens = create_dark_tokens()
        result = validate_tokens(tokens)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_low_contrast_error(self):
        """Tokens with poor contrast should fail validation."""
        tokens = create_light_tokens()
        # Set content to light gray on white - poor contrast
        tokens.content.primary = Color(200, 200, 200)
        result = validate_tokens(tokens)
        assert result.valid is False
        assert any("contrast" in e.lower() for e in result.errors)

    def test_low_secondary_contrast_error(self):
        """Secondary content with poor contrast should error."""
        tokens = create_light_tokens()
        tokens.content.secondary = Color(240, 240, 240)
        result = validate_tokens(tokens)
        assert result.valid is False
        assert any("secondary" in e.lower() for e in result.errors)

    def test_accent_visibility_warning(self):
        """Low accent contrast should warn but not fail."""
        tokens = create_light_tokens()
        tokens.accents.primary = Color(230, 230, 230)  # Light gray accent
        result = validate_tokens(tokens)
        # May still be valid but should have warning
        assert any("accent" in w.lower() for w in result.warnings)

    def test_validation_result_structure(self):
        result = TokenValidationResult(valid=True)
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []


class TestTokenSchema:
    """Test token schema structure."""

    def test_schema_has_all_components(self):
        tokens = create_light_tokens()
        assert hasattr(tokens, "surfaces")
        assert hasattr(tokens, "content")
        assert hasattr(tokens, "accents")
        assert hasattr(tokens, "states")
        assert hasattr(tokens, "borders")

    def test_state_defaults(self):
        tokens = create_light_tokens()
        assert tokens.states.hover_overlay == 0.08
        assert tokens.states.pressed_overlay == 0.12
        assert tokens.states.disabled_opacity == 0.38

    def test_source_tracking(self):
        tokens = create_light_tokens()
        assert tokens.source == "defaults"
