"""Layer 2 - Skill Loader: YAML skill file loading, validation, and registry.

Loads skills from ``skills/*.yaml`` files, validates them via Pydantic,
and provides search/lookup APIs for the MCP server and script engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import yaml

from src.layer_2.skill_schema import SkillConfig

# ---------------------------------------------------------------------------
# 公开 API
# ---------------------------------------------------------------------------


def load_skill(yaml_path: str) -> SkillConfig:
    """从单个 YAML 文件加载并校验技能配置。

    Args:
        yaml_path: 技能 YAML 文件的路径。

    Returns:
        校验通过后的 SkillConfig 对象。

    Raises:
        FileNotFoundError: 文件不存在。
        pydantic.ValidationError: YAML 内容不符合 schema。
    """
    path = Path(yaml_path)
    if not path.is_file():
        raise FileNotFoundError(f"技能文件不存在: {yaml_path}")

    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    config = SkillConfig.model_validate(raw)
    return config


def load_skills_from_dir(skills_dir: str = "skills") -> List[SkillConfig]:
    """递归扫描目录下所有 *.yaml 文件并加载为技能列表。

    跳过无法解析的文件（打印警告但不中断）。

    Args:
        skills_dir: 技能 YAML 文件所在目录。

    Returns:
        所有成功加载的 SkillConfig 列表。
    """
    dir_path = Path(skills_dir)
    if not dir_path.is_dir():
        return []

    configs: List[SkillConfig] = []
    for yaml_file in sorted(dir_path.rglob("*.yaml")):
        try:
            config = load_skill(str(yaml_file))
            configs.append(config)
        except Exception as exc:
            # 跳过无效文件，保持容错
            print(f"[skill_loader] 跳过 {yaml_file.name}: {exc}")

    return configs


# ---------------------------------------------------------------------------
# 技能注册表（内存索引）
# ---------------------------------------------------------------------------


class SkillYamlRegistry:
    """基于 YAML 的技能注册表。

    提供按 ID、关键词、URL 模式的查找能力。
    与 ``skill_library/registry.py`` 的 JSON 注册表并行，
    但直接从 YAML 文件加载，无需维护 registry.json。
    """

    def __init__(self) -> None:
        self._skills: Dict[str, SkillConfig] = {}

    # ---- 注册 ----

    def register(self, config: SkillConfig) -> None:
        """注册单个技能（同 ID 覆盖）。"""
        self._skills[config.id] = config

    def load_dir(self, skills_dir: str = "skills") -> int:
        """从目录加载全部 YAML 技能并注册。

        Returns:
            成功注册的技能数量。
        """
        configs = load_skills_from_dir(skills_dir)
        for cfg in configs:
            self.register(cfg)
        return len(configs)

    # ---- 查找 ----

    def get(self, skill_id: str) -> Optional[SkillConfig]:
        """按 ID 获取技能。"""
        return self._skills.get(skill_id)

    def list_all(self) -> List[SkillConfig]:
        """列出所有已注册技能。"""
        return list(self._skills.values())

    def search(
        self,
        query: Optional[str] = None,
        url: Optional[str] = None,
    ) -> List[SkillConfig]:
        """按关键词或 URL 模式查找匹配的技能。

        Args:
            query: 搜索关键词，与 triggers 列表做子串匹配。
            url: 目标 URL，与 url_patterns 做通配符匹配。

        Returns:
            匹配的技能列表。
        """
        results: List[SkillConfig] = []
        for skill in self._skills.values():
            if query and _matches_query(skill, query):
                results.append(skill)
            elif url and _matches_url(skill, url):
                results.append(skill)
        return results

    @property
    def count(self) -> int:
        """已注册技能数量。"""
        return len(self._skills)


# ---------------------------------------------------------------------------
# 内部辅助
# ---------------------------------------------------------------------------


def _matches_query(skill: SkillConfig, query: str) -> bool:
    """检查 query 是否命中技能的 triggers 或 name/description。"""
    q = query.lower()
    # 优先匹配 triggers
    for trigger in skill.triggers:
        if trigger.lower() in q:
            return True
    # 退化到 name / description
    if q in skill.name.lower() or q in skill.description.lower():
        return True
    return False


def _matches_url(skill: SkillConfig, url: str) -> bool:
    """检查 url 是否匹配技能的 url_patterns（* 通配符）。"""
    if not skill.url_patterns:
        return False
    url_lower = url.lower()
    for pattern in skill.url_patterns:
        core = pattern.lower().strip("*")
        if core in url_lower:
            return True
    return False


# ---------------------------------------------------------------------------
# 全局单例
# ---------------------------------------------------------------------------

_instance: Optional[SkillYamlRegistry] = None


def get_skill_yaml_registry(skills_dir: str = "skills") -> SkillYamlRegistry:
    """获取全局单例 SkillYamlRegistry（惰性加载）。

    Args:
        skills_dir: 技能 YAML 文件所在目录，仅首次调用时生效。

    Returns:
        全局注册表实例。
    """
    global _instance
    if _instance is None:
        _instance = SkillYamlRegistry()
        _instance.load_dir(skills_dir)
    return _instance


def reset_skill_yaml_registry() -> None:
    """重置全局单例（用于测试）。"""
    global _instance
    _instance = None
