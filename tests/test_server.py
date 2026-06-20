"""Tests for server.py — MCP tool registration and integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_bm():
    """Mock BrowserManager with a mock page."""
    bm = MagicMock()
    bm.is_alive.return_value = True
    page = MagicMock()
    page.url = "https://example.com"
    response = MagicMock()
    response.status = 200
    page.goto.return_value = response
    page.is_visible.return_value = True
    page.click.return_value = None
    page.screenshot.return_value = None
    bm.get_page.return_value = page
    return bm


# ---------------------------------------------------------------------------
# ping
# ---------------------------------------------------------------------------


class TestPing:
    def test_ping_returns_pong(self):
        from src.server import ping
        assert ping() == "pong"


# ---------------------------------------------------------------------------
# browser_launch
# ---------------------------------------------------------------------------


class TestBrowserLaunch:
    @patch("src.server.get_browser_manager")
    def test_already_running(self, mock_get_bm):
        from src.server import browser_launch
        bm = MagicMock()
        bm.is_alive.return_value = True
        mock_get_bm.return_value = bm
        result = browser_launch()
        assert "already running" in result.lower()

    @patch("src.server.get_browser_manager")
    @patch.dict("os.environ", {"BROWSER_HEADLESS": "true"})
    def test_launch_success(self, mock_get_bm):
        from src.server import browser_launch
        bm = MagicMock()
        bm.is_alive.return_value = False
        page = MagicMock()
        page.url = "about:blank"
        bm.launch.return_value = page
        mock_get_bm.return_value = bm
        result = browser_launch()
        assert "launched" in result.lower()

    @patch("src.server.get_browser_manager")
    def test_launch_failure(self, mock_get_bm):
        from src.server import browser_launch
        bm = MagicMock()
        bm.is_alive.return_value = False
        bm.launch.side_effect = RuntimeError("no browser")
        mock_get_bm.return_value = bm
        result = browser_launch()
        assert "failed" in result.lower()


# ---------------------------------------------------------------------------
# screenshot
# ---------------------------------------------------------------------------


class TestScreenshot:
    @patch("src.server.get_browser_manager")
    def test_screenshot_no_browser(self, mock_get_bm):
        from src.server import screenshot
        bm = MagicMock()
        bm.get_page.side_effect = RuntimeError("not launched")
        mock_get_bm.return_value = bm
        result = screenshot("test.png")
        assert "not launched" in result.lower() or "browser_launch" in result.lower()

    @patch("src.layer_1.actions.do_screenshot", return_value="test.png")
    @patch("src.server.get_browser_manager")
    def test_screenshot_success(self, mock_get_bm, mock_do_ss, mock_bm):
        from src.server import screenshot
        mock_get_bm.return_value = mock_bm
        result = screenshot("test.png")
        assert "saved" in result.lower() or "截图" in result


# ---------------------------------------------------------------------------
# browse_skills
# ---------------------------------------------------------------------------


class TestBrowseSkills:
    @patch("src.skill_library.registry.get_skill_registry")
    def test_list_all(self, mock_get_reg):
        from src.server import browse_skills
        from src.skill_library.registry import SkillEntry

        reg = MagicMock()
        reg.list_all.return_value = [
            SkillEntry(id="test", name="Test", type="domain", triggers=["test"]),
        ]
        reg.search.return_value = []
        mock_get_reg.return_value = reg

        result = browse_skills()
        assert "Test" in result

    @patch("src.skill_library.registry.get_skill_registry")
    def test_search_by_query(self, mock_get_reg):
        from src.server import browse_skills
        from src.skill_library.registry import SkillEntry

        reg = MagicMock()
        reg.search.return_value = [
            SkillEntry(id="baidu", name="百度搜索", type="domain", triggers=["百度"]),
        ]
        mock_get_reg.return_value = reg

        result = browse_skills(query="百度")
        assert "百度搜索" in result

    @patch("src.skill_library.registry.get_skill_registry")
    def test_no_results(self, mock_get_reg):
        from src.server import browse_skills

        reg = MagicMock()
        reg.search.return_value = []
        mock_get_reg.return_value = reg

        result = browse_skills(query="不存在")
        assert "No matching" in result


# ---------------------------------------------------------------------------
# get_skill
# ---------------------------------------------------------------------------


class TestGetSkill:
    @patch("src.skill_library.registry.get_skill_registry")
    def test_get_existing_skill(self, mock_get_reg):
        from src.server import get_skill
        from src.skill_library.registry import SkillDetail
        from src.skill_library.skill_base import SkillMeta

        reg = MagicMock()
        reg.get_detail.return_value = SkillDetail(
            meta=SkillMeta(id="test", name="Test", type="domain", triggers=[]),
            source_code="def run(): pass",
            guide="# How to",
        )
        mock_get_reg.return_value = reg

        result = get_skill("test")
        assert "Test" in result
        assert "def run" in result

    @patch("src.skill_library.registry.get_skill_registry")
    def test_get_nonexistent_skill(self, mock_get_reg):
        from src.server import get_skill

        reg = MagicMock()
        reg.get_detail.return_value = None
        mock_get_reg.return_value = reg

        result = get_skill("nonexistent")
        assert "not found" in result.lower()


# ---------------------------------------------------------------------------
# run_script
# ---------------------------------------------------------------------------


class TestRunScript:
    @patch("src.server._init_script_engine")
    @patch("src.server.get_browser_manager")
    def test_no_browser(self, mock_get_bm, mock_init):
        from src.server import run_script
        bm = MagicMock()
        bm.is_alive.return_value = False
        mock_get_bm.return_value = bm

        result = run_script("print('hello')")
        assert "not launched" in result.lower() or "error" in result.lower()

    @patch("src.server._init_script_engine")
    @patch("src.server.get_browser_manager")
    def test_success(self, mock_get_bm, mock_init):
        from src.server import run_script
        from src.core.script_engine import ScriptResult

        bm = MagicMock()
        bm.is_alive.return_value = True
        mock_get_bm.return_value = bm

        engine = MagicMock()
        engine.execute.return_value = ScriptResult(
            success=True, output="hello\n"
        )
        mock_init.return_value = engine

        result = run_script("print('hello')")
        assert "success" in result.lower()
        assert "hello" in result

    @patch("src.server._init_script_engine")
    @patch("src.server.get_browser_manager")
    def test_failure(self, mock_get_bm, mock_init):
        from src.server import run_script
        from src.core.script_engine import ScriptResult

        bm = MagicMock()
        bm.is_alive.return_value = True
        mock_get_bm.return_value = bm

        engine = MagicMock()
        engine.execute.return_value = ScriptResult(
            success=False, error="NameError: undefined"
        )
        mock_init.return_value = engine

        result = run_script("print(undefined)")
        assert "failed" in result.lower()


# ---------------------------------------------------------------------------
# analyze_page
# ---------------------------------------------------------------------------


class TestAnalyzePage:
    @patch("src.server.get_browser_manager")
    def test_no_browser(self, mock_get_bm):
        from src.server import analyze_page
        bm = MagicMock()
        bm.is_alive.return_value = False
        mock_get_bm.return_value = bm

        result = analyze_page()
        assert "not launched" in result.lower() or "error" in result.lower()

    @patch("src.core.vision.get_vision_module")
    @patch("src.server.get_browser_manager")
    def test_success(self, mock_get_bm, mock_get_vision):
        from src.server import analyze_page
        from src.core.vision import PageAnalysis, ElementInfo

        bm = MagicMock()
        bm.is_alive.return_value = True
        mock_get_bm.return_value = bm

        vision = MagicMock()
        vision.analyze_page.return_value = PageAnalysis(
            summary="登录页面",
            elements=[
                ElementInfo(description="登录按钮", x=100, y=200, suggested_selector="#login"),
            ],
            suggested_actions=["点击登录"],
        )
        mock_get_vision.return_value = vision

        result = analyze_page(question="找登录按钮")
        assert "登录页面" in result
        assert "登录按钮" in result

    @patch("src.server.get_browser_manager")
    def test_no_api_key(self, mock_get_bm):
        from src.server import analyze_page
        import os

        bm = MagicMock()
        bm.is_alive.return_value = True
        mock_get_bm.return_value = bm

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            os.environ.pop("OPENAI_API_KEY", None)
            result = analyze_page()
            assert "error" in result.lower() or "api key" in result.lower()


# ---------------------------------------------------------------------------
# run_task
# ---------------------------------------------------------------------------


class TestRunTask:
    @patch("src.server.get_browser_manager")
    def test_no_browser(self, mock_get_bm):
        from src.server import run_task
        bm = MagicMock()
        bm.is_alive.return_value = False
        mock_get_bm.return_value = bm

        result = run_task("测试任务")
        assert "not launched" in result.lower() or "error" in result.lower()

    @patch("src.core.agent_loop.run_task")
    @patch("src.server.get_browser_manager")
    def test_success(self, mock_get_bm, mock_run_task):
        from src.server import run_task
        from src.core.agent_loop import AgentTaskResult, AgentStep, AgentState

        bm = MagicMock()
        bm.is_alive.return_value = True
        mock_get_bm.return_value = bm

        mock_run_task.return_value = AgentTaskResult(
            success=True,
            task="测试任务",
            steps=[
                AgentStep(step_number=1, state=AgentState.OBSERVE, result="页面: 测试", success=True),
                AgentStep(step_number=2, state=AgentState.ACT, result="执行成功", success=True),
            ],
            final_url="https://example.com",
            output="done",
        )

        result = run_task("测试任务")
        assert "completed" in result.lower()
        assert "测试" in result

    @patch("src.core.agent_loop.run_task")
    @patch("src.server.get_browser_manager")
    def test_failure(self, mock_get_bm, mock_run_task):
        from src.server import run_task
        from src.core.agent_loop import AgentTaskResult, AgentStep, AgentState

        bm = MagicMock()
        bm.is_alive.return_value = True
        mock_get_bm.return_value = bm

        mock_run_task.return_value = AgentTaskResult(
            success=False,
            task="测试任务",
            steps=[
                AgentStep(step_number=1, state=AgentState.ACT, result="执行失败", success=False, error="boom"),
            ],
            error="任务未完成",
        )

        result = run_task("测试任务")
        assert "failed" in result.lower()
