# Unified Theming Application - Requirements Specification

**Version:** 1.0
**Date:** 2025-10-20
**Author:** Claude Code (Phase 1)
**Status:** Draft for Review

---

## 1. Executive Summary

This document specifies the functional and non-functional requirements for the Unified Theming Application, a tool designed to apply consistent themes across multiple GUI toolkits and application packaging formats on Linux systems.

### 1.1 Goals

- **Primary Goal**: Enable users to apply a single theme across GTK, Qt, and containerized applications
- **Secondary Goal**: Provide both novice-friendly GUI and power-user CLI interfaces
- **Tertiary Goal**: Maintain system stability with backup/rollback capabilities

### 1.2 Target Coverage

| Toolkit/Format | Expected Coverage | Priority |
|----------------|-------------------|----------|
| GTK2/3 | 95% | High |
| GTK4 (vanilla) | 85% | High |
| Libadwaita | 70% (CSS) → 95% (future patch) | High |
| Qt5/6 | 75% | High |
| Flatpak | 70% | Medium |
| Snap | 65% | Medium |
| AppImage | 20% | Low/Deferred |

**Overall Expected Coverage:** 65-75% of desktop applications

---

## 2. Functional Requirements

### FR-1: Theme Discovery & Parsing

#### FR-1.1: Directory Scanning
**Priority:** CRITICAL
**Description:** Scan standard Linux theme directories for installed themes.

**Acceptance Criteria:**
- Scans `~/.themes`, `~/.local/share/themes`, `/usr/share/themes`
- Returns list of discovered theme names with paths
- Completes scan in <5 seconds for 100+ themes
- Handles permission errors gracefully

**Error Handling:**
- Log warning for inaccessible directories
- Continue scanning remaining directories
- Return partial results rather than failing completely

#### FR-1.2: Theme Metadata Extraction
**Priority:** HIGH
**Description:** Parse theme directories to extract metadata and capabilities.

**Acceptance Criteria:**
- Detects GTK2, GTK3, GTK4 support by directory presence
- Extracts theme name, author, description from index.theme (if present)
- Identifies icon theme association
- Detects dark/light variants

**Supported Theme Structures:**
```
ThemeName/
├── gtk-2.0/
│   └── gtkrc
├── gtk-3.0/
│   └── gtk.css
├── gtk-4.0/
│   └── gtk.css
├── index.theme (optional)
└── README (optional)
```

#### FR-1.3: Color Palette Extraction
**Priority:** HIGH
**Description:** Extract color definitions from CSS files for cross-toolkit translation.

**Acceptance Criteria:**
- Parses `@define-color` statements from GTK CSS
- Handles both hex (#RRGGBB) and rgba() color formats
- Resolves color variable references (e.g., `@theme_bg_color`)
- Extracts minimum 20 semantic color variables

**Critical Color Variables:**
- `theme_bg_color`, `theme_fg_color`
- `theme_base_color`, `theme_text_color`
- `theme_selected_bg_color`, `theme_selected_fg_color`
- `accent_bg_color`, `accent_fg_color`
- `destructive_bg_color`, `warning_bg_color`, `success_bg_color`
- `error_bg_color`, `error_fg_color`

#### FR-1.4: Theme Validation
**Priority:** MEDIUM
**Description:** Validate theme structure and detect common issues.

**Acceptance Criteria:**
- Checks for required files (gtk.css for each GTK version)
- Validates CSS syntax (basic check)
- Warns about missing color definitions
- Reports incomplete theme support

**Validation Levels:**
- **ERROR**: Theme unusable (missing critical files)
- **WARNING**: Theme may have issues (missing optional features)
- **INFO**: Theme complete and valid

---

### FR-2: Cross-Toolkit Theming

#### FR-2.1: GTK2/3 Theme Application
**Priority:** HIGH
**Description:** Apply themes to GTK2 and GTK3 applications using native methods.

**Acceptance Criteria:**
- Sets theme via GSettings: `org.gnome.desktop.interface gtk-theme`
- Updates icon theme if specified
- Sets cursor theme if specified
- Changes take effect for newly launched apps immediately
- Running apps update on next restart

**Implementation Method:**
```bash
gsettings set org.gnome.desktop.interface gtk-theme "ThemeName"
```

#### FR-2.2: GTK4/Libadwaita Theme Application
**Priority:** CRITICAL
**Description:** Apply themes to GTK4 and libadwaita applications via CSS injection.

**Acceptance Criteria:**
- Generates CSS file with color variables
- Writes to `~/.config/gtk-4.0/gtk.css`
- Maps GTK3 colors to libadwaita equivalents
- Backs up existing configuration before changes
- Notifies running apps of theme change (best effort)

**Color Mapping (GTK → Libadwaita):**
| GTK Variable | Libadwaita Variable |
|--------------|---------------------|
| theme_bg_color | window_bg_color |
| theme_fg_color | window_fg_color |
| theme_base_color | view_bg_color |
| theme_text_color | view_fg_color |
| theme_selected_bg_color | accent_bg_color |
| theme_selected_fg_color | accent_fg_color |

**Coverage:** 70% of libadwaita applications (colors only, not widget structure)

#### FR-2.3: Qt5/6 Theme Application
**Priority:** HIGH
**Description:** Translate GTK themes to Qt format and apply.

**Acceptance Criteria:**
- Generates kdeglobals configuration file
- Translates GTK colors to Qt equivalents
- Configures qt5ct/qt6ct if available
- Creates Kvantum theme if Kvantum installed
- Handles both Qt5 and Qt6 simultaneously

**Implementation Methods:**
1. **kdeglobals**: Color scheme configuration (`~/.config/kdeglobals`)
2. **Kvantum**: Full theme engine (optional, better coverage)
3. **qt5ct/qt6ct**: Qt configuration tools integration

**Color Translation (GTK → Qt):**
| GTK Variable | Qt Variable |
|--------------|-------------|
| theme_bg_color | BackgroundNormal |
| theme_fg_color | ForegroundNormal |
| theme_base_color | Base |
| theme_text_color | Text |
| theme_selected_bg_color | Highlight |
| theme_selected_fg_color | HighlightedText |

**Coverage:** 75% of Qt applications

#### FR-2.4: Flatpak Theme Application
**Priority:** MEDIUM
**Description:** Configure Flatpak applications to use system themes.

**Acceptance Criteria:**
- Grants filesystem access to theme directories
- Sets environment variables for theme selection
- Configures portal settings
- Supports per-app overrides
- Works with Flatpak 1.12+

**Implementation Method:**
```bash
flatpak override --user --filesystem=~/.themes:ro
flatpak override --user --env=GTK_THEME=ThemeName
```

**Coverage:** 70% of Flatpak applications (depends on app permissions)

#### FR-2.5: Snap Theme Application
**Priority:** MEDIUM
**Description:** Configure Snap applications to use system themes.

**Acceptance Criteria:**
- Connects desktop-theme-gtk interface
- Connects desktop-theme-qt interface
- Uses XDG desktop portal for settings
- Works with snapd 2.45+

**Implementation Method:**
```bash
snap connect APP:desktop
gsettings set org.gnome.desktop.interface gtk-theme "ThemeName"
```

**Coverage:** 65% of Snap applications (limited by snap confinement)

---

### FR-3: Theme Application Operations

#### FR-3.1: System-Wide Theme Application
**Priority:** HIGH
**Description:** Apply selected theme to all supported toolkits simultaneously.

**Acceptance Criteria:**
- Applies to all enabled toolkits in single operation
- Shows progress for each toolkit
- Reports success/failure per toolkit
- Continues on partial failure (doesn't abort entire operation)
- Returns detailed result status

**Result Format:**
```python
{
    'gtk2_3': {'success': True, 'message': 'Applied successfully'},
    'gtk4': {'success': True, 'message': 'Applied successfully'},
    'libadwaita': {'success': True, 'message': 'CSS injection complete'},
    'qt5': {'success': True, 'message': 'kdeglobals updated'},
    'qt6': {'success': True, 'message': 'kdeglobals updated'},
    'flatpak': {'success': False, 'message': 'Flatpak not installed'},
    'snap': {'success': True, 'message': 'Portal configured'}
}
```

#### FR-3.2: Selective Target Application
**Priority:** MEDIUM
**Description:** Apply theme to specific toolkits only.

**Acceptance Criteria:**
- Allows user to select target toolkits
- Skips non-selected toolkits
- Maintains current theme for unselected toolkits
- Useful for testing or troubleshooting

**Use Cases:**
- Apply only to libadwaita to test compatibility
- Apply to Qt only when using KDE applications
- Skip containerized apps if not used

#### FR-3.3: Theme Preview
**Priority:** MEDIUM
**Description:** Preview theme before applying system-wide.

**Acceptance Criteria:**
- Launches sample applications with theme
- Does not modify system configuration
- Shows color swatches and sample UI elements
- Optional: launches real applications (nautilus, calculator, etc.)

**Preview Applications:**
- GTK: gtk4-demo, gtk4-widget-factory
- Libadwaita: adwaita-1-demo
- Qt: qt5ct, qt6ct (if installed)

#### FR-3.4: Configuration Rollback
**Priority:** HIGH
**Description:** Restore previous theme configuration.

**Acceptance Criteria:**
- Maintains backup of previous configuration
- Restores all toolkit configurations atomically
- Works even if current configuration is broken
- Supports rolling back to any of last 5 configurations

**Backup Strategy:**
- Backup before every theme change
- Store in `~/.config/unified-theming/backups/`
- Include timestamp and theme name
- Compress old backups to save space

---

### FR-4: Error Handling & Recovery

#### FR-4.1: Configuration Backup
**Priority:** CRITICAL
**Description:** Automatically backup configurations before any changes.

**Acceptance Criteria:**
- Backs up before every theme application
- Includes all modified files (gtk.css, kdeglobals, etc.)
- Stores metadata (timestamp, theme name, toolkit versions)
- Prunes old backups (keeps last 10)
- Backup operation must succeed before applying changes

**Backup Contents:**
- GTK4: `~/.config/gtk-4.0/gtk.css`
- Qt: `~/.config/kdeglobals`, `~/.config/Kvantum/`
- Flatpak: Override configurations
- GSettings: Current GTK theme name

#### FR-4.2: Incompatibility Detection
**Priority:** HIGH
**Description:** Detect and warn about theme compatibility issues.

**Acceptance Criteria:**
- Checks theme structure before application
- Warns about missing toolkit support
- Detects malformed CSS
- Warns about incomplete color palettes
- Allows user to proceed despite warnings

**Warning Categories:**
- **BLOCKING**: Cannot apply theme (critical errors)
- **WARNING**: May have issues but can proceed
- **INFO**: Minor issues or recommendations

#### FR-4.3: Graceful Degradation
**Priority:** MEDIUM
**Description:** Handle missing dependencies without failing.

**Acceptance Criteria:**
- Detects missing toolkits (Qt, Flatpak, Snap)
- Skips unavailable toolkits gracefully
- Logs INFO message for skipped components
- Continues with available toolkits
- Reports partial success clearly

**Detection Methods:**
- Qt: Check for `qmake` or `qmake6` in PATH
- Flatpak: Check for `flatpak` command
- Snap: Check for `snap` command
- Kvantum: Check for `kvantummanager` or config directory

#### FR-4.4: State Restoration on Failure
**Priority:** HIGH
**Description:** Automatically restore previous state if theme application fails.

**Acceptance Criteria:**
- Detects critical failures during application
- Automatically triggers rollback
- Restores all modified files
- Logs detailed error information
- Notifies user of failure and restoration

**Failure Triggers:**
- File write permission denied
- Invalid CSS generated
- GSettings write failure
- Partial application with critical toolkit failure

---

## 3. Non-Functional Requirements

### NFR-1: Performance

#### NFR-1.1: Theme Switching Performance
**Requirement:** Theme switching completes in <2 seconds (excluding app restarts)

**Measurement:**
- Time from user initiating theme change to completion message
- Measured on system with 50 installed themes
- Test hardware: 4-core CPU, SSD storage

**Performance Budget:**
- Theme discovery: <500ms
- Color extraction: <200ms
- CSS generation: <100ms
- File writing: <200ms
- GSettings updates: <100ms
- Total overhead: <1000ms (1 second)

#### NFR-1.2: Theme Discovery Performance
**Requirement:** Complete theme discovery in <5 seconds for 100+ themes

**Measurement:**
- Full scan of all theme directories
- Metadata extraction for each theme
- Color palette extraction

**Optimization Strategies:**
- Parallel directory scanning
- Lazy color extraction (only when needed)
- Caching of theme metadata

#### NFR-1.3: Memory Usage
**Requirement:** Application memory usage <100MB during operation

**Measurement:**
- Resident Set Size (RSS) during theme application
- GUI application idle memory usage

**Memory Budget:**
- Theme data cache: <20MB
- GTK4 GUI: <50MB
- Parser and handlers: <10MB
- Overhead: <20MB

---

### NFR-2: Compatibility

#### NFR-2.1: GTK Version Support
**Requirement:** Support GTK 4.10+ (released 2023)

**Rationale:** GTK 4.10 introduced stable libadwaita integration

**Testing Matrix:**
- GTK 4.10 (minimum)
- GTK 4.12 (current stable)
- GTK 4.14+ (future compatibility)

#### NFR-2.2: Qt Version Support
**Requirement:** Support Qt 5.15+ and Qt 6.2+

**Rationale:**
- Qt 5.15: Last LTS release of Qt 5
- Qt 6.2: First LTS release of Qt 6

**Testing Matrix:**
- Qt 5.15 LTS
- Qt 6.2 LTS
- Qt 6.5+ (current)

#### NFR-2.3: Python Version Support
**Requirement:** Python 3.10+ required

**Rationale:**
- Type hint improvements (PEP 604, 612, 613)
- Match statement support
- Performance improvements
- Available in Ubuntu 22.04+, Fedora 35+, Debian 12+

#### NFR-2.4: Display Server Support
**Requirement:** Support both Wayland and X11

**Testing Requirements:**
- Primary testing on Wayland (GNOME 43+)
- Secondary testing on X11
- No display-server-specific code paths

#### NFR-2.5: Distribution Support
**Requirement:** Work on major Linux distributions

**Target Distributions:**
- Ubuntu 22.04+ / Pop!_OS 22.04+
- Fedora 37+
- Debian 12+
- Arch Linux (rolling)
- openSUSE Tumbleweed

---

### NFR-3: Usability

#### NFR-3.1: CLI Usability
**Requirement:** Intuitive command-line interface for power users

**Acceptance Criteria:**
- Commands follow standard Unix conventions
- Helpful error messages with actionable suggestions
- Man page or comprehensive `--help` output
- Tab completion support (bash, zsh)
- Non-interactive mode for scripting

**Example Commands:**
```bash
unified-theming list
unified-theming apply Nord
unified-theming preview Dracula
unified-theming rollback
unified-theming current
```

#### NFR-3.2: GUI Usability
**Requirement:** Accessible to non-technical users

**Acceptance Criteria:**
- Follows GNOME HIG (Human Interface Guidelines)
- Clear visual feedback for all operations
- Progress indicators for long operations
- No technical jargon in user-facing messages
- Keyboard navigation support
- Accessible to screen readers

**Design Principles:**
- Progressive disclosure (simple by default, advanced options hidden)
- Confirmation for destructive operations
- Undo/rollback easily accessible

#### NFR-3.3: Error Message Quality
**Requirement:** Clear, actionable error messages

**Good Error Message Pattern:**
```
Error: Cannot apply theme 'CustomTheme'
Reason: Theme missing GTK4 support
Solution: Select a different theme or create gtk-4.0/gtk.css
Details: Expected file at ~/.themes/CustomTheme/gtk-4.0/gtk.css
```

**Bad Error Message:**
```
Error: Theme application failed (code 42)
```

#### NFR-3.4: Documentation Quality
**Requirement:** Comprehensive, clear documentation

**Required Documentation:**
- Installation guide (per distribution)
- Quick start tutorial
- Theme creation guide
- CLI reference
- FAQ and troubleshooting
- Developer documentation

---

### NFR-4: Maintainability

#### NFR-4.1: Code Architecture
**Requirement:** Modular, loosely coupled architecture

**Acceptance Criteria:**
- Clear separation of concerns (parser, handlers, UI)
- Each handler independent and testable
- Dependency injection for configurability
- Plugin architecture for future toolkit support

**Module Independence:**
- GTK handler can be used without Qt handler
- CLI can function without GUI
- Handlers don't depend on each other

#### NFR-4.2: Test Coverage
**Requirement:** Minimum 80% code coverage

**Testing Strategy:**
- Unit tests for each module
- Integration tests for cross-module interactions
- End-to-end tests for complete workflows
- Performance regression tests

**Coverage Breakdown:**
- Core modules (parser, manager): 90%+
- Handlers: 85%+
- CLI: 80%+
- GUI: 70%+ (GUI testing challenging)

#### NFR-4.3: Type Safety
**Requirement:** Complete type hints with mypy validation

**Acceptance Criteria:**
- Type hints on all public functions
- Type hints on all class methods
- mypy in strict mode passes
- No use of `Any` type without justification

**Benefits:**
- Better IDE support
- Catch errors at development time
- Self-documenting code

#### NFR-4.4: Code Style
**Requirement:** Consistent code style across project

**Tools:**
- **black**: Code formatting (line length: 88)
- **flake8**: Style checking
- **isort**: Import sorting
- **pylint**: Additional static analysis

**Style Guide:** PEP 8 + Google docstring format

---

## 4. Constraints

### 4.1: Technical Constraints

- **No root privileges required**: Must work as regular user
- **No system file modification**: Only modify user configuration files
- **No binary compilation**: Pure Python (except optional C extensions)
- **No network requirement**: Fully offline capable

### 4.2: Design Constraints

- **GTK4 for GUI**: Use GTK4/Libadwaita to dogfood the theming
- **Click for CLI**: Standard Python CLI framework
- **No theme forking**: Contribute to existing themes, don't fork
- **Conservative defaults**: Safe operations by default

### 4.3: Compatibility Constraints

- **No breaking changes**: Maintain backward compatibility after 1.0
- **Semantic versioning**: Follow SemVer strictly
- **Deprecation policy**: 2 version notice before removal

---

## 5. Future Considerations (Post-1.0)

### 5.1: libAdapta Integration (Phase 3+)
- Evaluate contribution vs. fork decision
- Implement full libadwaita theming if feasible
- Increase libadwaita coverage to 95%

### 5.2: Theme Creation Tools
- Visual theme editor
- Color palette generator
- Theme testing suite
- One-click theme packaging

### 5.3: Advanced Features
- Per-application theme overrides
- Time-based theme switching (dark mode schedule)
- Theme inheritance and mixing
- Cloud theme sync

### 5.4: Additional Toolkit Support
- Elementary OS styling
- Flutter Linux apps
- Electron apps (limited)
- Wine application theming

---

## 6. Success Criteria

### 6.1: Technical Success
- [ ] All functional requirements implemented
- [ ] All non-functional requirements met
- [ ] 80%+ test coverage achieved
- [ ] Zero critical bugs in release
- [ ] Performance benchmarks met

### 6.2: User Success
- [ ] 70%+ of desktop applications themed
- [ ] <5% error rate in theme application
- [ ] 1000+ active users in 6 months
- [ ] 4+ star average user rating
- [ ] <10% support request rate

### 6.3: Community Success
- [ ] 10+ contributors
- [ ] Monthly release cadence
- [ ] Active community channels
- [ ] Sustainable funding ($500+/month)
- [ ] Documentation completeness >90%

---

## 7. Acceptance Testing

### 7.1: Test Scenarios

#### Scenario 1: Basic Theme Application
1. User has fresh system with default theme
2. User installs 5 different themes
3. User applies each theme sequentially
4. **Expected:** All themes apply without errors, apps reflect changes

#### Scenario 2: Rollback After Failure
1. User applies theme with corrupted CSS
2. Application detects error during application
3. **Expected:** Automatic rollback to previous working theme

#### Scenario 3: Partial Toolkit Support
1. User system has GTK but no Qt
2. User applies theme with both GTK and Qt support
3. **Expected:** GTK applied successfully, Qt skipped with info message

#### Scenario 4: Theme Preview
1. User wants to test theme before applying
2. User launches preview with theme
3. **Expected:** Demo applications launch with theme, no system changes

#### Scenario 5: Containerized Applications
1. User has Flatpak applications installed
2. User applies theme
3. User launches Flatpak app
4. **Expected:** Flatpak app reflects new theme

### 7.2: Performance Testing
- Apply theme 100 times, measure average time
- Scan directory with 200 themes, measure time
- Monitor memory usage during GUI operation
- Stress test with malformed themes

### 7.3: Compatibility Testing
- Test on each target distribution
- Test with minimum GTK/Qt versions
- Test with and without optional dependencies
- Test on both Wayland and X11

---

## 8. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-20 | Claude Code | Initial specification |

---

## 9. Approval

**Specification Status:** Draft
**Review Date:** [TBD]
**Approved By:** [TBD]
**Next Phase:** Architecture Design

---

**End of Requirements Specification**
