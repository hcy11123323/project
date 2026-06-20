"""Tests for the structured logging module."""

import json
import logging
import os
from io import StringIO
from unittest.mock import patch

import pytest

from src.logging import (
    JSONFormatter,
    TextFormatter,
    bind_context,
    clear_context,
    configure_logging_from_env,
    get_logger,
    log_browser_event,
    log_mcp_tool,
    log_operation,
    log_script_execution,
    log_timing,
    _get_log_level,
    _get_log_format,
    _initialize_root_logger,
    _context,
)


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging state between tests."""
    import src.logging

    src.logging._initialized = False
    src.logging._loggers.clear()
    clear_context()
    yield
    src.logging._initialized = False
    src.logging._loggers.clear()
    clear_context()


@pytest.fixture
def capture_logs():
    """Capture log output to a StringIO buffer."""
    handler = logging.StreamHandler(StringIO())
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(TextFormatter(use_colors=False))
    return handler


# ---------------------------------------------------------------------------
# Logger creation and naming
# ---------------------------------------------------------------------------


class TestGetLogger:
    def test_creates_logger_with_normalized_name(self):
        logger = get_logger("src.server")
        assert logger.name == "agentic_playwright.server"

    def test_creates_logger_for_main(self):
        logger = get_logger("__main__")
        assert logger.name == "agentic_playwright.main"

    def test_caches_loggers(self):
        logger1 = get_logger("src.test")
        logger2 = get_logger("src.test")
        assert logger1 is logger2

    def test_preserves_existing_prefix(self):
        logger = get_logger("agentic_playwright.core")
        assert logger.name == "agentic_playwright.core"

    def test_plain_name_gets_prefixed(self):
        logger = get_logger("custom_module")
        assert logger.name == "agentic_playwright.custom_module"

    def test_logger_level_matches_env(self):
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}):
            import src.logging
            src.logging._initialized = False
            src.logging._loggers.clear()
            logger = get_logger("src.level_test")
            assert logger.level == logging.WARNING


# ---------------------------------------------------------------------------
# Internal level/format helpers
# ---------------------------------------------------------------------------


class TestLogConfigHelpers:
    def test_get_log_level_default_is_info(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("LOG_LEVEL", None)
            assert _get_log_level() == logging.INFO

    def test_get_log_level_debug(self):
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            assert _get_log_level() == logging.DEBUG

    def test_get_log_level_case_insensitive(self):
        with patch.dict(os.environ, {"LOG_LEVEL": "warning"}):
            assert _get_log_level() == logging.WARNING

    def test_get_log_level_invalid_defaults_to_info(self):
        with patch.dict(os.environ, {"LOG_LEVEL": "BOGUS"}):
            assert _get_log_level() == logging.INFO

    def test_get_log_format_default_is_text(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("LOG_FORMAT", None)
            assert _get_log_format() == "text"

    def test_get_log_format_json(self):
        with patch.dict(os.environ, {"LOG_FORMAT": "JSON"}):
            assert _get_log_format() == "json"

    def test_get_log_format_case_insensitive(self):
        with patch.dict(os.environ, {"LOG_FORMAT": "Text"}):
            assert _get_log_format() == "text"


# ---------------------------------------------------------------------------
# Root logger initialization
# ---------------------------------------------------------------------------


class TestInitializeRootLogger:
    def test_idempotent(self):
        import src.logging

        _initialize_root_logger()
        assert src.logging._initialized is True
        root = logging.getLogger("agentic_playwright")
        handler_count = len(root.handlers)

        # Second call should be a no-op
        _initialize_root_logger()
        assert len(root.handlers) == handler_count

    def test_sets_propagate_false(self):
        _initialize_root_logger()
        root = logging.getLogger("agentic_playwright")
        assert root.propagate is False

    def test_json_format_creates_json_formatter(self):
        with patch.dict(os.environ, {"LOG_FORMAT": "json"}):
            import src.logging
            src.logging._initialized = False
            _initialize_root_logger()
            root = logging.getLogger("agentic_playwright")
            assert isinstance(root.handlers[0].formatter, JSONFormatter)

    def test_no_color_env_disables_colors(self):
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            import src.logging
            src.logging._initialized = False
            _initialize_root_logger()
            root = logging.getLogger("agentic_playwright")
            formatter = root.handlers[0].formatter
            assert isinstance(formatter, TextFormatter)
            assert formatter.use_colors is False

    def test_clears_existing_handlers_on_reinit(self):
        import src.logging
        _initialize_root_logger()
        root = logging.getLogger("agentic_playwright")
        root.addHandler(logging.StreamHandler())  # add extra
        src.logging._initialized = False
        _initialize_root_logger()
        # Should have exactly 1 handler after re-init
        assert len(root.handlers) == 1


# ---------------------------------------------------------------------------
# JSON formatter
# ---------------------------------------------------------------------------


class TestJSONFormatter:
    def test_formats_basic_record(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=10, msg="Test message", args=(), exc_info=None,
        )
        data = json.loads(formatter.format(record))

        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert "timestamp" in data

    def test_includes_extra_fields(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=10, msg="Test", args=(), exc_info=None,
        )
        record.operation = "screenshot"
        record.duration_ms = 150

        data = json.loads(formatter.format(record))
        assert data["extra"]["operation"] == "screenshot"
        assert data["extra"]["duration_ms"] == 150

    def test_includes_context(self):
        formatter = JSONFormatter()
        token = _context.set({"request_id": "abc123"})
        try:
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="test.py",
                lineno=10, msg="Test", args=(), exc_info=None,
            )
            data = json.loads(formatter.format(record))
            assert data["context"]["request_id"] == "abc123"
        finally:
            _context.reset(token)

    def test_includes_exception_info(self):
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py",
            lineno=10, msg="Error occurred", args=(), exc_info=exc_info,
        )
        data = json.loads(formatter.format(record))

        assert "exception" in data
        assert data["exception"]["type"] == "ValueError"
        assert data["exception"]["message"] == "test error"
        assert "traceback" in data["exception"]

    def test_debug_level_includes_source_location(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.DEBUG, pathname="/app/test.py",
            lineno=42, msg="Debug msg", args=(), exc_info=None,
        )
        record.funcName = "my_func"

        data = json.loads(formatter.format(record))
        assert "source" in data
        assert data["source"]["file"] == "/app/test.py"
        assert data["source"]["line"] == 42
        assert data["source"]["function"] == "my_func"

    def test_info_level_excludes_source_location(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="/app/test.py",
            lineno=42, msg="Info msg", args=(), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        assert "source" not in data

    def test_no_extra_field_when_none_present(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="clean", args=(), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        assert "extra" not in data

    def test_no_context_field_when_empty(self):
        formatter = JSONFormatter()
        clear_context()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="no ctx", args=(), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        assert "context" not in data

    def test_output_is_valid_json(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="unicode: 中文", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "中文" in parsed["message"]

    def test_args_are_interpolated(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="Hello %s, count=%d", args=("world", 42), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        assert data["message"] == "Hello world, count=42"


# ---------------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------------


class TestTextFormatter:
    def test_formats_basic_record(self):
        formatter = TextFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=10, msg="Test message", args=(), exc_info=None,
        )
        output = formatter.format(record)

        assert "INFO" in output
        assert "test" in output
        assert "Test message" in output

    def test_includes_extra_fields(self):
        formatter = TextFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=10, msg="Test", args=(), exc_info=None,
        )
        record.operation = "screenshot"

        output = formatter.format(record)
        assert "operation=screenshot" in output

    def test_long_name_truncated(self):
        formatter = TextFormatter(use_colors=False)
        record = logging.LogRecord(
            name="agentic_playwright.very_long_module_name_here",
            level=logging.INFO, pathname="test.py",
            lineno=1, msg="msg", args=(), exc_info=None,
        )
        output = formatter.format(record)
        # Should contain the truncated prefix (last 17 chars after "...")
        assert "..._module_name_here" in output

    def test_short_name_not_truncated(self):
        formatter = TextFormatter(use_colors=False)
        record = logging.LogRecord(
            name="short", level=logging.INFO, pathname="test.py",
            lineno=1, msg="msg", args=(), exc_info=None,
        )
        output = formatter.format(record)
        assert "short" in output

    def test_context_appears_in_output(self):
        formatter = TextFormatter(use_colors=False)
        token = _context.set({"req_id": "xyz"})
        try:
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="test.py",
                lineno=1, msg="msg", args=(), exc_info=None,
            )
            output = formatter.format(record)
            assert "req_id=xyz" in output
        finally:
            _context.reset(token)

    def test_exception_appended(self):
        formatter = TextFormatter(use_colors=False)
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py",
            lineno=1, msg="err", args=(), exc_info=exc_info,
        )
        output = formatter.format(record)
        assert "RuntimeError" in output
        assert "boom" in output
        assert "Traceback" in output

    def test_no_exception_when_none(self):
        formatter = TextFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="ok", args=(), exc_info=None,
        )
        output = formatter.format(record)
        assert "Traceback" not in output

    def test_color_codes_present_when_enabled(self, monkeypatch):
        # Force isatty to return True
        monkeypatch.setattr("sys.stderr.isatty", lambda: True)
        formatter = TextFormatter(use_colors=True)
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py",
            lineno=1, msg="err", args=(), exc_info=None,
        )
        output = formatter.format(record)
        # ANSI red for ERROR
        assert "\033[31m" in output

    def test_color_codes_absent_when_disabled(self):
        formatter = TextFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py",
            lineno=1, msg="err", args=(), exc_info=None,
        )
        output = formatter.format(record)
        assert "\033[" not in output

    def test_multiple_extra_fields(self):
        formatter = TextFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="msg", args=(), exc_info=None,
        )
        record.a = 1
        record.b = 2
        output = formatter.format(record)
        assert "a=1" in output
        assert "b=2" in output


# ---------------------------------------------------------------------------
# Context binding
# ---------------------------------------------------------------------------


class TestContextBinding:
    def test_bind_context_adds_values(self):
        assert _context.get() == {}

        with bind_context(request_id="abc", user_id="123"):
            ctx = _context.get()
            assert ctx["request_id"] == "abc"
            assert ctx["user_id"] == "123"

        assert _context.get() == {}

    def test_bind_context_nests(self):
        with bind_context(outer="a"):
            with bind_context(inner="b"):
                ctx = _context.get()
                assert ctx["outer"] == "a"
                assert ctx["inner"] == "b"

            assert _context.get() == {"outer": "a"}

    def test_clear_context(self):
        with bind_context(key="value"):
            clear_context()
            assert _context.get() == {}

    def test_bind_overwrites_existing_key(self):
        with bind_context(key="first"):
            with bind_context(key="second"):
                assert _context.get()["key"] == "second"
            assert _context.get()["key"] == "first"

    def test_bind_empty_is_noop(self):
        with bind_context():
            assert _context.get() == {}

    def test_context_restored_on_exception(self):
        with bind_context(k="v"):
            try:
                with bind_context(inner="boom"):
                    raise ValueError("fail")
            except ValueError:
                pass
            # Outer context should still be intact
            assert _context.get() == {"k": "v"}

    def test_clear_context_outside_block(self):
        clear_context()  # should not raise
        assert _context.get() == {}


# ---------------------------------------------------------------------------
# log_operation helper
# ---------------------------------------------------------------------------


class TestLogOperation:
    def test_logs_success(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_operation("screenshot", success=True, duration_ms=150)

        output = capture_logs.stream.getvalue()
        assert "screenshot" in output
        assert "completed" in output.lower() or "success" in output.lower()

    def test_logs_failure(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_operation("screenshot", success=False, error="timeout")

        output = capture_logs.stream.getvalue()
        assert "screenshot" in output
        assert "failed" in output.lower()

    def test_logs_with_extra_kwargs(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_operation("navigate", success=True, url="https://example.com", status=200)

        output = capture_logs.stream.getvalue()
        assert "navigate" in output

    def test_duration_ms_rounded(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_operation("op", success=True, duration_ms=123.456789)

        # Duration should be rounded to 2 decimal places in the log
        output = capture_logs.stream.getvalue()
        assert "123.46" in output

    def test_no_duration_when_none(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_operation("op", success=True)

        output = capture_logs.stream.getvalue()
        assert "op" in output

    def test_failure_uses_error_level(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_operation("op", success=False)

        output = capture_logs.stream.getvalue()
        assert "ERROR" in output


# ---------------------------------------------------------------------------
# log_timing context manager
# ---------------------------------------------------------------------------


class TestLogTiming:
    def test_logs_successful_timing(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        with log_timing("test_op") as meta:
            meta["extra"] = "value"

        output = capture_logs.stream.getvalue()
        assert "test_op" in output
        assert "ms" in output

    def test_logs_failed_timing(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        with pytest.raises(ValueError, match="test error"):
            with log_timing("test_op"):
                raise ValueError("test error")

        output = capture_logs.stream.getvalue()
        assert "test_op" in output
        assert "failed" in output.lower()

    def test_meta_dict_populated_on_success(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        with log_timing("op") as meta:
            meta["custom"] = "data"

        assert meta["success"] is True
        assert "duration_ms" in meta
        assert meta["duration_ms"] >= 0
        assert meta["custom"] == "data"

    def test_meta_dict_populated_on_failure(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        with pytest.raises(RuntimeError):
            with log_timing("op") as meta:
                meta["attempt"] = 1
                raise RuntimeError("nope")

        assert meta["success"] is False
        assert "duration_ms" in meta
        assert "error" in meta
        assert "nope" in meta["error"]

    def test_timing_with_extra_kwargs(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        with log_timing("page_load", url="https://example.com"):
            pass

        output = capture_logs.stream.getvalue()
        assert "page_load" in output

    def test_re_raises_exception(self):
        import src.logging
        src.logging._initialized = True

        with pytest.raises(KeyError, match="missing"):
            with log_timing("op"):
                raise KeyError("missing")


# ---------------------------------------------------------------------------
# Convenience logging functions
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    def test_log_browser_event(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.handlers.clear()
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_browser_event("launched", engine="playwright")

        output = capture_logs.stream.getvalue()
        assert "launched" in output
        assert "playwright" in output

    def test_log_mcp_tool_success(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_mcp_tool("run_script", success=True, duration_ms=100)

        output = capture_logs.stream.getvalue()
        assert "run_script" in output

    def test_log_mcp_tool_failure(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_mcp_tool("run_script", success=False)

        output = capture_logs.stream.getvalue()
        assert "run_script" in output
        assert "WARNING" in output or "failed" in output.lower()

    def test_log_mcp_tool_duration_rounded(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_mcp_tool("tool", success=True, duration_ms=99.999)

        output = capture_logs.stream.getvalue()
        assert "100.0" in output

    def test_log_script_execution_success(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_script_execution("test_script", success=True)

        output = capture_logs.stream.getvalue()
        assert "test_script" in output

    def test_log_script_execution_failure(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_script_execution("bad_script", success=False, duration_ms=50)

        output = capture_logs.stream.getvalue()
        assert "bad_script" in output
        assert "ERROR" in output

    def test_log_script_execution_with_extra(self, capture_logs):
        import src.logging
        root = logging.getLogger("agentic_playwright")
        root.addHandler(capture_logs)
        root.setLevel(logging.DEBUG)
        src.logging._initialized = True

        log_script_execution("s1", success=True, language="python")

        output = capture_logs.stream.getvalue()
        assert "s1" in output


# ---------------------------------------------------------------------------
# Environment-based configuration
# ---------------------------------------------------------------------------


class TestConfigureFromEnv:
    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "LOG_FORMAT": "json"})
    def test_configures_json_debug(self):
        configure_logging_from_env()
        import src.logging
        assert src.logging._initialized is True

    @patch.dict(os.environ, {"LOG_LEVEL": "WARNING", "LOG_FORMAT": "text"})
    def test_configures_text_warning(self):
        configure_logging_from_env()
        import src.logging
        assert src.logging._initialized is True

    def test_reconfigures_after_env_change(self):
        import src.logging

        # First init with default
        configure_logging_from_env()
        assert src.logging._initialized is True

        # Change env and reconfigure
        with patch.dict(os.environ, {"LOG_LEVEL": "CRITICAL", "LOG_FORMAT": "json"}):
            configure_logging_from_env()
            assert src.logging._initialized is True
            root = logging.getLogger("agentic_playwright")
            assert isinstance(root.handlers[0].formatter, JSONFormatter)

    def test_clears_logger_cache_on_reconfigure(self):
        import src.logging

        logger1 = get_logger("src.cached")
        configure_logging_from_env()
        logger2 = get_logger("src.cached")
        # After reconfigure the cache was cleared, so these are new instances
        # (but same underlying stdlib logger)
        assert logger2.name == logger1.name
