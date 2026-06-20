"""Tests for layer_2.skill_schema -- Pydantic models for skill configuration."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.layer_2.skill_schema import (
    ParamType,
    SkillConfig,
    SkillParam,
    SkillStep,
    SkillType,
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestSkillType:
    def test_values(self):
        assert SkillType.DOMAIN == "domain"
        assert SkillType.INTERACTION == "interaction"
        assert SkillType.COMPOSITE == "composite"

    def test_from_string(self):
        assert SkillType("domain") == SkillType.DOMAIN
        assert SkillType("interaction") == SkillType.INTERACTION

    def test_invalid_value(self):
        with pytest.raises(ValueError):
            SkillType("nonexistent")


class TestParamType:
    def test_values(self):
        assert ParamType.STRING == "string"
        assert ParamType.INTEGER == "integer"
        assert ParamType.FLOAT == "float"
        assert ParamType.BOOLEAN == "boolean"


# ---------------------------------------------------------------------------
# SkillParam
# ---------------------------------------------------------------------------


class TestSkillParam:
    def test_defaults(self):
        param = SkillParam()
        assert param.type == ParamType.STRING
        assert param.required is True
        assert param.default is None
        assert param.description == ""

    def test_custom(self):
        param = SkillParam(
            type=ParamType.INTEGER,
            required=False,
            default=10,
            description="Max pages",
        )
        assert param.type == ParamType.INTEGER
        assert param.required is False
        assert param.default == 10

    def test_from_dict(self):
        data = {"type": "boolean", "required": False, "default": True}
        param = SkillParam.model_validate(data)
        assert param.type == ParamType.BOOLEAN
        assert param.default is True


# ---------------------------------------------------------------------------
# SkillStep
# ---------------------------------------------------------------------------


class TestSkillStep:
    def test_minimal(self):
        step = SkillStep(action="goto")
        assert step.action == "goto"
        assert step.target is None
        assert step.value is None
        assert step.args is None
        assert step.comment is None
        assert step.on_error is None

    def test_full(self):
        step = SkillStep(
            action="fill",
            target="search_input",
            value="{{keyword}}",
            args={"timeout": 5000},
            comment="Fill the search box",
            on_error="continue",
        )
        assert step.action == "fill"
        assert step.target == "search_input"
        assert step.value == "{{keyword}}"
        assert step.args == {"timeout": 5000}
        assert step.comment == "Fill the search box"
        assert step.on_error == "continue"

    def test_action_required(self):
        with pytest.raises(ValidationError):
            SkillStep()  # type: ignore[call-arg]

    def test_from_dict(self):
        data = {"action": "click", "target": "submit_btn"}
        step = SkillStep.model_validate(data)
        assert step.action == "click"
        assert step.target == "submit_btn"


# ---------------------------------------------------------------------------
# SkillConfig
# ---------------------------------------------------------------------------


class TestSkillConfig:
    def test_minimal(self):
        config = SkillConfig(id="test", name="Test")
        assert config.id == "test"
        assert config.name == "Test"
        assert config.type == SkillType.INTERACTION
        assert config.description == ""
        assert config.version == "1.0.0"
        assert config.triggers == []
        assert config.url_patterns == []
        assert config.domain is None
        assert config.parameters == {}
        assert config.steps == []

    def test_full(self):
        config = SkillConfig(
            id="baidu_search",
            name="百度搜索",
            type=SkillType.DOMAIN,
            description="在百度搜索关键词",
            version="2.0.0",
            triggers=["百度", "baidu"],
            url_patterns=["*.baidu.com"],
            domain="baidu",
            parameters={
                "keyword": SkillParam(
                    type=ParamType.STRING, required=True, description="搜索关键词"
                )
            },
            steps=[
                SkillStep(action="goto", value="https://www.baidu.com"),
                SkillStep(action="fill", target="search_input", value="{{keyword}}"),
                SkillStep(action="click", target="search_button"),
            ],
        )
        assert config.type == SkillType.DOMAIN
        assert config.domain == "baidu"
        assert len(config.parameters) == 1
        assert len(config.steps) == 3

    def test_id_required(self):
        with pytest.raises(ValidationError):
            SkillConfig(name="Test")  # type: ignore[call-arg]

    def test_name_required(self):
        with pytest.raises(ValidationError):
            SkillConfig(id="test")  # type: ignore[call-arg]

    def test_from_dict(self):
        data = {
            "id": "login",
            "name": "Login",
            "type": "domain",
            "triggers": ["login"],
            "steps": [{"action": "fill", "target": "user"}],
        }
        config = SkillConfig.model_validate(data)
        assert config.id == "login"
        assert config.type == SkillType.DOMAIN
        assert len(config.steps) == 1

    def test_type_default(self):
        config = SkillConfig(id="x", name="X")
        assert config.type == SkillType.INTERACTION

    def test_version_default(self):
        config = SkillConfig(id="x", name="X")
        assert config.version == "1.0.0"


# ---------------------------------------------------------------------------
# SkillConfig -- serialization round-trip
# ---------------------------------------------------------------------------


class TestSkillConfigSerialization:
    def test_model_dump(self):
        config = SkillConfig(
            id="test", name="Test", triggers=["a", "b"], type=SkillType.DOMAIN
        )
        dumped = config.model_dump()
        assert dumped["id"] == "test"
        assert dumped["triggers"] == ["a", "b"]
        assert dumped["type"] == "domain"

    def test_round_trip(self):
        original = SkillConfig(
            id="test",
            name="Test",
            type=SkillType.INTERACTION,
            triggers=["t1"],
            steps=[SkillStep(action="goto", value="https://example.com")],
        )
        dumped = original.model_dump()
        restored = SkillConfig.model_validate(dumped)
        assert restored.id == original.id
        assert restored.steps[0].action == "goto"
