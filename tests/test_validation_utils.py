import pytest
from unified_theming.core.types import ThemeData, Toolkit, ValidationLevel
from unified_theming.core.validation_utils import validate_wcag_contrast


@pytest.fixture
def mock_theme_data():
    """Fixture for a ThemeData object with various colors."""
    return ThemeData(
        name="TestTheme",
        toolkit=Toolkit.GTK3,
        colors={
            "passing_fg": "#FFFFFF",  # White
            "passing_bg": "#000000",  # Black
            "failing_fg": "#777777",  # Gray
            "failing_bg": "#AAAAAA",  # Light Gray
            "malformed_fg": "invalid_hex",
            "malformed_bg": "#000",  # Technically valid short hex, but will be caught if strict
            "valid_short_hex_fg": "#FFF",
            "valid_short_hex_bg": "#000",
            "medium_contrast_fg": "#FFFFFF",
            "medium_contrast_bg": "#777777",  # Should pass AA for large text, fail for normal
            "another_failing_fg": "#888888",
            "another_failing_bg": "#BBBBBB",
        },
    )


def test_validate_wcag_contrast_passing_ratio(mock_theme_data):
    """Test with a color pair that meets the minimum contrast."""
    color_pairs = [("passing_fg", "passing_bg")]
    messages = validate_wcag_contrast(mock_theme_data, color_pairs, "TestComponent")
    assert not messages, "No warnings expected for passing contrast."


def test_validate_wcag_contrast_failing_ratio(mock_theme_data):
    """Test with a color pair that fails the minimum contrast."""
    color_pairs = [("failing_fg", "failing_bg")]
    messages = validate_wcag_contrast(mock_theme_data, color_pairs, "TestComponent")
    assert len(messages) == 1
    assert messages[0].level == ValidationLevel.WARNING
    assert "Insufficient contrast ratio" in messages[0].message
    assert "failing_fg" in messages[0].message
    assert "failing_bg" in messages[0].message


def test_validate_wcag_contrast_missing_color(mock_theme_data):
    """Test with a color pair where one color is truly missing from theme_data."""
    color_pairs = [
        ("non_existent_fg", "passing_bg")
    ]  # non_existent_fg is not in mock_theme_data.colors
    messages = validate_wcag_contrast(mock_theme_data, color_pairs, "TestComponent")
    assert not messages, "No warnings expected when a color is truly missing."


def test_validate_wcag_contrast_malformed_hex(mock_theme_data):
    """Test with a malformed hex color string."""
    color_pairs = [("malformed_fg", "passing_bg")]
    messages = validate_wcag_contrast(mock_theme_data, color_pairs, "TestComponent")
    assert len(messages) == 1
    assert messages[0].level == ValidationLevel.WARNING
    assert "Could not parse hex color" in messages[0].message
    assert "malformed_fg" in messages[0].message


def test_validate_wcag_contrast_multiple_pairs(mock_theme_data):
    """Test with multiple color pairs, some passing, some failing, and some with missing colors."""
    color_pairs = [
        ("passing_fg", "passing_bg"),
        ("failing_fg", "failing_bg"),
        ("non_existent_fg", "passing_bg"),  # This should now not generate a warning
        ("another_failing_fg", "another_failing_bg"),
    ]
    messages = validate_wcag_contrast(mock_theme_data, color_pairs, "TestComponent")
    assert (
        len(messages) == 2
    )  # Expecting two failures: failing_fg/bg and another_failing_fg/bg
    assert any("failing_fg" in m.message for m in messages)
    assert any("another_failing_fg" in m.message for m in messages)


def test_validate_wcag_contrast_custom_min_contrast(mock_theme_data):
    """Test with a custom minimum contrast requirement."""
    color_pairs = [("medium_contrast_fg", "medium_contrast_bg")]

    # This pair should fail AA (4.5) but pass AAA large text (4.5) if interpreted as such
    # For normal text, it should fail 4.5
    messages = validate_wcag_contrast(
        mock_theme_data, color_pairs, "TestComponent", min_contrast=7.0
    )
    assert len(messages) == 1
    assert messages[0].level == ValidationLevel.WARNING
    assert "Required: 7.00" in messages[0].message

    messages = validate_wcag_contrast(
        mock_theme_data, color_pairs, "TestComponent", min_contrast=3.0
    )
    assert not messages, "Should pass with lower contrast requirement"


def test_validate_wcag_contrast_component_name(mock_theme_data):
    """Test that the component name is correctly included in the message."""
    color_pairs = [("failing_fg", "failing_bg")]
    messages = validate_wcag_contrast(mock_theme_data, color_pairs, "MyAwesomeHandler")
    assert len(messages) == 1
    assert messages[0].component == "MyAwesomeHandler"


def test_validate_wcag_contrast_valid_short_hex(mock_theme_data):
    """Test with valid 3-digit hex codes, which should be handled correctly."""
    color_pairs = [("valid_short_hex_fg", "valid_short_hex_bg")]
    messages = validate_wcag_contrast(mock_theme_data, color_pairs, "TestComponent")
    assert not messages, "No warnings expected for valid short hex codes."
