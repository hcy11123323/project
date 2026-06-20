# 架构决策记录 (ADR)

本目录记录 Agentic Playwright MCP 项目中的关键架构决策。

## 什么是 ADR？

架构决策记录 (Architecture Decision Record) 是一种轻量级文档格式，用于记录项目中的重要技术决策。每个 ADR 包含：

- **标题**：决策的简短描述
- **状态**：提议、接受、废弃、取代
- **上下文**：决策的背景和问题
- **决策**：做出的选择
- **后果**：决策带来的影响

## 决策列表

| 编号 | 标题 | 状态 | 日期 |
|------|------|------|------|
| [001](001-three-layer-architecture.md) | 三层架构设计 | 接受 | 2024-01 |
| [002](002-sandboxed-script-engine.md) | 沙箱脚本引擎 | 接受 | 2024-01 |
| [003](003-agent-loop-design.md) | Agent 循环设计 | 接受 | 2024-01 |

## 为什么需要 ADR？

1. **知识传承**：新成员可以快速理解决策背景
2. **避免重复讨论**：已决策的事项不需要重新讨论
3. **追溯历史**：可以追溯决策的演变过程
4. **团队共识**：确保团队对架构方向达成一致

## 如何编写 ADR？

1. 在 `docs/adr/` 目录下创建新文件：`<编号>-<标题>.md`
2. 使用 [ADR 模板](https://adr.github.io/) 编写内容
3. 在本页面添加链接
4. 提交 PR 进行评审

## 参考资源

- [ADR GitHub Organization](https://adr.github.io/)
- [Michael Nygard 的原始文章](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ThoughtWorks 技术雷达](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
