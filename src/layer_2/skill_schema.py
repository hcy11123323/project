"""Layer 2 - Skill Schema: Pydantic models for skills.yaml validation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SkillType(str, Enum):
    """技能类型。"""

    DOMAIN = "domain"  # 站点专属技能
    INTERACTION = "interaction"  # 通用交互技能
    COMPOSITE = "composite"  # 组合技能（编排其他技能）


class ParamType(str, Enum):
    """参数类型。"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"


# ---------------------------------------------------------------------------
# 参数定义
# ---------------------------------------------------------------------------


class SkillParam(BaseModel):
    """单个输入参数的描述。"""

    type: ParamType = ParamType.STRING
    required: bool = True
    default: Optional[Any] = None
    description: str = ""


# ---------------------------------------------------------------------------
# 步骤定义
# ---------------------------------------------------------------------------


class SkillStep(BaseModel):
    """技能流程中的单个步骤。

    每个步骤对应一个 Layer 1 原语或 Layer 2 控件函数。
    ``target`` 引用域配置中的元素名，``value`` 支持 ``{{param}}`` 模板变量。
    """

    action: str = Field(
        ...,
        description=(
            "要执行的动作名称，如 goto / click / fill / wait_for_navigation / "
            "smart_click / smart_fill / screenshot 等。"
        ),
    )
    target: Optional[str] = Field(
        None,
        description="域配置中的元素名（locators key），仅 click/fill 类动作需要。",
    )
    value: Optional[str] = Field(
        None,
        description="填充值，支持 {{param}} 模板语法。",
    )
    args: Optional[Dict[str, Any]] = Field(
        None,
        description="传递给动作函数的额外关键字参数。",
    )
    comment: Optional[str] = Field(None, description="步骤说明（仅供人类阅读）。")
    on_error: Optional[str] = Field(
        None,
        description="错误处理策略：'stop'（默认，终止）或 'continue'（跳过）。",
    )


# ---------------------------------------------------------------------------
# 技能主模型
# ---------------------------------------------------------------------------


class SkillConfig(BaseModel):
    """技能配置 —— 由 skills/*.yaml 反序列化得到。

    一个 YAML 文件描述一个完整的可复用技能，
    包含元数据、输入参数和有序执行步骤。
    """

    id: str = Field(..., description="技能唯一标识符，如 baidu_search、login_flow。")
    name: str = Field(..., description="人类可读名称。")
    type: SkillType = Field(SkillType.INTERACTION, description="技能类型。")
    description: str = Field("", description="技能描述。")
    version: str = Field("1.0.0", description="语义化版本号。")

    # 检索索引
    triggers: List[str] = Field(default_factory=list, description="触发关键词列表。")
    url_patterns: List[str] = Field(
        default_factory=list, description="URL 匹配模式列表，支持 * 通配符。"
    )

    # 域关联
    domain: Optional[str] = Field(
        None,
        description="关联的域配置名称（对应 domains/{domain}.yaml），为 None 表示无域依赖。",
    )

    # 输入参数
    parameters: Dict[str, SkillParam] = Field(
        default_factory=dict, description="输入参数定义。键为参数名。"
    )

    # 执行步骤
    steps: List[SkillStep] = Field(
        default_factory=list, description="有序执行步骤列表。"
    )
