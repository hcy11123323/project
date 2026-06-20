"""
Structured logging module for agentic-playwright-mcp.

Provides JSON-formatted logs for production and human-readable output
for development. Supports context binding for request/operation tracking.

Usage:
    from src.logging import get_logger, bind_context, log_operation

    logger = get_logger(__name__)
    logger.info("Browser launched", extra={"engine": "playwright"})

    with bind_context(operation="screenshot", url="https://example.com"):
        log_operation("screenshot", success=True, duration_ms=150)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

# ---------------------------------------------------------------------------
# Context variables for request/operation tracking
# ---------------------------------------------------------------------------

_context: ContextVar[dict[str, Any]] = ContextVar("log_context", default={})

# ---------------------------------------------------------------------------
# Log level configuration from environment
# ---------------------------------------------------------------------------

_LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _get_log_level() -> int:
    """Get log level from environment variable or default to INFO."""
    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    return _LOG_LEVELS.get(level_str, logging.INFO)


def _get_log_format() -> str:
    """Get log format from environment: 'json' or 'text'."""
    return os.getenv("LOG_FORMAT", "text").lower()


# ---------------------------------------------------------------------------
# JSON formatter for structured logging
# ---------------------------------------------------------------------------

class JSONFormatter(logging.Formatter):
    """Format log records as JSON lines for machine consumption."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context from ContextVar
        ctx = _context.get()
        if ctx:
            log_entry["context"] = ctx

        # Add extra fields from the log call
        standard_attrs = logging.LogRecord(
            "", 0, "", 0, "", (), None
        ).__dict__.keys()
        extra = {
            k: v
            for k, v in record.__dict__.items()
            if k not in standard_attrs and not k.startswith("_")
        }
        if extra:
            log_entry["extra"] = extra

        # Add exception info if present
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add source location for debug
        if record.levelno <= logging.DEBUG:
            log_entry["source"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        return json.dumps(log_entry, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# Human-readable formatter for development
# ---------------------------------------------------------------------------

class TextFormatter(logging.Formatter):
    """Format log records as human-readable text for development."""

    # ANSI color codes for terminal output
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        # Timestamp
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]

        # Level with optional color
        level = record.levelname
        if self.use_colors:
            color = self.COLORS.get(level, "")
            level = f"{color}{level}{self.RESET}"

        # Logger name (shortened)
        name = record.name
        if len(name) > 20:
            name = "..." + name[-17:]

        # Message
        message = record.getMessage()

        # Context
        ctx = _context.get()
        context_str = ""
        if ctx:
            context_parts = [f"{k}={v}" for k, v in ctx.items()]
            context_str = f" [{', '.join(context_parts)}]"

        # Extra fields
        standard_attrs = logging.LogRecord(
            "", 0, "", 0, "", (), None
        ).__dict__.keys()
        extra = {
            k: v
            for k, v in record.__dict__.items()
            if k not in standard_attrs and not k.startswith("_")
        }
        extra_str = ""
        if extra:
            extra_parts = [f"{k}={v}" for k, v in extra.items()]
            extra_str = f" {' '.join(extra_parts)}"

        # Format the line
        line = f"{timestamp} {level: <19} {name: <20} {message}{context_str}{extra_str}"

        # Add exception if present
        if record.exc_info and record.exc_info[1]:
            line += f"\n{self.formatException(record.exc_info)}"

        return line


# ---------------------------------------------------------------------------
# Logger factory with singleton pattern
# ---------------------------------------------------------------------------

_loggers: dict[str, logging.Logger] = {}
_initialized = False


def _initialize_root_logger() -> None:
    """Initialize the root logger with the appropriate handler."""
    global _initialized
    if _initialized:
        return

    root_logger = logging.getLogger("agentic_playwright")
    root_logger.setLevel(_get_log_level())

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(_get_log_level())

    # Set formatter based on environment
    log_format = _get_log_format()
    if log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        # Check if NO_COLOR is set (for MCP stdio transport)
        no_color = os.getenv("NO_COLOR", "").lower() in ("1", "true", "yes")
        handler.setFormatter(TextFormatter(use_colors=not no_color))

    root_logger.addHandler(handler)

    # Prevent propagation to root logger
    root_logger.propagate = False

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the given name.

    Args:
        name: Logger name, typically __name__ from the calling module.

    Returns:
        Configured logger instance.
    """
    _initialize_root_logger()

    # Normalize name to use dot notation under agentic_playwright
    if not name.startswith("agentic_playwright"):
        # Convert src.module to agentic_playwright.module
        if name.startswith("src."):
            name = "agentic_playwright." + name[4:]
        elif name == "__main__":
            name = "agentic_playwright.main"
        else:
            name = "agentic_playwright." + name

    if name not in _loggers:
        logger = logging.getLogger(name)
        logger.setLevel(_get_log_level())
        _loggers[name] = logger

    return _loggers[name]


# ---------------------------------------------------------------------------
# Context management for operation tracking
# ---------------------------------------------------------------------------

@contextmanager
def bind_context(**kwargs: Any) -> Generator[None, None, None]:
    """Bind context variables for the duration of a block.

    Context is included in all log messages within the block.

    Args:
        **kwargs: Key-value pairs to add to the logging context.

    Example:
        with bind_context(request_id="abc123", user_id="user456"):
            logger.info("Processing request")
            # Log includes: context={"request_id": "abc123", "user_id": "user456"}
    """
    old_context = _context.get().copy()
    new_context = {**old_context, **kwargs}
    token = _context.set(new_context)
    try:
        yield
    finally:
        _context.reset(token)


def clear_context() -> None:
    """Clear all context variables."""
    _context.set({})


# ---------------------------------------------------------------------------
# Operation logging helper
# ---------------------------------------------------------------------------

def log_operation(
    operation: str,
    *,
    success: bool,
    duration_ms: float | None = None,
    logger_name: str = "agentic_playwright.operations",
    **kwargs: Any,
) -> None:
    """Log an operation with structured metadata.

    Args:
        operation: Operation name (e.g., "screenshot", "browser_launch").
        success: Whether the operation succeeded.
        duration_ms: Operation duration in milliseconds.
        logger_name: Logger to use.
        **kwargs: Additional metadata to include.

    Example:
        log_operation(
            "navigate",
            success=True,
            duration_ms=245,
            url="https://example.com",
            status_code=200,
        )
    """
    logger = get_logger(logger_name)

    extra = {
        "operation": operation,
        "success": success,
        **kwargs,
    }
    if duration_ms is not None:
        extra["duration_ms"] = round(duration_ms, 2)

    if success:
        logger.info("Operation completed: %s", operation, extra=extra)
    else:
        logger.error("Operation failed: %s", operation, extra=extra)


# ---------------------------------------------------------------------------
# Performance timer context manager
# ---------------------------------------------------------------------------

@contextmanager
def log_timing(
    operation: str,
    *,
    logger_name: str = "agentic_playwright.performance",
    **kwargs: Any,
) -> Generator[dict[str, Any], None, None]:
    """Time a block and log its duration.

    Yields a dict that can be updated with additional metadata.

    Args:
        operation: Operation name.
        logger_name: Logger to use.
        **kwargs: Additional metadata to include in the log.

    Example:
        with log_timing("page_load", url=url) as meta:
            page.goto(url)
            meta["status_code"] = page.response.status
    """
    logger = get_logger(logger_name)
    meta: dict[str, Any] = {"operation": operation, **kwargs}
    start_time = time.monotonic()

    try:
        yield meta
        duration_ms = (time.monotonic() - start_time) * 1000
        meta["duration_ms"] = round(duration_ms, 2)
        meta["success"] = True
        logger.info("Timing: %s completed in %.2fms", operation, duration_ms, extra=meta)
    except Exception as exc:
        duration_ms = (time.monotonic() - start_time) * 1000
        meta["duration_ms"] = round(duration_ms, 2)
        meta["success"] = False
        meta["error"] = str(exc)
        logger.error(
            "Timing: %s failed after %.2fms: %s",
            operation,
            duration_ms,
            exc,
            extra=meta,
            exc_info=True,
        )
        raise


# ---------------------------------------------------------------------------
# Convenience functions for common logging patterns
# ---------------------------------------------------------------------------

def log_browser_event(event: str, **kwargs: Any) -> None:
    """Log a browser-related event."""
    logger = get_logger("agentic_playwright.browser")
    logger.info("Browser event: %s", event, extra={"event": event, **kwargs})


def log_mcp_tool(tool_name: str, *, success: bool, duration_ms: float | None = None, **kwargs: Any) -> None:
    """Log an MCP tool invocation."""
    logger = get_logger("agentic_playwright.mcp")
    extra = {"tool": tool_name, "success": success, **kwargs}
    if duration_ms is not None:
        extra["duration_ms"] = round(duration_ms, 2)

    if success:
        logger.info("MCP tool executed: %s", tool_name, extra=extra)
    else:
        logger.warning("MCP tool failed: %s", tool_name, extra=extra)


def log_script_execution(script_id: str, *, success: bool, duration_ms: float | None = None, **kwargs: Any) -> None:
    """Log a script execution."""
    logger = get_logger("agentic_playwright.script")
    extra = {"script_id": script_id, "success": success, **kwargs}
    if duration_ms is not None:
        extra["duration_ms"] = round(duration_ms, 2)

    if success:
        logger.info("Script executed: %s", script_id, extra=extra)
    else:
        logger.error("Script failed: %s", script_id, extra=extra)


# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------

def configure_logging_from_env() -> None:
    """Reconfigure logging based on current environment variables.

    Call this after loading .env to apply any logging configuration changes.

    Environment variables:
        LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
        LOG_FORMAT: json or text (default: text)
        NO_COLOR: Disable ANSI colors (set automatically for stdio transport)
    """
    global _initialized
    _initialized = False
    _loggers.clear()
    _initialize_root_logger()
