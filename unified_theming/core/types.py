"""
Data types and structures for Unified Theming Application.

This module defines all data classes, type aliases, and enumerations
used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..handlers.base import BaseHandler


class Toolkit(Enum):
    """Supported GUI toolkits."""

    GTK2 = "gtk2"
    GTK3 = "gtk3"
    GTK4 = "gtk4"
    LIBADWAITA = "libadwaita"
    QT5 = "qt5"
    QT6 = "qt6"
    FLATPAK = "flatpak"
    SNAP = "snap"


class ValidationLevel(Enum):
    """Validation result severity levels."""

    ERROR = "error"  # Cannot use theme
    WARNING = "warning"  # May have issues
    INFO = "info"  # Informational only


class ColorFormat(Enum):
    """Color representation formats."""

    HEX = "hex"  # #RRGGBB or #RRGGBBAA
    RGB = "rgb"  # rgb(r, g, b)
    RGBA = "rgba"  # rgba(r, g, b, a)
    HSL = "hsl"  # hsl(h, s, l)
    NAMED = "named"  # Color name (e.g., "red")


@dataclass
class ThemeInfo:
    """Complete information about a discovered theme."""

    name: str
    """Theme name (directory name)."""

    path: Path
    """Absolute path to theme directory."""

    supported_toolkits: List[Toolkit]
    """List of toolkits this theme supports."""

    colors: Dict[str, str] = field(default_factory=dict)
    """Color palette extracted from theme (variable_name → color_value)."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """
    Theme metadata from index.theme or parsed from structure.

    Common keys:
    - author: str
    - description: str
    - version: str
    - license: str
    - icon_theme: str (associated icon theme)
    - has_dark_variant: bool
    """

    validation_result: Optional["ValidationResult"] = None
    """Result of theme validation (if validated)."""

    def has_toolkit_support(self, toolkit: Toolkit) -> bool:
        """Check if theme supports a specific toolkit."""
        return toolkit in self.supported_toolkits

    def get_color(self, variable: str, default: Optional[str] = None) -> Optional[str]:
        """Get color value by variable name with optional default."""
        return self.colors.get(variable, default)


@dataclass
class ValidationMessage:
    """Single validation message (error, warning, or info)."""

    level: ValidationLevel
    """Severity level of this message."""

    message: str
    """Human-readable description of the issue."""

    component: Optional[str] = None
    """Component that generated this message (e.g., "parser", "gtk_handler")."""

    details: Optional[str] = None
    """Additional technical details for debugging."""

    def __str__(self) -> str:
        """Format message for display."""
        prefix = f"[{self.level.value.upper()}]"
        if self.component:
            prefix += f" [{self.component}]"
        msg = f"{prefix} {self.message}"
        if self.details:
            msg += f"\n  Details: {self.details}"
        return msg


@dataclass
class ValidationResult:
    """Result of theme validation."""

    valid: bool
    """Overall validation status (True if no errors)."""

    messages: List[ValidationMessage] = field(default_factory=list)
    """List of validation messages."""

    def add_error(
        self,
        message: str,
        component: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """Add an error message."""
        self.messages.append(
            ValidationMessage(
                level=ValidationLevel.ERROR,
                message=message,
                component=component,
                details=details,
            )
        )
        self.valid = False

    def add_warning(
        self,
        message: str,
        component: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """Add a warning message."""
        self.messages.append(
            ValidationMessage(
                level=ValidationLevel.WARNING,
                message=message,
                component=component,
                details=details,
            )
        )

    def add_info(
        self,
        message: str,
        component: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """Add an informational message."""
        self.messages.append(
            ValidationMessage(
                level=ValidationLevel.INFO,
                message=message,
                component=component,
                details=details,
            )
        )

    def has_errors(self) -> bool:
        """Check if there are any error messages."""
        return any(msg.level == ValidationLevel.ERROR for msg in self.messages)

    def has_warnings(self) -> bool:
        """Check if there are any warning messages."""
        return any(msg.level == ValidationLevel.WARNING for msg in self.messages)

    def get_messages_by_level(self, level: ValidationLevel) -> List[ValidationMessage]:
        """Get all messages of a specific level."""
        return [msg for msg in self.messages if msg.level == level]


@dataclass
class ThemeData:
    """
    Theme data prepared for application to a specific toolkit.

    This is the processed form of ThemeInfo, ready for handlers to use.
    """

    name: str
    """Theme name."""

    toolkit: Toolkit
    """Target toolkit for this data."""

    colors: Dict[str, str]
    """Color palette (possibly translated for target toolkit)."""

    css_content: Optional[str] = None
    """Pre-generated CSS content (for GTK handlers)."""

    additional_data: Dict[str, Any] = field(default_factory=dict)
    """
    Toolkit-specific additional data.

    Examples:
    - kvantum_config: str (for Qt Kvantum theme)
    - icon_theme: str (associated icon theme)
    - font_settings: dict (font configuration)
    """


@dataclass
class HandlerResult:
    """Result of a single handler's theme application."""

    handler_name: str
    """Name of the handler (e.g., "GTKHandler", "QtHandler")."""

    toolkit: Toolkit
    """Toolkit this handler manages."""

    success: bool
    """Whether the operation succeeded."""

    message: str
    """Human-readable result message."""

    details: Optional[str] = None
    """Additional details (error traceback, file paths modified, etc.)."""

    files_modified: List[Path] = field(default_factory=list)
    """List of files modified by this handler."""

    warnings: List[str] = field(default_factory=list)
    """Non-fatal warnings during application."""


@dataclass
class ApplicationResult:
    """
    Aggregated result of theme application across all handlers.

    This is returned by UnifiedThemeManager.apply_theme().
    """

    theme_name: str
    """Name of theme that was applied."""

    overall_success: bool
    """True if all critical handlers succeeded."""

    handler_results: Dict[str, HandlerResult]
    """Results from each handler (handler_name → result)."""

    backup_id: Optional[str] = None
    """ID of backup created before application (for rollback)."""

    timestamp: datetime = field(default_factory=datetime.now)
    """When the theme was applied."""

    def get_successful_handlers(self) -> List[str]:
        """Get list of handler names that succeeded."""
        return [name for name, result in self.handler_results.items() if result.success]

    def get_failed_handlers(self) -> List[str]:
        """Get list of handler names that failed."""
        return [
            name for name, result in self.handler_results.items() if not result.success
        ]

    def has_failures(self) -> bool:
        """Check if any handlers failed."""
        return len(self.get_failed_handlers()) > 0

    def get_all_warnings(self) -> List[str]:
        """Get all warnings from all handlers."""
        warnings = []
        for result in self.handler_results.values():
            warnings.extend(result.warnings)
        return warnings


@dataclass
class Backup:
    """Represents a configuration backup."""

    backup_id: str
    """Unique identifier for this backup (typically timestamp-based)."""

    timestamp: datetime
    """When this backup was created."""

    theme_name: str
    """Name of theme that was active when backup was created."""

    backup_path: Path
    """Path to backup directory."""

    toolkits: List[Toolkit]
    """Toolkits that were backed up."""

    size_bytes: int = 0
    """Total size of backup in bytes."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """
    Additional metadata.

    Common keys:
    - gtk_version: str
    - qt_version: str
    - system: str (OS name/version)
    - compressed: bool
    """

    def __str__(self) -> str:
        """Format backup for display."""
        return (
            f"Backup {self.backup_id}: {self.theme_name} "
            f"({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
        )


@dataclass
class PlannedChange:
    """
    Represents a planned change that would be made during theme application.

    Used by dry-run mode to show what would change without actually applying.
    """

    handler_name: str
    """Name of the handler that would make this change."""

    file_path: Path
    """Path to the file that would be modified or created."""

    change_type: str
    """Type of change: 'create', 'modify', 'delete'."""

    description: str
    """Human-readable description of what would change."""

    current_value: Optional[str] = None
    """Current value/content (if file exists)."""

    new_value: Optional[str] = None
    """New value/content that would be written."""

    toolkit: Optional[Toolkit] = None
    """Toolkit this change affects."""


@dataclass
class PlanResult:
    """
    Result of planning theme changes (dry-run mode).

    Contains all changes that would be made without actually applying them.
    """

    theme_name: str
    """Name of theme being planned."""

    planned_changes: List[PlannedChange]
    """List of all planned changes."""

    validation_result: Optional[ValidationResult] = None
    """Result of theme validation."""

    available_handlers: Dict[str, bool] = field(default_factory=dict)
    """Handler availability status."""

    estimated_files_affected: int = 0
    """Total number of files that would be affected."""

    warnings: List[str] = field(default_factory=list)
    """Warnings about the planned operation."""

    def __post_init__(self):
        """Calculate derived fields."""
        self.estimated_files_affected = len(
            set(change.file_path for change in self.planned_changes)
        )

    def get_changes_by_handler(self, handler_name: str) -> List[PlannedChange]:
        """Get all planned changes for a specific handler."""
        return [c for c in self.planned_changes if c.handler_name == handler_name]

    def get_changes_by_type(self, change_type: str) -> List[PlannedChange]:
        """Get all planned changes of a specific type."""
        return [c for c in self.planned_changes if c.change_type == change_type]


@dataclass
class ColorMapping:
    """
    Mapping between GTK and Qt color variables.

    Used by color translation utilities.
    """

    gtk_variable: str
    """GTK color variable name (e.g., "theme_bg_color")."""

    qt_variable: str
    """Qt color variable name (e.g., "BackgroundNormal")."""

    priority: str = "normal"
    """Priority: "critical", "high", "normal", "low"."""

    fallback: Optional[str] = None
    """Fallback color value if translation fails."""


# Type aliases for clarity
ThemeDict = Dict[str, ThemeInfo]
"""Dictionary mapping theme names to ThemeInfo objects."""

ColorPalette = Dict[str, str]
"""Dictionary mapping color variable names to color values."""

HandlerDict = Dict[str, "BaseHandler"]
"""Dictionary mapping handler names to handler instances."""


# Common color variable names
GTK_COLOR_VARIABLES = [
    # Background and foreground
    "theme_bg_color",
    "theme_fg_color",
    "theme_base_color",
    "theme_text_color",
    # Selection
    "theme_selected_bg_color",
    "theme_selected_fg_color",
    # Borders and shadows
    "borders",
    "shadow",
    # Special states
    "insensitive_bg_color",
    "insensitive_fg_color",
    "insensitive_base_color",
    # Links
    "link_color",
    "visited_link_color",
    # Semantic colors
    "success_color",
    "warning_color",
    "error_color",
]

LIBADWAITA_COLOR_VARIABLES = [
    # Window colors
    "window_bg_color",
    "window_fg_color",
    # View colors
    "view_bg_color",
    "view_fg_color",
    # Accent colors
    "accent_bg_color",
    "accent_fg_color",
    "accent_color",
    # Destructive colors
    "destructive_bg_color",
    "destructive_fg_color",
    "destructive_color",
    # Success colors
    "success_bg_color",
    "success_fg_color",
    "success_color",
    # Warning colors
    "warning_bg_color",
    "warning_fg_color",
    "warning_color",
    # Error colors
    "error_bg_color",
    "error_fg_color",
    "error_color",
    # Header bar
    "headerbar_bg_color",
    "headerbar_fg_color",
    "headerbar_border_color",
    "headerbar_backdrop_color",
    "headerbar_shade_color",
    # Sidebar
    "sidebar_bg_color",
    "sidebar_fg_color",
    "sidebar_backdrop_color",
    "sidebar_shade_color",
    # Cards
    "card_bg_color",
    "card_fg_color",
    "card_shade_color",
    # Popovers
    "popover_bg_color",
    "popover_fg_color",
    # Dialogs
    "dialog_bg_color",
    "dialog_fg_color",
    # Thumbnails
    "thumbnail_bg_color",
    "thumbnail_fg_color",
]

QT_COLOR_VARIABLES = [
    "BackgroundNormal",
    "BackgroundAlternate",
    "ForegroundNormal",
    "ForegroundInactive",
    "ForegroundActive",
    "ForegroundLink",
    "ForegroundVisited",
    "ForegroundNegative",
    "ForegroundNeutral",
    "ForegroundPositive",
    "Base",
    "Text",
    "Button",
    "ButtonText",
    "Highlight",
    "HighlightedText",
    "Link",
    "VisitedLink",
    "ToolTipBase",
    "ToolTipText",
]
