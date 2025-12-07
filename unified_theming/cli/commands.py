"""
Command-line interface for Unified Theming Application.

This module implements the CLI using Click framework, providing
a user-friendly command-line interface for all core operations.
"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click

from unified_theming.core.manager import UnifiedThemeManager
from unified_theming.core.types import Toolkit


def map_toolkits_to_handlers(targets: Tuple[str, ...]) -> tuple[List[str], List[str]]:
    """
    Map toolkit names to handler names.

    Args:
        targets: Tuple of toolkit names from CLI

    Returns:
        Tuple of (handler_names, unknown_targets)
    """
    handler_mapping = {
        "gtk2": "gtk",
        "gtk3": "gtk",
        "gtk4": "gtk",
        "libadwaita": "gtk",
        "qt5": "qt",
        "qt6": "qt",
        "flatpak": "flatpak",
        "snap": "snap",
    }

    handlers = set()
    unknown_targets = []
    for target in targets:
        if target == "all":
            return (["gtk", "qt", "flatpak", "snap"], [])
        elif target in handler_mapping:
            handlers.add(handler_mapping[target])
        else:
            unknown_targets.append(target)

    return ([*handlers], unknown_targets)


# Version information
__version__ = "1.0.0"


# ============================================================================
# Main CLI Group
# ============================================================================


@click.group()
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (can be used multiple times: -v, -vv, -vvv)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option("--no-color", is_flag=True, help="Disable colored output")
@click.version_option(version=__version__, prog_name="unified-theming")
@click.pass_context
def cli(ctx, verbose: int, config: Optional[Path], no_color: bool):
    """
    Unified Theming Application - Apply themes across toolkits.

    This tool helps you apply consistent themes across GTK, Qt,
    and containerized applications on Linux.

    \b
    Examples:
        unified-theming list
        unified-theming apply_theme Nord
        unified-theming apply_theme --from-tokens tokens.json
        unified-theming current
        unified-theming convert Adwaita-dark --output tokens.json
        unified-theming render tokens.json --target gtk --output ./out
        unified-theming rollback

    For more information, visit: https://github.com/yourusername/unified-theming
    """
    # Initialize context object
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config
    ctx.obj["no_color"] = no_color


# ============================================================================
# List Command
# ============================================================================


@cli.command()
@click.option(
    "--targets", multiple=True, type=str, help="Target toolkits (default: all)"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "list", "json"], case_sensitive=False),
    default="table",
    help="Output format (default: table)",
)
@click.pass_context
def list(ctx, targets: Tuple[str, ...], format: str):
    """
    List all available themes.

    \b
    Examples:
        unified-theming list
        unified-theming list --targets gtk4
        unified-theming list --format json
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get("config"))
        themes = manager.discover_themes()

        if targets:
            # Filter themes by toolkit support
            filtered_themes = {
                name: info
                for name, info in themes.items()
                if any(Toolkit[tk.upper()] in info.supported_toolkits for tk in targets)
            }
        else:
            filtered_themes = themes

        if not filtered_themes:
            click.echo("No themes found")
            return

        if format == "table":
            # Print table format
            click.echo(f"{'Theme Name':<30} {'Toolkits':<40}")
            click.echo("-" * 70)
            for name, info in sorted(filtered_themes.items()):
                toolkits = ", ".join(t.value for t in info.supported_toolkits)
                click.echo(f"{name:<30} {toolkits:<40}")

        elif format == "list":
            # Print simple list
            for name in sorted(filtered_themes.keys()):
                click.echo(name)

        elif format == "json":
            # Print JSON format
            import json

            output = {
                name: {
                    "path": str(info.path),
                    "toolkits": [t.value for t in info.supported_toolkits],
                    "colors": len(info.colors),
                }
                for name, info in filtered_themes.items()
            }
            click.echo(json.dumps(output, indent=2))

    except Exception as e:
        click.secho(f"Error listing themes: {e}", fg="red", err=True)
        sys.exit(1)


# ============================================================================
# Apply Command (main command that was problematic)
# ============================================================================


@cli.command(name="apply_theme")
@click.argument("theme_name", required=False)
@click.option(
    "--targets",
    multiple=True,
    type=click.Choice(
        ["gtk2", "gtk3", "gtk4", "libadwaita", "qt5", "qt6", "flatpak", "snap", "all"],
        case_sensitive=False,
    ),
    help="Target toolkits (default: all)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without applying them (safe, non-destructive)",
)
@click.option(
    "--from-tokens",
    "token_file",
    type=click.Path(exists=True, path_type=Path),
    help="Apply configuration from a JSON token file instead of a discovered theme",
)
@click.pass_context
def apply(
    ctx, theme_name: Optional[str], targets: Tuple[str, ...], dry_run: bool, token_file
):
    """
    Apply THEME_NAME to specified targets.

    \b
    Examples:
        unified-theming apply_theme Nord
        unified-theming apply_theme Nord --dry-run
        unified-theming apply_theme Dracula --targets gtk4 --targets libadwaita
        unified-theming apply_theme --from-tokens tokens.json
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get("config"))

        # Map targets to handler names
        if not targets:
            target_list = None  # None means all available toolkits
        else:
            mapped_handlers, unknown_targets = map_toolkits_to_handlers(targets)
            if unknown_targets:
                click.secho(
                    f"Warning: Unknown targets {', '.join(unknown_targets)}, ignoring",
                    fg="yellow",
                    err=True,
                )
            if not mapped_handlers:
                target_list = None  # No valid targets, apply to all
            else:
                target_list = mapped_handlers

        # Token-based application path
        if token_file:
            if dry_run:
                click.secho(
                    "Dry-run is not supported with --from-tokens; applying directly.",
                    fg="yellow",
                )
            click.echo(f"Applying tokens from '{token_file}'...")
            result = manager.apply_theme_from_tokens(token_file, targets=target_list)
            theme_label = result.theme_name
        else:
            if not theme_name:
                click.secho(
                    "Please provide THEME_NAME or --from-tokens PATH",
                    fg="red",
                    err=True,
                )
                sys.exit(2)

            # Dry-run mode: preview changes without applying
            if dry_run:
                click.secho(
                    f"Planning theme '{theme_name}' (dry-run mode)...", fg="cyan"
                )
                plan_result = manager.plan_changes(theme_name, targets=target_list)

                # Display plan summary
                click.secho(
                    f"\n✓ Planning complete for theme '{theme_name}'", fg="green"
                )
                click.echo(
                    f"  Files that would be affected: {plan_result.estimated_files_affected}"
                )
                click.echo(f"  Total changes: {len(plan_result.planned_changes)}")

                # Show handler availability
                click.echo("\nHandler Availability:")
                for handler_name, available in plan_result.available_handlers.items():
                    status = "✓ Available" if available else "✗ Not available"
                    color = "green" if available else "yellow"
                    click.secho(f"  {handler_name}: {status}", fg=color)

                # Show validation results
                if (
                    plan_result.validation_result
                    and plan_result.validation_result.messages
                ):
                    click.echo("\nValidation:")
                    for msg in plan_result.validation_result.messages:
                        color = {
                            "ERROR": "red",
                            "WARNING": "yellow",
                            "INFO": "blue",
                        }.get(msg.level.value.upper(), "white")
                        click.secho(
                            f"  [{msg.level.value.upper()}] {msg.message}", fg=color
                        )

                # Show planned changes by handler
                if plan_result.planned_changes:
                    click.echo("\nPlanned Changes:")
                    for handler_name in plan_result.available_handlers.keys():
                        handler_changes = plan_result.get_changes_by_handler(
                            handler_name
                        )
                        if handler_changes:
                            click.echo(f"\n  {handler_name}:")
                            for change in handler_changes:
                                click.echo(
                                    f"    {change.change_type.upper()}: {change.file_path}"
                                )
                                click.echo(f"      {change.description}")
                else:
                    click.echo("\nNo changes would be made.")

                # Show warnings
                if plan_result.warnings:
                    click.echo("\nWarnings:")
                    for warning in plan_result.warnings:
                        click.secho(f"  ⚠ {warning}", fg="yellow")

                click.echo("\n" + "=" * 70)
                click.secho(
                    "DRY-RUN MODE: No changes were made to your system.",
                    fg="cyan",
                    bold=True,
                )
                click.echo("Run without --dry-run to apply these changes.")
                return

            # Apply theme (actual mode)
            click.echo(f"Applying theme '{theme_name}'...")
            result = manager.apply_theme(theme_name, targets=target_list)
            theme_label = theme_name

        # Display results for both token and theme paths
        if result.overall_success:
            click.secho(f"✓ Theme '{theme_label}' applied successfully!", fg="green")
        else:
            click.secho(f"⚠ Theme applied with warnings", fg="yellow")

        # Show per-handler results
        for handler_name, handler_result in result.handler_results.items():
            if handler_result.success:
                click.echo(f"  ✓ {handler_name}: {handler_result.message}")
            else:
                click.echo(f"  ✗ {handler_name}: {handler_result.message}", err=True)

        # Show warnings if any
        warnings = result.get_all_warnings()
        if warnings:
            click.echo("\nWarnings:")
            for warning in warnings:
                click.secho(f"  ⚠ {warning}", fg="yellow")

    except Exception as e:
        click.secho(f"✗ Error applying theme: {e}", fg="red", err=True)
        sys.exit(1)


# ============================================================================
# Convert Command
# ============================================================================


@cli.command()
@click.argument("theme_name")
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(path_type=Path),
    help="Path to write JSON token output",
)
@click.pass_context
def convert(ctx, theme_name: str, output: Path):
    """
    Convert THEME_NAME into a JSON token file.

    \b
    Examples:
        unified-theming convert Adwaita-dark --output tokens.json
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get("config"))
        tokens = manager.convert_theme_to_tokens(theme_name)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(manager.tokens_to_json(tokens))
        click.secho(f"✓ Tokens for '{theme_name}' written to {output}", fg="green")
    except Exception as e:
        click.secho(f"✗ Error converting theme: {e}", fg="red", err=True)
        sys.exit(1)


# ============================================================================
# Render Command
# ============================================================================


@cli.command()
@click.argument("token_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--target",
    required=True,
    type=click.Choice(["gtk", "qt", "gnome-shell"], case_sensitive=False),
    help="Target toolkit to render for",
)
@click.option(
    "--output",
    "-o",
    default=Path.cwd(),
    type=click.Path(path_type=Path),
    help="Directory to write rendered configuration files",
)
@click.pass_context
def render(ctx, token_file: Path, target: str, output: Path):
    """
    Render TOKEN_FILE to configuration files for a target toolkit.

    \b
    Examples:
        unified-theming render tokens.json --target gtk --output ./out
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get("config"))
        written = manager.render_tokens(token_file, target, output)
        click.secho(
            f"✓ Rendered {len(written)} files for {target} into {output}",
            fg="green",
        )
        for path in written:
            click.echo(f"  - {path}")
    except Exception as e:
        click.secho(f"✗ Error rendering tokens: {e}", fg="red", err=True)
        sys.exit(1)


# ============================================================================
# Current Command
# ============================================================================


@cli.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "list", "json"], case_sensitive=False),
    default="table",
    help="Output format (default: table)",
)
@click.pass_context
def current(ctx, format: str):
    """
    Show currently applied themes for each toolkit.

    \b
    Examples:
        unified-theming current
        unified-theming current --format json
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get("config"))
        current_themes = manager.get_current_themes()

        if not current_themes:
            click.echo("No current theme information available")
            return

        if format == "table":
            click.echo(f"{'Toolkit':<15} {'Current Theme':<30}")
            click.echo("-" * 45)
            for toolkit, theme_name in sorted(current_themes.items()):
                click.echo(f"{toolkit:<15} {theme_name or 'None':<30}")

        elif format == "list":
            for toolkit, theme_name in sorted(current_themes.items()):
                click.echo(f"{toolkit}: {theme_name or 'None'}")

        elif format == "json":
            import json

            output = {k: v or None for k, v in current_themes.items()}
            click.echo(json.dumps(output, indent=2))

    except Exception as e:
        click.secho(f"Error getting current themes: {e}", fg="red", err=True)
        sys.exit(1)


# ============================================================================
# Rollback Command
# ============================================================================


@cli.command()
@click.option("--list-backups", "-l", is_flag=True, help="List available backups")
@click.pass_context
def rollback(ctx, list_backups: bool):
    """
    Rollback to previous theme configuration.

    \b
    Examples:
        unified-theming rollback
        unified-theming rollback --list-backups
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get("config"))

        if list_backups:
            # List available backups
            backups = manager.config_manager.get_backups()

            if not backups:
                click.echo("No backups available")
                return

            click.echo(f"{'Backup ID':<35} {'Theme':<20} {'Date':<20}")
            click.echo("-" * 75)
            for backup in sorted(backups, key=lambda b: b.timestamp, reverse=True):
                click.echo(
                    f"{backup.backup_id:<35} {backup.theme_name:<20} "
                    f"{backup.timestamp.strftime('%Y-%m-%d %H:%M:%S'):<20}"
                )
            return

        # Perform rollback
        click.echo("Rolling back to previous configuration...")
        success = manager.rollback()

        if success:
            click.secho("✓ Rollback successful!", fg="green")
        else:
            click.secho("✗ Rollback failed", fg="red", err=True)
            sys.exit(1)

    except Exception as e:
        click.secho(f"✗ Error during rollback: {e}", fg="red", err=True)
        sys.exit(1)


# ============================================================================
# Validate Command
# ============================================================================


@cli.command()
@click.argument("theme_name")
@click.pass_context
def validate(ctx, theme_name: str):
    """
    Validate THEME_NAME structure and compatibility.

    \b
    Examples:
        unified-theming validate Nord
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get("config"))
        themes = manager.discover_themes()

        if theme_name not in themes:
            click.secho(f"✗ Theme '{theme_name}' not found", fg="red", err=True)
            sys.exit(1)

        theme_info = themes[theme_name]

        # Validate theme
        validation_result = manager.parser.validate_theme(theme_info.path)

        # Display results
        if validation_result.valid:
            click.secho(f"✓ Theme '{theme_name}' is valid", fg="green")
        else:
            click.secho(f"✗ Theme '{theme_name}' has issues", fg="red")

        # Show all validation messages
        for msg in validation_result.messages:
            color = {"ERROR": "red", "WARNING": "yellow", "INFO": "blue"}.get(
                msg.level.value.upper(), "white"
            )

            click.secho(f"  [{msg.level.value.upper()}] {msg.message}", fg=color)
            if msg.details:
                click.echo(f"    Details: {msg.details}")

        # Exit with error code if validation failed
        if not validation_result.valid:
            sys.exit(1)

    except Exception as e:
        click.secho(f"Error validating theme: {e}", fg="red", err=True)
        sys.exit(1)


# ============================================================================
# TEST Command (debugging --targets issue)
# ============================================================================


@cli.command()
@click.argument("theme_name")
@click.option(
    "--targets",
    multiple=True,
    type=click.Choice(
        ["gtk2", "gtk3", "gtk4", "libadwaita", "qt5", "qt6", "flatpak", "snap", "all"],
        case_sensitive=False,
    ),
    help="Target toolkits (default: all)",
)
@click.option("--dry-run", is_flag=True, help="Preview changes without applying them")
@click.pass_context
def testcmd(ctx, theme_name: str, targets: Tuple[str, ...], dry_run: bool):
    """Test command with same structure as apply."""
    click.echo(f"Theme: {theme_name}")
    click.echo(f"Targets: {targets}")
    click.echo(f"Dry-run: {dry_run}")


@cli.command("check-deps")
def check_deps():
    """Check cross-toolkit theming dependencies.

    Detects Qt apps on GTK desktops (or vice versa) and shows
    which packages are needed for consistent theming.
    """
    from unified_theming.utils.system_detect import (
        detect_environment,
        get_install_command,
    )

    env = detect_environment()

    click.echo(f"Desktop: {env.desktop.upper()}")
    click.echo(f"GTK apps detected: {'Yes' if env.has_gtk_apps else 'No'}")
    click.echo(f"Qt apps detected: {'Yes' if env.has_qt_apps else 'No'}")
    click.echo()

    if env.qt_packages_installed:
        click.secho("✓ Qt theming packages installed:", fg="green")
        for pkg in env.qt_packages_installed:
            click.echo(f"  • {pkg}")

    if env.qt_packages_missing:
        click.secho("✗ Qt theming packages missing:", fg="yellow")
        for pkg in env.qt_packages_missing:
            click.echo(f"  • {pkg}")
        click.echo()
        click.secho("Install with:", fg="cyan")
        click.echo(f"  {get_install_command(env.qt_packages_missing)}")

    if env.gtk_packages_missing:
        click.secho("✗ GTK theming packages missing:", fg="yellow")
        for pkg in env.gtk_packages_missing:
            click.echo(f"  • {pkg}")
        click.echo()
        click.secho("Install with:", fg="cyan")
        click.echo(f"  {get_install_command(env.gtk_packages_missing)}")

    if not env.qt_packages_missing and not env.gtk_packages_missing:
        click.secho("✓ All cross-toolkit theming packages installed!", fg="green")


# ============================================================================
# Create Command (Day 4)
# ============================================================================


@cli.command()
@click.argument("theme_name")
@click.option(
    "--accent",
    "-a",
    type=str,
    help="Accent color in hex format (e.g., #3584e4)",
)
@click.option(
    "--variant",
    "-v",
    type=click.Choice(["light", "dark"], case_sensitive=False),
    default="dark",
    help="Theme variant (default: dark)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output path for token JSON file",
)
@click.option(
    "--apply",
    is_flag=True,
    help="Apply the created theme immediately",
)
@click.pass_context
def create(
    ctx,
    theme_name: str,
    accent: Optional[str],
    variant: str,
    output: Optional[str],
    apply: bool,
):
    """Create a new theme from scratch using tokens.

    \b
    Examples:
        unified-theming create MyTheme
        unified-theming create MyTheme --accent "#ff5500" --variant dark
        unified-theming create MyTheme --accent "#3584e4" --apply
        unified-theming create MyTheme -a "#2ec27e" -v light -o mytheme.json
    """
    from unified_theming.color.spaces import Color
    from unified_theming.tokens import create_light_tokens, create_dark_tokens
    from unified_theming.tokens.validation import validate_tokens

    try:
        # Parse accent color if provided
        accent_color = None
        if accent:
            try:
                accent_color = Color.from_hex(accent)
                click.echo(f"Using accent color: {accent}")
            except Exception as e:
                click.secho(
                    f"✗ Invalid accent color '{accent}': {e}", fg="red", err=True
                )
                sys.exit(1)

        # Create tokens based on variant
        click.echo(f"Creating {variant} theme '{theme_name}'...")
        if variant == "light":
            tokens = create_light_tokens(accent=accent_color, name=theme_name)
        else:
            tokens = create_dark_tokens(accent=accent_color, name=theme_name)

        # Validate tokens
        validation = validate_tokens(tokens)
        if not validation.valid:
            click.secho("✗ Token validation failed:", fg="red")
            for msg in validation.messages:
                click.echo(f"  - {msg.message}")
            sys.exit(1)

        click.secho(f"✓ Created valid {variant} theme tokens", fg="green")

        # Save to file if output specified
        if output:
            import json

            output_path = Path(output)
            token_dict = {
                "name": tokens.name,
                "variant": tokens.variant,
                "surface": {
                    "primary": {"$value": tokens.surfaces.primary.to_hex()},
                    "secondary": {"$value": tokens.surfaces.secondary.to_hex()},
                    "tertiary": {"$value": tokens.surfaces.tertiary.to_hex()},
                    "elevated": {"$value": tokens.surfaces.elevated.to_hex()},
                },
                "content": {
                    "primary": {"$value": tokens.content.primary.to_hex()},
                    "secondary": {"$value": tokens.content.secondary.to_hex()},
                    "inverse": {"$value": tokens.content.inverse.to_hex()},
                    "link": {"$value": tokens.content.link.to_hex()},
                    "link_visited": {"$value": tokens.content.link_visited.to_hex()},
                },
                "accent": {
                    "primary": {"$value": tokens.accents.primary.to_hex()},
                    "primary_container": {
                        "$value": tokens.accents.primary_container.to_hex()
                    },
                    "success": {"$value": tokens.accents.success.to_hex()},
                    "warning": {"$value": tokens.accents.warning.to_hex()},
                    "error": {"$value": tokens.accents.error.to_hex()},
                },
            }
            output_path.write_text(json.dumps(token_dict, indent=2))
            click.secho(f"✓ Saved tokens to: {output_path}", fg="green")

        # Apply if requested
        if apply:
            click.echo("Applying theme...")
            manager = UnifiedThemeManager(config_path=ctx.obj.get("config"))

            from unified_theming.handlers.gtk_handler import GTKHandler
            from unified_theming.handlers.qt_handler import QtHandler

            gtk_handler = GTKHandler()
            qt_handler = QtHandler()

            gtk_success = gtk_handler.apply_from_tokens(tokens)
            qt_success = qt_handler.apply_from_tokens(tokens)

            if gtk_success:
                click.secho("  ✓ Applied to GTK", fg="green")
            else:
                click.secho("  ✗ Failed to apply to GTK", fg="red")

            if qt_success:
                click.secho("  ✓ Applied to Qt", fg="green")
            else:
                click.secho("  ✗ Failed to apply to Qt", fg="red")

            if gtk_success and qt_success:
                click.secho(f"✓ Theme '{theme_name}' applied successfully!", fg="green")
            else:
                click.secho("⚠ Theme partially applied", fg="yellow")

        # Show summary if not saving or applying
        if not output and not apply:
            click.echo()
            click.echo("Token summary:")
            click.echo(f"  Name: {tokens.name}")
            click.echo(f"  Variant: {tokens.variant}")
            click.echo(f"  Primary surface: {tokens.surfaces.primary.to_hex()}")
            click.echo(f"  Primary accent: {tokens.accents.primary.to_hex()}")
            click.echo()
            click.echo("Use --output to save or --apply to apply immediately")

    except Exception as e:
        click.secho(f"✗ Error creating theme: {e}", fg="red", err=True)
        sys.exit(1)


# ============================================================================
# Entry Point
# ============================================================================


def main():
    """Main entry point for CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
