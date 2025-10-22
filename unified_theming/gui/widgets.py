"""
GUI widgets for Unified Theming Application.

This module contains reusable widget classes for the GTK4/Libadwaita interface.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from gi.repository import Adw, Gdk, GLib, Gtk

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from unified_theming.core.types import ThemeInfo
from unified_theming.utils.logging_config import get_logger

logger = get_logger(__name__)


class ThemeListBox(Gtk.ListBox):
    """
    A list box widget for displaying available themes.

    This widget shows themes in a scrollable list with theme names
    and toolkit support information.
    """

    def __init__(self):
        """
        Initialize the theme list box.
        """
        super().__init__()

        # Configure list box
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_show_separators(True)
        self.add_css_class("boxed-list")

        # Store theme data
        self.themes: Dict[str, ThemeInfo] = {}
        self.theme_rows: Dict[str, ThemeListRow] = {}

        logger.info("ThemeListBox initialized")

    def set_themes(self, themes: Dict[str, ThemeInfo]):
        """
        Update the list with new themes.

        Args:
            themes: Dictionary of theme names to ThemeInfo objects
        """
        # Clear existing rows
        self.clear_themes()

        # Store themes
        self.themes = themes

        # Add new rows
        for theme_name, theme_info in sorted(themes.items()):
            row = ThemeListRow(theme_name, theme_info)
            self.theme_rows[theme_name] = row
            self.append(row)

        logger.info(f"Added {len(themes)} themes to list")

    def clear_themes(self):
        """
        Clear all themes from the list.
        """
        for row in self.theme_rows.values():
            self.remove(row)
        self.theme_rows.clear()
        self.themes.clear()

    def get_selected_theme(self) -> Optional[str]:
        """
        Get the currently selected theme name.

        Returns:
            Theme name or None if no selection
        """
        selected_row = self.get_selected_row()
        if selected_row and isinstance(selected_row, ThemeListRow):
            return selected_row.theme_name
        return None

    def select_theme(self, theme_name: Optional[str]):
        """
        Select a theme by name.

        Args:
            theme_name: Name of theme to select, or None to clear selection
        """
        if theme_name and theme_name in self.theme_rows:
            self.select_row(self.theme_rows[theme_name])
        else:
            self.unselect_all()


class ThemeListRow(Gtk.ListBoxRow):
    """
    A single row in the theme list.

    Shows theme name, toolkit count, and selection state.
    """

    def __init__(self, theme_name: str, theme_info: ThemeInfo):
        """
        Initialize the theme list row.

        Args:
            theme_name: Name of the theme
            theme_info: Theme information
        """
        super().__init__()

        self.theme_name = theme_name
        self.theme_info = theme_info

        # Create row content
        self.setup_content()

    def setup_content(self):
        """
        Set up the row content layout.
        """
        # Main box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        # Theme name
        name_label = Gtk.Label.new(self.theme_name)
        name_label.set_halign(Gtk.Align.START)
        name_label.set_hexpand(True)
        name_label.add_css_class("heading")
        box.append(name_label)

        # Toolkit information
        toolkit_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        # Toolkit count
        toolkit_count = len(self.theme_info.supported_toolkits)
        count_label = Gtk.Label.new(
            f"{toolkit_count} toolkit{'s' if toolkit_count != 1 else ''}"
        )
        count_label.set_halign(Gtk.Align.END)
        count_label.add_css_class("dim-label")
        toolkit_box.append(count_label)

        # Toolkit names
        toolkits = [t.value for t in self.theme_info.supported_toolkits]
        toolkit_label = Gtk.Label.new(", ".join(toolkits))
        toolkit_label.set_halign(Gtk.Align.END)
        toolkit_label.add_css_class("caption")
        toolkit_label.add_css_class("dim-label")
        toolkit_box.append(toolkit_label)

        box.append(toolkit_box)

        self.set_child(box)


class ThemePreviewWidget(Gtk.Box):
    """
    Widget for previewing theme colors and information.

    Shows color swatches, theme details, and supported toolkits.
    """

    def __init__(self):
        """
        Initialize the theme preview widget.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        # Current theme info
        self.current_theme: Optional[ThemeInfo] = None

        # Setup UI
        self.setup_ui()

        logger.info("ThemePreviewWidget initialized")

    def setup_ui(self):
        """
        Set up the preview widget UI.
        """
        # Title
        self.title_label = Gtk.Label.new("Theme Preview")
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.add_css_class("title-2")
        self.append(self.title_label)

        # Theme name
        self.name_label = Gtk.Label.new("No theme selected")
        self.name_label.set_halign(Gtk.Align.START)
        self.name_label.add_css_class("title-3")
        self.append(self.name_label)

        # Color palette section
        palette_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        palette_label = Gtk.Label.new("Color Palette")
        palette_label.set_halign(Gtk.Align.START)
        palette_label.add_css_class("heading")
        palette_box.append(palette_label)

        # Color grid
        self.color_grid = Gtk.FlowBox()
        self.color_grid.set_max_children_per_line(6)
        self.color_grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self.color_grid.set_homogeneous(True)
        palette_box.append(self.color_grid)

        self.append(palette_box)

        # Theme information section
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        info_label = Gtk.Label.new("Theme Information")
        info_label.set_halign(Gtk.Align.START)
        info_label.add_css_class("heading")
        info_box.append(info_label)

        # Supported toolkits
        self.toolkits_label = Gtk.Label.new("")
        self.toolkits_label.set_halign(Gtk.Align.START)
        self.toolkits_label.add_css_class("body")
        info_box.append(self.toolkits_label)

        # Theme path
        self.path_label = Gtk.Label.new("")
        self.path_label.set_halign(Gtk.Align.START)
        self.path_label.add_css_class("caption")
        self.path_label.add_css_class("dim-label")
        info_box.append(self.path_label)

        self.append(info_box)

    def set_theme(self, theme_info: Optional[ThemeInfo]):
        """
        Set the theme to preview.

        Args:
            theme_info: Theme information to display, or None to clear
        """
        self.current_theme = theme_info

        if theme_info is None:
            self.show_no_theme()
        else:
            self.show_theme(theme_info)

    def show_no_theme(self):
        """
        Show placeholder when no theme is selected.
        """
        self.name_label.set_text("No theme selected")
        self.clear_color_grid()
        self.toolkits_label.set_text("")
        self.path_label.set_text("")

    def show_theme(self, theme_info: ThemeInfo):
        """
        Display theme information and colors.

        Args:
            theme_info: Theme information to display
        """
        theme_name = theme_info.name if theme_info.name else "Unnamed Theme"
        self.name_label.set_text(theme_name)

        # Update color grid
        self.update_color_grid(theme_info.colors)

        # Update toolkit information
        toolkits = [t.value for t in theme_info.supported_toolkits]
        self.toolkits_label.set_text(f"Supports: {', '.join(toolkits)}")

        # Update path
        self.path_label.set_text(f"Location: {theme_info.path}")

    def update_color_grid(self, colors: Dict[str, str]):
        """
        Update the color swatches grid.

        Args:
            colors: Dictionary of color names to hex values
        """
        self.clear_color_grid()

        # Add color swatches (limit to 12 for preview)
        for i, (name, hex_color) in enumerate(list(colors.items())[:12]):
            swatch = ColorSwatch(name, hex_color)
            self.color_grid.append(swatch)

    def clear_color_grid(self):
        """
        Clear all color swatches from the grid.
        """
        while True:
            child = self.color_grid.get_first_child()
            if child is None:
                break
            self.color_grid.remove(child)


class ColorSwatch(Gtk.Box):
    """
    A widget displaying a color swatch with name and hex value.
    """

    def __init__(self, name: str, hex_color: str):
        """
        Initialize the color swatch.

        Args:
            name: Color variable name
            hex_color: Hex color value
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        self.name = name
        self.hex_color = hex_color

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """
        Set up the swatch UI.
        """
        # Color square
        self.color_square = Gtk.DrawingArea()
        self.color_square.set_size_request(48, 48)
        self.color_square.set_draw_func(self.draw_color_square)
        self.append(self.color_square)

        # Color name
        name_label = Gtk.Label.new(self.name)
        name_label.set_max_width_chars(10)
        name_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        name_label.add_css_class("caption")
        self.append(name_label)

        # Hex value
        hex_label = Gtk.Label.new(self.hex_color.upper())
        hex_label.add_css_class("caption")
        hex_label.add_css_class("dim-label")
        self.append(hex_label)

    def draw_color_square(self, area, cr, width, height, user_data):
        """
        Draw the color square.

        Args:
            area: The drawing area
            cr: Cairo context
            width: Width of area
            height: Height of area
            user_data: User data (unused)
        """
        # Parse hex color
        try:
            # Remove # if present
            hex_color = self.hex_color
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


class ProgressDialog(Adw.Window):
    """
    A modal dialog showing operation progress.
    """

    def __init__(self, parent: Gtk.Window, title: str = "Working..."):
        """
        Initialize the progress dialog.

        Args:
            parent: Parent window
            title: Dialog title
        """
        super().__init__()

        self.set_modal(True)
        self.set_transient_for(parent)
        self.set_title(title)
        self.set_default_size(300, 150)
        self.set_resizable(False)

        # Setup UI
        self.setup_ui()

        # Progress tracking
        self.operation_complete = False

    def setup_ui(self):
        """
        Set up the dialog UI.
        """
        # Main box
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(24)
        box.set_margin_end(24)
        box.set_margin_top(24)
        box.set_margin_bottom(24)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Starting...")
        box.append(self.progress_bar)

        # Status label
        self.status_label = Gtk.Label.new("Preparing operation...")
        self.status_label.set_halign(Gtk.Align.START)
        box.append(self.status_label)

        # Cancel button
        self.cancel_button = Gtk.Button.new_with_label("Cancel")
        self.cancel_button.connect("clicked", self.on_cancel_clicked)
        box.append(self.cancel_button)

        self.set_content(box)

    def update_progress(
        self, fraction: float, text: Optional[str] = None, status: Optional[str] = None
    ):
        """
        Update progress display.

        Args:
            fraction: Progress fraction (0.0 to 1.0)
            text: Progress bar text
            status: Status label text
        """
        self.progress_bar.set_fraction(fraction)
        if text:
            self.progress_bar.set_text(text)
        if status:
            self.status_label.set_text(status)

    def on_cancel_clicked(self, button):
        """
        Called when cancel button is clicked.
        """
        self.close()

    def complete(self, success: bool = True, message: Optional[str] = None):
        """
        Mark operation as complete.

        Args:
            success: Whether operation succeeded
            message: Completion message
        """
        self.operation_complete = True

        if success:
            self.progress_bar.set_fraction(1.0)
            self.progress_bar.set_text("Complete")
            if message:
                self.status_label.set_text(message)
        else:
            self.progress_bar.set_text("Failed")
            if message:
                self.status_label.set_text(message)

        # Change cancel button to close
        self.cancel_button.set_label("Close")
        self.cancel_button.disconnect_by_func(self.on_cancel_clicked)
        self.cancel_button.connect("clicked", lambda b: self.close())
