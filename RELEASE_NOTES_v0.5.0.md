# Unified Theming v0.5.0 - CLI Alpha Release

**Release Date:** October 21, 2025
**Type:** Alpha Release (CLI-only)
**Status:** Feature Complete, Testing In Progress

---

## 🎉 What's New

### CLI Commands Available
- `unified-theming list` - List all available themes
- `unified-theming apply <theme>` - Apply a theme across toolkits
- `unified-theming current` - Show currently applied themes
- `unified-theming rollback` - Rollback to previous theme
- `unified-theming validate <theme>` - Validate theme compatibility

### Supported Toolkits
- ✅ GTK2/3/4 themes
- ✅ Libadwaita applications (70% coverage via CSS injection)
- ✅ Qt5/6 applications (kdeglobals + Kvantum)
- ✅ Flatpak containerized apps (global + per-app overrides)
- ✅ Snap applications (basic support)

### Core Features
- **Theme Discovery:** Automatically finds themes in ~/.themes, /usr/share/themes
- **Cross-Toolkit Application:** Applies themes to all supported toolkits at once
- **Color Translation:** Converts GTK color variables to Qt format
- **Backup/Restore:** Automatic backup before theme changes, rollback on failure
- **Graceful Degradation:** Continues if one toolkit unavailable

---

## 📊 Test Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| color.py | 86% | ✅ Excellent |
| manager.py | 93% | ✅ Excellent |
| config.py | 75% | ✅ Good |
| flatpak_handler.py | 100% | ✅ Excellent |
| **Overall** | **48%** | ⚠️ **In Progress (target: 80%)** |

**Test Suite:**
- 144 tests passing (99.3% pass rate)
- Comprehensive unit tests for core modules
- Integration tests in progress (Week 3)

---

## 🚀 Installation

### From Source (Recommended for v0.5.0)
```bash
git clone https://github.com/yourusername/unified-theming
cd unified-theming
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### System Dependencies (Ubuntu/Debian)
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
```

---

## 🎯 Quick Start

```bash
# List available themes
unified-theming list

# Apply a theme
unified-theming apply Adwaita-dark

# Check current themes
unified-theming current

# Rollback if something goes wrong
unified-theming rollback
```

---

## ⚠️ Known Limitations (v0.5.0)

### Not Yet Implemented
- ❌ **GUI application** (planned for Week 4-6)
- ❌ **Percentage RGB colors** (TC-C-030, deferred to post-v0.5)
- ❌ **Theme preview** (planned for v1.0)
- ❌ **Packaging** (Flatpak/AppImage/PPA planned for Weeks 7-9)

### Partial Support
- ⚠️ **Libadwaita:** 70% coverage (colors only, no widget structure changes)
- ⚠️ **Qt translation:** Approximate (GTK and Qt have different color models)
- ⚠️ **Snap:** Basic support (76% coverage, but limited by Snap permissions)

### Testing Status
- ⚠️ **Integration tests:** In progress (Week 3 planned)
- ⚠️ **Performance tests:** Not yet implemented (Week 3 planned)
- ⚠️ **Stress tests:** Not yet implemented (Week 3 planned)

---

## 🐛 Known Issues

1. **Backup timestamp collisions** - Fixed in v0.5.0 (added microsecond precision)
2. **CLI commands untested** - Basic tests added in v0.5.0 (full coverage Week 3)
3. **Handler coordination** - Tested individually, integration tests pending

---

## 📚 Documentation

- [Requirements Specification](docs/requirements_specification.md)
- [Architecture Guide](docs/architecture.md)
- [Developer Guide](docs/developer_guide.md)
- [Test Plan](docs/test_plan_week1.md)
- [CLAUDE.md](CLAUDE.md) - Claude Code integration guide

---

## 🤝 Contributing

This project is in **active development** (Phase 2, ~70% complete).

**Current Focus:** Testing and integration (Weeks 2-3)
**Next Phase:** GUI development (Weeks 4-6)

See [HANDOFF_PROTOCOL.md](docs/HANDOFF_PROTOCOL.md) for multi-agent development workflow.

---

## 📅 Roadmap

- **v0.5.0 (Week 2):** ✅ CLI-only alpha release
- **v0.9.0 (Week 6):** GUI beta release
- **v1.0.0 (Week 9-11):** Production release with packaging

---

## 🙏 Acknowledgments

Built with multi-agent collaboration:
- **Claude Code:** Architecture, design, documentation
- **Qwen Coder:** Implementation, testing
- **Opencode AI:** QA validation, packaging

---

## 📄 License

MIT License (see LICENSE file)

---

**This is an alpha release. Expect bugs and missing features. Report issues at:**
https://github.com/yourusername/unified-theming/issues

🤖 Generated with [Claude Code](https://claude.com/claude-code)