"""
GTK4/Libadwaita GUI Application for Unified Theming.

This module implements the main GUI application using GTK4 and Libadwaita,
providing a modern, native interface for theme management.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gio
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys
import os

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from unified_theming.core.manager import UnifiedThemeManager
from unified_theming.core.types import ThemeInfo, ApplicationResult
from unified_theming.utils.logging_config import get_logger
from .widgets import ThemeListBox, ThemePreviewWidget, ProgressDialog
from .dialogs import SettingsDialog

logger = get_logger(__name__)


class ThemeApp(Adw.Application):
    """
    Main application class for Unified Theming GUI.

    This class manages the application lifecycle, window creation,
    and integration with the core theming components.
    """

    def __init__(self):
        """
        Initialize the application.
        """
        super().__init__(
            application_id="com.example.unified-theming",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        # Connect signals
        self.connect('activate', self.on_activate)
        self.connect('shutdown', self.on_shutdown)

        # Initialize core components
        self.manager: Optional[UnifiedThemeManager] = None
        self.themes: Dict[str, ThemeInfo] = {}
        self.current_operation: Optional[Any] = None

        logger.info("ThemeApp initialized")

    def on_activate(self, app):
        """
        Called when the application is activated.

        Args:
            app: The application instance
        """
        logger.info("Application activated")

        # Create main window
        self.window = MainWindow(application=app)
        self.window.present()

        # Initialize theme manager after window is created
        GLib.idle_add(self.initialize_manager)

    def on_shutdown(self, app):
        """
        Called when the application is shutting down.

        Args:
            app: The application instance
        """
        logger.info("Application shutting down")

        # Cancel any ongoing operations
        if self.current_operation:
            self.current_operation.cancel()

    def initialize_manager(self):
        """
        Initialize the theme manager and discover themes.
        """
        try:
            # Initialize theme manager
            self.manager = UnifiedThemeManager()

            # Discover themes
            self.themes = self.manager.discover_themes()

            # Update window with themes
            self.window.set_themes(self.themes)

            logger.info(f"Discovered {len(self.themes)} themes")

        except Exception as e:
            logger.error(f"Failed to initialize theme manager: {e}")
            self.show_error_dialog(f"Failed to initialize: {e}")

    def show_error_dialog(self, message: str):
        """
        Show an error dialog.

        Args:
            message: Error message to display
        """
        dialog = Adw.MessageDialog.new(
            self.window,
            "Error",
            message
        )
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.present()

    def apply_theme(self, theme_name: str, callback=None):
        """
        Apply a theme asynchronously with progress dialog.

        Args:
            theme_name: Name of theme to apply
            callback: Optional callback function
        """
        if not self.manager:
            self.show_error_dialog("Theme manager not initialized")
            return

        # Create progress dialog
        progress_dialog = ProgressDialog(self.window, f"Applying {theme_name}")
        progress_dialog.present()

        def apply_async():
            try:
                GLib.idle_add(lambda: progress_dialog.update_progress(0.1, "Initializing..."))

                result = self.manager.apply_theme(theme_name)

                GLib.idle_add(lambda: progress_dialog.update_progress(1.0, "Complete"))
                GLib.idle_add(lambda: progress_dialog.complete(True, "Theme applied successfully"))
                GLib.idle_add(lambda: self.on_theme_applied(result, callback))

            except Exception as e:
                GLib.idle_add(lambda: progress_dialog.complete(False, f"Failed: {str(e)}"))
                GLib.idle_add(lambda: self.on_theme_error(str(e), callback))

        # Run in thread to avoid blocking UI
        from threading import Thread
        thread = Thread(target=apply_async, daemon=True)
        thread.start()

    def on_theme_applied(self, result: ApplicationResult, callback):
        """
        Called when theme application completes.

        Args:
            result: Application result
            callback: Optional callback
        """
        if result.overall_success:
            # Show success toast
            toast = Adw.Toast.new("Theme applied successfully")
            toast.set_timeout(3)
            self.window.toast_overlay.add_toast(toast)
        else:
            # Show warning dialog
            self.show_error_dialog("Theme applied with warnings")

        if callback:
            callback(result)

    def on_theme_error(self, error: str, callback):
        """
        Called when theme application fails.

        Args:
            error: Error message
            callback: Optional callback
        """
        self.show_error_dialog(f"Failed to apply theme: {error}")
        if callback:
            callback(None)


class MainWindow(Adw.ApplicationWindow):
    """
    Main application window.

    This window contains the theme list, preview, and controls.
    """

    def __init__(self, application):
        """
        Initialize the main window.

        Args:
            application: The parent application
        """
        super().__init__(application=application)

        # Window properties
        self.set_title("Unified Theming")
        self.set_default_size(1000, 700)

        # Initialize components
        self.themes: Dict[str, ThemeInfo] = {}
        self.selected_theme: Optional[str] = None

        # Setup UI
        self.setup_ui()

        logger.info("MainWindow initialized")

    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Create main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)

        # Create header bar
        self.setup_header_bar()

        # Create main content area
        self.setup_content_area()

        # Create toast overlay for notifications
        self.toast_overlay = Adw.ToastOverlay.new()
        self.toast_overlay.set_child(self.main_box)
        self.set_content(self.toast_overlay)

    def setup_header_bar(self):
        """
        Set up the header bar with title and actions.
        """
        header_bar = Adw.HeaderBar.new()

        # Title
        header_bar.set_title_widget(Adw.WindowTitle.new("Unified Theming", ""))

        # Apply button
        self.apply_button = Gtk.Button.new_with_label("Apply Theme")
        self.apply_button.set_sensitive(False)
        self.apply_button.connect("clicked", self.on_apply_clicked)
        header_bar.pack_end(self.apply_button)

        # Settings button
        settings_button = Gtk.Button.new_from_icon_name("preferences-system-symbolic")
        settings_button.set_tooltip_text("Settings")
        settings_button.connect("clicked", self.on_settings_clicked)
        header_bar.pack_end(settings_button)

        # Add header bar to main box
        self.main_box.append(header_bar)

    def setup_content_area(self):
        """
        Set up the main content area with theme list and preview.
        """
        # Create paned container for split view
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_wide_handle(True)

        # Left side: Theme list
        self.setup_theme_list(paned)

        # Right side: Theme preview
        self.setup_theme_preview(paned)

        # Add paned to main box
        self.main_box.append(paned)

    def setup_theme_list(self, paned):
        """
        Set up the theme list panel.

        Args:
            paned: The paned container
        """
        # Create scrolled window for theme list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_width(300)

        # Create theme list widget
        self.theme_list = ThemeListBox()
        self.theme_list.connect("row-selected", self.on_theme_selected)

        # Add list to scrolled window
        scrolled.set_child(self.theme_list)

        # Create frame for visual separation
        frame = Gtk.Frame()
        frame.set_child(scrolled)

        # Add to paned
        paned.set_start_child(frame)

    def setup_theme_preview(self, paned):
        """
        Set up the theme preview panel.

        Args:
            paned: The paned container
        """
        # Create theme preview widget
        self.theme_preview = ThemePreviewWidget()

        # Add to paned
        paned.set_end_child(self.theme_preview)

    def set_themes(self, themes: Dict[str, ThemeInfo]):
        """
        Update the theme list with discovered themes.

        Args:
            themes: Dictionary of theme names to ThemeInfo objects
        """
        self.themes = themes
        self.theme_list.set_themes(themes)



    def on_apply_clicked(self, button):
        """
        Called when the apply button is clicked.

        Args:
            button: The button that was clicked
        """
        if not self.selected_theme:
            return

        # Disable button during operation
        self.apply_button.set_sensitive(False)

        # Apply theme (progress dialog will be shown)
        def on_complete(result):
            self.apply_button.set_sensitive(True)

        self.get_application().apply_theme(self.selected_theme, on_complete)

    def on_settings_clicked(self, button):
        """
        Called when the settings button is clicked.

        Args:
            button: The button that was clicked
        """
        # Show settings dialog
        dialog = SettingsDialog(self)
        dialog.present()


def main():
    """
    Main entry point for the GUI application.
    """
    app = ThemeApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())