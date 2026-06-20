# Examples

可运行的示例脚本，演示 **Agentic Playwright MCP** 的核心功能。

## 前置条件

```bash
# 安装项目（在项目根目录执行）
pip install -e .

# 安装 Playwright 浏览器
playwright install chromium

# （可选）复制 .env 并配置 API Key（视觉功能需要）
cp .env.example .env
```

## 运行方式

所有示例都是独立脚本，在**项目根目录**运行：

```bash
python examples/01_basic_browser.py
```

## 示例列表

| # | 文件 | 说明 |
|---|------|------|
| 01 | `01_basic_browser.py` | 启动浏览器、导航、截图、提取文本 |
| 02 | `02_script_engine.py` | 脚本引擎沙箱演示（不需要真实浏览器） |
| 03 | `03_domain_automation.py` | 域配置驱动的自动化 + 自愈机制 |
| 04 | `04_event_hooks.py` | 事件钩子系统演示 |
| 05 | `05_mcp_client.py` | MCP 客户端连接演示 |

## 示例详解

### 01 — 基础浏览器操作

展示最底层 API：`BrowserManager` 管理浏览器生命周期，`do_goto` / `do_screenshot` 执行操作。

核心概念：
- `get_browser_manager()` 返回单例
- `bm.launch(headless=False)` 打开可见浏览器
- `do_goto(page, url)` 导航并处理错误
- 操作完毕后调用 `bm.close()`

### 02 — 脚本引擎

脚本引擎在受限命名空间中执行 AI 生成的 Python 代码。只有白名单的内置函数和注入的函数可用。

核心概念：
- `get_script_engine().execute(code)` 安全执行代码
- 可用函数：`goto`, `click`, `fill`, `screenshot`, `get_url`, `get_title`, `print`, `log`
- 脚本中禁止 `import`、文件系统访问、网络访问
- 输出通过 `ScriptResult.output` 捕获

### 03 — 域配置自动化

域配置（YAML 文件）定义站点特定的选择器，支持多个备选。`smart_*` 函数按顺序尝试选择器，成功后自动提升优先级。

核心概念：
- `domains/*.yaml` 定义元素定位器（CSS + XPath 备选）
- `smart_fill("search_input", "text", domain="baidu")` 从配置解析选择器
- 自愈机制：主选择器失败时，备选选择器被尝试并提升
- 组合操作：`smart_search`, `smart_login`, `smart_fill_form`

### 04 — 事件钩子

`EventBus` 在 Agent 循环的关键点提供钩子，用于日志、监控、拦截。

核心概念：
- `EventBus.on(event_name, callback)` 注册钩子
- 7 种标准事件：`task.start`, `task.end`, `step.start`, `step.end`, `error`, `skill.found`, `script.exec`
- 钩子可以修改数据或阻止操作

### 05 — MCP 客户端

使用 MCP Python SDK 连接 MCP Server。支持 stdio（子进程）和 SSE（网络）两种传输方式。

核心概念：
- `StdioServerParameters` 以子进程方式启动 Server
- `session.call_tool("tool_name", arguments={...})` 调用 MCP 工具
- 可用工具：`ping`, `browser_launch`, `screenshot`, `run_script`, `browse_skills` 等

## 输出目录

截图和其他输出保存到 `examples/output/`，目录会自动创建。

## CLI 替代方式

除了运行 Python 脚本，也可以使用 CLI：

```bash
# 单次执行任务
browser-agent run "打开 https://example.com 并截图"

# 启动 MCP 服务
browser-agent serve

# 检查环境
browser-agent doctor
```
