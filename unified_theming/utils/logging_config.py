"""
Logging configuration for Unified Theming Application.

This module provides centralized logging setup with support for
console and file logging, colored output, and proper formatting.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


# ANSI color codes for console output
class LogColors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Levels
    DEBUG = "\033[36m"  # Cyan
    INFO = "\033[32m"  # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"  # Red
    CRITICAL = "\033[35m"  # Magenta

    # Components
    TIME = "\033[90m"  # Gray
    MODULE = "\033[94m"  # Blue


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to console output.

    Only adds colors when output is a TTY (terminal).
    """

    LEVEL_COLORS = {
        logging.DEBUG: LogColors.DEBUG,
        logging.INFO: LogColors.INFO,
        logging.WARNING: LogColors.WARNING,
        logging.ERROR: LogColors.ERROR,
        logging.CRITICAL: LogColors.CRITICAL,
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        use_colors: Optional[bool] = True,
    ):
        """
        Initialize formatter.

        Args:
            fmt: Log format string
            datefmt: Date format string
            use_colors: Whether to use colors (auto-detected if None)
        """
        super().__init__(fmt, datefmt)

        # Auto-detect if we should use colors
        if use_colors is None:
            use_colors = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        if not self.use_colors:
            return super().format(record)

        # Save original values
        levelname = record.levelname
        name = record.name
        msg = record.getMessage()

        # Add colors
        level_color = self.LEVEL_COLORS.get(record.levelno, "")
        record.levelname = f"{level_color}{levelname}{LogColors.RESET}"
        record.name = f"{LogColors.MODULE}{name}{LogColors.RESET}"

        # Format the record
        formatted = super().format(record)

        # Restore original values (for other handlers)
        record.levelname = levelname
        record.name = name

        return formatted


def get_log_directory() -> Path:
    """
    Get the application log directory.

    Returns:
        Path to log directory (creates if doesn't exist)
    """
    # Use XDG_STATE_HOME if available, otherwise ~/.local/state
    state_home = os.getenv("XDG_STATE_HOME")
    if state_home:
        log_dir = Path(state_home) / "unified-theming"
    else:
        log_dir = Path.home() / ".local" / "state" / "unified-theming"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
    file_output: bool = True,
    colored_output: Optional[bool] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 3,
) -> logging.Logger:
    """
    Configure application-wide logging.

    This should be called once at application startup.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: auto-generated in log directory)
        console_output: Whether to output to console
        file_output: Whether to output to file
        colored_output: Whether to use colored console output (auto-detect if None)
        max_file_size: Maximum size of log file before rotation (bytes)
        backup_count: Number of backup log files to keep

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging(log_level="DEBUG")
        >>> logger.info("Application started")
        [2025-10-20 10:30:45] [INFO] [unified_theming] Application started
    """
    # Get root logger for our application
    logger = logging.getLogger("unified_theming")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        console_format = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        console_formatter = ColoredFormatter(
            console_format, datefmt="%Y-%m-%d %H:%M:%S", use_colors=colored_output
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if file_output:
        if log_file is None:
            log_dir = get_log_directory()
            log_file = log_dir / "unified-theming.log"

        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)

        file_format = (
            "[%(asctime)s] [%(levelname)s] [%(name)s] "
            "[%(module)s:%(funcName)s:%(lineno)d] %(message)s"
        )
        file_formatter = logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    logger.info(f"Logging initialized at {log_level} level")
    if file_output and log_file:
        logger.debug(f"Log file: {log_file}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Parsing theme file")
    """
    # Ensure name starts with our application namespace
    if not name.startswith("unified_theming"):
        name = f"unified_theming.{name}"

    return logging.getLogger(name)


def log_exception(
    logger: logging.Logger, exception: Exception, message: str = "An error occurred"
) -> None:
    """
    Log an exception with full traceback.

    Args:
        logger: Logger instance
        exception: Exception to log
        message: Additional context message

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_exception(logger, e, "Failed to apply theme")
    """
    logger.error(f"{message}: {exception}", exc_info=True)


def set_log_level(level: str) -> None:
    """
    Change the log level at runtime.

    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> set_log_level("DEBUG")  # Enable verbose logging
    """
    logger = logging.getLogger("unified_theming")
    logger.setLevel(getattr(logging, level.upper()))
    logger.info(f"Log level changed to {level}")


# Logging guidelines for developers
"""
Logging Level Guidelines
========================

DEBUG:
------
- Detailed diagnostic information
- Variable values, intermediate results
- Entry/exit of major functions
- File paths being accessed
- Theme parsing details

Example:
    logger.debug(f"Parsing theme file: {theme_path}")
    logger.debug(f"Extracted {len(colors)} colors from CSS")

INFO:
-----
- General informational messages
- Major operations starting/completing
- User actions
- Theme applications
- Configuration changes

Example:
    logger.info(f"Applying theme '{theme_name}' to {len(targets)} toolkits")
    logger.info("Theme applied successfully")

WARNING:
--------
- Non-critical issues
- Unexpected but handled conditions
- Missing optional dependencies
- Theme compatibility warnings
- Deprecated feature usage

Example:
    logger.warning(f"Theme '{theme_name}' missing GTK4 support")
    logger.warning("Kvantum not installed, using kdeglobals only")

ERROR:
------
- Errors that prevent specific operations
- Handler failures (recoverable)
- File operation errors
- Configuration errors

Example:
    logger.error(f"Failed to apply Qt theme: {error}")
    logger.error(f"Cannot write to {config_file}: Permission denied")

CRITICAL:
---------
- System-breaking errors
- Data corruption
- Unrecoverable failures
- Should rarely be used

Example:
    logger.critical("Backup restoration failed - manual intervention required")
    logger.critical("Application configuration corrupted")

Best Practices:
---------------

1. Use structured logging:
   logger.info("Theme applied", extra={'theme': theme_name, 'toolkit': 'gtk4'})

2. Include context:
   logger.error(f"Failed to parse {file_path}: {error}")
   # NOT: logger.error("Parse error")

3. Use lazy string formatting:
   logger.debug("Processing %s with %d items", name, count)
   # NOT: logger.debug(f"Processing {name} with {count} items")

4. Log exceptions properly:
   try:
       risky_operation()
   except Exception as e:
       logger.exception("Operation failed")  # Includes traceback
       # OR
       log_exception(logger, e, "Operation failed")

5. Don't log sensitive information:
   # NEVER log passwords, tokens, personal data
"""


# Pre-configured logger for quick imports
default_logger = logging.getLogger("unified_theming")

# Convenience exports
__all__ = [
    "setup_logging",
    "get_logger",
    "log_exception",
    "set_log_level",
    "LogColors",
    "ColoredFormatter",
    "default_logger",
]
