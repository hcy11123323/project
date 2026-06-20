# 技能库指南

本文档介绍如何使用和创建 Agentic Playwright MCP 的技能。

## 概述

技能库是 Agentic Playwright MCP 的核心组件，它包含：

- **站点适配器** (`domains/`)：针对特定网站的自动化脚本
- **交互模板** (`interactions/`)：通用的 UI 交互模式
- **使用指南** (`guides/`)：Markdown 格式的说明文档

## 技能类型

### 站点适配器

针对特定网站的完整自动化流程：

```python
# src/skill_library/domains/baidu_search.py
from skill_library.skill_base import SkillBase, SkillResult, SkillContext

class BaiduSearchSkill(SkillBase):
    id = "baidu_search"
    name = "百度搜索"
    description = "在百度搜索关键词并获取结果"
    triggers = ["百度", "搜索", "baidu"]
    url_patterns = ["*.baidu.com"]

    async def execute(self, page, context: SkillContext) -> SkillResult:
        await page.goto("https://www.baidu.com")
        await page.fill("#kw", context.task)
        await page.click("#su")
        await page.wait_for_navigation()
        return SkillResult(success=True, output="搜索完成")
```

### 交互模板

通用的 UI 交互模式，适用于任意网站：

```python
# src/skill_library/interactions/login_flow.py
from skill_library.skill_base import SkillBase, SkillResult, SkillContext

class LoginFlowSkill(SkillBase):
    id = "login_flow"
    name = "通用登录"
    description = "在任意网站实现登录功能"
    triggers = ["登录", "login", "sign in"]
    url_patterns = ["*"]

    async def execute(self, page, context: SkillContext) -> SkillResult:
        # 通用登录逻辑
        username = context.variables.get("username")
        password = context.variables.get("password")
        # ... 实现登录流程
        return SkillResult(success=True, output="登录成功")
```

## SkillBase 接口

所有技能都必须继承 `SkillBase` 抽象类：

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    output: str
    error: Optional[str] = None

@dataclass
class SkillContext:
    """技能执行上下文"""
    task: str
    domain: Optional[str] = None
    page_url: str = ""
    variables: dict = None

class SkillBase(ABC):
    """技能基类"""

    id: str  # 技能唯一标识
    name: str  # 技能名称
    description: str  # 技能描述
    triggers: list[str]  # 触发关键词
    url_patterns: list[str]  # URL 匹配模式

    @abstractmethod
    async def execute(self, page, context: SkillContext) -> SkillResult:
        """执行技能"""
        pass
```

### 属性说明

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 技能唯一标识，如 `"baidu_search"` |
| `name` | `str` | 人类可读的技能名称 |
| `description` | `str` | 技能功能描述 |
| `triggers` | `list[str]` | 触发关键词列表，用于技能匹配 |
| `url_patterns` | `list[str]` | URL 匹配模式，支持通配符 |

### execute 方法

```python
async def execute(self, page, context: SkillContext) -> SkillResult:
    """
    执行技能

    Args:
        page: Playwright Page 对象
        context: 执行上下文，包含任务描述、域名、变量等

    Returns:
        SkillResult: 执行结果
    """
    pass
```

## skills.yaml 配置

除了 Python 类，还可以通过 YAML 声明式配置技能：

```yaml
# src/skill_library/skills.yaml
skills:
  - id: baidu_search
    name: 百度搜索
    type: domain
    triggers:
      - 百度
      - 搜索
      - baidu
    url_patterns:
      - "*.baidu.com"
    file: domains/baidu_search.py
    function: run
    description: 在百度搜索关键词
    priority: 10
    dependencies: []

  - id: login_flow
    name: 通用登录
    type: interaction
    triggers:
      - 登录
      - login
      - sign in
    url_patterns:
      - "*"
    file: interactions/login_flow.py
    function: run
    description: 通用登录流程
    priority: 5
    dependencies: []
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | `string` | 是 | 技能唯一标识 |
| `name` | `string` | 是 | 技能名称 |
| `type` | `string` | 是 | 技能类型：`domain` 或 `interaction` |
| `triggers` | `list[string]` | 是 | 触发关键词 |
| `url_patterns` | `list[string]` | 是 | URL 匹配模式 |
| `file` | `string` | 是 | 技能文件路径 |
| `function` | `string` | 是 | 入口函数名 |
| `description` | `string` | 是 | 技能描述 |
| `priority` | `int` | 否 | 优先级（默认 0，数值越大优先级越高） |
| `dependencies` | `list[string]` | 否 | 依赖的其他技能 |

## 创建新技能

### 方式一：继承 SkillBase

1. 创建技能文件：

```python
# src/skill_library/domains/my_site.py
from skill_library.skill_base import SkillBase, SkillResult, SkillContext

class MySiteSkill(SkillBase):
    id = "my_site"
    name = "我的网站"
    description = "自动化操作我的网站"
    triggers = ["我的网站", "my site"]
    url_patterns = ["*.example.com"]

    async def execute(self, page, context: SkillContext) -> SkillResult:
        try:
            # 1. 导航到目标页面
            await page.goto("https://example.com")

            # 2. 执行操作
            await page.fill("#search", context.task)
            await page.click("#submit")

            # 3. 等待结果
            await page.wait_for_navigation()

            # 4. 返回结果
            return SkillResult(
                success=True,
                output="操作完成"
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output="",
                error=str(e)
            )
```

2. 注册技能（自动发现）：

将文件放入 `src/skill_library/domains/` 目录，系统会自动发现并注册。

### 方式二：YAML + 函数

1. 创建技能函数：

```python
# src/skill_library/domains/my_site.py
async def run(page, task: str, **kwargs):
    """我的网站自动化"""
    await page.goto("https://example.com")
    await page.fill("#search", task)
    await page.click("#submit")
    await page.wait_for_navigation()
    return {"success": True, "output": "操作完成"}
```

2. 在 `skills.yaml` 中声明：

```yaml
skills:
  - id: my_site
    name: 我的网站
    type: domain
    triggers:
      - 我的网站
      - my site
    url_patterns:
      - "*.example.com"
    file: domains/my_site.py
    function: run
    description: 自动化操作我的网站
```

## 技能查找

### 使用 browse_skills

```python
# 按关键词查找
results = await browse_skills("百度 搜索")

# 按 URL 查找
results = await browse_skills("https://www.baidu.com")
```

### 查找逻辑

1. **关键词匹配**：将查询词与技能的 `triggers` 列表匹配
2. **URL 模式匹配**：将 URL 与技能的 `url_patterns` 匹配
3. **优先级排序**：匹配结果按 `priority` 降序排列
4. **返回 Top N**：默认返回前 5 个匹配结果

## 使用指南文档

每个技能都可以附带一个 Markdown 格式的使用指南：

```markdown
# 如何实现百度搜索

## 适用场景
需要在百度搜索关键词并获取搜索结果。

## 模式
1. 导航到 `https://www.baidu.com`
2. 在搜索框 (`#kw`) 输入关键词
3. 点击搜索按钮 (`#su`)
4. 等待搜索结果页加载

## 选择器
| 元素 | 主选择器 | 备选 |
|------|---------|------|
| 搜索框 | `#kw` | `input[name='wd']`, `.s_ipt` |
| 搜索按钮 | `#su` | `input[type='submit']`, `.btn-search` |

## 常见问题
- 百度有时会弹出验证码，需要视觉识别辅助
- 搜索结果页的 URL 会变化为 `www.baidu.com/s?wd=...`
```

指南文件放在 `src/skill_library/guides/` 目录下，文件名格式为 `how_to_<skill_id>.md`。

## 域配置（Layer 3）

站点适配器通常需要域配置文件：

```yaml
# domains/my_site.yaml
name: my_site
base_url: https://example.com
locators:
  search_input:
    css:
      - "#search"
      - "input[name='q']"
      - ".search-box"
    xpath:
      - "//input[@id='search']"
  submit_button:
    css:
      - "#submit"
      - "button[type='submit']"
      - ".btn-search"
    xpath:
      - "//button[@id='submit']"
```

### 选择器优先级

1. CSS 选择器（优先）
2. XPath 选择器（备选）
3. 视觉识别（最后手段）

### 自愈写回

当选择器失效时，系统会：

1. 尝试所有备选选择器
2. 如果全部失败，使用视觉识别定位元素
3. 自动更新 YAML 配置文件
4. 下次执行时使用新的选择器

## 最佳实践

### 1. 提供多个备选选择器

```yaml
locators:
  element:
    css:
      - "#primary-id"          # 最稳定
      - ".class-name"          # 次稳定
      - "div[data-type='x']"   # 备选
    xpath:
      - "//div[@id='primary-id']"  # XPath 备选
```

### 2. 使用有意义的触发词

```yaml
triggers:
  - 百度搜索      # 具体
  - 搜索引擎      # 通用
  - baidu        # 英文
  - web search   # 英文通用
```

### 3. 编写详细的指南文档

指南文档帮助 AI 理解技能的使用场景和注意事项。

### 4. 测试技能

```bash
# 运行技能测试
python -m pytest tests/test_skills.py -v

# 手动测试
browser-agent run "在百度搜索 Python 教程" --max-steps 5
```

## 示例技能

### 百度搜索

```python
# src/skill_library/domains/baidu_search.py
class BaiduSearchSkill(SkillBase):
    id = "baidu_search"
    name = "百度搜索"
    triggers = ["百度", "搜索", "baidu"]
    url_patterns = ["*.baidu.com"]

    async def execute(self, page, context):
        await page.goto("https://www.baidu.com")
        await page.fill("#kw", context.task)
        await page.click("#su")
        await page.wait_for_navigation()
        return SkillResult(success=True, output="搜索完成")
```

### GitHub 登录

```python
# src/skill_library/domains/github_login.py
class GithubLoginSkill(SkillBase):
    id = "github_login"
    name = "GitHub 登录"
    triggers = ["github", "登录", "login"]
    url_patterns = ["*.github.com"]

    async def execute(self, page, context):
        username = context.variables["username"]
        password = context.variables["password"]
        await page.goto("https://github.com/login")
        await page.fill("#login_field", username)
        await page.fill("#password", password)
        await page.click("input[type='submit']")
        await page.wait_for_navigation()
        return SkillResult(success=True, output="登录成功")
```

### 通用登录

```python
# src/skill_library/interactions/login_flow.py
class LoginFlowSkill(SkillBase):
    id = "login_flow"
    name = "通用登录"
    triggers = ["登录", "login", "sign in"]
    url_patterns = ["*"]

    async def execute(self, page, context):
        url = context.variables["url"]
        username_sel = context.variables["username_selector"]
        password_sel = context.variables["password_selector"]
        submit_sel = context.variables["submit_selector"]
        username = context.variables["username"]
        password = context.variables["password"]

        await page.goto(url)
        await page.fill(username_sel, username)
        await page.fill(password_sel, password)
        await page.click(submit_sel)
        await page.wait_for_navigation()
        return SkillResult(success=True, output="登录成功")
```
