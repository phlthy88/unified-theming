"""
GTK4/Libadwaita GUI Application for Unified Theming.

This module implements a modern GUI application using GTK4 and Libadwaita,
providing a native GNOME-style interface for theme management.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import sys
from pathlib import Path
from threading import Thread
from typing import Any, Dict, List, Optional

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from unified_theming.core.manager import UnifiedThemeManager
from unified_theming.core.types import ApplicationResult, ThemeInfo, Toolkit
from unified_theming.utils.logging_config import get_logger

from .dialogs import ConfirmationDialog, SettingsDialog, ThemeDetailsDialog
from .widgets import ProgressDialog, ThemePreviewWidget

logger = get_logger(__name__)

# Application metadata
APP_ID = "com.github.unified_theming"
APP_NAME = "Unified Theming"
APP_VERSION = "1.0.0"
APP_DEVELOPER = "Unified Theming Contributors"
APP_WEBSITE = "https://github.com/phlthy88/unified-theming"


class ThemeApp(Adw.Application):
    """
    Main application class for Unified Theming GUI.

    This class manages the application lifecycle, window creation,
    actions, and integration with the core theming components.
    """

    def __init__(self):
        """Initialize the application."""
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

        # Connect signals
        self.connect("activate", self.on_activate)
        self.connect("shutdown", self.on_shutdown)

        # Initialize core components
        self.manager: Optional[UnifiedThemeManager] = None
        self.themes: Dict[str, ThemeInfo] = {}
        self.current_operation: Optional[Any] = None
        self.settings: Dict[str, Any] = self._load_default_settings()

        # Setup actions
        self.setup_actions()

        logger.info("ThemeApp initialized")

    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings."""
        return {
            "auto_refresh": True,
            "show_hidden": False,
            "enable_backups": True,
            "max_backups": 10,
            "parallel_processing": True,
            "enable_cache": True,
            "cache_expiry_hours": 24,
            "enabled_toolkits": [t.value for t in Toolkit],
        }

    def setup_actions(self):
        """Set up application actions with keyboard shortcuts."""
        # Refresh themes action
        refresh_action = Gio.SimpleAction.new("refresh", None)
        refresh_action.connect("activate", self.on_refresh_action)
        self.add_action(refresh_action)
        self.set_accels_for_action("app.refresh", ["<Control>r", "F5"])

        # Apply theme action
        apply_action = Gio.SimpleAction.new("apply", None)
        apply_action.connect("activate", self.on_apply_action)
        self.add_action(apply_action)
        self.set_accels_for_action("app.apply", ["<Control>Return"])

        # Settings action
        settings_action = Gio.SimpleAction.new("preferences", None)
        settings_action.connect("activate", self.on_settings_action)
        self.add_action(settings_action)
        self.set_accels_for_action("app.preferences", ["<Control>comma"])

        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_action)
        self.add_action(about_action)

        # Quit action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_action)
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Control>q"])

        # Search action
        search_action = Gio.SimpleAction.new("search", None)
        search_action.connect("activate", self.on_search_action)
        self.add_action(search_action)
        self.set_accels_for_action("app.search", ["<Control>f"])

        # Theme details action
        details_action = Gio.SimpleAction.new("theme-details", None)
        details_action.connect("activate", self.on_details_action)
        self.add_action(details_action)
        self.set_accels_for_action("app.theme-details", ["<Control>i"])

        # Rollback action
        rollback_action = Gio.SimpleAction.new("rollback", None)
        rollback_action.connect("activate", self.on_rollback_action)
        self.add_action(rollback_action)
        self.set_accels_for_action("app.rollback", ["<Control>z"])

    def on_activate(self, app):
        """Called when the application is activated."""
        logger.info("Application activated")

        # Create main window
        self.window = MainWindow(application=app)
        self.window.present()

        # Initialize theme manager after window is created
        GLib.idle_add(self.initialize_manager)

    def on_shutdown(self, app):
        """Called when the application is shutting down."""
        logger.info("Application shutting down")
        if self.current_operation:
            self.current_operation.cancel()

    def initialize_manager(self):
        """Initialize the theme manager and discover themes."""
        self.window.set_loading(True, "Discovering themes...")

        def discover_async():
            try:
                self.manager = UnifiedThemeManager()
                themes = self.manager.discover_themes()
                GLib.idle_add(lambda: self.on_themes_discovered(themes))
            except Exception as e:
                logger.error(f"Failed to initialize theme manager: {e}")
                GLib.idle_add(lambda: self.on_discovery_error(str(e)))

        thread = Thread(target=discover_async, daemon=True)
        thread.start()

    def on_themes_discovered(self, themes: Dict[str, ThemeInfo]):
        """Called when theme discovery completes."""
        self.themes = themes
        self.window.set_loading(False)
        self.window.set_themes(themes)
        self.window.show_toast(f"Discovered {len(themes)} themes")
        logger.info(f"Discovered {len(themes)} themes")

    def on_discovery_error(self, error: str):
        """Called when theme discovery fails."""
        self.window.set_loading(False)
        self.show_error_dialog(f"Failed to discover themes: {error}")

    def show_error_dialog(self, message: str):
        """Show an error dialog."""
        dialog = Adw.MessageDialog.new(self.window, "Error", message)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.present()

    def apply_theme(self, theme_name: str, callback=None):
        """Apply a theme asynchronously with progress dialog."""
        if not self.manager:
            self.show_error_dialog("Theme manager not initialized")
            return

        progress_dialog = ProgressDialog(self.window, f"Applying {theme_name}")
        progress_dialog.present()

        def apply_async():
            try:
                GLib.idle_add(
                    lambda: progress_dialog.update_progress(0.2, "Creating backup...")
                )
                result = self.manager.apply_theme(theme_name)
                GLib.idle_add(lambda: progress_dialog.update_progress(1.0, "Complete!"))
                GLib.idle_add(lambda: self.on_theme_applied(result, progress_dialog))
            except Exception as e:
                error_msg = str(e)
                GLib.idle_add(
                    lambda: progress_dialog.complete(False, f"Failed: {error_msg}")
                )
                GLib.idle_add(lambda: self.on_theme_error(error_msg, callback))

        thread = Thread(target=apply_async, daemon=True)
        thread.start()

    def on_theme_applied(self, result: ApplicationResult, progress_dialog):
        """Called when theme application completes."""
        progress_dialog.complete(result.overall_success)

        if result.overall_success:
            successful = result.get_successful_handlers()
            self.window.show_toast(
                f"Theme applied to {len(successful)} toolkit(s)",
                button_label="Details",
                button_action=lambda: self.show_result_details(result),
            )
        else:
            failed = result.get_failed_handlers()
            self.show_error_dialog(f"Theme application failed for: {', '.join(failed)}")

    def show_result_details(self, result: ApplicationResult):
        """Show details about theme application result."""
        successful = result.get_successful_handlers()
        failed = result.get_failed_handlers()

        message = f"Applied to: {', '.join(successful)}"
        if failed:
            message += f"\nFailed for: {', '.join(failed)}"

        dialog = Adw.MessageDialog.new(self.window, "Application Result", message)
        dialog.add_response("ok", "OK")
        dialog.present()

    def on_theme_error(self, error: str, callback):
        """Called when theme application fails."""
        self.show_error_dialog(f"Failed to apply theme: {error}")
        if callback:
            callback(None)

    # Action handlers
    def on_refresh_action(self, action, param):
        """Handle refresh action."""
        self.initialize_manager()

    def on_apply_action(self, action, param):
        """Handle apply action."""
        if hasattr(self, "window") and self.window.selected_theme:
            self.apply_theme(self.window.selected_theme)

    def on_settings_action(self, action, param):
        """Handle settings action."""
        if hasattr(self, "window"):
            dialog = SettingsDialog(self.window, self.settings)
            dialog.connect("close-request", self.on_settings_closed)
            dialog.present()

    def on_settings_closed(self, dialog):
        """Handle settings dialog close."""
        if dialog.has_changes():
            self.settings = dialog.get_config()
            self.window.show_toast("Settings saved")

    def on_about_action(self, action, param):
        """Handle about action."""
        about = Adw.AboutWindow.new()
        about.set_transient_for(self.window)
        about.set_application_name(APP_NAME)
        about.set_application_icon(APP_ID)
        about.set_version(APP_VERSION)
        about.set_developer_name(APP_DEVELOPER)
        about.set_website(APP_WEBSITE)
        about.set_issue_url(f"{APP_WEBSITE}/issues")
        about.set_copyright("Copyright 2024 Unified Theming Contributors")
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_comments(
            "Apply consistent themes across GTK, Qt, Flatpak, and Snap applications"
        )
        about.set_developers(["Unified Theming Contributors"])
        about.set_designers(["Unified Theming Contributors"])
        about.add_credit_section("Special Thanks", ["GNOME Project", "KDE Project"])
        about.present()

    def on_quit_action(self, action, param):
        """Handle quit action."""
        self.quit()

    def on_search_action(self, action, param):
        """Handle search action."""
        if hasattr(self, "window"):
            self.window.focus_search()

    def on_details_action(self, action, param):
        """Handle theme details action."""
        if hasattr(self, "window") and self.window.selected_theme:
            theme_info = self.themes.get(self.window.selected_theme)
            if theme_info:
                dialog = ThemeDetailsDialog(
                    self.window, self.window.selected_theme, theme_info
                )
                dialog.present()

    def on_rollback_action(self, action, param):
        """Handle rollback action."""
        if not self.manager:
            return

        dialog = ConfirmationDialog(
            self.window,
            "Rollback Theme",
            "This will restore your previous theme configuration. Continue?",
            "Rollback",
            destructive=True,
        )

        def on_response(response):
            if response == "confirm":
                self.perform_rollback()

        dialog.run_async(on_response)

    def perform_rollback(self):
        """Perform theme rollback."""
        try:
            success = self.manager.rollback()
            if success:
                self.window.show_toast("Theme rolled back successfully")
            else:
                self.show_error_dialog("No backup available for rollback")
        except Exception as e:
            self.show_error_dialog(f"Rollback failed: {e}")


class MainWindow(Adw.ApplicationWindow):
    """
    Main application window with modern Adwaita design.

    Uses NavigationSplitView for responsive sidebar layout with
    theme list and preview panels.
    """

    def __init__(self, application):
        """Initialize the main window."""
        super().__init__(application=application)

        # Window properties
        self.set_title(APP_NAME)
        self.set_default_size(1100, 750)
        self.set_size_request(360, 500)

        # State
        self.themes: Dict[str, ThemeInfo] = {}
        self.filtered_themes: Dict[str, ThemeInfo] = {}
        self.selected_theme: Optional[str] = None
        self.theme_rows: Dict[str, Gtk.ListBoxRow] = {}

        # Build UI
        self.setup_ui()
        self.setup_css()

        logger.info("MainWindow initialized")

    def setup_css(self):
        """Set up custom CSS styling."""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            .theme-row {
                padding: 12px;
            }
            .theme-row:selected {
                background-color: alpha(@accent_color, 0.15);
            }
            .toolkit-badge {
                background-color: alpha(@accent_color, 0.2);
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 0.8em;
            }
            .color-swatch {
                border-radius: 6px;
                border: 1px solid alpha(currentColor, 0.2);
            }
            .sidebar-header {
                padding: 12px;
            }
            .content-placeholder {
                opacity: 0.5;
            }
            .apply-button {
                padding: 8px 24px;
            }
            """
        )
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def setup_ui(self):
        """Set up the user interface."""
        # Main container with toast overlay
        self.toast_overlay = Adw.ToastOverlay.new()
        self.set_content(self.toast_overlay)

        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toast_overlay.set_child(main_box)

        # Header bar
        self.setup_header_bar(main_box)

        # Loading overlay
        self.loading_overlay = Adw.ToolbarView.new()
        main_box.append(self.loading_overlay)

        # Navigation split view
        self.split_view = Adw.NavigationSplitView.new()
        self.split_view.set_vexpand(True)
        self.loading_overlay.set_content(self.split_view)

        # Sidebar
        self.setup_sidebar()

        # Content
        self.setup_content()

        # Status page for loading
        self.loading_page = Adw.StatusPage.new()
        self.loading_page.set_icon_name("folder-saved-search-symbolic")
        self.loading_page.set_title("Discovering Themes")
        self.loading_page.set_description("Scanning theme directories...")
        spinner = Gtk.Spinner()
        spinner.set_size_request(32, 32)
        spinner.start()
        self.loading_page.set_child(spinner)

    def setup_header_bar(self, parent):
        """Set up the header bar."""
        header_bar = Adw.HeaderBar.new()

        # App title
        title_widget = Adw.WindowTitle.new(APP_NAME, "")
        header_bar.set_title_widget(title_widget)

        # Left side: Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_tooltip_text("Main Menu")

        # Create menu
        menu = Gio.Menu.new()
        menu.append("Refresh Themes", "app.refresh")
        menu.append("Rollback", "app.rollback")
        menu.append("Preferences", "app.preferences")
        menu.append("Keyboard Shortcuts", "win.show-help-overlay")
        menu.append("About", "app.about")
        menu.append("Quit", "app.quit")
        menu_button.set_menu_model(menu)
        header_bar.pack_start(menu_button)

        # Right side: Apply button (prominent)
        self.apply_button = Gtk.Button.new_with_label("Apply Theme")
        self.apply_button.add_css_class("suggested-action")
        self.apply_button.add_css_class("apply-button")
        self.apply_button.set_sensitive(False)
        self.apply_button.set_tooltip_text("Apply selected theme (Ctrl+Enter)")
        self.apply_button.connect("clicked", self.on_apply_clicked)
        header_bar.pack_end(self.apply_button)

        # Search toggle button
        self.search_button = Gtk.ToggleButton()
        self.search_button.set_icon_name("system-search-symbolic")
        self.search_button.set_tooltip_text("Search themes (Ctrl+F)")
        self.search_button.connect("toggled", self.on_search_toggled)
        header_bar.pack_end(self.search_button)

        parent.append(header_bar)

        # Setup keyboard shortcuts help
        self.setup_shortcuts_window()

    def setup_shortcuts_window(self):
        """Set up the keyboard shortcuts help window."""
        builder = Gtk.Builder.new_from_string(
            """
            <interface>
              <object class="GtkShortcutsWindow" id="shortcuts">
                <property name="modal">True</property>
                <child>
                  <object class="GtkShortcutsSection">
                    <property name="section-name">shortcuts</property>
                    <child>
                      <object class="GtkShortcutsGroup">
                        <property name="title">General</property>
                        <child>
                          <object class="GtkShortcutsShortcut">
                            <property name="title">Apply theme</property>
                            <property name="accelerator">&lt;Control&gt;Return</property>
                          </object>
                        </child>
                        <child>
                          <object class="GtkShortcutsShortcut">
                            <property name="title">Refresh themes</property>
                            <property name="accelerator">&lt;Control&gt;r</property>
                          </object>
                        </child>
                        <child>
                          <object class="GtkShortcutsShortcut">
                            <property name="title">Search themes</property>
                            <property name="accelerator">&lt;Control&gt;f</property>
                          </object>
                        </child>
                        <child>
                          <object class="GtkShortcutsShortcut">
                            <property name="title">Theme details</property>
                            <property name="accelerator">&lt;Control&gt;i</property>
                          </object>
                        </child>
                        <child>
                          <object class="GtkShortcutsShortcut">
                            <property name="title">Rollback theme</property>
                            <property name="accelerator">&lt;Control&gt;z</property>
                          </object>
                        </child>
                        <child>
                          <object class="GtkShortcutsShortcut">
                            <property name="title">Preferences</property>
                            <property name="accelerator">&lt;Control&gt;comma</property>
                          </object>
                        </child>
                        <child>
                          <object class="GtkShortcutsShortcut">
                            <property name="title">Quit</property>
                            <property name="accelerator">&lt;Control&gt;q</property>
                          </object>
                        </child>
                      </object>
                    </child>
                  </object>
                </child>
              </object>
            </interface>
            """,
            -1,
        )
        shortcuts_window = builder.get_object("shortcuts")
        shortcuts_window.set_transient_for(self)
        self.set_help_overlay(shortcuts_window)

    def setup_sidebar(self):
        """Set up the sidebar with theme list."""
        sidebar_page = Adw.NavigationPage.new(Gtk.Box(), "Themes")
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_page.set_child(sidebar_box)

        # Search bar
        self.search_bar = Gtk.SearchBar.new()
        self.search_bar.set_key_capture_widget(self)
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search themes...")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_bar.set_child(self.search_entry)
        self.search_bar.connect_entry(self.search_entry)
        sidebar_box.append(self.search_bar)

        # Theme count label
        self.count_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.count_box.add_css_class("sidebar-header")
        self.count_label = Gtk.Label()
        self.count_label.set_xalign(0)
        self.count_label.add_css_class("dim-label")
        self.count_box.append(self.count_label)

        # Refresh button
        refresh_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh theme list")
        refresh_button.add_css_class("flat")
        refresh_button.connect(
            "clicked", lambda b: self.get_application().on_refresh_action(None, None)
        )
        self.count_box.append(refresh_button)

        sidebar_box.append(self.count_box)

        # Theme list in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.theme_list = Gtk.ListBox()
        self.theme_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.theme_list.add_css_class("navigation-sidebar")
        self.theme_list.connect("row-selected", self.on_theme_selected)
        self.theme_list.set_placeholder(self.create_empty_placeholder())
        scrolled.set_child(self.theme_list)

        sidebar_box.append(scrolled)

        self.split_view.set_sidebar(sidebar_page)

    def create_empty_placeholder(self) -> Gtk.Widget:
        """Create placeholder for empty theme list."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_valign(Gtk.Align.CENTER)
        box.set_margin_top(48)
        box.set_margin_bottom(48)

        icon = Gtk.Image.new_from_icon_name("folder-symbolic")
        icon.set_pixel_size(48)
        icon.add_css_class("dim-label")
        box.append(icon)

        label = Gtk.Label.new("No themes found")
        label.add_css_class("dim-label")
        box.append(label)

        return box

    def setup_content(self):
        """Set up the content area with theme preview."""
        content_page = Adw.NavigationPage.new(Gtk.Box(), "Preview")
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_page.set_child(content_box)

        # Content header
        content_header = Adw.HeaderBar.new()
        content_header.add_css_class("flat")

        # Details button
        details_button = Gtk.Button.new_from_icon_name("info-symbolic")
        details_button.set_tooltip_text("Theme details (Ctrl+I)")
        details_button.set_sensitive(False)
        details_button.connect("clicked", self.on_details_clicked)
        self.details_button = details_button
        content_header.pack_end(details_button)

        content_box.append(content_header)

        # Theme preview
        self.theme_preview = ThemePreviewWidget()
        self.theme_preview.set_vexpand(True)
        content_box.append(self.theme_preview)

        # Empty state
        self.empty_content = Adw.StatusPage.new()
        self.empty_content.set_icon_name("color-select-symbolic")
        self.empty_content.set_title("Select a Theme")
        self.empty_content.set_description(
            "Choose a theme from the sidebar to preview its colors and details"
        )
        self.empty_content.add_css_class("content-placeholder")

        # Stack for switching between empty and preview
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.content_stack.add_named(self.empty_content, "empty")
        self.content_stack.add_named(content_box, "preview")
        self.content_stack.set_visible_child_name("empty")

        content_wrapper = Adw.NavigationPage.new(self.content_stack, "Preview")
        self.split_view.set_content(content_wrapper)

    def set_loading(self, loading: bool, message: str = "Loading..."):
        """Set loading state."""
        if loading:
            self.loading_page.set_description(message)
            self.loading_overlay.set_content(self.loading_page)
        else:
            self.loading_overlay.set_content(self.split_view)

    def set_themes(self, themes: Dict[str, ThemeInfo]):
        """Update the theme list with discovered themes."""
        self.themes = themes
        self.filtered_themes = themes.copy()
        self.update_theme_list()
        self.update_count_label()

    def update_theme_list(self):
        """Rebuild the theme list from filtered themes."""
        # Clear existing rows
        while True:
            row = self.theme_list.get_first_child()
            if row is None:
                break
            self.theme_list.remove(row)
        self.theme_rows.clear()

        # Add rows for filtered themes
        for theme_name in sorted(self.filtered_themes.keys()):
            theme_info = self.filtered_themes[theme_name]
            row = self.create_theme_row(theme_name, theme_info)
            self.theme_rows[theme_name] = row
            self.theme_list.append(row)

    def create_theme_row(
        self, theme_name: str, theme_info: ThemeInfo
    ) -> Gtk.ListBoxRow:
        """Create a row for the theme list."""
        row = Gtk.ListBoxRow()
        row.theme_name = theme_name

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.add_css_class("theme-row")

        # Theme icon (based on toolkit support)
        icon_name = self.get_theme_icon(theme_info)
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(32)
        box.append(icon)

        # Theme info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_hexpand(True)

        # Name
        name_label = Gtk.Label.new(theme_name)
        name_label.set_xalign(0)
        name_label.add_css_class("heading")
        name_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        info_box.append(name_label)

        # Toolkit badges
        badge_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        for toolkit in theme_info.supported_toolkits[:4]:  # Limit to 4 badges
            badge = Gtk.Label.new(toolkit.value.upper())
            badge.add_css_class("toolkit-badge")
            badge.add_css_class("caption")
            badge_box.append(badge)

        if len(theme_info.supported_toolkits) > 4:
            more_badge = Gtk.Label.new(f"+{len(theme_info.supported_toolkits) - 4}")
            more_badge.add_css_class("toolkit-badge")
            more_badge.add_css_class("caption")
            badge_box.append(more_badge)

        info_box.append(badge_box)
        box.append(info_box)

        # Chevron
        chevron = Gtk.Image.new_from_icon_name("go-next-symbolic")
        chevron.add_css_class("dim-label")
        box.append(chevron)

        row.set_child(box)
        return row

    def get_theme_icon(self, theme_info: ThemeInfo) -> str:
        """Get appropriate icon for theme based on toolkit support."""
        toolkits = [t.value for t in theme_info.supported_toolkits]
        if "gtk4" in toolkits or "libadwaita" in toolkits:
            return "preferences-desktop-appearance-symbolic"
        elif "qt5" in toolkits or "qt6" in toolkits:
            return "preferences-desktop-theme-symbolic"
        return "applications-graphics-symbolic"

    def update_count_label(self):
        """Update the theme count label."""
        total = len(self.themes)
        filtered = len(self.filtered_themes)
        if filtered == total:
            self.count_label.set_text(f"{total} themes")
        else:
            self.count_label.set_text(f"{filtered} of {total} themes")

    def on_theme_selected(self, listbox, row):
        """Handle theme selection."""
        if row is None:
            self.selected_theme = None
            self.apply_button.set_sensitive(False)
            self.details_button.set_sensitive(False)
            self.content_stack.set_visible_child_name("empty")
            self.theme_preview.set_theme(None)
            return

        self.selected_theme = row.theme_name
        theme_info = self.themes.get(self.selected_theme)

        self.apply_button.set_sensitive(True)
        self.details_button.set_sensitive(True)
        self.content_stack.set_visible_child_name("preview")
        self.theme_preview.set_theme(theme_info)

        # Update split view for mobile
        self.split_view.set_show_content(True)

    def on_apply_clicked(self, button):
        """Handle apply button click."""
        if self.selected_theme:
            self.apply_button.set_sensitive(False)

            def on_complete(result):
                self.apply_button.set_sensitive(True)

            self.get_application().apply_theme(self.selected_theme, on_complete)

    def on_details_clicked(self, button):
        """Handle details button click."""
        if self.selected_theme:
            theme_info = self.themes.get(self.selected_theme)
            if theme_info:
                dialog = ThemeDetailsDialog(self, self.selected_theme, theme_info)
                dialog.present()

    def on_search_toggled(self, button):
        """Handle search toggle."""
        self.search_bar.set_search_mode(button.get_active())
        if button.get_active():
            self.search_entry.grab_focus()

    def on_search_changed(self, entry):
        """Handle search text changes."""
        search_text = entry.get_text().lower().strip()

        if not search_text:
            self.filtered_themes = self.themes.copy()
        else:
            self.filtered_themes = {
                name: info
                for name, info in self.themes.items()
                if search_text in name.lower()
                or any(search_text in t.value.lower() for t in info.supported_toolkits)
            }

        self.update_theme_list()
        self.update_count_label()

    def focus_search(self):
        """Focus the search entry."""
        self.search_button.set_active(True)
        self.search_entry.grab_focus()

    def show_toast(
        self,
        message: str,
        timeout: int = 3,
        button_label: Optional[str] = None,
        button_action: Optional[callable] = None,
    ):
        """Show a toast notification."""
        toast = Adw.Toast.new(message)
        toast.set_timeout(timeout)

        if button_label and button_action:
            toast.set_button_label(button_label)
            toast.connect("button-clicked", lambda t: button_action())

        self.toast_overlay.add_toast(toast)


def main():
    """Main entry point for the GUI application."""
    try:
        app = ThemeApp()
        return app.run(sys.argv)
    except ImportError as e:
        if "gi" in str(e):
            print("Error: GTK4/PyGObject not available.")
            print("\nTo use the GUI, install system dependencies:")
            print("\nUbuntu/Debian:")
            print("  sudo apt install libgtk-4-dev libadwaita-1-dev python3-gi")
            print("  pip install -e '.[gui]'")
            print("\nFedora/RHEL:")
            print("  sudo dnf install gtk4-devel libadwaita-devel python3-gobject")
            print("  pip install -e '.[gui]'")
            print("\nAlternatively, use the CLI:")
            print("  unified-theming list")
            print("  unified-theming apply_theme <theme_name>")
            return 1
        raise
    except Exception as e:
        print(f"Error starting GUI: {e}")
        print("\nTry using the CLI instead:")
        print("  unified-theming --help")
        return 1


if __name__ == "__main__":
    sys.exit(main())
