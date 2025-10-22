# Unified Theming Application - System Architecture

**Version:** 1.0
**Date:** 2025-10-20
**Author:** Claude Code (Phase 1)
**Status:** Design Specification

---

## 1. Architecture Overview

The Unified Theming Application follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────┐              ┌──────────────┐            │
│  │   CLI Tool   │              │  GUI (GTK4)  │            │
│  │   (Click)    │              │ (Libadwaita) │            │
│  └──────┬───────┘              └──────┬───────┘            │
│         │                             │                     │
│         └─────────────┬───────────────┘                     │
└───────────────────────┼─────────────────────────────────────┘
                        │
┌───────────────────────┼─────────────────────────────────────┐
│              Application Core Layer                          │
│                        │                                     │
│         ┌──────────────▼──────────────┐                     │
│         │  UnifiedThemeManager        │                     │
│         │  - Orchestrate operations   │                     │
│         │  - Handle state/transactions│                     │
│         │  - Coordinate handlers      │                     │
│         │  - Error aggregation        │                     │
│         └──────────────┬──────────────┘                     │
│                        │                                     │
│         ┌──────────────┴──────────────┐                     │
│         │                              │                     │
│    ┌────▼─────┐                  ┌────▼────┐               │
│    │  Theme   │                  │ Config  │               │
│    │  Parser  │                  │ Manager │               │
│    │          │                  │         │               │
│    │ - Scan   │                  │ - Backup│               │
│    │ - Parse  │                  │ - State │               │
│    │ - Extract│                  │ - Restore│              │
│    │ - Validate                  │         │               │
│    └────┬─────┘                  └────┬────┘               │
└─────────┼──────────────────────────────┼───────────────────┘
          │                              │
┌─────────┼──────────────────────────────┼───────────────────┐
│    Toolkit Handler Layer               │                    │
│         │                              │                    │
│    ┌────▼──────────┐  ┌───────────────▼──────┐            │
│    │ GTK Handler   │  │  Qt Handler           │            │
│    │               │  │                       │            │
│    │ ├─ GTK2/3     │  │  ├─ kdeglobals        │            │
│    │ │  (GSettings)│  │  ├─ Kvantum           │            │
│    │ ├─ GTK4       │  │  ├─ qt5ct/qt6ct       │            │
│    │ │  (CSS link) │  │  └─ Color translation │            │
│    │ └─ libadwaita │  │                       │            │
│    │    (CSS inject│  │                       │            │
│    └───────────────┘  └──────────────────────┘            │
│                                                             │
│    ┌─────────────────────────────────────────┐            │
│    │       Container Handler                  │            │
│    │                                          │            │
│    │  ├─ Flatpak Handler                     │            │
│    │  │  ├─ Portal configuration             │            │
│    │  │  ├─ Filesystem overrides             │            │
│    │  │  └─ Environment variables            │            │
│    │  │                                      │            │
│    │  └─ Snap Handler                        │            │
│    │     ├─ Interface connections            │            │
│    │     ├─ Portal integration               │            │
│    │     └─ Theme access configuration       │            │
│    └─────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
          │                              │
┌─────────┼──────────────────────────────┼───────────────────┐
│    System Integration Layer            │                    │
│         │                              │                    │
│    ┌────▼─────┐  ┌─────────┐    ┌─────▼────┐              │
│    │ GSettings│  │  File   │    │Subprocess│              │
│    │  / dconf │  │ System  │    │  Manager │              │
│    │          │  │ Monitor │    │          │              │
│    │ - Read   │  │         │    │ - Launch │              │
│    │ - Write  │  │ - Watch │    │ - Monitor│              │
│    │ - Listen │  │ - Events│    │ - Control│              │
│    └──────────┘  └─────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Layer Descriptions

### 2.1 User Interface Layer

**Purpose:** Provide user interaction interfaces

**Components:**
- **CLI (Command-Line Interface)**
  - Framework: Click
  - Purpose: Power user and scripting interface
  - Features: All core operations, non-interactive mode

- **GUI (Graphical Interface)**
  - Framework: GTK4 + Libadwaita
  - Purpose: General user-friendly interface
  - Features: Visual theme browser, preview, progress feedback

**Communication:** Both UIs communicate with Application Core Layer via `UnifiedThemeManager` API

---

### 2.2 Application Core Layer

**Purpose:** Business logic and orchestration

#### 2.2.1 UnifiedThemeManager

**Responsibilities:**
- Central orchestrator for all theme operations
- Transaction-like behavior (all-or-nothing with rollback)
- Error aggregation and reporting
- State management
- Handler coordination

**Key Methods:**
- `discover_themes()` → Dict[str, ThemeInfo]
- `apply_theme(name, targets)` → ApplicationResult
- `preview_theme(name, apps)` → None
- `rollback()` → bool
- `get_current_themes()` → Dict[str, str]

**Design Pattern:** Facade pattern - provides simplified interface to complex subsystem

#### 2.2.2 ThemeParser

**Responsibilities:**
- Theme discovery across directories
- Metadata extraction
- Color palette parsing
- Theme validation

**Key Methods:**
- `discover_themes()` → List[ThemeInfo]
- `parse_theme(path)` → ThemeInfo
- `extract_colors(path, toolkit)` → Dict[str, str]
- `validate_theme(path)` → ValidationResult

**Design Pattern:** Strategy pattern - different parsing strategies for different theme formats

#### 2.2.3 ConfigManager

**Responsibilities:**
- Configuration backup
- State persistence
- Backup management (pruning old backups)
- State restoration

**Key Methods:**
- `backup_current_state()` → BackupID
- `restore_backup(backup_id)` → bool
- `get_backups()` → List[Backup]
- `prune_old_backups()` → None

**Design Pattern:** Memento pattern - save and restore object state

---

### 2.3 Toolkit Handler Layer

**Purpose:** Toolkit-specific theme application logic

**Design Pattern:** Strategy pattern - interchangeable toolkit handlers

**Base Handler Interface:**
```python
class BaseHandler(ABC):
    @abstractmethod
    def apply_theme(self, theme_data: ThemeData) -> bool:
        """Apply theme to this toolkit."""
        pass

    @abstractmethod
    def get_current_theme(self) -> str:
        """Get currently applied theme name."""
        pass

    @abstractmethod
    def validate_compatibility(self, theme_data: ThemeData) -> ValidationResult:
        """Check if theme is compatible."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this toolkit is installed."""
        pass
```

#### 2.3.1 GTKHandler

**Responsibilities:**
- GTK2/3 theme application via GSettings
- GTK4 theme application via CSS linking
- Libadwaita CSS injection
- Color mapping for libadwaita

**Implementation Methods:**
- GTK2/3: `gsettings set org.gnome.desktop.interface gtk-theme`
- GTK4: Create/update `~/.config/gtk-4.0/gtk.css`
- Libadwaita: CSS variable injection

**Coverage:**
- GTK2/3: 95%
- GTK4: 85%
- Libadwaita: 70% (colors only)

#### 2.3.2 QtHandler

**Responsibilities:**
- Color translation GTK → Qt
- kdeglobals generation
- Kvantum theme creation (optional)
- qt5ct/qt6ct configuration

**Implementation Methods:**
- kdeglobals: INI file at `~/.config/kdeglobals`
- Kvantum: Theme files in `~/.config/Kvantum/ThemeName/`
- qt5ct/qt6ct: Configuration files

**Coverage:** 75% of Qt applications

#### 2.3.3 FlatpakHandler

**Responsibilities:**
- Portal configuration
- Filesystem override management
- Environment variable setup
- Per-application overrides (optional)

**Implementation Method:**
```bash
flatpak override --user --filesystem=~/.themes:ro
flatpak override --user --env=GTK_THEME=ThemeName
```

**Coverage:** 70% (depends on app permissions)

#### 2.3.4 SnapHandler

**Responsibilities:**
- Desktop interface connections
- Portal integration
- Theme access configuration

**Implementation Method:**
```bash
snap connect APP:desktop
# Themes applied via portal settings
```

**Coverage:** 65% (limited by snap confinement)

---

### 2.4 System Integration Layer

**Purpose:** Low-level system interactions

**Components:**

#### 2.4.1 GSettings/dconf Interface
- Read/write GNOME settings
- Listen for external changes
- Notification of settings changes

#### 2.4.2 File System Monitor
- Watch configuration files for changes
- Detect manual modifications
- Trigger synchronization if needed

#### 2.4.3 Subprocess Manager
- Launch preview applications
- Monitor application status
- Control application lifecycle

---

## 3. Data Flow

### 3.1 Theme Application Flow

```
User Request
    ↓
[1] UI Layer receives request (CLI or GUI)
    ↓
[2] UnifiedThemeManager.apply_theme("ThemeName", targets=["all"])
    ↓
[3] ThemeParser.parse_theme("/path/to/ThemeName")
    ↓
[4] ConfigManager.backup_current_state()
    ↓
[5] Validation: theme_data.validate()
    ↓
[6] For each target toolkit:
    ├─ GTKHandler.apply_theme(theme_data)
    ├─ QtHandler.apply_theme(theme_data)
    ├─ FlatpakHandler.apply_theme(theme_data)
    └─ SnapHandler.apply_theme(theme_data)
    ↓
[7] Aggregate results
    ↓
[8] If any CRITICAL failure:
    └─ ConfigManager.restore_backup()
    ↓
[9] Return ApplicationResult to UI
    ↓
[10] UI displays results to user
```

### 3.2 Theme Discovery Flow

```
Discovery Request
    ↓
[1] ThemeParser.discover_themes()
    ↓
[2] Scan directories in parallel:
    ├─ ~/.themes
    ├─ ~/.local/share/themes
    └─ /usr/share/themes
    ↓
[3] For each theme directory:
    ├─ Check structure (gtk-2.0, gtk-3.0, gtk-4.0)
    ├─ Parse index.theme (if exists)
    ├─ Extract metadata
    └─ Lazy: Extract colors (on demand)
    ↓
[4] Return List[ThemeInfo]
    ↓
[5] Cache results for performance
```

### 3.3 Rollback Flow

```
Rollback Request
    ↓
[1] ConfigManager.get_backups()
    ↓
[2] Select most recent backup
    ↓
[3] For each backed-up file:
    ├─ Restore ~/.config/gtk-4.0/gtk.css
    ├─ Restore ~/.config/kdeglobals
    ├─ Restore Kvantum configurations
    └─ Restore Flatpak/Snap settings
    ↓
[4] Restore GSettings values
    ↓
[5] Verify restoration successful
    ↓
[6] Return success status
```

---

## 4. Module Structure

```
unified_theming/
│
├── __init__.py
├── __main__.py                 # Entry point: python -m unified_theming
│
├── core/                       # Application Core Layer
│   ├── __init__.py
│   ├── manager.py              # UnifiedThemeManager
│   ├── parser.py               # ThemeParser
│   ├── config.py               # ConfigManager
│   ├── types.py                # Data classes and type definitions
│   └── exceptions.py           # Custom exceptions
│
├── handlers/                   # Toolkit Handler Layer
│   ├── __init__.py
│   ├── base.py                 # BaseHandler abstract class
│   ├── gtk_handler.py          # GTKHandler
│   ├── qt_handler.py           # QtHandler
│   ├── flatpak_handler.py      # FlatpakHandler
│   └── snap_handler.py         # SnapHandler
│
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── color.py                # Color translation and normalization
│   ├── file.py                 # File operations and utilities
│   ├── validation.py           # Validation logic
│   └── logging_config.py       # Logging setup
│
├── cli/                        # CLI Interface
│   ├── __init__.py
│   └── commands.py             # Click commands
│
├── gui/                        # GUI Interface
│   ├── __init__.py
│   ├── application.py          # GTK Application
│   ├── window.py               # Main window
│   ├── widgets.py              # Custom widgets
│   └── dialogs.py              # Dialogs (preview, settings, etc.)
│
└── tests/                      # Test Suite
    ├── __init__.py
    ├── test_manager.py
    ├── test_parser.py
    ├── test_gtk_handler.py
    ├── test_qt_handler.py
    ├── test_integration.py
    └── fixtures/               # Test themes
        ├── TestTheme/
        ├── IncompleteTheme/
        └── MalformedTheme/
```

---

## 5. Component Details

### 5.1 Core Components

#### UnifiedThemeManager

**State:**
```python
@dataclass
class ManagerState:
    current_theme: Dict[str, str]  # toolkit → theme name
    available_handlers: List[BaseHandler]
    config_manager: ConfigManager
    parser: ThemeParser
```

**Thread Safety:** Not thread-safe (single-threaded execution model)

**Error Handling:** Aggregate errors from handlers, continue on partial failure

#### ThemeParser

**Caching Strategy:**
- Cache theme list after initial scan
- Cache color palettes after extraction
- Invalidate cache on file system changes (optional with file monitor)
- TTL: 5 minutes for theme list cache

**Performance Optimization:**
- Parallel directory scanning (ThreadPoolExecutor)
- Lazy color extraction (only when needed)
- Incremental parsing (parse metadata first, details on demand)

#### ConfigManager

**Backup Storage:**
```
~/.config/unified-theming/backups/
├── backup_20251020_103045_Nord/
│   ├── metadata.json
│   ├── gtk-4.0_gtk.css
│   ├── kdeglobals
│   └── kvantum_config.tar.gz
├── backup_20251020_104523_Dracula/
│   └── ...
└── backup_20251020_110215_Adwaita/
    └── ...
```

**Backup Strategy:**
- Keep last 10 backups
- Compress backups older than 1 day
- Prune backups on startup or after new backup

---

### 5.2 Handler Components

#### GTKHandler

**Color Mapping Table:**

| GTK Variable | Libadwaita Variable | Priority |
|--------------|---------------------|----------|
| theme_bg_color | window_bg_color | CRITICAL |
| theme_fg_color | window_fg_color | CRITICAL |
| theme_base_color | view_bg_color | HIGH |
| theme_text_color | view_fg_color | HIGH |
| theme_selected_bg_color | accent_bg_color | HIGH |
| theme_selected_fg_color | accent_fg_color | HIGH |
| error_color | error_bg_color | MEDIUM |
| warning_color | warning_bg_color | MEDIUM |
| success_color | success_bg_color | MEDIUM |

**CSS Generation Template:**
```css
/* Generated by Unified Theming App */
/* Theme: {theme_name} */
/* Timestamp: {timestamp} */

/* Color Variables */
@define-color window_bg_color {value};
@define-color window_fg_color {value};
...

/* Optional: Custom overrides */
{custom_css}
```

#### QtHandler

**Color Translation Algorithm:**
1. Parse GTK color definitions
2. Normalize color format (hex, rgb, rgba → #RRGGBB)
3. Map GTK semantics to Qt semantics
4. Generate derived colors (hover, disabled states)
5. Write kdeglobals INI file
6. Optionally generate Kvantum theme

**kdeglobals Structure:**
```ini
[Colors:Window]
BackgroundNormal={r},{g},{b}
ForegroundNormal={r},{g},{b}
...

[Colors:Button]
...

[Colors:Selection]
...
```

---

## 6. Design Patterns Summary

| Pattern | Component | Purpose |
|---------|-----------|---------|
| **Facade** | UnifiedThemeManager | Simplify complex subsystem |
| **Strategy** | BaseHandler + implementations | Interchangeable algorithms |
| **Memento** | ConfigManager | Save and restore state |
| **Observer** | FileSystemMonitor | Watch for changes |
| **Template Method** | BaseHandler | Define algorithm structure |
| **Dependency Injection** | Handler construction | Testability and flexibility |

---

## 7. Error Handling Strategy

### 7.1 Error Classification

| Level | Description | Handler Action | User Notification |
|-------|-------------|----------------|-------------------|
| **CRITICAL** | Cannot continue | Abort + Rollback | Error dialog with details |
| **ERROR** | Handler failed | Skip handler, continue | Warning in results |
| **WARNING** | Non-ideal condition | Continue with warning | Info in results |
| **INFO** | Informational | Continue | Optional log message |

### 7.2 Error Propagation

```python
try:
    # Apply theme
    result = handler.apply_theme(theme_data)
except CriticalError as e:
    # Immediate rollback
    config_manager.restore_backup()
    raise ThemeApplicationError(f"Critical failure: {e}")
except HandlerError as e:
    # Log and continue
    logger.error(f"Handler {handler.name} failed: {e}")
    results[handler.name] = {'success': False, 'error': str(e)}
```

### 7.3 Rollback Triggers

- File write permission denied
- Invalid CSS generated (syntax error)
- GSettings write failure
- Multiple handler failures (>50% of enabled handlers)

---

## 8. Performance Considerations

### 8.1 Critical Path Optimization

**Critical Path:** User clicks "Apply" → Theme visible in apps

**Optimization Targets:**
1. **Theme Discovery:** Parallel scanning, caching
2. **Color Extraction:** Lazy loading, memoization
3. **CSS Generation:** Template-based, minimal computation
4. **File I/O:** Batch writes, minimize fsync
5. **GSettings:** Single write transaction

### 8.2 Memory Management

**Memory Budget:**
- Theme metadata cache: 20MB max (≈200 themes)
- Color palette cache: 10MB max
- UI components: 50MB (GTK4)
- Runtime overhead: 20MB

**Cache Eviction:**
- LRU eviction for theme metadata
- Clear color palette cache if memory pressure
- Periodic garbage collection

### 8.3 Scalability

**Design for:**
- 500+ installed themes
- 100+ simultaneous GTK/Qt applications
- 50+ Flatpak applications

**Limitations:**
- Single-user desktop environment (not server)
- Synchronous operations (no async/await complexity)
- Local file system only (no network themes)

---

## 9. Security Considerations

### 9.1 Input Validation

- **Theme Paths:** Prevent directory traversal attacks
- **Color Values:** Validate CSS color syntax
- **File Names:** Sanitize to prevent code injection

### 9.2 Privilege Separation

- **No root required:** All operations in user space
- **No system files:** Only modify `~/.config` and `~/.themes`
- **Sandboxing:** GUI runs as regular user with standard permissions

### 9.3 Safe Defaults

- **Backup by default:** Always backup before changes
- **Validation before application:** Reject malformed themes
- **Fallback to default:** If all else fails, restore Adwaita

---

## 10. Testing Strategy

### 10.1 Unit Testing

**Coverage Target:** 90% for core modules

**Test Fixtures:**
- ValidTheme: Complete GTK2/3/4 theme
- IncompleteTheme: Missing GTK4 support
- MalformedTheme: Syntax errors in CSS
- EmptyTheme: No color definitions

### 10.2 Integration Testing

**Test Scenarios:**
1. Full theme application (all handlers)
2. Partial application (some handlers fail)
3. Rollback after failure
4. Discovery with 100+ themes

### 10.3 End-to-End Testing

**Manual Test Plan:**
1. Install on fresh Ubuntu 22.04
2. Install 10 popular themes
3. Apply each theme via GUI
4. Verify GTK, Qt, Flatpak apps
5. Test rollback functionality

---

## 11. Deployment Architecture

### 11.1 Packaging Formats

- **Flatpak:** Primary distribution method
- **Debian/Ubuntu PPA:** .deb package
- **AUR:** Arch Linux package
- **PyPI:** Python package (fallback)

### 11.2 Dependencies

**Required:**
- Python 3.10+
- GTK 4.10+
- PyGObject

**Optional:**
- Qt 5.15+ / Qt 6.2+ (for Qt theming)
- Flatpak (for Flatpak theming)
- Snapd (for Snap theming)
- Kvantum (for enhanced Qt theming)

### 11.3 Installation Locations

```
/usr/bin/unified-theming           # Executable
/usr/lib/python3/dist-packages/    # Python modules
~/.config/unified-theming/          # User configuration
~/.local/share/applications/        # Desktop entry
```

---

## 12. Future Architecture Considerations

### 12.1 Plugin System (Post-1.0)

Enable third-party toolkit handlers:

```python
class PluginHandler(BaseHandler):
    """Base for plugin handlers."""

    @classmethod
    def load_from_module(cls, module_path):
        """Dynamically load handler plugin."""
        pass
```

### 12.2 DBus Interface (Post-1.0)

System-wide theme service:

```python
class ThemeService(DBusService):
    """DBus service for theme operations."""

    @dbus_method()
    def ApplyTheme(self, theme_name: str) -> dict:
        """Apply theme via DBus."""
        pass
```

### 12.3 Remote Theme Repository (Post-2.0)

Fetch themes from online repository:
- Theme browser with screenshots
- One-click installation
- Automatic updates
- Rating and reviews

---

## 13. Architecture Decision Records (ADRs)

### ADR-001: Use GTK4 for GUI

**Decision:** Use GTK4 + Libadwaita for GUI framework

**Rationale:**
- Dogfooding: Tests libadwaita theming in real app
- Native look on GNOME
- Good Python bindings (PyGObject)
- Modern UI components

**Alternatives Considered:**
- Qt: Would add Qt dependency for GTK-focused app
- Electron: Too heavy, web-based UI not ideal
- GTK3: Older, missing modern components

### ADR-002: CSS Injection for Libadwaita (MVP)

**Decision:** Use CSS injection for libadwaita theming in v1.0

**Rationale:**
- Low maintenance burden
- Safe, no system modifications
- Proven by Gradience project
- 70% coverage acceptable for MVP

**Alternatives Considered:**
- Library patching: Too complex for MVP
- LibAdapta fork: Requires C expertise, defer to Phase 3+

### ADR-003: Synchronous Operations

**Decision:** Use synchronous (blocking) operations, no async/await

**Rationale:**
- Simpler code, easier to maintain
- Operations complete in <2 seconds (acceptable)
- Desktop application, not server
- Threading for parallelism where needed

**Alternatives Considered:**
- asyncio: Adds complexity for minimal benefit
- Multiprocessing: Overkill for file I/O operations

### ADR-004: Click for CLI Framework

**Decision:** Use Click for command-line interface

**Rationale:**
- Industry standard for Python CLIs
- Excellent documentation
- Built-in help generation
- Easy testing

**Alternatives Considered:**
- argparse: Lower-level, more boilerplate
- typer: Newer, less mature ecosystem

---

## 14. Conclusion

This architecture provides:

✅ **Modularity:** Independent, testable components
✅ **Extensibility:** Easy to add new toolkit handlers
✅ **Maintainability:** Clear separation of concerns
✅ **Performance:** Optimized critical paths
✅ **Reliability:** Comprehensive error handling and rollback

**Next Steps:**
1. Review and approve architecture
2. Define detailed API specifications
3. Implement exception hierarchy
4. Create logging configuration
5. Begin Phase 2 implementation (Qwen Coder)

---

**End of Architecture Document**
