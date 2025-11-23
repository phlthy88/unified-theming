"""
GUI widgets for Unified Theming Application.

This module contains reusable widget classes for the modern GTK4/Libadwaita interface.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from gi.repository import Adw, Gdk, GLib, Gtk, Pango

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from unified_theming.core.types import ThemeInfo, Toolkit
from unified_theming.utils.logging_config import get_logger

logger = get_logger(__name__)


class ThemePreviewWidget(Gtk.Box):
    """
    Modern widget for previewing theme colors and information.

    Features a clean Adwaita design with color palette display,
    theme metadata, and toolkit compatibility information.
    """

    def __init__(self):
        """Initialize the theme preview widget."""
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.current_theme: Optional[ThemeInfo] = None

        # Build UI
        self.setup_ui()

        logger.info("ThemePreviewWidget initialized")

    def setup_ui(self):
        """Set up the preview widget UI."""
        # Scrolled container
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        # Main content box
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.content_box.set_margin_start(24)
        self.content_box.set_margin_end(24)
        self.content_box.set_margin_top(24)
        self.content_box.set_margin_bottom(24)
        scrolled.set_child(self.content_box)

        # Header section
        self.setup_header_section()

        # Color palette section
        self.setup_color_section()

        # Metadata section
        self.setup_metadata_section()

        # Toolkit compatibility section
        self.setup_toolkit_section()

    def setup_header_section(self):
        """Set up the theme header with name and description."""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.content_box.append(header_box)

        # Theme name
        self.name_label = Gtk.Label.new("Theme Preview")
        self.name_label.set_xalign(0)
        self.name_label.add_css_class("title-1")
        header_box.append(self.name_label)

        # Theme description/subtitle
        self.desc_label = Gtk.Label.new("Select a theme to see its details")
        self.desc_label.set_xalign(0)
        self.desc_label.add_css_class("dim-label")
        self.desc_label.set_wrap(True)
        self.desc_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        header_box.append(self.desc_label)

    def setup_color_section(self):
        """Set up the color palette section."""
        # Color palette group
        self.color_group = Adw.PreferencesGroup.new()
        self.color_group.set_title("Color Palette")
        self.color_group.set_description("Theme color variables")
        self.content_box.append(self.color_group)

        # Color flow box for swatches
        self.color_flow = Gtk.FlowBox()
        self.color_flow.set_max_children_per_line(6)
        self.color_flow.set_min_children_per_line(3)
        self.color_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.color_flow.set_homogeneous(True)
        self.color_flow.set_row_spacing(12)
        self.color_flow.set_column_spacing(12)
        self.color_flow.set_margin_top(12)

        # Wrap in a frame
        color_frame = Gtk.Frame()
        color_frame.set_child(self.color_flow)
        color_frame.add_css_class("view")

        # Add expand row for colors
        self.color_expander = Adw.ExpanderRow.new()
        self.color_expander.set_title("View Color Swatches")
        self.color_expander.set_subtitle("Click to expand")
        self.color_expander.set_expanded(True)
        self.color_expander.add_row(self.create_color_container())
        self.color_group.add(self.color_expander)

    def create_color_container(self) -> Gtk.Widget:
        """Create the container for color swatches."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.append(self.color_flow)
        return box

    def setup_metadata_section(self):
        """Set up the theme metadata section."""
        self.metadata_group = Adw.PreferencesGroup.new()
        self.metadata_group.set_title("Theme Information")
        self.content_box.append(self.metadata_group)

        # Path row
        self.path_row = Adw.ActionRow.new()
        self.path_row.set_title("Location")
        self.path_row.set_subtitle("Unknown")
        self.path_row.add_prefix(Gtk.Image.new_from_icon_name("folder-symbolic"))

        # Copy path button
        copy_btn = Gtk.Button.new_from_icon_name("edit-copy-symbolic")
        copy_btn.set_valign(Gtk.Align.CENTER)
        copy_btn.add_css_class("flat")
        copy_btn.set_tooltip_text("Copy path")
        copy_btn.connect("clicked", self.on_copy_path)
        self.path_row.add_suffix(copy_btn)
        self.metadata_group.add(self.path_row)

        # Author row (if available)
        self.author_row = Adw.ActionRow.new()
        self.author_row.set_title("Author")
        self.author_row.set_subtitle("Unknown")
        self.author_row.add_prefix(
            Gtk.Image.new_from_icon_name("avatar-default-symbolic")
        )
        self.metadata_group.add(self.author_row)

        # Version row
        self.version_row = Adw.ActionRow.new()
        self.version_row.set_title("Version")
        self.version_row.set_subtitle("Unknown")
        self.version_row.add_prefix(
            Gtk.Image.new_from_icon_name("emblem-system-symbolic")
        )
        self.metadata_group.add(self.version_row)

    def setup_toolkit_section(self):
        """Set up the toolkit compatibility section."""
        self.toolkit_group = Adw.PreferencesGroup.new()
        self.toolkit_group.set_title("Toolkit Compatibility")
        self.toolkit_group.set_description("Supported desktop toolkits")
        self.content_box.append(self.toolkit_group)

        # Container for toolkit badges
        self.toolkit_box = Gtk.FlowBox()
        self.toolkit_box.set_max_children_per_line(4)
        self.toolkit_box.set_min_children_per_line(2)
        self.toolkit_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.toolkit_box.set_homogeneous(True)
        self.toolkit_box.set_row_spacing(8)
        self.toolkit_box.set_column_spacing(8)

        toolkit_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        toolkit_container.set_margin_top(12)
        toolkit_container.set_margin_bottom(12)
        toolkit_container.set_margin_start(12)
        toolkit_container.set_margin_end(12)
        toolkit_container.append(self.toolkit_box)

        # Wrap in ActionRow
        toolkit_row = Adw.ActionRow.new()
        toolkit_row.set_title("Supported Toolkits")
        toolkit_row.add_suffix(toolkit_container)
        toolkit_row.set_activatable(False)
        self.toolkit_group.add(toolkit_row)

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
        """Show placeholder when no theme is selected."""
        self.name_label.set_text("No Theme Selected")
        self.desc_label.set_text("Select a theme from the sidebar to preview")
        self.clear_colors()
        self.path_row.set_subtitle("—")
        self.author_row.set_subtitle("—")
        self.version_row.set_subtitle("—")
        self.clear_toolkits()

    def show_theme(self, theme_info: ThemeInfo):
        """Display theme information and colors."""
        # Header
        self.name_label.set_text(theme_info.name or "Unnamed Theme")

        # Description from metadata
        desc = theme_info.metadata.get("Comment", "")
        if not desc:
            toolkit_count = len(theme_info.supported_toolkits)
            desc = (
                f"Supports {toolkit_count} toolkit{'s' if toolkit_count != 1 else ''}"
            )
        self.desc_label.set_text(desc)

        # Colors
        self.update_colors(theme_info.colors)

        # Metadata
        self.path_row.set_subtitle(str(theme_info.path))

        author = theme_info.metadata.get("Author", "Unknown")
        self.author_row.set_subtitle(author)

        version = theme_info.metadata.get("Version", "—")
        self.version_row.set_subtitle(version)

        # Toolkits
        self.update_toolkits(theme_info.supported_toolkits)

    def update_colors(self, colors: Dict[str, str]):
        """Update the color swatches."""
        self.clear_colors()

        if not colors:
            # Add placeholder
            placeholder = Gtk.Label.new("No colors extracted")
            placeholder.add_css_class("dim-label")
            placeholder.set_margin_top(24)
            placeholder.set_margin_bottom(24)
            self.color_flow.append(placeholder)
            self.color_expander.set_subtitle("No colors available")
            return

        # Add color swatches (show all, up to 24)
        for name, hex_color in list(colors.items())[:24]:
            swatch = ColorSwatch(name, hex_color)
            self.color_flow.append(swatch)

        count = len(colors)
        if count > 24:
            self.color_expander.set_subtitle(f"Showing 24 of {count} colors")
        else:
            self.color_expander.set_subtitle(f"{count} colors")

    def clear_colors(self):
        """Clear all color swatches."""
        while True:
            child = self.color_flow.get_first_child()
            if child is None:
                break
            self.color_flow.remove(child)

    def update_toolkits(self, toolkits: List[Toolkit]):
        """Update the toolkit badges."""
        self.clear_toolkits()

        for toolkit in toolkits:
            badge = ToolkitBadge(toolkit)
            self.toolkit_box.append(badge)

    def clear_toolkits(self):
        """Clear all toolkit badges."""
        while True:
            child = self.toolkit_box.get_first_child()
            if child is None:
                break
            self.toolkit_box.remove(child)

    def on_copy_path(self, button):
        """Copy theme path to clipboard."""
        if self.current_theme:
            clipboard = Gdk.Display.get_default().get_clipboard()
            clipboard.set(str(self.current_theme.path))

            # Show feedback via tooltip
            button.set_tooltip_text("Copied!")
            GLib.timeout_add(1500, lambda: button.set_tooltip_text("Copy path"))


class ColorSwatch(Gtk.Box):
    """
    Modern widget displaying a color swatch with name and hex value.

    Features rounded corners, hover effects, and copy-on-click.
    """

    def __init__(self, name: str, hex_color: str):
        """
        Initialize the color swatch.

        Args:
            name: Color variable name
            hex_color: Hex color value
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.name = name
        self.hex_color = self.normalize_hex(hex_color)

        self.set_margin_start(4)
        self.set_margin_end(4)
        self.set_margin_top(4)
        self.set_margin_bottom(4)

        self.setup_ui()

    def normalize_hex(self, color: str) -> str:
        """Normalize color to hex format."""
        color = color.strip()
        if not color.startswith("#"):
            # Try to parse rgb() format
            if color.startswith("rgb"):
                try:
                    parts = color.replace("rgb(", "").replace("rgba(", "")
                    parts = parts.replace(")", "").split(",")
                    r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"#{r:02x}{g:02x}{b:02x}"
                except (ValueError, IndexError):
                    return "#808080"
            return "#808080"
        return color

    def setup_ui(self):
        """Set up the swatch UI."""
        # Color square with rounded corners
        self.color_area = Gtk.DrawingArea()
        self.color_area.set_size_request(56, 56)
        self.color_area.set_draw_func(self.draw_color)
        self.color_area.add_css_class("color-swatch")

        # Make clickable for copying
        click_controller = Gtk.GestureClick.new()
        click_controller.connect("pressed", self.on_click)
        self.color_area.add_controller(click_controller)

        # Tooltip with full info
        self.color_area.set_tooltip_text(
            f"{self.name}\n{self.hex_color.upper()}\nClick to copy"
        )

        self.append(self.color_area)

        # Color name (truncated)
        name_label = Gtk.Label.new(self.get_short_name())
        name_label.set_max_width_chars(10)
        name_label.set_ellipsize(Pango.EllipsizeMode.END)
        name_label.add_css_class("caption")
        name_label.add_css_class("dim-label")
        self.append(name_label)

    def get_short_name(self) -> str:
        """Get shortened color name."""
        name = self.name
        # Remove common prefixes
        for prefix in ["theme_", "gtk_", "@", "$"]:
            if name.startswith(prefix):
                name = name[len(prefix) :]
        return name[:12]

    def draw_color(self, area, cr, width, height):
        """Draw the color square with rounded corners."""
        try:
            hex_color = self.hex_color
            if hex_color.startswith("#"):
                hex_color = hex_color[1:]

            if len(hex_color) >= 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
            else:
                r = g = b = 0.5

            # Draw rounded rectangle
            radius = 8
            degrees = 3.14159 / 180.0

            cr.new_sub_path()
            cr.arc(width - radius, radius, radius, -90 * degrees, 0 * degrees)
            cr.arc(width - radius, height - radius, radius, 0 * degrees, 90 * degrees)
            cr.arc(radius, height - radius, radius, 90 * degrees, 180 * degrees)
            cr.arc(radius, radius, radius, 180 * degrees, 270 * degrees)
            cr.close_path()

            cr.set_source_rgb(r, g, b)
            cr.fill_preserve()

            # Border
            cr.set_source_rgba(0, 0, 0, 0.1)
            cr.set_line_width(1)
            cr.stroke()

        except (ValueError, IndexError):
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.rectangle(0, 0, width, height)
            cr.fill()

    def on_click(self, gesture, n_press, x, y):
        """Handle click to copy color."""
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(self.hex_color.upper())
        self.color_area.set_tooltip_text(f"Copied {self.hex_color.upper()}!")
        GLib.timeout_add(
            1500,
            lambda: self.color_area.set_tooltip_text(
                f"{self.name}\n{self.hex_color.upper()}\nClick to copy"
            ),
        )


class ToolkitBadge(Gtk.Box):
    """
    Badge widget showing toolkit support status.

    Displays toolkit name with appropriate icon and styling.
    """

    TOOLKIT_INFO = {
        "gtk2": ("GTK 2", "applications-graphics-symbolic", "#8b5cf6"),
        "gtk3": ("GTK 3", "preferences-desktop-appearance-symbolic", "#06b6d4"),
        "gtk4": ("GTK 4", "preferences-desktop-appearance-symbolic", "#3b82f6"),
        "libadwaita": (
            "Libadwaita",
            "preferences-desktop-appearance-symbolic",
            "#6366f1",
        ),
        "qt5": ("Qt 5", "preferences-desktop-theme-symbolic", "#22c55e"),
        "qt6": ("Qt 6", "preferences-desktop-theme-symbolic", "#10b981"),
        "flatpak": ("Flatpak", "package-x-generic-symbolic", "#f59e0b"),
        "snap": ("Snap", "package-x-generic-symbolic", "#ef4444"),
    }

    def __init__(self, toolkit: Toolkit):
        """Initialize the toolkit badge."""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.toolkit = toolkit
        info = self.TOOLKIT_INFO.get(
            toolkit.value,
            (toolkit.value, "application-x-executable-symbolic", "#6b7280"),
        )

        self.add_css_class("card")
        self.set_margin_start(4)
        self.set_margin_end(4)
        self.set_margin_top(4)
        self.set_margin_bottom(4)

        # Content box
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(8)
        content.set_margin_bottom(8)

        # Icon
        icon = Gtk.Image.new_from_icon_name(info[1])
        icon.set_pixel_size(16)
        content.append(icon)

        # Name
        label = Gtk.Label.new(info[0])
        label.add_css_class("heading")
        content.append(label)

        # Check mark
        check = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        check.set_pixel_size(16)
        check.add_css_class("success")
        content.append(check)

        self.append(content)


class ProgressDialog(Adw.Window):
    """
    Modern modal dialog showing operation progress.

    Features a progress bar, status message, and cancel functionality.
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
        self.set_default_size(400, 200)
        self.set_resizable(False)
        self.set_deletable(False)

        self.operation_complete = False
        self.setup_ui(title)

    def setup_ui(self, title: str):
        """Set up the dialog UI."""
        # Main box with toolbar view
        toolbar_view = Adw.ToolbarView.new()

        # Header
        header = Adw.HeaderBar.new()
        header.add_css_class("flat")
        toolbar_view.add_top_bar(header)

        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_valign(Gtk.Align.CENTER)

        # Icon and title
        icon = Gtk.Image.new_from_icon_name("preferences-desktop-appearance-symbolic")
        icon.set_pixel_size(48)
        content.append(icon)

        title_label = Gtk.Label.new(title)
        title_label.add_css_class("title-2")
        content.append(title_label)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Starting...")
        self.progress_bar.add_css_class("osd")
        content.append(self.progress_bar)

        # Status label
        self.status_label = Gtk.Label.new("Preparing operation...")
        self.status_label.add_css_class("dim-label")
        content.append(self.status_label)

        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(12)

        self.cancel_button = Gtk.Button.new_with_label("Cancel")
        self.cancel_button.add_css_class("pill")
        self.cancel_button.connect("clicked", self.on_cancel_clicked)
        button_box.append(self.cancel_button)

        content.append(button_box)
        toolbar_view.set_content(content)

        self.set_content(toolbar_view)

    def update_progress(
        self, fraction: float, text: Optional[str] = None, status: Optional[str] = None
    ):
        """Update progress display."""
        self.progress_bar.set_fraction(fraction)
        if text:
            self.progress_bar.set_text(text)
        if status:
            self.status_label.set_text(status)

    def on_cancel_clicked(self, button):
        """Called when cancel button is clicked."""
        self.close()

    def complete(self, success: bool = True, message: Optional[str] = None):
        """Mark operation as complete."""
        self.operation_complete = True
        self.set_deletable(True)

        if success:
            self.progress_bar.set_fraction(1.0)
            self.progress_bar.set_text("Complete")
            if message:
                self.status_label.set_text(message)
            else:
                self.status_label.set_text("Operation completed successfully")
        else:
            self.progress_bar.add_css_class("error")
            self.progress_bar.set_text("Failed")
            if message:
                self.status_label.set_text(message)

        self.cancel_button.set_label("Close")
        self.cancel_button.add_css_class("suggested-action")

        # Auto-close on success after delay
        if success:
            GLib.timeout_add(1500, self.close)


# Legacy compatibility exports
class ThemeListBox(Gtk.ListBox):
    """Legacy theme list box - use MainWindow's built-in list instead."""

    def __init__(self):
        super().__init__()
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.themes: Dict[str, ThemeInfo] = {}
        self.theme_rows: Dict[str, Gtk.ListBoxRow] = {}

    def set_themes(self, themes: Dict[str, ThemeInfo]):
        """Update themes."""
        self.themes = themes

    def clear_themes(self):
        """Clear themes."""
        self.themes.clear()


class ThemeListRow(Gtk.ListBoxRow):
    """Legacy theme list row."""

    def __init__(self, theme_name: str, theme_info: ThemeInfo):
        super().__init__()
        self.theme_name = theme_name
        self.theme_info = theme_info
