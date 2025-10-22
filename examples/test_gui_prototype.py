"""
Test script for the GUI prototype functionality without launching the GUI.
This validates the backend functionality works correctly.
"""

import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from unified_theming.core.manager import UnifiedThemeManager


def test_theme_discovery():
    """Test theme discovery functionality."""
    print("Testing theme discovery...")
    manager = UnifiedThemeManager()
    themes = manager.discover_themes()
    print(f"Found {len(themes)} themes:")
    for name in list(themes.keys())[:5]:  # Show first 5 themes
        print(f"  - {name}")
    if len(themes) > 5:
        print(f"  ... and {len(themes) - 5} more")
    return themes


def test_plan_changes(theme_name):
    """Test the plan_changes functionality with a theme."""
    print(f"\nTesting plan_changes for theme '{theme_name}'...")
    manager = UnifiedThemeManager()

    try:
        plan_result = manager.plan_changes(theme_name)
        print(f"Theme: {plan_result.theme_name}")
        print(f"Estimated files affected: {plan_result.estimated_files_affected}")
        print("Handler availability:")
        for handler_name, available in plan_result.available_handlers.items():
            status = "✓ Available" if available else "✗ Not Available"
            print(f"  - {handler_name}: {status}")
        print(f"Number of planned changes: {len(plan_result.planned_changes)}")
        print(f"Number of warnings: {len(plan_result.warnings)}")
        return plan_result
    except Exception as e:
        print(f"Error in plan_changes: {e}")
        return None


if __name__ == "__main__":
    print("Testing GUI prototype backend functionality...\n")

    # Test theme discovery
    themes = test_theme_discovery()

    # Test plan_changes with the first available theme
    if themes:
        first_theme = next(iter(themes))
        plan_result = test_plan_changes(first_theme)
        if plan_result:
            print("\n✅ All backend functionality working correctly!")
        else:
            print("\n❌ Plan changes functionality failed")
            sys.exit(1)
    else:
        print("\n⚠ No themes found to test with")

    print("\n✅ Test completed successfully")
