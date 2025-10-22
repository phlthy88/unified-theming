"""
Custom exceptions for Unified Theming Application.

This module defines all custom exceptions used throughout the application,
organized in a clear hierarchy for proper error handling.
"""

from typing import Optional, List
from pathlib import Path


class UnifiedThemingError(Exception):
    """
    Base exception for all unified theming errors.

    All custom exceptions in this application inherit from this class,
    making it easy to catch any application-specific error.
    """

    def __init__(self, message: str, details: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            details: Additional technical details for debugging
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        """Format exception for display."""
        msg = self.message
        if self.details:
            msg += f"\nDetails: {self.details}"
        return msg


# =============================================================================
# Theme Discovery and Parsing Errors
# =============================================================================

class ThemeDiscoveryError(UnifiedThemingError):
    """Raised when theme discovery fails."""

    def __init__(self, message: str, directory: Optional[Path] = None,
                 details: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            directory: Directory that failed to scan
            details: Additional details
        """
        super().__init__(message, details)
        self.directory = directory


class ThemeNotFoundError(UnifiedThemingError):
    """Raised when requested theme doesn't exist."""

    def __init__(self, theme_name: str, searched_paths: Optional[List[Path]] = None):
        """
        Initialize exception.

        Args:
            theme_name: Name of theme that wasn't found
            searched_paths: List of paths that were searched
        """
        message = f"Theme '{theme_name}' not found"
        if searched_paths:
            paths_str = ", ".join(str(p) for p in searched_paths)
            details = f"Searched in: {paths_str}"
        else:
            details = None

        super().__init__(message, details)
        self.theme_name = theme_name
        self.searched_paths = searched_paths or []


class InvalidThemeError(UnifiedThemingError):
    """Raised when theme structure is invalid or malformed."""

    def __init__(self, theme_name: str, reason: str,
                 theme_path: Optional[Path] = None):
        """
        Initialize exception.

        Args:
            theme_name: Name of invalid theme
            reason: Why the theme is invalid
            theme_path: Path to theme directory
        """
        message = f"Theme '{theme_name}' is invalid: {reason}"
        details = f"Theme path: {theme_path}" if theme_path else None

        super().__init__(message, details)
        self.theme_name = theme_name
        self.reason = reason
        self.theme_path = theme_path


class ThemeParseError(UnifiedThemingError):
    """Raised when theme file parsing fails."""

    def __init__(self, file_path: Path, reason: str,
                 line_number: Optional[int] = None):
        """
        Initialize exception.

        Args:
            file_path: Path to file that failed to parse
            reason: Why parsing failed
            line_number: Line number where error occurred (if known)
        """
        message = f"Failed to parse {file_path.name}: {reason}"
        details = f"File: {file_path}"
        if line_number is not None:
            details += f", Line: {line_number}"

        super().__init__(message, details)
        self.file_path = file_path
        self.reason = reason
        self.line_number = line_number


# =============================================================================
# Theme Application Errors
# =============================================================================

class ThemeApplicationError(UnifiedThemingError):
    """
    Raised when theme application fails.

    This is the main exception for failures during theme application.
    It includes information about which toolkit failed and whether
    the error is recoverable.
    """

    def __init__(self, message: str, toolkit: Optional[str] = None,
                 recoverable: bool = True, details: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            toolkit: Name of toolkit that failed (e.g., "gtk4", "qt5")
            recoverable: Whether the error can be recovered from
            details: Additional technical details
        """
        super().__init__(message, details)
        self.toolkit = toolkit
        self.recoverable = recoverable

    def __str__(self) -> str:
        """Format exception for display."""
        msg = self.message
        if self.toolkit:
            msg = f"[{self.toolkit}] {msg}"
        if not self.recoverable:
            msg = f"CRITICAL: {msg}"
        if self.details:
            msg += f"\nDetails: {self.details}"
        return msg


class HandlerNotAvailableError(ThemeApplicationError):
    """Raised when a required handler is not available."""

    def __init__(self, handler_name: str, reason: str):
        """
        Initialize exception.

        Args:
            handler_name: Name of unavailable handler
            reason: Why the handler is not available
        """
        message = f"Handler '{handler_name}' is not available: {reason}"
        super().__init__(message, toolkit=handler_name, recoverable=True)
        self.handler_name = handler_name


class ToolkitNotInstalledError(ThemeApplicationError):
    """Raised when target toolkit is not installed on the system."""

    def __init__(self, toolkit: str, suggestion: Optional[str] = None):
        """
        Initialize exception.

        Args:
            toolkit: Name of missing toolkit (e.g., "qt5", "flatpak")
            suggestion: Suggestion for how to install the toolkit
        """
        message = f"Toolkit '{toolkit}' is not installed"
        if suggestion:
            message += f". {suggestion}"

        super().__init__(message, toolkit=toolkit, recoverable=True)
        self.suggestion = suggestion


class ColorTranslationError(ThemeApplicationError):
    """Raised when color translation between toolkits fails."""

    def __init__(self, source_toolkit: str, target_toolkit: str,
                 color_variable: str, reason: str):
        """
        Initialize exception.

        Args:
            source_toolkit: Source toolkit (e.g., "gtk")
            target_toolkit: Target toolkit (e.g., "qt")
            color_variable: Color variable that failed to translate
            reason: Why translation failed
        """
        message = (f"Failed to translate '{color_variable}' from "
                   f"{source_toolkit} to {target_toolkit}: {reason}")

        super().__init__(message, toolkit=target_toolkit, recoverable=True)
        self.source_toolkit = source_toolkit
        self.target_toolkit = target_toolkit
        self.color_variable = color_variable


class CSSGenerationError(ThemeApplicationError):
    """Raised when CSS generation fails."""

    def __init__(self, theme_name: str, reason: str,
                 invalid_colors: Optional[List[str]] = None):
        """
        Initialize exception.

        Args:
            theme_name: Name of theme for which CSS generation failed
            reason: Why CSS generation failed
            invalid_colors: List of invalid color variables (if applicable)
        """
        message = f"Failed to generate CSS for theme '{theme_name}': {reason}"
        details = None
        if invalid_colors:
            details = f"Invalid colors: {', '.join(invalid_colors)}"

        super().__init__(message, toolkit="gtk", recoverable=False,
                         details=details)
        self.theme_name = theme_name
        self.invalid_colors = invalid_colors or []


# =============================================================================
# Configuration and Backup Errors
# =============================================================================

class BackupError(UnifiedThemingError):
    """Raised when configuration backup fails."""

    def __init__(self, message: str, backup_path: Optional[Path] = None,
                 details: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            backup_path: Path where backup was attempted
            details: Additional details
        """
        super().__init__(message, details)
        self.backup_path = backup_path


class BackupNotFoundError(BackupError):
    """Raised when requested backup doesn't exist."""

    def __init__(self, backup_id: str, backup_dir: Optional[Path] = None):
        """
        Initialize exception.

        Args:
            backup_id: ID of backup that wasn't found
            backup_dir: Directory where backups are stored
        """
        message = f"Backup '{backup_id}' not found"
        details = f"Backup directory: {backup_dir}" if backup_dir else None

        super().__init__(message, details=details)
        self.backup_id = backup_id


class RollbackError(UnifiedThemingError):
    """Raised when rollback operation fails."""

    def __init__(self, message: str, backup_id: Optional[str] = None,
                 partial_rollback: bool = False, details: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            backup_id: ID of backup that failed to restore
            partial_rollback: Whether rollback partially succeeded
            details: Additional details
        """
        super().__init__(message, details)
        self.backup_id = backup_id
        self.partial_rollback = partial_rollback


class ConfigurationError(UnifiedThemingError):
    """Raised when application configuration is invalid."""

    def __init__(self, message: str, config_key: Optional[str] = None,
                 invalid_value: Optional[str] = None, details: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            config_key: Configuration key that is invalid
            invalid_value: The invalid value
            details: Additional details
        """
        super().__init__(message, details)
        self.config_key = config_key
        self.invalid_value = invalid_value


# =============================================================================
# File System Errors
# =============================================================================

class FileSystemError(UnifiedThemingError):
    """Base class for file system related errors."""

    def __init__(self, message: str, path: Optional[Path] = None,
                 details: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            path: File or directory path related to error
            details: Additional details
        """
        super().__init__(message, details)
        self.path = path


class FilePermissionError(FileSystemError):
    """Raised when file operation fails due to permissions."""

    def __init__(self, path: Path, operation: str):
        """
        Initialize exception.

        Args:
            path: Path that couldn't be accessed
            operation: Operation that was attempted (e.g., "read", "write")
        """
        message = f"Permission denied: Cannot {operation} {path}"
        super().__init__(message, path=path)
        self.operation = operation


class FileReadError(FileSystemError):
    """Raised when file read operation fails."""

    def __init__(self, message: str, path: Optional[Path] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            path: Path that couldn't be read from
        """
        super().__init__(message, path=path)


class FileWriteError(FileSystemError):
    """Raised when file write operation fails."""

    def __init__(self, path: Path, reason: str):
        """
        Initialize exception.

        Args:
            path: Path that couldn't be written to
            reason: Why the write failed
        """
        message = f"Failed to write to {path}: {reason}"
        super().__init__(message, path=path)


class DirectoryNotFoundError(FileSystemError):
    """Raised when expected directory doesn't exist."""

    def __init__(self, path: Path, create_suggestion: bool = True):
        """
        Initialize exception.

        Args:
            path: Directory that doesn't exist
            create_suggestion: Whether to suggest creating the directory
        """
        message = f"Directory not found: {path}"
        if create_suggestion:
            details = "You may need to create this directory first"
        else:
            details = None

        super().__init__(message, path=path, details=details)


# =============================================================================
# Validation Errors
# =============================================================================

class ValidationError(UnifiedThemingError):
    """Raised when validation fails."""

    def __init__(self, message: str, validation_errors: Optional[List[str]] = None,
                 details: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Error message
            validation_errors: List of specific validation errors
            details: Additional details
        """
        super().__init__(message, details)
        self.validation_errors = validation_errors or []

    def __str__(self) -> str:
        """Format exception for display."""
        msg = self.message
        if self.validation_errors:
            msg += "\nValidation errors:"
            for error in self.validation_errors:
                msg += f"\n  - {error}"
        if self.details:
            msg += f"\nDetails: {self.details}"
        return msg


class ColorValidationError(ValidationError):
    """Raised when color value validation fails."""

    def __init__(self, color_variable: str, color_value: str, reason: str):
        """
        Initialize exception.

        Args:
            color_variable: Name of color variable
            color_value: Invalid color value
            reason: Why the color value is invalid
        """
        message = (f"Invalid color value for '{color_variable}': "
                   f"'{color_value}' - {reason}")

        super().__init__(message)
        self.color_variable = color_variable
        self.color_value = color_value


class CSSValidationError(ValidationError):
    """Raised when CSS validation fails."""

    def __init__(self, css_file: Path, errors: List[str]):
        """
        Initialize exception.

        Args:
            css_file: Path to CSS file with errors
            errors: List of CSS syntax errors
        """
        message = f"CSS validation failed for {css_file.name}"

        super().__init__(message, validation_errors=errors)
        self.css_file = css_file


# =============================================================================
# System Integration Errors
# =============================================================================

class GSettingsError(UnifiedThemingError):
    """Raised when GSettings operation fails."""

    def __init__(self, schema: str, key: str, operation: str, reason: str):
        """
        Initialize exception.

        Args:
            schema: GSettings schema
            key: GSettings key
            operation: Operation that failed (e.g., "read", "write")
            reason: Why the operation failed
        """
        message = f"GSettings {operation} failed for {schema}:{key}: {reason}"

        super().__init__(message)
        self.schema = schema
        self.key = key
        self.operation = operation


class SubprocessError(UnifiedThemingError):
    """Raised when subprocess execution fails."""

    def __init__(self, command: str, returncode: int, stderr: Optional[str] = None):
        """
        Initialize exception.

        Args:
            command: Command that was executed
            returncode: Non-zero return code
            stderr: Standard error output from command
        """
        message = f"Command failed with exit code {returncode}: {command}"
        details = f"stderr: {stderr}" if stderr else None

        super().__init__(message, details)
        self.command = command
        self.returncode = returncode
        self.stderr = stderr


# =============================================================================
# Utility Functions
# =============================================================================

def format_exception_chain(exception: Exception) -> str:
    """
    Format exception chain for logging.

    Args:
        exception: Exception to format

    Returns:
        Formatted string with exception chain
    """
    messages = []
    current = exception

    while current is not None:
        if isinstance(current, UnifiedThemingError):
            messages.append(str(current))
        else:
            messages.append(f"{type(current).__name__}: {str(current)}")

        current = current.__cause__

    return "\n".join(messages)


def is_recoverable_error(exception: Exception) -> bool:
    """
    Check if an exception is recoverable.

    Args:
        exception: Exception to check

    Returns:
        True if error is recoverable, False otherwise
    """
    if isinstance(exception, ThemeApplicationError):
        return exception.recoverable

    # These errors are generally recoverable
    recoverable_types = (
        HandlerNotAvailableError,
        ToolkitNotInstalledError,
        ColorTranslationError,
    )

    return isinstance(exception, recoverable_types)
