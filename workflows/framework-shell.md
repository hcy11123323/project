export const meta = {
  name: 'framework-shell',
  description: '从"能跑的代码"到"可扩展框架"的 4 个骨架增强',
  phases: [
    { title: 'Plugin', detail: '插件化技能加载：SkillBase + skills.yaml 规范' },
    { title: 'CLI', detail: 'CLI 工具雏形：cli.py + serve/run/doctor 命令' },
    { title: 'Logging', detail: '日志/事件钩子：logging.py + hooks.py' },
    { title: 'Docs', detail: '文档生成器 + 示例：MkDocs 配置 + examples/' },
    { title: 'Verify', detail: '测试 + 代码检查 + 完整性验证' },
  ],
}

// ---------------------------------------------------------------------------
// Phase 1: 插件化技能加载
// ---------------------------------------------------------------------------
phase('Plugin')

// 1.1 SkillBase 抽象类
await agent('Create src/skill_library/skill_base.py with SkillBase abstract class', {
  label: 'skill_base',
  phase: 'Plugin',
  prompt: `Create the file src/skill_library/skill_base.py in the project at D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Requirements:
- Define a SkillBase abstract class with:
  - Abstract method execute(self, page, context) -> SkillResult
  - Properties: id, name, description, triggers (list[str]), url_patterns (list[str])
  - A SkillResult dataclass: success (bool), output (str), error (str|None)
  - A SkillContext dataclass: task (str), domain (str|None), page_url (str), variables (dict)
- The execute method receives the Playwright page and context, returns SkillResult
- Include docstrings in Chinese
- Use abc.ABC and abc.abstractmethod
- This is the base class that all site adapters and interaction templates will inherit from`,
})

// 1.2 skills.yaml 规范
await agent('Create skills.yaml schema and loader', {
  label: 'skills_yaml',
  phase: 'Plugin',
  prompt: `Create TWO files in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp:

1. src/skill_library/skills_schema.py:
- Define Pydantic models for the skills.yaml schema:
  - SkillDeclaration(BaseModel): id, name, type (domain/interaction), triggers (list[str]), url_patterns (list[str]), file (str), function (str), description (str), priority (int, default 0), dependencies (list[str], default empty)
  - SkillsConfig(BaseModel): skills (list[SkillDeclaration])
- Include a load_skills_yaml(path) function that reads and validates skills.yaml
- Include a discover_skills(directory) function that scans a directory for .py files and auto-generates declarations

2. src/skill_library/skills.yaml:
- Migrate the existing registry.json content into YAML format
- Add priority field to each skill
- Add a comment header explaining the schema

This replaces registry.json with a more extensible format.`,
})

// 1.3 更新 registry.py 使用新系统
await agent('Update registry.py to use SkillBase and skills.yaml', {
  label: 'registry_update',
  phase: 'Plugin',
  prompt: `Update the file src/skill_library/registry.py in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Changes needed:
- Import SkillBase, SkillResult, SkillContext from skill_base
- Import SkillsConfig, load_skills_yaml from skills_schema
- Add a register_skill_class method that accepts a SkillBase subclass instance
- Add a discover_skills method that scans a directory for .py files, imports them, and registers any SkillBase subclasses found
- Keep backward compatibility with existing load_from_json method
- The get_detail method should now also check skill classes for source code
- Add a run_skill(skill_id, page, context) method that executes a skill via SkillBase.execute()
- Keep all existing functionality working

Do NOT break existing tests.`,
})

// 1.4 测试插件系统
await agent('Write tests for plugin system', {
  label: 'plugin_tests',
  phase: 'Plugin',
  prompt: `Create tests/test_skill_plugin.py in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Test the following:
1. SkillBase subclass can be created and executed
2. SkillsConfig Pydantic model validates correctly
3. load_skills_yaml reads and parses YAML
4. discover_skills finds .py files in a directory
5. register_skill_class adds a skill class
6. run_skill executes a skill class and returns SkillResult
7. Backward compatibility: existing load_from_json still works

Use tmp_path for temp files. Mock Playwright page for execute tests.
Run with: python -m pytest tests/test_skill_plugin.py -v`,
})

// ---------------------------------------------------------------------------
// Phase 2: CLI 工具雏形
// ---------------------------------------------------------------------------
phase('CLI')

// 2.1 CLI 入口
await agent('Create CLI entry point with serve/run/doctor commands', {
  label: 'cli',
  phase: 'CLI',
  prompt: `Create src/cli.py in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Requirements:
- Use argparse (no external dependencies)
- Three subcommands:
  1. serve: Start MCP server (calls src.server.main())
  2. run "task description": Execute a single task via AgentLoop, print results, then exit
     - Options: --max-steps N, --headless, --cloak
  3. doctor: Check environment health
     - Check Python version >= 3.11
     - Check playwright installed
     - Check chromium browser installed (playwright install --dry-run or similar)
     - Check .env file exists
     - Check API keys configured (ANTHROPIC_API_KEY or OPENAI_API_KEY)
     - Print status for each check
- Add a main() function as entry point
- Use Chinese for user-facing messages`,
})

// 2.2 更新 pyproject.toml 注册 CLI
await agent('Update pyproject.toml to register browser-agent CLI', {
  label: 'pyproject_cli',
  phase: 'CLI',
  prompt: `Update pyproject.toml in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Add a new entry point under [project.scripts]:
  browser-agent = "src.cli:main"

Keep the existing entry point:
  agentic-playwright-mcp = "src.server:main"

Also update the version to "0.2.0" since we're adding major features.`,
})

// 2.3 CLI 测试
await agent('Write CLI tests', {
  label: 'cli_tests',
  phase: 'CLI',
  prompt: `Create tests/test_cli.py in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Test the following:
1. serve subcommand calls main()
2. run subcommand calls AgentLoop.run() with correct task
3. doctor subcommand checks environment
4. --help flag works for all subcommands
5. Missing task for 'run' shows error

Use unittest.mock to patch dependencies. Do NOT actually start servers or browsers.
Run with: python -m pytest tests/test_cli.py -v`,
})

// ---------------------------------------------------------------------------
// Phase 3: 日志/事件钩子
// ---------------------------------------------------------------------------
phase('Logging')

// 3.1 结构化日志
await agent('Create structured logging module', {
  label: 'logging_mod',
  phase: 'Logging',
  prompt: `Create src/core/logging.py in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Requirements:
- Use Python standard library logging (no external deps for now)
- Define a setup_logging(level="INFO", log_file=None) function
- Configure JSON-formatted log output:
  - timestamp, level, logger name, message, extra fields
  - Include trace_id in each log entry (generate UUID per task)
- Define a get_logger(name) function that returns a configured logger
- Define log levels for Agent events:
  - AGENT_STEP = 25 (between INFO and WARNING)
  - AGENT_ACTION = 26
  - LLM_CALL = 27
- Include a context manager trace_context(task_id) that sets the trace_id for all logs within the block
- All log output should be JSON lines (one JSON object per line)`,
})

// 3.2 事件钩子系统
await agent('Create event hooks system', {
  label: 'hooks',
  phase: 'Logging',
  prompt: `Create src/core/hooks.py in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Requirements:
- Define an EventBus class:
  - on(event_name: str, callback: Callable) -> None
  - off(event_name: str, callback: Callable) -> None
  - emit(event_name: str, data: dict) -> None
  - Registered callbacks are called in order for each emit
- Define standard event names as constants:
  - ON_TASK_START = "task.start"
  - ON_TASK_END = "task.end"
  - ON_STEP_START = "step.start"
  - ON_STEP_END = "step.end"
  - ON_ERROR = "error"
  - ON_SKILL_FOUND = "skill.found"
  - ON_SCRIPT_EXEC = "script.exec"
  - ON_VISION_CALL = "vision.call"
- Define a global get_event_bus() -> EventBus singleton
- Include a default logging hook that logs all events via the logging module
- Include register_default_hooks(bus) that registers the logging hook`,
})

// 3.3 集成到 AgentLoop
await agent('Integrate logging and hooks into AgentLoop', {
  label: 'integrate_hooks',
  phase: 'Logging',
  prompt: `Update src/core/agent_loop.py in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Changes:
- Import and use get_event_bus from src.core.hooks
- Import and use get_logger from src.core.logging
- At the start of run(): emit ON_TASK_START with task info, get a logger
- At each step: emit ON_STEP_START and ON_STEP_END with step info
- On error: emit ON_ERROR with error info
- In _do_plan when skill found: emit ON_SKILL_FOUND
- In _do_act: emit ON_SCRIPT_EXEC
- Add on_step callback to emit step events
- Do NOT break existing tests

Also update src/server.py to call register_default_hooks() on startup.`,
})

// 3.4 测试
await agent('Write logging and hooks tests', {
  label: 'logging_tests',
  phase: 'Logging',
  prompt: `Create tests/test_hooks.py in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Test the following:
1. EventBus on/emit/off works correctly
2. Multiple callbacks are called in order
3. emit with no callbacks doesn't crash
4. Standard event name constants exist
5. get_event_bus returns singleton
6. register_default_hooks registers a logging hook

Also create tests/test_logging.py:
1. setup_logging configures root logger
2. get_logger returns a logger with correct name
3. trace_context sets trace_id
4. Log output is valid JSON

Use mock and capture log output for verification.`,
})

// ---------------------------------------------------------------------------
// Phase 4: 文档生成器 + 示例
// ---------------------------------------------------------------------------
phase('Docs')

// 4.1 MkDocs 配置
await agent('Create MkDocs configuration', {
  label: 'mkdocs',
  phase: 'Docs',
  prompt: `Create the following files in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp:

1. mkdocs.yml (project root):
  - site_name: Agentic Playwright MCP
  - theme: material
  - nav:
    - Home: index.md
    - Quick Start: quickstart.md
    - Architecture: architecture.md
    - API Reference: api.md
    - Skill Library: skills.md
    - ADR: adr/index.md
  - plugins: [search, mkdocstrings]
  - mkdocstrings config: handler: python, options: show_source: true

2. docs/index.md: Project overview (copy/adapt from README.md)

3. docs/quickstart.md: 5-minute quickstart guide
  - pip install
  - make dev
  - Configure .env
  - Run first task
  - Example Claude Desktop config

4. docs/architecture.md: Architecture overview
  - 4-layer diagram
  - Script engine explanation
  - Agent loop state machine
  - Skill library structure

5. docs/skills.md: Skill library guide
  - How to create a new skill
  - SkillBase interface
  - skills.yaml format
  - Example: creating a site adapter

6. docs/adr/index.md: ADR index page with links
  - Create docs/adr/001-three-layer-architecture.md
  - Create docs/adr/002-sandboxed-script-engine.md
  - Create docs/adr/003-agent-loop-design.md
  - Each ADR: Title, Status, Context, Decision, Consequences`,
})

// 4.2 Examples 目录
await agent('Create examples directory with runnable scripts', {
  label: 'examples',
  phase: 'Docs',
  prompt: `Create the following files in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp:

1. examples/README.md: Index of all examples

2. examples/01_hello_browser.py:
  - Minimal example: launch browser, navigate, screenshot
  - Includes comments explaining each step
  - Can run standalone: python examples/01_hello_browser.py

3. examples/02_script_engine_demo.py:
  - Demonstrates script engine sandbox
  - Shows what's allowed and what's blocked
  - No real browser needed (mock mode)

4. examples/03_skill_library_demo.py:
  - Demonstrates browsing skills, getting skill details
  - Shows how to search by keyword and URL

5. examples/04_agent_loop_demo.py:
  - Demonstrates the agent loop with a simple task
  - Uses mock mode (no real browser)
  - Shows step-by-step execution

6. examples/05_custom_skill.py:
  - Shows how to create a custom skill
  - Defines a SkillBase subclass
  - Registers it and runs it

Each example should:
- Have a docstring explaining what it does
- Include Chinese comments
- Be runnable standalone
- Handle the case where browser is not available (graceful skip)`,
})

// 4.3 pyproject.toml 更新文档依赖
await agent('Add docs dependencies to pyproject.toml', {
  label: 'docs_deps',
  phase: 'Docs',
  prompt: `Update pyproject.toml in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Add a new optional dependency group:
  docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "mkdocstrings[python]>=0.24.0",
  ]

Also add a Makefile target:
  docs:
\tmkdocs serve

  docs-build:
\tmkdocs build

  docs-deploy:
\tmkdocs gh-deploy`,
})

// ---------------------------------------------------------------------------
// Phase 5: 验证
// ---------------------------------------------------------------------------
phase('Verify')

// 5.1 运行全部测试
await agent('Run full test suite', {
  label: 'test_all',
  phase: 'Verify',
  prompt: `Run the full test suite in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Execute: python -m pytest -v

If any tests fail, fix them. The target is ALL tests passing.
Report the total count of tests and pass/fail status.`,
})

// 5.2 代码检查
await agent('Run linting and format check', {
  label: 'lint',
  phase: 'Verify',
  prompt: `Run code quality checks in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Execute:
  ruff check .
  ruff format --check .

If there are issues, run:
  ruff check --fix .
  ruff format .

Report the results.`,
})

// 5.3 完整性检查
await agent('Verify project completeness', {
  label: 'completeness',
  phase: 'Verify',
  prompt: `Verify the project completeness in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Check that all these files exist and are non-empty:
1. src/skill_library/skill_base.py
2. src/skill_library/skills_schema.py
3. src/skill_library/skills.yaml
4. src/cli.py
5. src/core/logging.py
6. src/core/hooks.py
7. docs/index.md
8. docs/quickstart.md
9. docs/architecture.md
10. docs/skills.md
11. docs/adr/index.md
12. examples/01_hello_browser.py
13. examples/05_custom_skill.py
14. mkdocs.yml
15. tests/test_skill_plugin.py
16. tests/test_cli.py
17. tests/test_hooks.py
18. tests/test_logging.py

For each file, confirm it exists and report line count.
Also verify pyproject.toml has the browser-agent entry point and docs dependencies.

Report a summary table of all files with status (exists/missing) and line count.`,
})

// 5.4 更新 README
await agent('Update README.md with new features', {
  label: 'readme_update',
  phase: 'Verify',
  prompt: `Update README.md in D:\\Agentic-Playwright-Harness\\agentic-playwright-mcp

Add these sections (keep existing content):

## CLI 工具
\`\`\`bash
# 启动 MCP 服务
browser-agent serve

# 单次执行任务（调试用）
browser-agent run "帮我在百度搜索 Python 教程" --max-steps 5

# 检查环境
browser-agent doctor
\`\`\`

## 插件化技能
- skills.yaml 声明式配置
- SkillBase 抽象类，继承即可添加新技能
- 自动发现：丢 .py 文件到 domains/ 或 interactions/ 即可

## 文档
\`\`\`bash
pip install -e ".[docs]"
make docs  # 启动本地文档服务器
\`\`\`

Update the MCP tool list to include run_task (8 tools total).
Update the test count to reflect actual total.
Update the project structure to include new files.`,
})

log('Framework shell workflow complete.')
