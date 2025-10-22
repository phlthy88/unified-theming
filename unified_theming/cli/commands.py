"""
Command-line interface for Unified Theming Application.

This module implements the CLI using Click framework, providing
a user-friendly command-line interface for all core operations.
"""

import click
from typing import Optional, List, Tuple
from pathlib import Path
import sys

from unified_theming.core.manager import UnifiedThemeManager
from unified_theming.core.types import Toolkit


# Version information
__version__ = "1.0.0"


# ============================================================================
# Main CLI Group
# ============================================================================

@click.group()
@click.option(
    '--verbose', '-v',
    count=True,
    help='Increase verbosity (can be used multiple times: -v, -vv, -vvv)'
)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True, path_type=Path),
    help='Path to configuration file'
)
@click.option(
    '--no-color',
    is_flag=True,
    help='Disable colored output'
)
@click.version_option(version=__version__, prog_name='unified-theming')
@click.pass_context
def cli(ctx, verbose: int, config: Optional[Path], no_color: bool):
    """
    Unified Theming Application - Apply themes across toolkits.

    This tool helps you apply consistent themes across GTK, Qt,
    and containerized applications on Linux.

    \b
    Examples:
        unified-theming list
        unified-theming apply Nord
        unified-theming current
        unified-theming rollback

    For more information, visit: https://github.com/yourusername/unified-theming
    """
    # Initialize context object
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    ctx.obj['no_color'] = no_color


# ============================================================================
# List Command
# ============================================================================

@cli.command()
@click.option(
    '--toolkit', '-t',
    multiple=True,
    type=click.Choice([
        'gtk2', 'gtk3', 'gtk4', 'libadwaita',
        'qt5', 'qt6', 'all'
    ], case_sensitive=False),
    help='Filter themes by toolkit support'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['table', 'list', 'json'], case_sensitive=False),
    default='table',
    help='Output format (default: table)'
)
@click.pass_context
def list(ctx, toolkit: Tuple[str, ...], format: str):
    """
    List all available themes.

    \b
    Examples:
        unified-theming list
        unified-theming list --toolkit gtk4
        unified-theming list --format json
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get('config'))
        themes = manager.discover_themes()

        if toolkit:
            # Filter themes by toolkit support
            filtered_themes = {
                name: info for name, info in themes.items()
                if any(Toolkit[tk.upper()] in info.supported_toolkits for tk in toolkit)
            }
        else:
            filtered_themes = themes

        if not filtered_themes:
            click.echo("No themes found")
            return

        if format == 'table':
            # Print table format
            click.echo(f"{'Theme Name':<30} {'Toolkits':<40}")
            click.echo("-" * 70)
            for name, info in sorted(filtered_themes.items()):
                toolkits = ', '.join(t.value for t in info.supported_toolkits)
                click.echo(f"{name:<30} {toolkits:<40}")

        elif format == 'list':
            # Print simple list
            for name in sorted(filtered_themes.keys()):
                click.echo(name)

        elif format == 'json':
            # Print JSON format
            import json
            output = {
                name: {
                    'path': str(info.path),
                    'toolkits': [t.value for t in info.supported_toolkits],
                    'colors': len(info.colors)
                }
                for name, info in filtered_themes.items()
            }
            click.echo(json.dumps(output, indent=2))

    except Exception as e:
        click.secho(f"Error listing themes: {e}", fg='red', err=True)
        sys.exit(1)


# ============================================================================
# Apply Command
# ============================================================================

@cli.command()
@click.option(
    '--targets',
    multiple=True,
    type=click.Choice([
        'gtk2', 'gtk3', 'gtk4', 'libadwaita',
        'qt5', 'qt6', 'flatpak', 'snap', 'all'
    ], case_sensitive=False),
    help='Target toolkits (default: all)'
)
@click.argument('theme_name')
@click.pass_context
def apply(ctx, targets: Tuple[str, ...], theme_name: str):
    """
    Apply THEME_NAME to specified targets.

    \b
    Examples:
        unified-theming apply Nord
        unified-theming apply Dracula --targets gtk4 --targets libadwaita
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get('config'))

        # Convert targets to string list
        # If no targets specified, or 'all' is in targets, apply to all
        if not targets or 'all' in targets:
            target_list = None  # None means all available toolkits
        else:
            target_list = list(targets)

        # Apply theme
        click.echo(f"Applying theme '{theme_name}'...")
        result = manager.apply_theme(theme_name, targets=target_list)

        # Display results
        if result.overall_success:
            click.secho(f"✓ Theme '{theme_name}' applied successfully!", fg='green')
        else:
            click.secho(f"⚠ Theme applied with warnings", fg='yellow')

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
                click.secho(f"  ⚠ {warning}", fg='yellow')

    except Exception as e:
        click.secho(f"✗ Error applying theme: {e}", fg='red', err=True)
        sys.exit(1)


# ============================================================================
# Current Command
# ============================================================================

@cli.command()
@click.option(
    '--format', '-f',
    type=click.Choice(['table', 'list', 'json'], case_sensitive=False),
    default='table',
    help='Output format (default: table)'
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
        manager = UnifiedThemeManager(config_path=ctx.obj.get('config'))
        current_themes = manager.get_current_themes()

        if not current_themes:
            click.echo("No current theme information available")
            return

        if format == 'table':
            click.echo(f"{'Toolkit':<15} {'Current Theme':<30}")
            click.echo("-" * 45)
            for toolkit, theme_name in sorted(current_themes.items()):
                click.echo(f"{toolkit:<15} {theme_name or 'None':<30}")

        elif format == 'list':
            for toolkit, theme_name in sorted(current_themes.items()):
                click.echo(f"{toolkit}: {theme_name or 'None'}")

        elif format == 'json':
            import json
            output = {k: v or None for k, v in current_themes.items()}
            click.echo(json.dumps(output, indent=2))

    except Exception as e:
        click.secho(f"Error getting current themes: {e}", fg='red', err=True)
        sys.exit(1)


# ============================================================================
# Rollback Command
# ============================================================================

@cli.command()
@click.option(
    '--list-backups', '-l',
    is_flag=True,
    help='List available backups'
)
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
        manager = UnifiedThemeManager(config_path=ctx.obj.get('config'))

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
            click.secho("✓ Rollback successful!", fg='green')
        else:
            click.secho("✗ Rollback failed", fg='red', err=True)
            sys.exit(1)

    except Exception as e:
        click.secho(f"✗ Error during rollback: {e}", fg='red', err=True)
        sys.exit(1)


# ============================================================================
# Validate Command
# ============================================================================

@cli.command()
@click.argument('theme_name')
@click.pass_context
def validate(ctx, theme_name: str):
    """
    Validate THEME_NAME structure and compatibility.

    \b
    Examples:
        unified-theming validate Nord
    """
    try:
        manager = UnifiedThemeManager(config_path=ctx.obj.get('config'))
        themes = manager.discover_themes()

        if theme_name not in themes:
            click.secho(f"✗ Theme '{theme_name}' not found", fg='red', err=True)
            sys.exit(1)

        theme_info = themes[theme_name]

        # Validate theme
        validation_result = manager.parser.validate_theme(theme_info.path)

        # Display results
        if validation_result.valid:
            click.secho(f"✓ Theme '{theme_name}' is valid", fg='green')
        else:
            click.secho(f"✗ Theme '{theme_name}' has issues", fg='red')

        # Show all validation messages
        for msg in validation_result.messages:
            color = {
                'ERROR': 'red',
                'WARNING': 'yellow',
                'INFO': 'blue'
            }.get(msg.level.value.upper(), 'white')

            click.secho(f"  [{msg.level.value.upper()}] {msg.message}", fg=color)
            if msg.details:
                click.echo(f"    Details: {msg.details}")

        # Exit with error code if validation failed
        if not validation_result.valid:
            sys.exit(1)

    except Exception as e:
        click.secho(f"Error validating theme: {e}", fg='red', err=True)
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
        click.secho(f"Unexpected error: {e}", fg='red', err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
