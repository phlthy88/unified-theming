"""
Tests for example files and GUI prototype validation.
"""

import pytest
import subprocess
import sys
from pathlib import Path


def test_gui_prototype_syntax():
    """Validate GUI prototype has correct Python syntax."""
    gui_path = Path(__file__).parent.parent / "examples" / "gui_prototype.py"
    result = subprocess.run([sys.executable, "-m", "py_compile", str(gui_path)])
    assert result.returncode == 0, f"Syntax error in {gui_path}"


def test_gui_prototype_imports():
    """Validate GUI prototype can import project modules."""
    # Temporarily add project root to path
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Import and validate
    import unified_theming.core.manager
    from unified_theming.core.types import PlanResult  # type: ignore
    assert hasattr(unified_theming.core.manager.UnifiedThemeManager, 'plan_changes')


def test_gui_prototype_structure():
    """Validate GUI prototype has expected structure."""
    from pathlib import Path
    gui_path = Path(__file__).parent.parent / "examples" / "gui_prototype.py"

    # Read the file and check for expected content
    content = gui_path.read_text()

    # Check for developer notes
    assert "DEVELOPER NOTES FOR AGENT 3" in content

    # Check for required imports
    assert "import gi" in content
    assert 'gi.require_version("Gtk", "4.0")' in content or "gi.require_version('Gtk', '4.0')" in content
    assert 'gi.require_version("Adw", "1")' in content or "gi.require_version('Adw', '1')" in content

    # Check for class definition
    assert "class ThemeAppPrototype(Adw.Application):" in content

    # Check for required methods
    assert "def on_activate" in content
    assert "def load_themes" in content
    assert "def run_cli_command" in content


def test_gui_prototype_dependencies_documented():
    """Validate that GUI dependencies are properly documented."""
    from pathlib import Path
    gui_path = Path(__file__).parent.parent / "examples" / "gui_prototype.py"

    content = gui_path.read_text()

    # Check for dependency documentation in developer notes
    assert "Dependencies: Requires Python 3.10+, GTK 4.10+, Libadwaita 1.0+, PyGObject" in content
    assert "Install PyGObject with: pip install PyGObject" in content


def test_gui_prototype_cli_path_handling():
    """Validate GUI prototype handles CLI path correctly."""
    from pathlib import Path
    gui_path = Path(__file__).parent.parent / "examples" / "gui_prototype.py"

    content = gui_path.read_text()

    # Check for CLI path handling
    assert "self.cli_path" in content
    assert "cmd = [self.cli_path] + command_args" in content


def test_gui_prototype_threading():
    """Validate GUI prototype uses proper threading."""
    from pathlib import Path
    gui_path = Path(__file__).parent.parent / "examples" / "gui_prototype.py"

    content = gui_path.read_text()

    # Check for threading usage
    assert "import threading" in content
    assert "threading.Thread" in content
    assert "daemon=True" in content
    assert "GLib.idle_add" in content


def test_gui_prototype_error_handling():
    """Validate GUI prototype has error handling."""
    from pathlib import Path
    gui_path = Path(__file__).parent.parent / "examples" / "gui_prototype.py"

    content = gui_path.read_text()

    # Check for error handling patterns
    assert "try:" in content
    assert "except" in content
    assert "Error loading themes" in content
    assert "Command failed with exit code" in content