"""Tests for layer_2.skill_loader -- YAML-based skill loading and SkillYamlRegistry."""

from __future__ import annotations

import pytest
import yaml

from src.layer_2.skill_loader import (
    SkillYamlRegistry,
    _matches_query,
    _matches_url,
    get_skill_yaml_registry,
    load_skill,
    load_skills_from_dir,
    reset_skill_yaml_registry,
)
from src.layer_2.skill_schema import SkillConfig, SkillType

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_skill_data():
    return {
        "id": "baidu_search",
        "name": "百度搜索",
        "type": "domain",
        "description": "在百度搜索关键词",
        "version": "1.0.0",
        "triggers": ["百度", "baidu", "搜索"],
        "url_patterns": ["baidu.com"],
        "domain": "baidu",
        "parameters": {
            "keyword": {
                "type": "string",
                "required": True,
                "description": "搜索关键词",
            }
        },
        "steps": [
            {"action": "goto", "value": "https://www.baidu.com"},
            {"action": "fill", "target": "search_input", "value": "{{keyword}}"},
            {"action": "click", "target": "search_button"},
        ],
    }


@pytest.fixture
def skill_yaml_file(tmp_path, sample_skill_data):
    """Write a single skill YAML file and return its path."""
    path = tmp_path / "baidu_search.yaml"
    path.write_text(yaml.dump(sample_skill_data, allow_unicode=True), encoding="utf-8")
    return path


@pytest.fixture
def skills_dir(tmp_path, sample_skill_data):
    """Create a directory with multiple skill YAML files."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # baidu_search
    (skills_dir / "baidu_search.yaml").write_text(
        yaml.dump(sample_skill_data, allow_unicode=True), encoding="utf-8"
    )

    # login_flow
    login_data = {
        "id": "login_flow",
        "name": "通用登录",
        "type": "interaction",
        "description": "通用登录流程",
        "triggers": ["登录", "login"],
        "url_patterns": [],
        "steps": [
            {"action": "fill", "target": "username", "value": "{{user}}"},
            {"action": "fill", "target": "password", "value": "{{pass}}"},
            {"action": "click", "target": "submit"},
        ],
    }
    (skills_dir / "login_flow.yaml").write_text(
        yaml.dump(login_data, allow_unicode=True), encoding="utf-8"
    )

    # invalid file (should be skipped)
    (skills_dir / "invalid.yaml").write_text("not: [valid: yaml: {", encoding="utf-8")

    return skills_dir


# ---------------------------------------------------------------------------
# load_skill -- single file
# ---------------------------------------------------------------------------


class TestLoadSkill:
    def test_load_valid_skill(self, skill_yaml_file):
        config = load_skill(str(skill_yaml_file))
        assert isinstance(config, SkillConfig)
        assert config.id == "baidu_search"
        assert config.name == "百度搜索"
        assert config.type == SkillType.DOMAIN
        assert config.triggers == ["百度", "baidu", "搜索"]
        assert config.url_patterns == ["baidu.com"]
        assert config.domain == "baidu"
        assert len(config.parameters) == 1
        assert len(config.steps) == 3

    def test_load_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="技能文件不存在"):
            load_skill(str(tmp_path / "nonexistent.yaml"))

    def test_load_invalid_yaml(self, tmp_path):
        path = tmp_path / "bad.yaml"
        path.write_text("not: [valid: yaml: {", encoding="utf-8")
        # Should raise a YAML or Pydantic error
        with pytest.raises(Exception):
            load_skill(str(path))

    def test_load_minimal_skill(self, tmp_path):
        """Only required fields."""
        data = {"id": "minimal", "name": "Minimal"}
        path = tmp_path / "minimal.yaml"
        path.write_text(yaml.dump(data), encoding="utf-8")
        config = load_skill(str(path))
        assert config.id == "minimal"
        assert config.type == SkillType.INTERACTION  # default
        assert config.triggers == []
        assert config.steps == []


# ---------------------------------------------------------------------------
# load_skills_from_dir
# ---------------------------------------------------------------------------


class TestLoadSkillsFromDir:
    def test_load_multiple(self, skills_dir):
        configs = load_skills_from_dir(str(skills_dir))
        assert len(configs) == 2
        ids = {c.id for c in configs}
        assert ids == {"baidu_search", "login_flow"}

    def test_load_nested_directories(self, tmp_path, sample_skill_data):
        skills_dir = tmp_path / "skills"
        nested_dir = skills_dir / "search"
        nested_dir.mkdir(parents=True)
        (nested_dir / "baidu_search.yaml").write_text(
            yaml.dump(sample_skill_data, allow_unicode=True), encoding="utf-8"
        )

        configs = load_skills_from_dir(str(skills_dir))

        assert [c.id for c in configs] == ["baidu_search"]

    def test_skip_invalid_files(self, skills_dir, capsys):
        configs = load_skills_from_dir(str(skills_dir))
        # Should load 2 valid, skip 1 invalid
        assert len(configs) == 2
        captured = capsys.readouterr()
        assert "跳过" in captured.out

    def test_nonexistent_dir(self, tmp_path):
        configs = load_skills_from_dir(str(tmp_path / "nonexistent"))
        assert configs == []

    def test_empty_dir(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        configs = load_skills_from_dir(str(empty))
        assert configs == []

    def test_sorted_output(self, skills_dir):
        """Skills should be sorted by filename."""
        configs = load_skills_from_dir(str(skills_dir))
        ids = [c.id for c in configs]
        assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# SkillYamlRegistry -- register
# ---------------------------------------------------------------------------


class TestSkillYamlRegistryRegister:
    def test_register_single(self):
        reg = SkillYamlRegistry()
        config = SkillConfig(id="test", name="Test")
        reg.register(config)
        assert reg.count == 1
        assert reg.get("test") is config

    def test_register_overwrite(self):
        reg = SkillYamlRegistry()
        config1 = SkillConfig(id="test", name="V1")
        config2 = SkillConfig(id="test", name="V2")
        reg.register(config1)
        reg.register(config2)
        assert reg.count == 1
        assert reg.get("test").name == "V2"

    def test_count(self):
        reg = SkillYamlRegistry()
        assert reg.count == 0
        reg.register(SkillConfig(id="a", name="A"))
        assert reg.count == 1
        reg.register(SkillConfig(id="b", name="B"))
        assert reg.count == 2


# ---------------------------------------------------------------------------
# SkillYamlRegistry -- load_dir
# ---------------------------------------------------------------------------


class TestSkillYamlRegistryLoadDir:
    def test_load_dir(self, skills_dir):
        reg = SkillYamlRegistry()
        count = reg.load_dir(str(skills_dir))
        assert count == 2
        assert reg.count == 2

    def test_load_nonexistent_dir(self, tmp_path):
        reg = SkillYamlRegistry()
        count = reg.load_dir(str(tmp_path / "nope"))
        assert count == 0


# ---------------------------------------------------------------------------
# SkillYamlRegistry -- get / list_all
# ---------------------------------------------------------------------------


class TestSkillYamlRegistryLookup:
    def test_get_existing(self):
        reg = SkillYamlRegistry()
        config = SkillConfig(id="test", name="Test")
        reg.register(config)
        assert reg.get("test") is config

    def test_get_nonexistent(self):
        reg = SkillYamlRegistry()
        assert reg.get("nope") is None

    def test_list_all(self):
        reg = SkillYamlRegistry()
        reg.register(SkillConfig(id="a", name="A"))
        reg.register(SkillConfig(id="b", name="B"))
        all_skills = reg.list_all()
        assert len(all_skills) == 2


# ---------------------------------------------------------------------------
# SkillYamlRegistry -- search by query
# ---------------------------------------------------------------------------


class TestSkillYamlRegistrySearchQuery:
    def test_match_trigger(self):
        reg = SkillYamlRegistry()
        reg.register(SkillConfig(id="test", name="Test", triggers=["百度", "search"]))
        results = reg.search(query="百度一下")
        assert len(results) == 1
        assert results[0].id == "test"

    def test_match_name(self):
        reg = SkillYamlRegistry()
        reg.register(SkillConfig(id="test", name="百度搜索", triggers=[]))
        results = reg.search(query="百度")
        assert len(results) == 1

    def test_match_description(self):
        reg = SkillYamlRegistry()
        reg.register(
            SkillConfig(
                id="test", name="X", triggers=[], description="这是一个搜索技能"
            )
        )
        results = reg.search(query="搜索")
        assert len(results) == 1

    def test_no_match(self):
        reg = SkillYamlRegistry()
        reg.register(SkillConfig(id="test", name="Test", triggers=["百度"]))
        results = reg.search(query="google")
        assert len(results) == 0


# ---------------------------------------------------------------------------
# SkillYamlRegistry -- search by URL
# ---------------------------------------------------------------------------


class TestSkillYamlRegistrySearchUrl:
    def test_match_url(self):
        reg = SkillYamlRegistry()
        reg.register(SkillConfig(id="test", name="Test", url_patterns=["*.baidu.com"]))
        results = reg.search(url="https://www.baidu.com/s")
        assert len(results) == 1

    def test_no_url_match(self):
        reg = SkillYamlRegistry()
        reg.register(SkillConfig(id="test", name="Test", url_patterns=["*.baidu.com"]))
        results = reg.search(url="https://google.com")
        assert len(results) == 0

    def test_empty_patterns(self):
        reg = SkillYamlRegistry()
        reg.register(SkillConfig(id="test", name="Test", url_patterns=[]))
        results = reg.search(url="https://example.com")
        assert len(results) == 0


# ---------------------------------------------------------------------------
# _matches_query (module-level helper)
# ---------------------------------------------------------------------------


class TestMatchesQueryHelper:
    def test_trigger_match(self):
        skill = SkillConfig(id="t", name="T", triggers=["搜索"])
        assert _matches_query(skill, "帮我搜索") is True

    def test_name_match(self):
        skill = SkillConfig(id="t", name="百度搜索", triggers=[])
        assert _matches_query(skill, "百度") is True

    def test_description_match(self):
        skill = SkillConfig(id="t", name="X", triggers=[], description="搜索工具")
        assert _matches_query(skill, "搜索") is True

    def test_no_match(self):
        skill = SkillConfig(id="t", name="X", triggers=["百度"], description="百度工具")
        assert _matches_query(skill, "google") is False

    def test_case_insensitive(self):
        skill = SkillConfig(id="t", name="Test", triggers=["LOGIN"])
        assert _matches_query(skill, "please Login") is True


# ---------------------------------------------------------------------------
# _matches_url (module-level helper)
# ---------------------------------------------------------------------------


class TestMatchesUrlHelper:
    def test_wildcard_match(self):
        skill = SkillConfig(id="t", name="T", url_patterns=["*.github.com"])
        # Pattern '*.github.com' strips to '.github.com' (leading dot preserved)
        # Matches URLs like 'https://www.github.com/login' that contain '.github.com'
        assert _matches_url(skill, "https://www.github.com/login") is True

    def test_plain_match(self):
        skill = SkillConfig(id="t", name="T", url_patterns=["baidu.com"])
        assert _matches_url(skill, "https://baidu.com") is True

    def test_no_match(self):
        skill = SkillConfig(id="t", name="T", url_patterns=["*.baidu.com"])
        assert _matches_url(skill, "https://google.com") is False

    def test_empty_patterns(self):
        skill = SkillConfig(id="t", name="T", url_patterns=[])
        assert _matches_url(skill, "https://anything.com") is False


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestSkillYamlRegistrySingleton:
    def teardown_method(self):
        reset_skill_yaml_registry()

    def test_singleton(self):
        r1 = get_skill_yaml_registry(skills_dir="__nonexistent__")
        r2 = get_skill_yaml_registry(skills_dir="__nonexistent__")
        assert r1 is r2

    def test_reset(self):
        r1 = get_skill_yaml_registry(skills_dir="__nonexistent__")
        reset_skill_yaml_registry()
        r2 = get_skill_yaml_registry(skills_dir="__nonexistent__")
        assert r1 is not r2
