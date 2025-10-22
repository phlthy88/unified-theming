"""
Dialog windows for Unified Theming GUI.

This module contains dialog classes for settings, preferences, and other
modal interactions.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from gi.repository import Adw, GLib, Gtk

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
        self.max_backups_row = Adw.SpinRow.new()
        self.max_backups_row.set_title("Maximum backups")
        self.max_backups_row.set_subtitle("Maximum number of backups to keep")
        self.max_backups_row.set_adjustment(
            Gtk.Adjustment.new(self.config.get("max_backups", 10), 1, 100, 1, 5, 0)
        )
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
        self.cache_expiry_row = Adw.SpinRow.new()
        self.cache_expiry_row.set_title("Cache expiry (hours)")
        self.cache_expiry_row.set_subtitle("How long to keep cached theme data")
        self.cache_expiry_row.set_adjustment(
            Gtk.Adjustment.new(
                self.config.get("cache_expiry_hours", 24),
                1,
                168,
                1,
                6,
                0,  # 1 hour to 1 week
            )
        )
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
    Dialog showing detailed information about a theme.
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
        self.set_title(f"Theme Details - {theme_name}")
        self.set_default_size(600, 500)

        # Store theme info
        self.theme_name = theme_name
        self.theme_info = theme_info

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """
        Set up the dialog user interface.
        """
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)

        # Header
        header = Adw.HeaderBar.new()
        header.set_title_widget(
            Adw.WindowTitle.new(f"Theme Details - {self.theme_name}", "")
        )

        close_button = Gtk.Button.new_from_icon_name("window-close-symbolic")
        close_button.connect("clicked", lambda b: self.close())
        header.pack_end(close_button)

        main_box.append(header)

        # Content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_top(12)

        # Basic info
        info_group = Adw.PreferencesGroup.new()
        info_group.set_title("Basic Information")

        # Name row
        name_row = Adw.ActionRow.new()
        name_row.set_title("Name")
        name_row.set_subtitle(self.theme_name)
        info_group.add(name_row)

        # Path row
        path_row = Adw.ActionRow.new()
        path_row.set_title("Path")
        path_row.set_subtitle(str(getattr(self.theme_info, "path", "Unknown")))
        info_group.add(path_row)

        # Toolkits row
        toolkits = getattr(self.theme_info, "supported_toolkits", [])
        toolkit_names = [t.value for t in toolkits]
        toolkits_row = Adw.ActionRow.new()
        toolkits_row.set_title("Supported Toolkits")
        toolkits_row.set_subtitle(", ".join(toolkit_names))
        info_group.add(toolkits_row)

        content_box.append(info_group)

        # Colors section
        colors = getattr(self.theme_info, "colors", {})
        if colors:
            colors_group = Adw.PreferencesGroup.new()
            colors_group.set_title(f"Colors ({len(colors)})")

            # Show first 10 colors
            for name, hex_color in list(colors.items())[:10]:
                color_row = Adw.ActionRow.new()
                color_row.set_title(name)

                # Color indicator
                color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

                # Color square
                color_square = Gtk.DrawingArea()
                color_square.set_size_request(24, 24)
                color_square.set_draw_func(self.draw_color_square, hex_color)
                color_box.append(color_square)

                # Hex value
                hex_label = Gtk.Label.new(hex_color.upper())
                color_box.append(hex_label)

                color_row.add_suffix(color_box)
                colors_group.add(color_row)

            content_box.append(colors_group)

        # Scrollable content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(content_box)
        main_box.append(scrolled)

        self.set_content(main_box)

    def draw_color_square(self, area, cr, width, height, hex_color):
        """
        Draw a color square.

        Args:
            area: The drawing area
            cr: Cairo context
            width: Width of area
            height: Height of area
            hex_color: Hex color value
        """
        # Parse hex color
        try:
            # Remove # if present
            if hex_color.startswith("#"):
                hex_color = hex_color[1:]

            # Parse RGB
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0

            # Set color and draw rectangle
            cr.set_source_rgb(r, g, b)
            cr.rectangle(0, 0, width, height)
            cr.fill()

            # Draw border
            cr.set_source_rgb(0, 0, 0)
            cr.set_line_width(1)
            cr.rectangle(0, 0, width, height)
            cr.stroke()

        except (ValueError, IndexError):
            # Fallback to gray if color parsing fails
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.rectangle(0, 0, width, height)
            cr.fill()


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
