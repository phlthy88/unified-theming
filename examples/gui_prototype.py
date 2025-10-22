"""
GUI Prototype for Unified Theming System.

This is an experimental prototype to validate user workflows for the unified-theming
project. It provides a visual interface for theme selection, preview (dry-run),
application, and rollback operations.

**IMPORTANT:** This is a prototype, NOT production-ready code.

Author: Qwen Coder (Agent 2)
Sprint: Unified Theming Sprint Day 1
Date: October 22, 2025

System Requirements:
    - Python 3.10+
    - GTK 4.10+
    - Libadwaita 1.0+
    - PyGObject (Python GObject Introspection bindings)

Installation:
    On Debian/Ubuntu:
        sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

    Dependencies: Requires Python 3.10+, GTK 4.10+, Libadwaita 1.0+, PyGObject
    Install PyGObject with: pip install PyGObject

Usage:
    python3 examples/gui_prototype.py

Features:
    - Theme discovery and selection
    - Preview changes (dry-run mode) before applying
    - Apply theme with real-time CLI output
    - Rollback to previous theme
    - Activity spinner during operations
    - Non-editable log view for command output

Architecture:
    - Uses subprocess calls to unified-theming CLI
    - Threading for non-blocking operations
    - GLib.idle_add for thread-safe UI updates
    - Direct API access to UnifiedThemeManager for plan_changes()

DEVELOPER NOTES FOR AGENT 3:
    CI/CD Validation Requirements:
    1. Syntax Check: Ensure file compiles without syntax errors
    2. Import Check: Verify unified_theming modules can be imported
    3. Structure Check: Validate required classes and methods exist
    4. Threading Check: Confirm proper threading with daemon=True
    5. Error Handling: Verify try/except blocks for robustness

    Known Limitations:
    - GUI runtime tests require X server (skip in headless CI)
    - Subprocess calls to CLI require unified-theming to be installed
    - GTK/Libadwaita dependencies not available on all systems

    Testing Strategy:
    - Static validation: syntax, imports, structure (CI-friendly)
    - Manual validation: actual GUI launch and interaction (developer)
    - Skip: Runtime GUI tests in CI (no X server)

    Dependencies for CI:
        - python3-gi, python3-gi-cairo (for imports)
        - gir1.2-gtk-4.0, gir1.2-adw-1 (for type stubs)
        - unified-theming package installed in editable mode

    Future Production Requirements:
    - Error recovery and retry mechanisms
    - Configuration persistence
    - Theme preview rendering
    - Proper application packaging (Flatpak/AppImage)
    - Desktop integration (D-Bus, notifications)
    - Accessibility support (screen readers, keyboard nav)
"""

import gi

gi.require_version("Gtk", "4.0")  # type: ignore
gi.require_version("Adw", "1")  # type: ignore

import json
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional, List

from gi.repository import Gtk, Adw, GLib, Gio, Pango  # type: ignore

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the core modules for direct API access
from unified_theming.core.manager import UnifiedThemeManager
from unified_theming.core.types import PlanResult  # type: ignore


class ThemeAppPrototype(Adw.Application):
    """
    Main application class for the GUI prototype.

    Provides a minimal interface with theme selection, apply/rollback functionality,
    activity spinner, and log output.
    """

    def __init__(self):
        """
        Initialize the prototype application.
        """
        super().__init__(
            application_id="com.example.unified-theming-gui-prototype",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

        # Connect activation signal
        self.connect("activate", self.on_activate)

        # Initialize CLI path
        self.cli_path = "unified-theming"

        # Store discovered themes
        self.themes = []

        # Track ongoing operations
        self.current_operation_thread = None
        self.operation_cancelled = False

        # Initialize theme manager for direct API calls
        self.theme_manager = UnifiedThemeManager()

    def on_activate(self, app):
        """
        Called when the application is activated.

        Args:
            app: The application instance
        """
        # Create and show the main window
        self.main_window = PrototypeWindow(application=app, prototype=self)
        self.main_window.present()

        # Load themes in the background
        GLib.idle_add(self.load_themes)

    def load_themes(self):
        """
        Load themes from CLI in a background thread.
        """

        def load_themes_thread():
            try:
                # Run the CLI list command to get themes
                result = subprocess.run(
                    [self.cli_path, "list", "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    themes_data = json.loads(result.stdout)
                    # Extract theme names
                    self.themes = list(themes_data.keys())

                    # Update UI in the main thread
                    GLib.idle_add(self.main_window.update_theme_list, self.themes)
                else:
                    # Show error in log
                    GLib.idle_add(
                        self.main_window.append_to_log,
                        f"Error loading themes: {result.stderr}",
                    )
            except subprocess.TimeoutExpired:
                GLib.idle_add(
                    self.main_window.append_to_log, "Error: Theme loading timed out"
                )
            except Exception as e:
                GLib.idle_add(
                    self.main_window.append_to_log, f"Error loading themes: {str(e)}"
                )

        # Run in a separate thread to avoid blocking the UI
        thread = threading.Thread(target=load_themes_thread, daemon=True)
        thread.start()

    def run_cli_command(
        self, command_args: List[str], success_message: Optional[str] = None
    ):
        """
        Run a CLI command in a separate thread.

        Args:
            command_args: List of command arguments for the CLI
            success_message: Message to show on success
        """
        self.operation_cancelled = False

        def run_command_thread():
            try:
                # Prepend the CLI path to the command arguments
                cmd = [self.cli_path] + command_args

                # Start the subprocess
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                )

                # Read output line by line to display in real-time
                while True:
                    if self.operation_cancelled:
                        process.terminate()
                        GLib.idle_add(
                            self.main_window.append_to_log,
                            "Operation cancelled by user",
                        )
                        return

                    if process.stdout is not None:
                        line_bytes = process.stdout.readline()
                        if line_bytes == b"" and process.poll() is not None:
                            break
                        if line_bytes:
                            if isinstance(line_bytes, bytes):
                                line_str = line_bytes.decode("utf-8", errors="replace")
                            else:
                                line_str = str(line_bytes)
                            GLib.idle_add(
                                self.main_window.append_to_log, line_str.strip()
                            )

                # Get the return code
                return_code = process.poll()

                if return_code == 0 and success_message:
                    GLib.idle_add(self.main_window.append_to_log, success_message)
                elif return_code != 0:
                    GLib.idle_add(
                        self.main_window.append_to_log,
                        f"Command failed with exit code: {return_code}",
                    )

            except Exception as e:
                GLib.idle_add(
                    self.main_window.append_to_log, f"Error running command: {str(e)}"
                )
            finally:
                # Operation complete, update UI
                GLib.idle_add(self.main_window.set_operation_complete)

        # Store the thread reference
        self.current_operation_thread = threading.Thread(
            target=run_command_thread, daemon=True
        )
        self.current_operation_thread.start()

        # Update UI to indicate operation is running
        self.main_window.set_operation_running()


class PrototypeWindow(Adw.ApplicationWindow):
    """
    Main window for the GUI prototype.

    Contains theme selection dropdown, apply/rollback buttons, spinner, and log view.
    """

    def __init__(self, **kwargs):
        """
        Initialize the window.

        Args:
            **kwargs: Arguments passed to parent constructor
        """
        # Extract prototype before calling parent constructor
        self.prototype = kwargs.pop("prototype", None)

        super().__init__(**kwargs)

        # Set window properties
        self.set_title("Unified Theming GUI Prototype")
        self.set_default_size(800, 600)

        # Main layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.box)

        # Setup UI components
        self.setup_header_bar()
        self.setup_content_area()
        self.setup_log_view()

        # Initialize state
        self.current_theme = None

    def setup_header_bar(self):
        """
        Setup the header bar with title and actions.
        """
        header_bar = Adw.HeaderBar.new()

        # Title
        header_bar.set_title_widget(
            Adw.WindowTitle.new("Unified Theming Prototype", "")
        )

        # Add header bar to main box
        self.box.append(header_bar)

    def setup_content_area(self):
        """
        Setup the main content area with theme selection and buttons.
        """
        # Main content container
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_start(18)
        content_box.set_margin_end(18)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)

        # Theme selection row
        theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        # Theme label
        theme_label = Gtk.Label.new("Select Theme:")
        theme_label.set_halign(Gtk.Align.START)
        theme_row.append(theme_label)

        # Theme selection dropdown
        self.theme_combo = Gtk.ComboBoxText()
        self.theme_combo.set_hexpand(True)
        self.theme_combo.connect("changed", self.on_theme_changed)
        theme_row.append(self.theme_combo)

        content_box.append(theme_row)

        # Buttons row
        buttons_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        # Preview changes button
        self.preview_button = Gtk.Button.new_with_label("Preview Changes")
        self.preview_button.add_css_class("accent")
        self.preview_button.connect("clicked", self.on_preview_clicked)
        self.preview_button.set_sensitive(False)  # Disabled until a theme is selected
        buttons_row.append(self.preview_button)

        # Apply button
        self.apply_button = Gtk.Button.new_with_label("Apply Theme")
        self.apply_button.add_css_class("suggested-action")
        self.apply_button.connect("clicked", self.on_apply_clicked)
        self.apply_button.set_sensitive(False)  # Disabled until a theme is selected
        buttons_row.append(self.apply_button)

        # Rollback button
        self.rollback_button = Gtk.Button.new_with_label("Rollback")
        self.rollback_button.add_css_class("destructive-action")
        self.rollback_button.connect("clicked", self.on_rollback_clicked)
        buttons_row.append(self.rollback_button)

        # Spinner for activity indication
        self.spinner = Gtk.Spinner()
        buttons_row.append(self.spinner)

        content_box.append(buttons_row)

        # Add content box to main layout
        self.box.append(content_box)

    def setup_log_view(self):
        """
        Setup the log view for displaying CLI output.
        """
        # Create scrolled window for log
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)

        # Create text view for log display
        self.log_text_view = Gtk.TextView()
        self.log_text_view.set_editable(False)
        self.log_text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.log_text_view.set_cursor_visible(False)

        # Use a text buffer to manage the display
        self.log_buffer = self.log_text_view.get_buffer()

        # Set monospace font for better readability
        self.log_text_view.override_font(
            Pango.FontDescription.from_string("monospace 10")
        )

        # Add text view to scrolled window
        scrolled_window.set_child(self.log_text_view)

        # Add scrolled window to main layout
        self.box.append(scrolled_window)

    def update_theme_list(self, themes):
        """
        Update the theme selection dropdown with discovered themes.

        Args:
            themes: List of theme names
        """
        # Clear existing items
        self.theme_combo.remove_all()

        # Add themes to the dropdown
        for theme in sorted(themes):
            self.theme_combo.append(theme.lower(), theme)

        # If there are themes, set the first one as active
        if themes:
            self.theme_combo.set_active(0)
            self.on_theme_changed(self.theme_combo)

    def on_theme_changed(self, combo):
        """
        Called when the theme selection changes.

        Args:
            combo: The theme selection combo box
        """
        active = combo.get_active()
        if active >= 0:
            self.current_theme = combo.get_active_id()
            self.apply_button.set_sensitive(True)
            self.preview_button.set_sensitive(True)
        else:
            self.current_theme = None
            self.apply_button.set_sensitive(False)
            self.preview_button.set_sensitive(False)

    def on_apply_clicked(self, button):
        """
        Called when the apply button is clicked.

        Args:
            button: The apply button that was clicked
        """
        if not self.current_theme:
            return

        # Log the action
        self.append_to_log(f"Applying theme '{self.current_theme}'...")

        # Run the CLI apply command
        self.prototype.run_cli_command(
            ["apply", self.current_theme],
            f"Theme '{self.current_theme}' applied successfully!",
        )

    def on_preview_clicked(self, button):
        """
        Called when the preview changes button is clicked.

        Args:
            button: The preview button that was clicked
        """
        if not self.current_theme:
            return

        # Log the action
        self.append_to_log(f"Previewing changes for theme '{self.current_theme}'...")

        # Run the preview operation in a separate thread
        def preview_thread():
            try:
                # Use the direct API to plan changes
                plan_result = self.prototype.theme_manager.plan_changes(
                    self.current_theme
                )

                # Format and display the plan result
                formatted_output = self.format_plan_result(plan_result)

                # Update UI in the main thread
                GLib.idle_add(self.append_to_log, formatted_output)
                GLib.idle_add(
                    self.append_to_log,
                    f"Preview for theme '{self.current_theme}' completed!",
                )
            except Exception as e:
                # Update UI in the main thread with error
                GLib.idle_add(self.append_to_log, f"Error in preview: {str(e)}")
            finally:
                # Operation complete, update UI
                GLib.idle_add(self.set_operation_complete)

        # Store the thread reference
        self.prototype.current_operation_thread = threading.Thread(
            target=preview_thread, daemon=True
        )
        self.prototype.current_operation_thread.start()

        # Update UI to indicate operation is running
        self.set_operation_running()

    def on_rollback_clicked(self, button):
        """
        Called when the rollback button is clicked.

        Args:
            button: The rollback button that was clicked
        """
        # Log the action
        self.append_to_log("Rolling back to previous configuration...")

        # Run the CLI rollback command
        self.prototype.run_cli_command(["rollback"], "Rollback completed successfully!")

    def set_operation_running(self):
        """
        Update UI to indicate an operation is running.
        """
        # Disable buttons to prevent multiple operations
        self.apply_button.set_sensitive(False)
        self.rollback_button.set_sensitive(False)

        # Start the spinner
        self.spinner.start()

        # Add separator to log to mark operation start
        self.append_to_log("-" * 50)

    def set_operation_complete(self):
        """
        Update UI to indicate an operation is complete.
        """
        # Re-enable buttons
        self.apply_button.set_sensitive(self.current_theme is not None)
        self.rollback_button.set_sensitive(True)

        # Stop the spinner
        self.spinner.stop()

        # Add separator to log to mark operation end
        self.append_to_log("-" * 50)

    def format_plan_result(self, plan_result: PlanResult) -> str:
        """
        Format the PlanResult for display in the log.

        Args:
            plan_result: The PlanResult object to format

        Returns:
            Formatted string representation of the plan result
        """
        lines = []
        lines.append("=" * 60)
        lines.append("DRY-RUN PREVIEW - Planned Changes")
        lines.append("=" * 60)

        # Add theme name
        lines.append(f"Theme: {plan_result.theme_name}")
        lines.append("")

        # Add summary of files affected
        lines.append(
            f"Estimated files affected: {plan_result.estimated_files_affected}"
        )
        lines.append("")

        # Add handler availability
        lines.append("Handler Availability:")
        for handler_name, available in plan_result.available_handlers.items():
            status = "✓ Available" if available else "✗ Not Available"
            lines.append(f"  - {handler_name}: {status}")
        lines.append("")

        # Add planned changes by handler
        if plan_result.planned_changes:
            lines.append("Planned Changes:")
            # Group changes by handler
            changes_by_handler = {}
            for change in plan_result.planned_changes:
                if change.handler_name not in changes_by_handler:
                    changes_by_handler[change.handler_name] = []
                changes_by_handler[change.handler_name].append(change)

            for handler_name, changes in changes_by_handler.items():
                lines.append(f"  {handler_name}:")
                for change in changes:
                    change_type = change.change_type.upper()
                    lines.append(
                        f"    [{change_type}] {change.file_path} - {change.description}"
                    )
        else:
            lines.append(
                "Planned Changes: None (handlers may not be fully implemented yet)"
            )

        lines.append("")

        # Add warnings if any
        if plan_result.warnings:
            lines.append("Warnings:")
            for warning in plan_result.warnings:
                lines.append(f"  ⚠ {warning}")
            lines.append("")

        # Add validation results if available
        if plan_result.validation_result:
            lines.append("Validation Results:")
            for msg in plan_result.validation_result.messages:
                level = msg.level.value
                lines.append(f"  [{level}] {msg.message}")
                if msg.details:
                    lines.append(f"      Details: {msg.details}")
            lines.append("")

        lines.append("=" * 60)
        lines.append("DRY-RUN MODE: No changes were made to your system")
        lines.append("=" * 60)

        return "\n".join(lines)

    def append_to_log(self, text):
        """
        Append text to the log view.

        Args:
            text: Text to append to the log
        """
        # Add timestamp to the message
        timestamp = time.strftime("%H:%M:%S")
        formatted_text = f"[{timestamp}] {text}\n"

        # Append to the text buffer
        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end_iter, formatted_text)

        # Scroll to the end
        self.log_text_view.scroll_to_mark(
            self.log_buffer.get_insert(), 0.0, True, 0.0, 1.0
        )


def main():
    """
    Main entry point for the GUI prototype.
    """
    # Create the application
    app = ThemeAppPrototype()

    # Run the application
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
