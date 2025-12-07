"""Tests for the JSONTokenParser."""

import json
import pytest
from pathlib import Path

from unified_theming.parsers import JSONTokenParser, ThemeParseError
from unified_theming.tokens.schema import UniversalTokenSchema


class TestJSONTokenParser:
    """Test JSON theme parser."""

    @pytest.fixture
    def parser(self):
        return JSONTokenParser()

    @pytest.fixture
    def valid_json_file(self, tmp_path):
        """Creates a valid JSON token file."""
        content = {
            "surface": {
                "primary": {"$value": "#ffffff", "$type": "color"},
                "secondary": {"$value": "#f6f6f6", "$type": "color"},
                "tertiary": {"$value": "#eeeeee", "$type": "color"}
            },
            "content": {
                "primary": {"$value": "#1a1a1a", "$type": "color"}
            },
            "accent": {
                "primary": {"$value": "#3584e4", "$type": "color"}
            }
        }
        file_path = tmp_path / "valid_tokens.json"
        file_path.write_text(json.dumps(content))
        return file_path

    @pytest.fixture
    def json_file_with_references(self, tmp_path):
        """Creates a JSON token file with internal references."""
        content = {
            "color": {
                "primary": {"$value": "#3584e4", "$type": "color"},
                "surface": {
                    "light": {"$value": "#ffffff", "$type": "color"}
                }
            },
            "button": {
                "background": {"$value": "{color.primary}", "$type": "color"},
                "text": {"$value": "{color.surface.light}", "$type": "color"}
            }
        }
        file_path = tmp_path / "referenced_tokens.json"
        file_path.write_text(json.dumps(content))
        return file_path

    @pytest.fixture
    def invalid_json_file(self, tmp_path):
        """Creates an invalid JSON file."""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("this is not json {")
        return file_path

    def test_can_parse_json_file(self, parser, valid_json_file):
        """Test that the parser can identify valid JSON files."""
        assert parser.can_parse(valid_json_file) is True

    def test_can_parse_non_json_returns_false(self, parser, tmp_path):
        """Test that the parser does not parse non-JSON files."""
        non_json_file = tmp_path / "not_json.txt"
        non_json_file.write_text("hello")
        assert parser.can_parse(non_json_file) is False

    def test_can_parse_nonexistent_file_returns_false(self, parser, tmp_path):
        """Test that the parser does not parse nonexistent files."""
        non_existent_file = tmp_path / "nonexistent.json"
        assert parser.can_parse(non_existent_file) is False

    def test_parse_simple_tokens(self, parser, valid_json_file):
        """Test parsing a simple JSON token file."""
        tokens: UniversalTokenSchema = parser.parse(valid_json_file)

        assert tokens is not None
        assert isinstance(tokens, UniversalTokenSchema)

        # Check a few specific values
        assert tokens.surfaces.primary.to_hex() == "#ffffff"
        assert tokens.content.primary.to_hex() == "#1a1a1a"
        assert tokens.accents.primary.to_hex() == "#3584e4"

    def test_parse_with_references(self, parser, json_file_with_references):
        """Test parsing JSON tokens with internal references."""
        tokens: UniversalTokenSchema = parser.parse(json_file_with_references)

        assert tokens is not None
        # In this specific test case, the references point to other sections
        # but are not directly mapped to UniversalTokenSchema's predefined fields
        # unless _map_to_universal_schema is adapted for 'button' or 'color.primary'
        # For now, we'll check if the parser runs without error.
        # A more detailed test would involve adapting the mapping logic or
        # creating a test fixture that maps directly to UniversalTokenSchema fields.

        # Since the example above only contains color, surface and button, content,
        # we can check if primary accent color is not None, as per the reference
        # The example_tokens_with_references.json maps color.primary to button.background,
        # which is not directly mapped to accents.primary.
        # Let's check for the referenced color in 'other.referenced_color' if it were mapped.
        # For this test, we'll assert that basic parsing and reference resolution occurs
        # and that some color from the referenced data makes its way to the schema if mapped.
        # Since button.background is "{color.primary}", and color.primary is "#3584e4",
        # if the mapping correctly picks up color.primary into accents.primary, it should be #3584e4
        assert tokens.accents.primary.to_hex() == "#3584e4" # This relies on the _map_to_universal_schema picking it up

    def test_parse_invalid_json_raises(self, parser, invalid_json_file):
        """Test that parsing an invalid JSON file raises ThemeParseError."""
        with pytest.raises(ThemeParseError, match="Invalid JSON format"):
            parser.parse(invalid_json_file)

    def test_parse_non_json_file_raises_error(self, parser, tmp_path):
        """Test that parsing a non-JSON file (even if it exists) raises ThemeParseError."""
        non_json_file = tmp_path / "not_json.txt"
        non_json_file.write_text("hello world")
        with pytest.raises(ThemeParseError, match="cannot parse source"):
            parser.parse(non_json_file)

    def test_parse_missing_required_tokens(self, parser, tmp_path):
        """Test that parsing a JSON file missing some expected tokens still works."""
        content = {
            "surface": {
                "primary": {"$value": "#ffffff", "$type": "color"}
            }
            # Missing content and accent
        }
        file_path = tmp_path / "missing_tokens.json"
        file_path.write_text(json.dumps(content))

        tokens: UniversalTokenSchema = parser.parse(file_path)
        assert tokens.surfaces.primary.to_hex() == "#ffffff"
        assert tokens.content.primary is not None # It will be default_inverse_color
        assert tokens.accents.primary is not None # It will be default accent color
