"""
Layer 2 — 技能基类（SkillBase）。

所有技能（站点适配器、通用交互模板）的抽象基类。
子类必须实现 metadata() 和 execute() 方法。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from playwright.sync_api import Page


# ---------------------------------------------------------------------------
# 技能元数据
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SkillMeta:
    """技能元数据 —— 用于注册表索引和检索。

    Attributes:
        id: 唯一标识符，格式为 "type/name"（如 "domain/baidu_search"）。
        name: 人类可读名称。
        type: 技能类型，"domain"（站点适配器）或 "interaction"（通用交互）。
        triggers: 触发关键词列表，用于语义匹配。
        url_patterns: URL 匹配模式列表，'*' 为通配符。
        description: 技能描述。
        version: 技能版本号。
    """

    id: str
    name: str
    type: str  # "domain" | "interaction"
    triggers: List[str] = field(default_factory=list)
    url_patterns: List[str] = field(default_factory=list)
    description: str = ""
    version: str = "1.0.0"


# ---------------------------------------------------------------------------
# 执行结果
# ---------------------------------------------------------------------------


@dataclass
class SkillResult:
    """技能执行结果。

    Attributes:
        success: 是否执行成功。
        message: 结果描述信息。
        data: 附带数据（如截图路径、提取的文本等）。
        error: 失败时的错误信息。
    """

    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    error: str = ""

    @classmethod
    def ok(cls, message: str = "", **data: Any) -> SkillResult:
        """创建成功结果。"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, error: str, message: str = "") -> SkillResult:
        """创建失败结果。"""
        return cls(success=False, message=message, error=error)


# ---------------------------------------------------------------------------
# 抽象基类
# ---------------------------------------------------------------------------


class SkillBase(ABC):
    """技能抽象基类 —— 所有技能必须继承此类。

    子类需要实现:
        - metadata(): 返回 SkillMeta 实例，描述技能的元数据。
        - execute(page, **params): 在给定页面上执行技能逻辑。

    可选覆盖:
        - validate_params(params): 校验参数合法性，默认全部通过。
        - setup(page): 执行前的准备工作（如等待页面加载）。
        - teardown(page): 执行后的清理工作（如关闭弹窗）。

    使用示例::

        class BaiduSearch(SkillBase):
            def metadata(self) -> SkillMeta:
                return SkillMeta(
                    id="domain/baidu_search",
                    name="百度搜索",
                    type="domain",
                    triggers=["百度", "搜索"],
                    url_patterns=["*.baidu.com"],
                )

            def execute(self, page: Page, keyword: str) -> SkillResult:
                page.goto("https://www.baidu.com")
                page.fill("#kw", keyword)
                page.click("#su")
                return SkillResult.ok(f"搜索完成: {keyword}")
    """

    # -------------------------------------------------------------------
    # 抽象接口
    # -------------------------------------------------------------------

    @abstractmethod
    def metadata(self) -> SkillMeta:
        """返回技能元数据。

        Returns:
            SkillMeta 实例，描述技能的标识、类型和触发条件。
        """

    @abstractmethod
    def execute(self, page: Page, **params: Any) -> SkillResult:
        """在给定页面上执行技能逻辑。

        Args:
            page: Playwright 页面实例。
            **params: 技能所需的参数（由子类定义）。

        Returns:
            SkillResult: 执行结果。
        """

    # -------------------------------------------------------------------
    # 可选覆盖
    # -------------------------------------------------------------------

    def validate_params(self, params: Dict[str, Any]) -> Optional[str]:
        """校验参数合法性。

        Args:
            params: 待校验的参数字典。

        Returns:
            None 表示校验通过；字符串表示错误信息。
        """
        return None

    def setup(self, page: Page) -> None:
        """执行前的准备工作。

        默认为空操作。子类可覆盖以添加等待加载、关闭弹窗等逻辑。

        Args:
            page: Playwright 页面实例。
        """

    def teardown(self, page: Page) -> None:
        """执行后的清理工作。

        默认为空操作。子类可覆盖以添加清理逻辑。

        Args:
            page: Playwright 页面实例。
        """

    # -------------------------------------------------------------------
    # 便利方法
    # -------------------------------------------------------------------

    def run(self, page: Page, **params: Any) -> SkillResult:
        """完整执行流程：校验 → 准备 → 执行 → 清理。

        这是外部调用的统一入口，封装了完整的生命周期。

        Args:
            page: Playwright 页面实例。
            **params: 技能参数。

        Returns:
            SkillResult: 执行结果。
        """
        # 1. 参数校验
        error = self.validate_params(params)
        if error is not None:
            return SkillResult.fail(error=f"参数校验失败: {error}")

        # 2. 准备阶段
        try:
            self.setup(page)
        except Exception as exc:
            return SkillResult.fail(error=f"setup 失败: {exc}")

        # 3. 执行阶段
        try:
            result = self.execute(page, **params)
        except Exception as exc:
            return SkillResult.fail(error=f"执行异常: {exc}")
        finally:
            # 4. 清理阶段（无论成功失败都执行）
            try:
                self.teardown(page)
            except Exception:
                pass  # 清理失败不覆盖主结果

        return result

    # -------------------------------------------------------------------
    # 魔术方法
    # -------------------------------------------------------------------

    def __repr__(self) -> str:
        meta = self.metadata()
        return f"<{self.__class__.__name__} id={meta.id!r}>"
