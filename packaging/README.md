# Packaging

This directory contains packaging scripts and resources for distributing Unified Theming.

## Files

- `build.sh` - Build script that runs tests, formatting, and creates distribution packages
- `unified-theming.desktop` - Desktop entry file for the GUI application

## Building

To build the package:

```bash
./packaging/build.sh
```

This will:
1. Clean previous builds
2. Install build dependencies
3. Run tests
4. Format and lint code
5. Build distribution packages
6. Check packages with twine

## Installation

After building, install with:

```bash
pip install dist/unified_theming-*.whl
```

Or for development:

```bash
pip install -e .
```

## Desktop Integration

To integrate with the desktop environment:

1. Copy the desktop file to the applications directory:
   ```bash
   cp packaging/unified-theming.desktop ~/.local/share/applications/
   ```

2. Install an icon (SVG or PNG) as `~/.local/share/icons/hicolor/scalable/apps/unified-theming.svg`

## Distribution

The package can be distributed via:
- PyPI (Python Package Index)
- System package managers (deb, rpm, etc.)
- Flatpak/Snap for sandboxed distribution