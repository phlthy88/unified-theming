# 🎨 Unified Theming

<p align="center">
  <strong>One theme. Every toolkit. Perfect consistency.</strong>
</p>

<p align="center">
  <a href="https://github.com/phlthy88/unified-theming"><img src="https://img.shields.io/badge/tests-386%20passing-brightgreen" alt="Tests"></a>
  <a href="https://github.com/phlthy88/unified-theming"><img src="https://img.shields.io/badge/coverage-53%25-yellow" alt="Coverage"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://github.com/phlthy88/unified-theming/releases"><img src="https://img.shields.io/badge/release-v0.5.0-green" alt="Release"></a>
</p>

---

## ✨ What is Unified Theming?

Unified Theming is a Linux desktop application that applies **consistent themes across all your apps** — GTK, Qt, Flatpak, and more. No more mismatched colors between Firefox and your file manager!

```bash
# Apply a theme everywhere with one command
unified-theming apply_theme Adwaita-dark
```

## 🚀 Features

### 🖌️ Toolkit Support
| Toolkit | Support Level |
|---------|---------------|
| GTK 2/3/4 | ✅ Full |
| Libadwaita | ✅ 95% (with patches) |
| Qt 5/6 | ✅ Full |
| Flatpak | ✅ Full |
| Snap | ⚡ Basic |

### 🎯 Key Capabilities
- 🔄 **One-click theming** — Apply themes to all toolkits simultaneously
- 🎨 **Perceptual color engine** — OKLCH-based color translation for accurate cross-toolkit matching
- ♿ **WCAG accessibility** — Built-in contrast checking ensures readable themes
- 💾 **Safe rollback** — Automatic backups before every change
- 🖥️ **Dual interface** — CLI for power users, GTK4 GUI for everyone else

## 📦 Installation

### Quick Start (CLI only)
```bash
git clone https://github.com/phlthy88/unified-theming.git
cd unified-theming
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
```

### With GUI Support
First install system dependencies:

<details>
<summary>Ubuntu/Debian 22.04+</summary>

```bash
sudo apt install -y libgtk-4-dev libadwaita-1-dev libgirepository1.0-dev \
  gir1.2-gtk-4.0 python3-gi python3-gi-cairo pkg-config python3-dev
```
</details>

<details>
<summary>Fedora/RHEL</summary>

```bash
sudo dnf install -y gtk4-devel libadwaita-devel gobject-introspection-devel \
  python3-gobject python3-cairo pkg-config python3-devel
```
</details>

<details>
<summary>Arch Linux</summary>

```bash
sudo pacman -S gtk4 libadwaita gobject-introspection python-gobject python-cairo pkgconf
```
</details>

Then install with GUI:
```bash
pip install -e ".[dev,gui]"
```

## 🛠️ Usage

### CLI Commands
```bash
# 📋 List available themes
unified-theming list

# 🎨 Apply a theme everywhere
unified-theming apply_theme Nord

# 👀 Preview without applying
unified-theming apply_theme Dracula --dry-run

# 🎯 Target specific toolkits
unified-theming apply_theme Catppuccin --targets gtk4 --targets flatpak

# 📊 Show current theme status
unified-theming current

# ✅ Validate theme compatibility
unified-theming validate Adwaita-dark

# ⏪ Rollback to previous config
unified-theming rollback
```

### GUI Application
```bash
unified-theming-gui
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI                                  │
│       apply_theme │ list │ current │ validate │ rollback    │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Parser    │   │   Tokens    │   │  Renderer   │
│  GTK/JSON   │──▶│   Schema    │──▶│ GTK/Qt/Shell│
└─────────────┘   └─────────────┘   └─────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       HANDLERS                               │
│  GTKHandler │ QtHandler │ GnomeShellHandler │ FlatpakHandler│
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM CONFIG                             │
│  gtk.css │ kdeglobals │ gnome-shell.css │ flatpak overrides │
└─────────────────────────────────────────────────────────────┘
```

### Token-Based Workflow (New)
```python
from unified_theming.tokens import create_dark_tokens
from unified_theming.renderers import GTKRenderer, QtRenderer
from unified_theming.handlers.gtk_handler import GTKHandler

# Create tokens from accent color
tokens = create_dark_tokens(name="MyTheme")

# Render to any toolkit
gtk_css = GTKRenderer().render(tokens)
qt_ini = QtRenderer().render(tokens)

# Apply via handler
handler = GTKHandler()
handler.apply_from_tokens(tokens)
```

## 📊 Project Status

| Component | Status |
|-----------|--------|
| 🎨 Color Engine | ✅ Complete |
| 📝 Theme Parser | ✅ Complete |
| 🖼️ GTK Handler | ✅ Complete |
| 🔷 Qt Handler | ✅ Complete |
| 🐚 GNOME Shell Handler | ✅ Complete |
| 📦 Flatpak Handler | ✅ Complete |
| 📦 Snap Handler | ⚡ Basic |
| 💻 CLI | ✅ Complete |
| 🖥️ GUI | 🚧 Beta |

**Test Suite:** 386 tests passing ✅

## 🗺️ Roadmap

- [x] **v0.5.0** — CLI alpha + basic GUI
- [ ] **v0.9.0** — GUI beta with full feature parity
- [ ] **v1.0.0** — Production release (Flatpak/AppImage)

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Quick setup
git clone https://github.com/phlthy88/unified-theming.git
cd unified-theming
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev,gui]"

# Run checks before PR
pytest && black --check unified_theming/ && flake8 unified_theming/
```

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Developer Guide](docs/developer_guide.md)
- [GUI Setup](docs/GUI_SETUP_AND_TROUBLESHOOTING.md)

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ for the Linux desktop
</p>
