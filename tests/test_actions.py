"""Tests for layer_1.actions — atomic Playwright operations."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.layer_1.actions import do_click, do_fill, do_goto, do_screenshot


# ---------------------------------------------------------------------------
# do_goto
# ---------------------------------------------------------------------------


class TestDoGoto:
    """Tests for do_goto()."""

    def test_successful_navigation(self, mock_page):
        """Should return success message with HTTP status."""
        result = do_goto(mock_page, "https://example.com")
        assert "导航成功" in result
        assert "200" in result
        mock_page.goto.assert_called_once_with("https://example.com", wait_until="domcontentloaded")

    def test_timeout(self, mock_page):
        """Should handle PlaywrightTimeoutError gracefully."""
        mock_page.goto.side_effect = PlaywrightTimeoutError("timeout")
        result = do_goto(mock_page, "https://slow.com")
        assert "超时" in result

    def test_generic_error(self, mock_page):
        """Should handle generic exceptions."""
        mock_page.goto.side_effect = RuntimeError("network error")
        result = do_goto(mock_page, "https://bad.com")
        assert "失败" in result

    def test_null_response(self, mock_page):
        """Should handle goto returning None."""
        mock_page.goto.return_value = None
        result = do_goto(mock_page, "https://example.com")
        assert "unknown" in result


# ---------------------------------------------------------------------------
# do_click
# ---------------------------------------------------------------------------


class TestDoClick:
    """Tests for do_click()."""

    def test_first_selector_visible(self, mock_page):
        """Should use the first visible selector."""
        mock_page.is_visible.return_value = True
        result = do_click(mock_page, ["#btn", ".btn"])
        assert result["success"] is True
        assert result["used_selector"] == "#btn"
        assert result["index"] == 0

    def test_fallback_to_second_selector(self, mock_page):
        """Should fall back to second selector when first is not visible."""
        mock_page.is_visible.side_effect = [False, True]
        result = do_click(mock_page, ["#gone", ".btn"])
        assert result["success"] is True
        assert result["used_selector"] == ".btn"
        assert result["index"] == 1

    def test_all_selectors_fail(self, mock_page):
        """Should return failure when no selector is visible."""
        mock_page.is_visible.return_value = False
        result = do_click(mock_page, ["#a", "#b"])
        assert result["success"] is False
        assert "所有选择器均不可用" in result["error"]

    def test_click_timeout_continues(self, mock_page):
        """Should continue to next selector on click timeout."""
        # First selector: visible but click times out
        # Second selector: visible and click succeeds
        mock_page.is_visible.side_effect = [True, True]
        mock_page.click.side_effect = [PlaywrightTimeoutError("timeout"), None]
        result = do_click(mock_page, ["#slow", "#fast"])
        assert result["success"] is True
        assert result["used_selector"] == "#fast"

    def test_empty_selector_list(self, mock_page):
        """Should handle empty selector list."""
        result = do_click(mock_page, [])
        assert result["success"] is False


# ---------------------------------------------------------------------------
# do_fill
# ---------------------------------------------------------------------------


class TestDoFill:
    """Tests for do_fill()."""

    def test_successful_fill(self, mock_page):
        """Should fill the first visible input."""
        mock_page.is_visible.return_value = True
        result = do_fill(mock_page, ["#input"], "hello")
        assert result["success"] is True
        assert result["used_selector"] == "#input"
        mock_page.fill.assert_called_once_with("#input", "hello", timeout=5000)

    def test_fallback_fill(self, mock_page):
        """Should fall back to second selector."""
        mock_page.is_visible.side_effect = [False, True]
        result = do_fill(mock_page, ["#gone", "#real"], "test")
        assert result["success"] is True
        assert result["used_selector"] == "#real"

    def test_all_selectors_fail(self, mock_page):
        """Should return failure when no selector is visible."""
        mock_page.is_visible.return_value = False
        result = do_fill(mock_page, ["#a"], "val")
        assert result["success"] is False


# ---------------------------------------------------------------------------
# do_screenshot
# ---------------------------------------------------------------------------


class TestDoScreenshot:
    """Tests for do_screenshot()."""

    @patch("src.layer_1.actions.os.makedirs")
    def test_screenshot_saves(self, makedirs, mock_page):
        """Should call page.screenshot and return the path."""
        result = do_screenshot(mock_page, "screenshots/test.png")
        assert result == "screenshots/test.png"
        mock_page.screenshot.assert_called_once_with(path="screenshots/test.png", full_page=True)

    @patch("src.layer_1.actions.os.makedirs")
    def test_screenshot_creates_dir(self, makedirs, mock_page):
        """Should create parent directory if it doesn't exist."""
        do_screenshot(mock_page, "a/b/c.png")
        makedirs.assert_called_once()
