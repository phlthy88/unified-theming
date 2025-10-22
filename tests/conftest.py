"""
Shared pytest fixtures for Unified Theming Application tests.
"""
import pytest
from pathlib import Path
from unified_theming.core.parser import UnifiedThemeParser
from unified_theming.core.types import ThemeInfo, ThemeData, Toolkit


@pytest.fixture
def tmp_theme_dir(tmp_path):
    """Create temporary theme directory."""
    theme_dir = tmp_path / ".themes"
    theme_dir.mkdir()
    return theme_dir


@pytest.fixture
def valid_theme(tmp_path):
    """Create a complete valid theme."""
    theme = tmp_path / "ValidTheme"
    theme.mkdir()

    # GTK4 support
    gtk4 = theme / "gtk-4.0"
    gtk4.mkdir()
    (gtk4 / "gtk.css").write_text("""
@define-color theme_bg_color #ffffff;
@define-color theme_fg_color #000000;
@define-color theme_selected_bg_color #3584e4;
@define-color theme_selected_fg_color #ffffff;
    """)

    # GTK3 support
    gtk3 = theme / "gtk-3.0"
    gtk3.mkdir()
    (gtk3 / "gtk.css").write_text("""
@define-color theme_bg_color #ffffff;
@define-color theme_fg_color #000000;
    """)

    return theme


@pytest.fixture
def incomplete_theme(tmp_path):
    """Create a theme with only GTK3 support."""
    theme = tmp_path / "IncompleteTheme"
    theme.mkdir()

    # Only GTK3 support (no GTK4)
    gtk3 = theme / "gtk-3.0"
    gtk3.mkdir()
    (gtk3 / "gtk.css").write_text("""
@define-color theme_bg_color #ffffff;
@define-color theme_fg_color #000000;
    """)

    return theme


@pytest.fixture
def malformed_theme(tmp_path):
    """Create a theme with malformed CSS."""
    theme = tmp_path / "MalformedTheme"
    theme.mkdir()

    # GTK4 with malformed CSS
    gtk4 = theme / "gtk-4.0"
    gtk4.mkdir()
    (gtk4 / "gtk.css").write_text("""
@define-color theme_bg_color #ffffff;
/* Intentionally malformed - unclosed brace */
.some-selector {
    color: red;
    """)

    return theme


@pytest.fixture
def parser():
    """Create ThemeParser instance."""
    return UnifiedThemeParser()


@pytest.fixture
def sample_theme_data():
    """Create sample theme data for testing."""
    return ThemeData(
        name="TestTheme",
        toolkit=Toolkit.GTK4,
        colors={
            "theme_bg_color": "#ffffff",
            "theme_fg_color": "#000000",
            "theme_selected_bg_color": "#3584e4",
            "theme_selected_fg_color": "#ffffff"
        }
    )