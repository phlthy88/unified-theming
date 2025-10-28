"""
GUI Launcher with graceful fallback for missing dependencies.

This module provides a safe entry point for the GUI that handles
missing GTK4/PyGObject dependencies gracefully.
"""

import sys
from pathlib import Path


def check_gui_dependencies():
    """
    Check if GUI dependencies are available.

    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gio, GLib, Gtk

        return True, ""
    except ImportError as e:
        if "gi" in str(e):
            return False, "PyGObject (gi) not available"
        else:
            return False, f"GTK4/Libadwaita not available: {e}"
    except Exception as e:
        return False, f"GUI dependency error: {e}"


def show_dependency_help():
    """Show help for installing GUI dependencies."""
    print("Error: GTK4/PyGObject dependencies not available.")
    print()
    print("To use the GUI, install system dependencies:")
    print()
    print("Ubuntu/Debian:")
    print("  sudo apt update")
    print("  sudo apt install -y \\")
    print("    libgtk-4-dev \\")
    print("    libadwaita-1-dev \\")
    print("    libgirepository1.0-dev \\")
    print("    python3-gi \\")
    print("    python3-gi-cairo")
    print("  pip install -e '.[gui]'")
    print()
    print("Fedora/RHEL:")
    print("  sudo dnf install -y \\")
    print("    gtk4-devel \\")
    print("    libadwaita-devel \\")
    print("    gobject-introspection-devel \\")
    print("    python3-gobject \\")
    print("    python3-cairo")
    print("  pip install -e '.[gui]'")
    print()
    print("Arch Linux:")
    print("  sudo pacman -S \\")
    print("    gtk4 \\")
    print("    libadwaita \\")
    print("    gobject-introspection \\")
    print("    python-gobject \\")
    print("    python-cairo")
    print("  pip install -e '.[gui]'")
    print()
    print("Alternative: Use the fully functional CLI:")
    print("  unified-theming list                    # List available themes")
    print("  unified-theming apply_theme <name>      # Apply a theme")
    print("  unified-theming apply_theme <name> --dry-run  # Preview changes")
    print("  unified-theming current                 # Show current theme")
    print("  unified-theming rollback                # Rollback to previous")
    print()


def launch_gui():
    """
    Launch the GUI application with dependency checking.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Check dependencies first
    deps_ok, error_msg = check_gui_dependencies()

    if not deps_ok:
        show_dependency_help()
        return 1

    # Dependencies are available, import and launch GUI
    try:
        from .application import ThemeApp

        app = ThemeApp()
        return app.run(sys.argv)

    except Exception as e:
        print(f"Error starting GUI application: {e}")
        print()
        print("Try using the CLI instead:")
        print("  unified-theming --help")
        return 1


def main():
    """
    Main entry point for GUI launcher.

    Returns:
        int: Exit code
    """
    return launch_gui()


if __name__ == "__main__":
    sys.exit(main())