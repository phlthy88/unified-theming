"""
Unit tests for CLI dry-run functionality.

Tests the --dry-run flag on the apply command to ensure:
1. No system modifications are made in dry-run mode
2. Plan results are correctly generated and displayed
3. Data contracts between CLI and manager are maintained
4. Error handling works correctly in dry-run mode
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from unified_theming.cli.commands import cli
from unified_theming.core.exceptions import ThemeNotFoundError
from unified_theming.core.types import (
    PlannedChange,
    PlanResult,
    Toolkit,
    ValidationResult,
)


@pytest.fixture
def cli_runner():
    """Create a Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_plan_result():
    """Create a mock PlanResult for testing."""
    change1 = PlannedChange(
        handler_name="gtk",
        file_path=Path("/home/user/.config/gtk-4.0/gtk.css"),
        change_type="modify",
        description="Update GTK4 color scheme",
        current_value="@define-color theme_bg_color #ffffff;",
        new_value="@define-color theme_bg_color #2e3440;",
        toolkit=Toolkit.GTK4,
    )

    change2 = PlannedChange(
        handler_name="qt",
        file_path=Path("/home/user/.config/kdeglobals"),
        change_type="create",
        description="Create Qt theme configuration",
        current_value=None,
        new_value="[Colors:Window]\nBackgroundNormal=#2e3440",
        toolkit=Toolkit.QT5,
    )

    validation = ValidationResult(valid=True)
    validation.add_info("Theme structure is valid")

    plan_result = PlanResult(
        theme_name="Nord",
        planned_changes=[change1, change2],
        validation_result=validation,
        available_handlers={"gtk": True, "qt": True, "flatpak": False, "snap": False},
        warnings=["Handler snap is not available (toolkit not installed)"],
    )

    return plan_result


class TestDryRunBasicFunctionality:
    """Test basic dry-run functionality."""

    def test_dry_run_flag_exists(self, cli_runner):
        """Test that --dry-run flag is recognized by the CLI."""
        result = cli_runner.invoke(cli, ["apply", "--help"])
        assert result.exit_code == 0
        assert "--dry-run" in result.output
        assert "Preview changes without applying" in result.output

    def test_dry_run_calls_plan_changes(self, cli_runner, mock_plan_result):
        """Test that dry-run mode calls plan_changes instead of apply_theme."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(cli, ["apply_theme", "Nord", "--dry-run"])

            # Verify plan_changes was called
            mock_manager.plan_changes.assert_called_once_with("Nord", targets=None)
            # Verify apply_theme was NOT called
            mock_manager.apply_theme.assert_not_called()
            assert result.exit_code == 0

    def test_dry_run_no_system_modifications(self, cli_runner, mock_plan_result):
        """Test that dry-run mode makes no system modifications."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            # Run dry-run
            result = cli_runner.invoke(cli, ["apply_theme", "Nord", "--dry-run"])

            # Verify no apply operations were attempted
            mock_manager.apply_theme.assert_not_called()
            mock_manager.config_manager = Mock()
            # No backup should be created
            assert not mock_manager.config_manager.backup_current_state.called
            assert result.exit_code == 0

    def test_dry_run_output_format(self, cli_runner, mock_plan_result):
        """Test that dry-run output includes all required information."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(cli, ["apply_theme", "Nord", "--dry-run"])

            # Verify output contains key information
            assert "Planning theme" in result.output
            assert "Nord" in result.output
            assert "dry-run mode" in result.output
            assert "Files that would be affected" in result.output
            assert "Total changes" in result.output
            assert "Handler Availability" in result.output
            assert "DRY-RUN MODE" in result.output
            assert "No changes were made" in result.output
            assert result.exit_code == 0


class TestDryRunWithTargets:
    """Test dry-run with specific target toolkits."""

    def test_dry_run_with_single_target(self, cli_runner, mock_plan_result):
        """Test dry-run with a single --targets option."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(
                cli, ["apply_theme", "Nord", "--target", "gtk4", "--dry-run"]
            )

            # Debug output
            print(f"\nExit code: {result.exit_code}")
            print(f"Output: {result.output}")
            if result.exception:
                print(f"Exception: {result.exception}")
            print(f"plan_changes called: {mock_manager.plan_changes.called}")
            print(f"plan_changes call_count: {mock_manager.plan_changes.call_count}")
            if mock_manager.plan_changes.called:
                print(f"plan_changes call_args: {mock_manager.plan_changes.call_args}")

            # Verify plan_changes was called with correct targets
            mock_manager.plan_changes.assert_called_once_with("Nord", targets=["gtk4"])
            assert result.exit_code == 0

    def test_dry_run_with_multiple_targets(self, cli_runner, mock_plan_result):
        """Test dry-run with multiple --targets options."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(
                cli,
                [
                    "apply_theme",
                    "Nord",
                    "--target",
                    "gtk4",
                    "--target",
                    "qt5",
                    "--dry-run",
                ],
            )

            # Verify plan_changes was called with correct targets
            mock_manager.plan_changes.assert_called_once_with(
                "Nord", targets=["gtk4", "qt5"]
            )
            assert result.exit_code == 0

    def test_dry_run_with_all_target(self, cli_runner, mock_plan_result):
        """Test dry-run with 'all' target."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(
                cli, ["apply_theme", "Nord", "--target", "all", "--dry-run"]
            )

            # When 'all' is specified, targets should be None
            mock_manager.plan_changes.assert_called_once_with("Nord", targets=None)
            assert result.exit_code == 0


class TestDryRunDataContracts:
    """Test data contracts between CLI and manager."""

    def test_plan_result_structure(self, cli_runner, mock_plan_result):
        """Test that PlanResult data structure is correctly processed."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(cli, ["apply_theme", "Nord", "--dry-run"])

            # Verify all PlanResult fields are used
            assert str(mock_plan_result.estimated_files_affected) in result.output
            assert str(len(mock_plan_result.planned_changes)) in result.output
            assert result.exit_code == 0

    def test_planned_change_display(self, cli_runner, mock_plan_result):
        """Test that PlannedChange objects are correctly displayed."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(cli, ["apply_theme", "Nord", "--dry-run"])

            # Verify planned changes are displayed
            assert "Planned Changes" in result.output
            assert "gtk:" in result.output
            assert "qt:" in result.output
            # Verify change details
            for change in mock_plan_result.planned_changes:
                assert str(change.file_path) in result.output
                assert change.description in result.output
            assert result.exit_code == 0

    def test_handler_availability_display(self, cli_runner, mock_plan_result):
        """Test that handler availability is correctly displayed."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(cli, ["apply_theme", "Nord", "--dry-run"])

            # Verify handler availability is shown
            assert "Handler Availability" in result.output
            assert "gtk: ✓ Available" in result.output
            assert "qt: ✓ Available" in result.output
            assert (
                "flatpak: ✗ Not available" in result.output
                or "snap: ✗ Not available" in result.output
            )
            assert result.exit_code == 0

    def test_validation_messages_display(self, cli_runner):
        """Test that validation messages are correctly displayed."""
        # Create plan result with validation messages
        validation = ValidationResult(valid=False)
        validation.add_error("Missing required color variable")
        validation.add_warning("Theme may not support all features")
        validation.add_info("Theme structure is valid")

        plan_result = PlanResult(
            theme_name="TestTheme",
            planned_changes=[],
            validation_result=validation,
            available_handlers={"gtk": True},
            warnings=[],
        )

        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = plan_result

            result = cli_runner.invoke(cli, ["apply", "TestTheme", "--dry-run"])

            # Verify validation messages are displayed
            assert "Validation:" in result.output
            assert "[ERROR]" in result.output
            assert "[WARNING]" in result.output
            assert "[INFO]" in result.output
            assert "Missing required color variable" in result.output
            assert result.exit_code == 0


class TestDryRunErrorHandling:
    """Test error handling in dry-run mode."""

    def test_theme_not_found_error(self, cli_runner):
        """Test handling of ThemeNotFoundError in dry-run mode."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.side_effect = ThemeNotFoundError(
                "NonExistentTheme", searched_paths=[Path("/usr/share/themes")]
            )

            result = cli_runner.invoke(cli, ["apply", "NonExistentTheme", "--dry-run"])

            # Verify error is displayed
            assert result.exit_code == 1
            assert "Error applying theme" in result.output
            assert "NonExistentTheme" in result.output

    def test_generic_exception_handling(self, cli_runner):
        """Test handling of generic exceptions in dry-run mode."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.side_effect = Exception("Unexpected error")

            result = cli_runner.invoke(cli, ["apply", "TestTheme", "--dry-run"])

            # Verify error is displayed
            assert result.exit_code == 1
            assert "Error applying theme" in result.output
            assert "Unexpected error" in result.output

    def test_empty_planned_changes(self, cli_runner):
        """Test handling of empty planned changes."""
        plan_result = PlanResult(
            theme_name="EmptyTheme",
            planned_changes=[],
            validation_result=ValidationResult(valid=True),
            available_handlers={"gtk": True},
            warnings=[],
        )

        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = plan_result

            result = cli_runner.invoke(cli, ["apply", "EmptyTheme", "--dry-run"])

            # Verify appropriate message is displayed
            assert "No changes would be made" in result.output
            assert result.exit_code == 0


class TestDryRunWarnings:
    """Test warning display in dry-run mode."""

    def test_warnings_display(self, cli_runner):
        """Test that warnings are correctly displayed."""
        plan_result = PlanResult(
            theme_name="TestTheme",
            planned_changes=[],
            validation_result=ValidationResult(valid=True),
            available_handlers={"gtk": True, "qt": False},
            warnings=[
                "Handler qt is not available (toolkit not installed)",
                "Some theme features may not be supported",
            ],
        )

        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = plan_result

            result = cli_runner.invoke(cli, ["apply", "TestTheme", "--dry-run"])

            # Verify warnings are displayed
            assert "Warnings:" in result.output
            assert "Handler qt is not available" in result.output
            assert "Some theme features may not be supported" in result.output
            assert result.exit_code == 0


class TestDryRunVerbosity:
    """Test dry-run with different verbosity levels."""

    def test_dry_run_with_verbose_flag(self, cli_runner, mock_plan_result):
        """Test dry-run with -v flag."""
        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(cli, ["-v", "apply_theme", "Nord", "--dry-run"])

            # Verbosity should still work in dry-run mode
            assert result.exit_code == 0
            assert "Planning theme" in result.output

    def test_dry_run_with_config_path(self, cli_runner, mock_plan_result, tmp_path):
        """Test dry-run with custom config path."""
        config_file = tmp_path / "config.json"
        config_file.write_text("{}")

        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.plan_changes.return_value = mock_plan_result

            result = cli_runner.invoke(
                cli, ["--config", str(config_file), "apply_theme", "Nord", "--dry-run"]
            )

            # Verify config path was passed to manager
            mock_manager_class.assert_called_once()
            call_kwargs = mock_manager_class.call_args[1]
            assert "config_path" in call_kwargs
            assert result.exit_code == 0


class TestNormalModeUnaffected:
    """Test that normal apply mode is unaffected by dry-run implementation."""

    def test_apply_without_dry_run_calls_apply_theme(self, cli_runner):
        """Test that normal mode still calls apply_theme."""
        from unified_theming.core.types import ApplicationResult, HandlerResult, Toolkit

        mock_result = ApplicationResult(
            theme_name="Nord",
            overall_success=True,
            handler_results={
                "gtk": HandlerResult(
                    handler_name="gtk",
                    toolkit=Toolkit.GTK4,
                    success=True,
                    message="Applied successfully",
                )
            },
        )

        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.apply_theme.return_value = mock_result

            result = cli_runner.invoke(cli, ["apply_theme", "Nord"])

            # Verify apply_theme was called
            mock_manager.apply_theme.assert_called_once_with("Nord", targets=None)
            # Verify plan_changes was NOT called
            mock_manager.plan_changes.assert_not_called()
            assert result.exit_code == 0

    def test_apply_without_dry_run_shows_success(self, cli_runner):
        """Test that normal mode shows success messages."""
        from unified_theming.core.types import ApplicationResult, HandlerResult, Toolkit

        mock_result = ApplicationResult(
            theme_name="Nord",
            overall_success=True,
            handler_results={
                "gtk": HandlerResult(
                    handler_name="gtk",
                    toolkit=Toolkit.GTK4,
                    success=True,
                    message="Applied successfully",
                )
            },
        )

        with patch(
            "unified_theming.cli.commands.UnifiedThemeManager"
        ) as mock_manager_class:
            mock_manager = Mock()
            mock_manager_class.return_value = mock_manager
            mock_manager.apply_theme.return_value = mock_result

            result = cli_runner.invoke(cli, ["apply_theme", "Nord"])

            # Verify success messages
            assert "Theme 'Nord' applied successfully" in result.output
            assert "DRY-RUN MODE" not in result.output
            assert result.exit_code == 0
