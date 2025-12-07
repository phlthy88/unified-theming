"""
Dialog windows for Unified Theming GUI.

This module contains modern dialog classes for settings, preferences,
and other modal interactions using GTK4 and Libadwaita.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from gi.repository import Adw, Gdk, GLib, Gtk, Pango

if TYPE_CHECKING:
    from unified_theming.utils.system_detect import ToolkitEnvironment

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from unified_theming.core.types import Toolkit
from unified_theming.utils.logging_config import get_logger

logger = get_logger(__name__)


class SettingsDialog(Adw.PreferencesWindow):
    """
    Settings and preferences dialog.

    Allows users to configure application behavior, toolkit selection,
    and backup settings.
    """

    def __init__(self, parent: Gtk.Window, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the settings dialog.

        Args:
            parent: Parent window
            config: Current configuration
        """
        super().__init__()

        self.set_modal(True)
        self.set_transient_for(parent)
        self.set_title("Settings")

        # Store config
        self.config = config or {}
        self.original_config = self.config.copy()

        # Setup UI
        self.setup_ui()

        logger.info("SettingsDialog initialized")

    def setup_ui(self):
        """
        Set up the dialog user interface.
        """
        # General page
        general_page = Adw.PreferencesPage.new()
        general_page.set_title("General")
        general_page.set_icon_name("preferences-system-symbolic")
        self.add(general_page)

        # Theme discovery group
        discovery_group = Adw.PreferencesGroup.new()
        discovery_group.set_title("Theme Discovery")
        discovery_group.set_description(
            "Configure how themes are discovered and displayed"
        )
        general_page.add(discovery_group)

        # Auto-refresh toggle
        self.auto_refresh_switch = Adw.SwitchRow.new()
        self.auto_refresh_switch.set_title("Auto-refresh themes")
        self.auto_refresh_switch.set_subtitle(
            "Automatically refresh theme list when directories change"
        )
        self.auto_refresh_switch.set_active(self.config.get("auto_refresh", True))
        discovery_group.add(self.auto_refresh_switch)

        # Show hidden themes toggle
        self.show_hidden_switch = Adw.SwitchRow.new()
        self.show_hidden_switch.set_title("Show hidden themes")
        self.show_hidden_switch.set_subtitle(
            "Include themes whose names start with a dot"
        )
        self.show_hidden_switch.set_active(self.config.get("show_hidden", False))
        discovery_group.add(self.show_hidden_switch)

        # Toolkit selection page
        toolkit_page = Adw.PreferencesPage.new()
        toolkit_page.set_title("Toolkits")
        toolkit_page.set_icon_name("applications-system-symbolic")
        self.add(toolkit_page)

        # Enabled toolkits group
        toolkits_group = Adw.PreferencesGroup.new()
        toolkits_group.set_title("Enabled Toolkits")
        toolkits_group.set_description(
            "Select which toolkits to theme when applying themes"
        )
        toolkit_page.add(toolkits_group)

        # Create switches for each toolkit
        self.toolkit_switches: Dict[str, Adw.SwitchRow] = {}

        enabled_toolkits = self.config.get(
            "enabled_toolkits", [t.value for t in Toolkit]
        )

        for toolkit in Toolkit:
            switch = Adw.SwitchRow.new()
            switch.set_title(toolkit.value.title())
            switch.set_subtitle(f"Apply themes to {toolkit.value}")
            switch.set_active(toolkit.value in enabled_toolkits)
            toolkits_group.add(switch)
            self.toolkit_switches[toolkit.value] = switch

        # Backup page
        backup_page = Adw.PreferencesPage.new()
        backup_page.set_title("Backup")
        backup_page.set_icon_name("document-save-symbolic")
        self.add(backup_page)

        # Backup settings group
        backup_group = Adw.PreferencesGroup.new()
        backup_group.set_title("Backup Settings")
        backup_group.set_description("Configure automatic backup behavior")
        backup_page.add(backup_group)

        # Enable backups toggle
        self.enable_backups_switch = Adw.SwitchRow.new()
        self.enable_backups_switch.set_title("Enable backups")
        self.enable_backups_switch.set_subtitle("Create backups before applying themes")
        self.enable_backups_switch.set_active(self.config.get("enable_backups", True))
        backup_group.add(self.enable_backups_switch)

        # Max backups spin button
        max_backups_adjustment = Gtk.Adjustment.new(
            self.config.get("max_backups", 10), 1, 100, 1, 5, 0
        )
        self.max_backups_row = Adw.SpinRow.new(
            max_backups_adjustment, 1, 0
        )  # climb rate 1, no decimals
        self.max_backups_row.set_title("Maximum backups")
        self.max_backups_row.set_subtitle("Maximum number of backups to keep")
        backup_group.add(self.max_backups_row)

        # Advanced page
        advanced_page = Adw.PreferencesPage.new()
        advanced_page.set_title("Advanced")
        advanced_page.set_icon_name("preferences-advanced-symbolic")
        self.add(advanced_page)

        # Performance group
        perf_group = Adw.PreferencesGroup.new()
        perf_group.set_title("Performance")
        perf_group.set_description("Performance and resource usage settings")
        advanced_page.add(perf_group)

        # Parallel processing toggle
        self.parallel_switch = Adw.SwitchRow.new()
        self.parallel_switch.set_title("Parallel processing")
        self.parallel_switch.set_subtitle("Use multiple threads for theme operations")
        self.parallel_switch.set_active(self.config.get("parallel_processing", True))
        perf_group.add(self.parallel_switch)

        # Cache settings
        cache_group = Adw.PreferencesGroup.new()
        cache_group.set_title("Cache")
        cache_group.set_description("Theme parsing and discovery cache settings")
        advanced_page.add(cache_group)

        # Enable cache toggle
        self.cache_switch = Adw.SwitchRow.new()
        self.cache_switch.set_title("Enable cache")
        self.cache_switch.set_subtitle("Cache parsed theme information")
        self.cache_switch.set_active(self.config.get("enable_cache", True))
        cache_group.add(self.cache_switch)

        # Cache expiry spin button
        cache_expiry_adjustment = Gtk.Adjustment.new(
            self.config.get("cache_expiry_hours", 24),
            1,
            168,
            1,
            6,
            0,  # 1 hour to 1 week
        )
        self.cache_expiry_row = Adw.SpinRow.new(
            cache_expiry_adjustment, 1, 0
        )  # climb rate 1, no decimals
        self.cache_expiry_row.set_title("Cache expiry (hours)")
        self.cache_expiry_row.set_subtitle("How long to keep cached theme data")
        cache_group.add(self.cache_expiry_row)

    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration from the dialog.

        Returns:
            Dictionary of configuration values
        """
        config = {}

        # General settings
        config["auto_refresh"] = self.auto_refresh_switch.get_active()
        config["show_hidden"] = self.show_hidden_switch.get_active()

        # Toolkit settings
        enabled_toolkits = [
            toolkit
            for toolkit, switch in self.toolkit_switches.items()
            if switch.get_active()
        ]
        config["enabled_toolkits"] = enabled_toolkits

        # Backup settings
        config["enable_backups"] = self.enable_backups_switch.get_active()
        config["max_backups"] = int(self.max_backups_row.get_value())

        # Advanced settings
        config["parallel_processing"] = self.parallel_switch.get_active()
        config["enable_cache"] = self.cache_switch.get_active()
        config["cache_expiry_hours"] = int(self.cache_expiry_row.get_value())

        return config

    def has_changes(self) -> bool:
        """
        Check if the configuration has changed.

        Returns:
            True if configuration has been modified
        """
        return self.get_config() != self.original_config


class ThemeDetailsDialog(Adw.Window):
    """
    Modern dialog showing detailed information about a theme.

    Features organized sections for metadata, colors, and toolkit support
    with copy functionality and modern Adwaita styling.
    """

    def __init__(self, parent: Gtk.Window, theme_name: str, theme_info: Any):
        """
        Initialize the theme details dialog.

        Args:
            parent: Parent window
            theme_name: Name of the theme
            theme_info: Theme information object
        """
        super().__init__()

        self.set_modal(True)
        self.set_transient_for(parent)
        self.set_title(f"Theme Details")
        self.set_default_size(550, 650)

        self.theme_name = theme_name
        self.theme_info = theme_info

        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog user interface."""
        # Toolbar view for proper header
        toolbar_view = Adw.ToolbarView.new()

        # Header
        header = Adw.HeaderBar.new()
        header.set_title_widget(Adw.WindowTitle.new(self.theme_name, "Theme Details"))
        toolbar_view.add_top_bar(header)

        # Scrolled content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Main content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_margin_top(24)
        content.set_margin_bottom(24)

        # Theme header with icon
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        header_box.set_halign(Gtk.Align.CENTER)

        theme_icon = Gtk.Image.new_from_icon_name(
            "preferences-desktop-appearance-symbolic"
        )
        theme_icon.set_pixel_size(64)
        theme_icon.add_css_class("dim-label")
        header_box.append(theme_icon)

        header_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header_info.set_valign(Gtk.Align.CENTER)

        name_label = Gtk.Label.new(self.theme_name)
        name_label.add_css_class("title-1")
        name_label.set_xalign(0)
        header_info.append(name_label)

        # Toolkit count subtitle
        toolkits = getattr(self.theme_info, "supported_toolkits", [])
        subtitle = (
            f"{len(toolkits)} toolkit{'s' if len(toolkits) != 1 else ''} supported"
        )
        subtitle_label = Gtk.Label.new(subtitle)
        subtitle_label.add_css_class("dim-label")
        subtitle_label.set_xalign(0)
        header_info.append(subtitle_label)

        header_box.append(header_info)
        content.append(header_box)

        # Basic info group
        info_group = Adw.PreferencesGroup.new()
        info_group.set_title("Information")
        content.append(info_group)

        # Path row with copy button
        path_row = Adw.ActionRow.new()
        path_row.set_title("Location")
        path_row.set_subtitle(str(getattr(self.theme_info, "path", "Unknown")))
        path_row.add_prefix(Gtk.Image.new_from_icon_name("folder-symbolic"))

        copy_btn = Gtk.Button.new_from_icon_name("edit-copy-symbolic")
        copy_btn.set_valign(Gtk.Align.CENTER)
        copy_btn.add_css_class("flat")
        copy_btn.set_tooltip_text("Copy path")
        copy_btn.connect("clicked", self.on_copy_path)
        path_row.add_suffix(copy_btn)
        info_group.add(path_row)

        # Author row
        metadata = getattr(self.theme_info, "metadata", {})
        author = metadata.get("Author", "Unknown")
        author_row = Adw.ActionRow.new()
        author_row.set_title("Author")
        author_row.set_subtitle(author)
        author_row.add_prefix(Gtk.Image.new_from_icon_name("avatar-default-symbolic"))
        info_group.add(author_row)

        # Version row
        version = metadata.get("Version", "—")
        version_row = Adw.ActionRow.new()
        version_row.set_title("Version")
        version_row.set_subtitle(version)
        version_row.add_prefix(Gtk.Image.new_from_icon_name("emblem-system-symbolic"))
        info_group.add(version_row)

        # Comment row if available
        comment = metadata.get("Comment", "")
        if comment:
            comment_row = Adw.ActionRow.new()
            comment_row.set_title("Description")
            comment_row.set_subtitle(comment)
            comment_row.add_prefix(
                Gtk.Image.new_from_icon_name("text-x-generic-symbolic")
            )
            info_group.add(comment_row)

        # Toolkits group
        if toolkits:
            toolkit_group = Adw.PreferencesGroup.new()
            toolkit_group.set_title("Supported Toolkits")
            toolkit_group.set_description("This theme can be applied to these toolkits")
            content.append(toolkit_group)

            for toolkit in toolkits:
                toolkit_row = Adw.ActionRow.new()
                toolkit_row.set_title(toolkit.value.upper())
                toolkit_row.add_prefix(
                    Gtk.Image.new_from_icon_name(self.get_toolkit_icon(toolkit.value))
                )

                check = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
                check.add_css_class("success")
                toolkit_row.add_suffix(check)
                toolkit_group.add(toolkit_row)

        # Colors group
        colors = getattr(self.theme_info, "colors", {})
        if colors:
            colors_group = Adw.PreferencesGroup.new()
            colors_group.set_title(f"Color Palette ({len(colors)} colors)")
            colors_group.set_description("Click any color to copy its value")
            content.append(colors_group)

            # Expandable color list
            expander = Adw.ExpanderRow.new()
            expander.set_title("View All Colors")
            expander.set_subtitle(f"{len(colors)} color variables")
            expander.set_expanded(False)
            colors_group.add(expander)

            for name, hex_color in list(colors.items())[:20]:
                color_row = self.create_color_row(name, hex_color)
                expander.add_row(color_row)

            if len(colors) > 20:
                more_label = Gtk.Label.new(f"... and {len(colors) - 20} more colors")
                more_label.add_css_class("dim-label")
                more_label.set_margin_top(12)
                more_label.set_margin_bottom(12)
                more_box = Gtk.Box()
                more_box.append(more_label)
                expander.add_row(more_box)

        scrolled.set_child(content)
        toolbar_view.set_content(scrolled)
        self.set_content(toolbar_view)

    def get_toolkit_icon(self, toolkit: str) -> str:
        """Get icon name for toolkit."""
        icons = {
            "gtk2": "applications-graphics-symbolic",
            "gtk3": "preferences-desktop-appearance-symbolic",
            "gtk4": "preferences-desktop-appearance-symbolic",
            "libadwaita": "preferences-desktop-appearance-symbolic",
            "qt5": "preferences-desktop-theme-symbolic",
            "qt6": "preferences-desktop-theme-symbolic",
            "flatpak": "package-x-generic-symbolic",
            "snap": "package-x-generic-symbolic",
        }
        return icons.get(toolkit, "application-x-executable-symbolic")

    def create_color_row(self, name: str, hex_color: str) -> Adw.ActionRow:
        """Create a row for a color."""
        row = Adw.ActionRow.new()
        row.set_title(name)

        # Color indicator
        color_area = Gtk.DrawingArea()
        color_area.set_size_request(24, 24)
        color_area.set_draw_func(self.draw_color_square, hex_color)
        row.add_prefix(color_area)

        # Hex value label
        hex_label = Gtk.Label.new(hex_color.upper())
        hex_label.add_css_class("monospace")
        hex_label.add_css_class("dim-label")
        row.add_suffix(hex_label)

        # Copy button
        copy_btn = Gtk.Button.new_from_icon_name("edit-copy-symbolic")
        copy_btn.set_valign(Gtk.Align.CENTER)
        copy_btn.add_css_class("flat")
        copy_btn.set_tooltip_text(f"Copy {hex_color}")
        copy_btn.connect("clicked", lambda b: self.copy_to_clipboard(hex_color.upper()))
        row.add_suffix(copy_btn)

        return row

    def draw_color_square(self, area, cr, width, height, hex_color):
        """Draw a rounded color square."""
        try:
            if hex_color.startswith("#"):
                hex_color = hex_color[1:]

            if len(hex_color) >= 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
            else:
                r = g = b = 0.5

            # Draw rounded rectangle
            radius = 4
            degrees = 3.14159 / 180.0

            cr.new_sub_path()
            cr.arc(width - radius, radius, radius, -90 * degrees, 0 * degrees)
            cr.arc(width - radius, height - radius, radius, 0 * degrees, 90 * degrees)
            cr.arc(radius, height - radius, radius, 90 * degrees, 180 * degrees)
            cr.arc(radius, radius, radius, 180 * degrees, 270 * degrees)
            cr.close_path()

            cr.set_source_rgb(r, g, b)
            cr.fill_preserve()

            cr.set_source_rgba(0, 0, 0, 0.15)
            cr.set_line_width(1)
            cr.stroke()

        except (ValueError, IndexError):
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.rectangle(0, 0, width, height)
            cr.fill()

    def on_copy_path(self, button):
        """Copy theme path to clipboard."""
        path = str(getattr(self.theme_info, "path", ""))
        self.copy_to_clipboard(path)
        button.set_tooltip_text("Copied!")
        GLib.timeout_add(1500, lambda: button.set_tooltip_text("Copy path"))

    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(text)


class ConfirmationDialog(Adw.MessageDialog):
    """
    Confirmation dialog for destructive actions.
    """

    def __init__(
        self,
        parent: Gtk.Window,
        title: str,
        message: str,
        confirm_label: str = "Confirm",
        destructive: bool = False,
    ):
        """
        Initialize the confirmation dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Dialog message
            confirm_label: Label for confirm button
            destructive: Whether this is a destructive action
        """
        super().__init__()

        self.set_modal(True)
        self.set_transient_for(parent)
        self.set_title(title)
        self.set_body(message)

        # Add buttons
        self.add_response("cancel", "Cancel")
        self.add_response("confirm", confirm_label)

        # Set default response
        self.set_default_response("cancel")
        self.set_close_response("cancel")

        # Style confirm button as destructive if needed
        if destructive:
            self.set_response_appearance("confirm", Adw.ResponseAppearance.DESTRUCTIVE)

    def run_async(self, callback: Callable[[str], None]):
        """
        Run the dialog asynchronously.

        Args:
            callback: Callback function called with response ID
        """

        def on_response(dialog, response):
            callback(response)
            dialog.destroy()

        self.connect("response", on_response)
        self.present()


class ToolkitCompatibilityDialog(Adw.MessageDialog):
    """
    Dialog showing cross-toolkit compatibility status and missing packages.

    Displays when Qt apps are detected on GTK desktops (or vice versa)
    and offers to install required theming packages.
    """

    def __init__(
        self,
        parent: Gtk.Window,
        environment: "ToolkitEnvironment",
        on_install: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize the compatibility dialog.

        Args:
            parent: Parent window
            environment: Detected toolkit environment
            on_install: Callback when user clicks install
        """
        super().__init__()

        self.environment = environment
        self.on_install = on_install

        self.set_modal(True)
        self.set_transient_for(parent)

        self._setup_content()

    def _setup_content(self):
        """Set up dialog content based on environment."""
        env = self.environment

        if env.desktop in ("gnome", "xfce", "cinnamon") and env.has_qt_apps:
            self._setup_qt_on_gtk()
        elif env.desktop == "kde" and env.has_gtk_apps:
            self._setup_gtk_on_kde()
        else:
            self._setup_all_good()

    def _setup_qt_on_gtk(self):
        """Configure dialog for Qt apps on GTK desktop."""
        self.set_heading("Qt Applications Detected")

        missing = self.environment.qt_packages_missing
        installed = self.environment.qt_packages_installed

        if missing:
            self.set_body(
                f"You have Qt applications installed, but some theming packages "
                f"are missing. Without these, Qt apps may look inconsistent.\n\n"
                f"✓ Installed: {', '.join(installed) if installed else 'None'}\n"
                f"✗ Missing: {', '.join(missing)}"
            )
            self.add_response("cancel", "Later")
            self.add_response("install", "Install Packages")
            self.set_response_appearance("install", Adw.ResponseAppearance.SUGGESTED)
            self.set_default_response("install")
        else:
            self.set_body(
                f"Qt theming packages are properly installed.\n\n"
                f"✓ Installed: {', '.join(installed)}\n\n"
                f"Your Qt applications should follow your GTK theme."
            )
            self.add_response("ok", "OK")
            self.set_default_response("ok")

        self.set_close_response("cancel" if missing else "ok")

    def _setup_gtk_on_kde(self):
        """Configure dialog for GTK apps on KDE desktop."""
        self.set_heading("GTK Applications Detected")

        missing = self.environment.gtk_packages_missing

        if missing:
            self.set_body(
                f"You have GTK applications installed, but some theming packages "
                f"are missing. Without these, GTK apps may look inconsistent.\n\n"
                f"✗ Missing: {', '.join(missing)}"
            )
            self.add_response("cancel", "Later")
            self.add_response("install", "Install Packages")
            self.set_response_appearance("install", Adw.ResponseAppearance.SUGGESTED)
            self.set_default_response("install")
        else:
            self.set_body("GTK theming packages are properly installed.")
            self.add_response("ok", "OK")
            self.set_default_response("ok")

        self.set_close_response("cancel" if missing else "ok")

    def _setup_all_good(self):
        """Configure dialog when no issues detected."""
        self.set_heading("Toolkit Compatibility")
        self.set_body(
            "Your system appears to have the necessary packages for "
            "consistent theming across all detected applications."
        )
        self.add_response("ok", "OK")
        self.set_default_response("ok")
        self.set_close_response("ok")

    def run_async(self, callback: Optional[Callable[[str], None]] = None):
        """Run dialog and handle response."""

        def on_response(dialog, response):
            if response == "install" and self.on_install:
                self.on_install()
            if callback:
                callback(response)
            dialog.destroy()

        self.connect("response", on_response)
        self.present()


def show_toolkit_check(parent: Gtk.Window) -> None:
    """
    Check toolkit environment and show dialog if issues found.

    Args:
        parent: Parent window for the dialog
    """
    from unified_theming.utils.system_detect import (
        detect_environment,
        get_install_command,
    )

    env = detect_environment()

    # Determine if we need to show anything
    missing = env.qt_packages_missing + env.gtk_packages_missing
    if not missing:
        return  # All good, no dialog needed

    def on_install():
        cmd = get_install_command(missing)
        # Copy to clipboard and show terminal command
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(cmd)

        # Show info dialog with command
        info = Adw.MessageDialog.new(parent, "Install Command Copied")
        info.set_body(
            f"Run this command in your terminal:\n\n{cmd}\n\n"
            "(Command has been copied to clipboard)"
        )
        info.add_response("ok", "OK")
        info.present()

    dialog = ToolkitCompatibilityDialog(parent, env, on_install=on_install)
    dialog.run_async()
