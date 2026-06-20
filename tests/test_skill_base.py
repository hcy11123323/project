"""Tests for skill_library.skill_base -- SkillMeta, SkillResult, SkillBase lifecycle."""

from __future__ import annotations

from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest

from src.skill_library.skill_base import SkillBase, SkillMeta, SkillResult


# ---------------------------------------------------------------------------
# SkillMeta (frozen dataclass)
# ---------------------------------------------------------------------------


class TestSkillMeta:
    def test_construction_with_all_fields(self):
        meta = SkillMeta(
            id="domain/baidu_search",
            name="百度搜索",
            type="domain",
            triggers=["百度", "baidu", "搜索"],
            url_patterns=["*.baidu.com"],
            description="在百度搜索关键词",
            version="2.0.0",
        )
        assert meta.id == "domain/baidu_search"
        assert meta.name == "百度搜索"
        assert meta.type == "domain"
        assert meta.triggers == ["百度", "baidu", "搜索"]
        assert meta.url_patterns == ["*.baidu.com"]
        assert meta.description == "在百度搜索关键词"
        assert meta.version == "2.0.0"

    def test_construction_with_defaults(self):
        meta = SkillMeta(id="test/skill", name="Test", type="interaction")
        assert meta.triggers == []
        assert meta.url_patterns == []
        assert meta.description == ""
        assert meta.version == "1.0.0"

    def test_frozen(self):
        meta = SkillMeta(id="test/skill", name="Test", type="interaction")
        with pytest.raises(AttributeError):
            meta.id = "changed"  # type: ignore[misc]

    def test_equality(self):
        meta1 = SkillMeta(id="a/b", name="X", type="domain", triggers=["t"])
        meta2 = SkillMeta(id="a/b", name="X", type="domain", triggers=["t"])
        assert meta1 == meta2

    def test_inequality(self):
        meta1 = SkillMeta(id="a/b", name="X", type="domain")
        meta2 = SkillMeta(id="a/c", name="X", type="domain")
        assert meta1 != meta2


# ---------------------------------------------------------------------------
# SkillResult
# ---------------------------------------------------------------------------


class TestSkillResult:
    def test_ok(self):
        result = SkillResult.ok(message="done", key="value")
        assert result.success is True
        assert result.message == "done"
        assert result.data == {"key": "value"}
        assert result.error == ""

    def test_ok_no_args(self):
        result = SkillResult.ok()
        assert result.success is True
        assert result.message == ""
        assert result.data == {}

    def test_fail(self):
        result = SkillResult.fail(error="something broke", message="oops")
        assert result.success is False
        assert result.error == "something broke"
        assert result.message == "oops"

    def test_fail_default_message(self):
        result = SkillResult.fail(error="err")
        assert result.success is False
        assert result.message == ""

    def test_manual_construction(self):
        result = SkillResult(success=True, message="m", data={"k": 1}, error="")
        assert result.success is True
        assert result.data["k"] == 1


# ---------------------------------------------------------------------------
# SkillBase -- concrete subclass for testing the abstract lifecycle
# ---------------------------------------------------------------------------


class DummySkill(SkillBase):
    """Minimal concrete SkillBase for testing lifecycle methods."""

    def __init__(
        self,
        validate_result: Optional[str] = None,
        setup_raises: Optional[Exception] = None,
        execute_raises: Optional[Exception] = None,
        teardown_raises: Optional[Exception] = None,
    ):
        self._validate_result = validate_result
        self._setup_raises = setup_raises
        self._execute_raises = execute_raises
        self._teardown_raises = teardown_raises
        self.setup_called = False
        self.teardown_called = False
        self.execute_called = False

    def metadata(self) -> SkillMeta:
        return SkillMeta(
            id="test/dummy",
            name="Dummy",
            type="interaction",
            triggers=["test", "dummy"],
            url_patterns=["*.example.com"],
        )

    def execute(self, page: Any, **params: Any) -> SkillResult:
        self.execute_called = True
        if self._execute_raises:
            raise self._execute_raises
        return SkillResult.ok(message="executed", **params)

    def validate_params(self, params: Dict[str, Any]) -> Optional[str]:
        return self._validate_result

    def setup(self, page: Any) -> None:
        if self._setup_raises:
            raise self._setup_raises
        self.setup_called = True

    def teardown(self, page: Any) -> None:
        if self._teardown_raises:
            raise self._teardown_raises
        self.teardown_called = True


# ---------------------------------------------------------------------------
# SkillBase -- abstract interface
# ---------------------------------------------------------------------------


class TestSkillBaseAbstract:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            SkillBase()  # type: ignore[abstract]

    def test_subclass_must_implement_metadata(self):
        class Incomplete(SkillBase):
            def execute(self, page, **params):
                return SkillResult.ok()

        with pytest.raises(TypeError):
            Incomplete()

    def test_subclass_must_implement_execute(self):
        class Incomplete(SkillBase):
            def metadata(self):
                return SkillMeta(id="x", name="x", type="interaction")

        with pytest.raises(TypeError):
            Incomplete()


# ---------------------------------------------------------------------------
# SkillBase -- default optional methods
# ---------------------------------------------------------------------------


class TestSkillBaseDefaults:
    def test_validate_params_default_returns_none(self):
        class Minimal(SkillBase):
            def metadata(self):
                return SkillMeta(id="m", name="m", type="interaction")

            def execute(self, page, **params):
                return SkillResult.ok()

        skill = Minimal()
        assert skill.validate_params({}) is None

    def test_setup_default_is_noop(self):
        class Minimal(SkillBase):
            def metadata(self):
                return SkillMeta(id="m", name="m", type="interaction")

            def execute(self, page, **params):
                return SkillResult.ok()

        skill = Minimal()
        skill.setup(MagicMock())  # should not raise

    def test_teardown_default_is_noop(self):
        class Minimal(SkillBase):
            def metadata(self):
                return SkillMeta(id="m", name="m", type="interaction")

            def execute(self, page, **params):
                return SkillResult.ok()

        skill = Minimal()
        skill.teardown(MagicMock())  # should not raise


# ---------------------------------------------------------------------------
# SkillBase.run() -- full lifecycle
# ---------------------------------------------------------------------------


class TestSkillBaseRun:
    def test_run_happy_path(self):
        page = MagicMock()
        skill = DummySkill()
        result = skill.run(page, keyword="test")

        assert result.success is True
        assert result.message == "executed"
        assert result.data["keyword"] == "test"
        assert skill.setup_called is True
        assert skill.execute_called is True
        assert skill.teardown_called is True

    def test_run_validation_failure(self):
        page = MagicMock()
        skill = DummySkill(validate_result="missing 'keyword'")
        result = skill.run(page)

        assert result.success is False
        assert "参数校验失败" in result.error
        assert "missing 'keyword'" in result.error
        # setup/execute/teardown should NOT be called
        assert skill.setup_called is False
        assert skill.execute_called is False
        assert skill.teardown_called is False

    def test_run_setup_failure(self):
        page = MagicMock()
        skill = DummySkill(setup_raises=RuntimeError("page not ready"))
        result = skill.run(page)

        assert result.success is False
        assert "setup 失败" in result.error
        assert "page not ready" in result.error
        assert skill.execute_called is False
        # teardown should NOT be called if setup fails
        assert skill.teardown_called is False

    def test_run_execute_failure_still_calls_teardown(self):
        page = MagicMock()
        skill = DummySkill(execute_raises=ValueError("bad input"))
        result = skill.run(page)

        assert result.success is False
        assert "执行异常" in result.error
        assert "bad input" in result.error
        # teardown MUST be called even when execute fails
        assert skill.teardown_called is True

    def test_run_teardown_failure_does_not_mask_execute_result(self):
        page = MagicMock()
        # Execute succeeds, but teardown raises
        skill = DummySkill(teardown_raises=RuntimeError("cleanup fail"))
        result = skill.run(page, keyword="ok")

        # The successful execute result should be returned
        assert result.success is True
        assert result.message == "executed"

    def test_run_teardown_failure_with_execute_failure(self):
        page = MagicMock()
        skill = DummySkill(
            execute_raises=ValueError("exec fail"),
            teardown_raises=RuntimeError("cleanup fail"),
        )
        result = skill.run(page)

        # Execute failure should be reported, not teardown failure
        assert result.success is False
        assert "执行异常" in result.error


# ---------------------------------------------------------------------------
# SkillBase.__repr__
# ---------------------------------------------------------------------------


class TestSkillBaseRepr:
    def test_repr(self):
        skill = DummySkill()
        assert "DummySkill" in repr(skill)
        assert "test/dummy" in repr(skill)


# ---------------------------------------------------------------------------
# Parameterized lifecycle edge cases
# ---------------------------------------------------------------------------


class TestSkillBaseEdgeCases:
    def test_run_with_no_params(self):
        page = MagicMock()
        skill = DummySkill()
        result = skill.run(page)
        assert result.success is True
        assert result.data == {}

    def test_run_with_multiple_params(self):
        page = MagicMock()
        skill = DummySkill()
        result = skill.run(page, a=1, b="two", c=[3])
        assert result.success is True
        assert result.data["a"] == 1
        assert result.data["b"] == "two"
        assert result.data["c"] == [3]

    def test_metadata_returns_fresh_instance(self):
        skill = DummySkill()
        m1 = skill.metadata()
        m2 = skill.metadata()
        # Frozen dataclass equality
        assert m1 == m2
