"""
Tests for GnomeShellHandler.

Tests cover GNOME Shell theme application, CSS generation,
User Theme extension detection, and validation.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from unified_theming.core.types import (
    ThemeData,
    Toolkit,
    ValidationResult,
)
from unified_theming.handlers.gnome_shell_handler import GnomeShellHandler


@pytest.fixture
def gnome_shell_handler():
    """Create a GnomeShellHandler instance for testing."""
    return GnomeShellHandler()


@pytest.fixture
def sample_gnome_shell_theme_data():
    """Create sample theme data for GNOME Shell testing."""
    return ThemeData(
        name="TestShellTheme",
        toolkit=Toolkit.GNOME_SHELL,
        colors={
            "theme_bg_color": "#303030",
            "theme_fg_color": "#ffffff",
            "theme_base_color": "#242424",
            "theme_text_color": "#eeeeee",
            "theme_selected_bg_color": "#3584e4",
            "theme_selected_fg_color": "#ffffff",
            "borders": "#1c1c1c",
            "success_color": "#33d17a",
            "warning_color": "#f5c211",
            "error_color": "#e01b24",
        },
        additional_data={},
    )


@pytest.fixture
def gnome_shell_theme_with_path(tmp_path):
    """Create a theme with gnome-shell directory."""
    theme_path = tmp_path / "ShellTheme"
    theme_path.mkdir()

    # Create gnome-shell directory with CSS
    gnome_shell_dir = theme_path / "gnome-shell"
    gnome_shell_dir.mkdir()

    shell_css = """
/* GNOME Shell Theme */
@define-color panel_bg_color #303030;
@define-color panel_fg_color #ffffff;
@define-color osd_bg_color #242424;
@define-color osd_fg_color #eeeeee;

#panel {
    background-color: @panel_bg_color;
    color: @panel_fg_color;
}
"""
    (gnome_shell_dir / "gnome-shell.css").write_text(shell_css)

    return theme_path


class TestGnomeShellHandlerInit:
    """Tests for GnomeShellHandler initialization."""

    def test_handler_init(self, gnome_shell_handler):
        """Test that handler initializes with correct toolkit."""
        assert gnome_shell_handler.toolkit == Toolkit.GNOME_SHELL

    def test_handler_config_paths(self, gnome_shell_handler):
        """Test that config paths are set correctly."""
        assert gnome_shell_handler.config_dir == Path.home() / ".config"
        assert gnome_shell_handler.shell_config_dir == Path.home() / ".config/gnome-shell"


class TestGnomeShellHandlerAvailability:
    """Tests for handler availability checks."""

    def test_is_available_with_gsettings(self, gnome_shell_handler):
        """Test availability when gsettings is available."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            assert gnome_shell_handler.is_available() is True

    def test_is_available_without_gsettings(self, gnome_shell_handler):
        """Test availability when gsettings is not available."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert gnome_shell_handler.is_available() is False

    def test_is_available_gsettings_error(self, gnome_shell_handler):
        """Test availability when gsettings returns error."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=1)
            assert gnome_shell_handler.is_available() is False


class TestUserThemeExtension:
    """Tests for User Theme extension detection."""

    def test_user_theme_enabled(self, gnome_shell_handler):
        """Test detection when User Theme extension is enabled."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="['user-theme@gnome-shell-extensions.gcampax.github.com']",
            )
            # Reset cached value
            gnome_shell_handler._user_theme_available = None
            assert gnome_shell_handler._is_user_theme_extension_enabled() is True

    def test_user_theme_disabled(self, gnome_shell_handler):
        """Test detection when User Theme extension is disabled."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="['other-extension@example.com']",
            )
            # Reset cached value
            gnome_shell_handler._user_theme_available = None
            assert gnome_shell_handler._is_user_theme_extension_enabled() is False

    def test_user_theme_check_caching(self, gnome_shell_handler):
        """Test that User Theme check result is cached."""
        gnome_shell_handler._user_theme_available = True
        # Should return cached value without calling subprocess
        assert gnome_shell_handler._is_user_theme_extension_enabled() is True


class TestGnomeShellCSSGeneration:
    """Tests for GNOME Shell CSS generation."""

    def test_generate_shell_css_basic(
        self, gnome_shell_handler, sample_gnome_shell_theme_data
    ):
        """Test basic CSS generation from theme colors."""
        css = gnome_shell_handler._generate_shell_css(sample_gnome_shell_theme_data)

        assert "/* Generated by Unified Theming App */" in css
        assert "/* Theme: TestShellTheme */" in css
        assert "@define-color panel_bg_color #303030;" in css
        assert "@define-color panel_fg_color #ffffff;" in css

    def test_generate_shell_css_panel_styles(
        self, gnome_shell_handler, sample_gnome_shell_theme_data
    ):
        """Test that panel styles are generated."""
        css = gnome_shell_handler._generate_shell_css(sample_gnome_shell_theme_data)

        assert "#panel {" in css
        assert "background-color: #303030;" in css
        assert "color: #ffffff;" in css

    def test_generate_shell_css_selection_styles(
        self, gnome_shell_handler, sample_gnome_shell_theme_data
    ):
        """Test that selection styles are generated."""
        css = gnome_shell_handler._generate_shell_css(sample_gnome_shell_theme_data)

        assert ".selected, :focus {" in css
        assert "background-color: #3584e4;" in css

    def test_generate_shell_css_popup_menu_styles(
        self, gnome_shell_handler, sample_gnome_shell_theme_data
    ):
        """Test that popup menu styles are generated."""
        css = gnome_shell_handler._generate_shell_css(sample_gnome_shell_theme_data)

        assert ".popup-menu-content {" in css

    def test_generate_shell_css_empty_colors(self, gnome_shell_handler):
        """Test CSS generation with empty colors."""
        theme_data = ThemeData(
            name="EmptyTheme",
            toolkit=Toolkit.GNOME_SHELL,
            colors={},
        )
        css = gnome_shell_handler._generate_shell_css(theme_data)

        # Should still have header comments
        assert "/* Generated by Unified Theming App */" in css
        assert "/* Theme: EmptyTheme */" in css


class TestGnomeShellThemeApplication:
    """Tests for theme application."""

    def test_apply_theme_gsettings_success(
        self, gnome_shell_handler, sample_gnome_shell_theme_data
    ):
        """Test successful theme application via GSettings."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="")
            # Mock user theme extension as enabled
            gnome_shell_handler._user_theme_available = True

            result = gnome_shell_handler._apply_shell_theme_gsettings("TestTheme")
            assert result is True

            # Verify gsettings was called correctly
            mock_run.assert_called_with(
                [
                    "gsettings",
                    "set",
                    "org.gnome.shell.extensions.user-theme",
                    "name",
                    "TestTheme",
                ],
                check=True,
                capture_output=True,
            )

    def test_apply_theme_gsettings_failure(self, gnome_shell_handler):
        """Test theme application failure via GSettings."""
        import subprocess

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "gsettings")

            result = gnome_shell_handler._apply_shell_theme_gsettings("TestTheme")
            assert result is False

    def test_apply_theme_with_user_extension(
        self, gnome_shell_handler, sample_gnome_shell_theme_data, tmp_path, monkeypatch
    ):
        """Test full theme application with User Theme extension."""
        # Mock home directory to tmp_path
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        gnome_shell_handler.config_dir = tmp_path / ".config"
        gnome_shell_handler.shell_config_dir = tmp_path / ".config" / "gnome-shell"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="")
            gnome_shell_handler._user_theme_available = True

            with patch.object(
                gnome_shell_handler, "_apply_shell_css", return_value=True
            ):
                result = gnome_shell_handler.apply_theme(sample_gnome_shell_theme_data)
                assert result is True

    def test_apply_theme_fallback_without_extension(
        self, gnome_shell_handler, sample_gnome_shell_theme_data, tmp_path, monkeypatch
    ):
        """Test theme application fallback when User Theme extension is not available."""
        # Mock home directory to tmp_path
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        gnome_shell_handler.config_dir = tmp_path / ".config"
        gnome_shell_handler.shell_config_dir = tmp_path / ".config" / "gnome-shell"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="")
            gnome_shell_handler._user_theme_available = False

            result = gnome_shell_handler.apply_theme(sample_gnome_shell_theme_data)

            # Should use fallback method
            css_file = gnome_shell_handler.shell_config_dir / "gnome-shell.css"
            assert css_file.exists()


class TestGnomeShellValidation:
    """Tests for theme validation."""

    def test_validate_compatibility_with_shell_theme(
        self, gnome_shell_handler, gnome_shell_theme_with_path
    ):
        """Test validation of theme with gnome-shell directory."""
        theme_data = ThemeData(
            name="ShellTheme",
            toolkit=Toolkit.GNOME_SHELL,
            colors={"theme_bg_color": "#303030"},
            additional_data={"theme_path": str(gnome_shell_theme_with_path)},
        )

        with patch.object(
            gnome_shell_handler, "_is_user_theme_extension_enabled", return_value=True
        ):
            result = gnome_shell_handler.validate_compatibility(theme_data)
            assert result.valid is True

    def test_validate_compatibility_without_colors(self, gnome_shell_handler):
        """Test validation of theme without color definitions."""
        theme_data = ThemeData(
            name="NoColorTheme",
            toolkit=Toolkit.GNOME_SHELL,
            colors={},
        )

        with patch.object(
            gnome_shell_handler, "_is_user_theme_extension_enabled", return_value=True
        ):
            result = gnome_shell_handler.validate_compatibility(theme_data)
            assert result.has_warnings() is True

    def test_validate_compatibility_without_extension(
        self, gnome_shell_handler, sample_gnome_shell_theme_data
    ):
        """Test validation when User Theme extension is not available."""
        with patch.object(
            gnome_shell_handler, "_is_user_theme_extension_enabled", return_value=False
        ):
            result = gnome_shell_handler.validate_compatibility(
                sample_gnome_shell_theme_data
            )
            # Should add warning about extension
            assert result.has_warnings() is True
            warning_messages = [msg.message for msg in result.messages]
            assert any("User Theme extension" in msg for msg in warning_messages)


class TestGnomeShellCurrentTheme:
    """Tests for getting current theme."""

    def test_get_current_theme_success(self, gnome_shell_handler):
        """Test getting current shell theme successfully."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="'Adwaita-dark'\n",
            )
            theme = gnome_shell_handler.get_current_theme()
            assert theme == "Adwaita-dark"

    def test_get_current_theme_empty(self, gnome_shell_handler):
        """Test getting current theme when none is set."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="''\n",
            )
            theme = gnome_shell_handler.get_current_theme()
            assert theme == "default"

    def test_get_current_theme_gsettings_unavailable(self, gnome_shell_handler):
        """Test getting current theme when gsettings is unavailable."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            theme = gnome_shell_handler.get_current_theme()
            assert theme == "default"


class TestGnomeShellSupportedFeatures:
    """Tests for supported features."""

    def test_get_supported_features_with_extension(self, gnome_shell_handler):
        """Test supported features when User Theme extension is available."""
        gnome_shell_handler._user_theme_available = True
        features = gnome_shell_handler.get_supported_features()
        assert "colors" in features
        assert "theme_name" in features
        assert "full_shell_theme" in features

    def test_get_supported_features_without_extension(self, gnome_shell_handler):
        """Test supported features when User Theme extension is not available."""
        gnome_shell_handler._user_theme_available = False
        features = gnome_shell_handler.get_supported_features()
        assert "colors" in features
        assert "theme_name" in features
        assert "full_shell_theme" not in features


class TestGnomeShellConfigPaths:
    """Tests for configuration paths."""

    def test_get_config_paths(self, gnome_shell_handler):
        """Test that config paths are returned correctly."""
        paths = gnome_shell_handler.get_config_paths()
        assert len(paths) == 2
        assert any("gnome-shell.css" in str(p) for p in paths)
        assert any("gnome-shell-custom.css" in str(p) for p in paths)


class TestGnomeShellPlanning:
    """Tests for theme change planning."""

    def test_plan_theme_with_gsettings_change(
        self, gnome_shell_handler, sample_gnome_shell_theme_data
    ):
        """Test planning when theme name would change."""
        gnome_shell_handler._user_theme_available = True

        with patch.object(
            gnome_shell_handler, "get_current_theme", return_value="OldTheme"
        ):
            changes = gnome_shell_handler.plan_theme(sample_gnome_shell_theme_data)

            # Should plan a gsettings change
            gsettings_changes = [
                c for c in changes if "user-theme" in str(c.file_path)
            ]
            assert len(gsettings_changes) >= 1

    def test_plan_theme_with_css_generation(
        self, gnome_shell_handler, sample_gnome_shell_theme_data, tmp_path, monkeypatch
    ):
        """Test planning CSS generation."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        gnome_shell_handler.shell_config_dir = tmp_path / ".config" / "gnome-shell"
        gnome_shell_handler._user_theme_available = False

        changes = gnome_shell_handler.plan_theme(sample_gnome_shell_theme_data)

        # Should plan CSS file creation
        css_changes = [c for c in changes if "css" in str(c.file_path)]
        assert len(css_changes) >= 1


class TestGnomeShellAvailableThemes:
    """Tests for available shell themes discovery."""

    def test_get_available_shell_themes(
        self, gnome_shell_handler, tmp_path, monkeypatch
    ):
        """Test discovering available shell themes."""
        # Create mock theme directories
        themes_dir = tmp_path / ".local" / "share" / "themes"
        themes_dir.mkdir(parents=True)

        # Create a theme with gnome-shell directory
        shell_theme = themes_dir / "TestShellTheme"
        shell_theme.mkdir()
        (shell_theme / "gnome-shell").mkdir()

        # Create a theme without gnome-shell (should not be listed)
        gtk_theme = themes_dir / "GtkOnlyTheme"
        gtk_theme.mkdir()
        (gtk_theme / "gtk-3.0").mkdir()

        gnome_shell_handler.USER_SHELL_THEMES_DIR = themes_dir
        gnome_shell_handler.SYSTEM_SHELL_THEMES_DIR = tmp_path / "nonexistent"

        themes = gnome_shell_handler.get_available_shell_themes()
        assert "TestShellTheme" in themes
        assert "GtkOnlyTheme" not in themes


class TestGnomeShellColorMapping:
    """Tests for GTK to GNOME Shell color mapping."""

    def test_gtk_to_shell_mapping_exists(self, gnome_shell_handler):
        """Test that GTK to shell color mapping is defined."""
        mapping = gnome_shell_handler.GTK_TO_SHELL_MAPPING
        assert "theme_bg_color" in mapping
        assert "theme_fg_color" in mapping
        assert mapping["theme_bg_color"] == "panel_bg_color"
        assert mapping["theme_fg_color"] == "panel_fg_color"

    def test_generate_css_uses_mapping(
        self, gnome_shell_handler, sample_gnome_shell_theme_data
    ):
        """Test that CSS generation uses the color mapping."""
        css = gnome_shell_handler._generate_shell_css(sample_gnome_shell_theme_data)

        # Should use mapped shell color names, not GTK names
        assert "panel_bg_color" in css
        assert "panel_fg_color" in css


class TestGnomeShellIntegration:
    """Integration tests for GNOME Shell handler."""

    def test_full_theme_application_workflow(
        self, gnome_shell_handler, sample_gnome_shell_theme_data, tmp_path, monkeypatch
    ):
        """Test complete theme application workflow."""
        # Setup mock environment
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        gnome_shell_handler.config_dir = tmp_path / ".config"
        gnome_shell_handler.shell_config_dir = tmp_path / ".config" / "gnome-shell"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="")
            gnome_shell_handler._user_theme_available = True

            # Validate
            validation = gnome_shell_handler.validate_compatibility(
                sample_gnome_shell_theme_data
            )
            assert validation.valid is True

            # Plan
            changes = gnome_shell_handler.plan_theme(sample_gnome_shell_theme_data)
            assert len(changes) > 0

            # Apply
            with patch.object(
                gnome_shell_handler, "_apply_shell_css", return_value=True
            ):
                result = gnome_shell_handler.apply_theme(sample_gnome_shell_theme_data)
                assert result is True
