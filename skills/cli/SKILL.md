---
name: cli
description: 现代 CLI 应用程序开发的完整指南：架构分层、参数解析、交互式提示、结构化日志、配置管理、错误处理与测试。在开发命令行工具、脚手架或终端应用时使用；用户提到「CLI / 命令行工具 / 终端应用 / commander / clack / 参数解析 / 交互式命令行」等时也应触发。
metadata:
  author: Shenyan Du
  version: "2026.11.16"
  source: Generated from file-wizard project, scripts located at https://github.com/dushenyan/skills
---

> 该技能基于 file-wizard v0.1.0，生成于 2026-03-26。

此技能提供构建现代、用户友好的命令行界面（CLI）应用程序的完整指南，涵盖架构设计、参数解析、交互式提示、日志输出、配置管理、错误处理和测试策略等关键方面。

## 核心参考

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 架构设计 | CLI 应用程序的核心架构设计模式和最佳实践 | [core-architecture](references/core-architecture.md) |
| 参数解析 | Commander.js 参数解析和选项处理 | [core-argument-parsing](references/core-argument-parsing.md) |
| 日志输出 | 实现结构化日志和美观的命令行输出 | [core-logging-output](references/core-logging-output.md) |
| 配置管理 | CLI 应用程序的配置管理，包括 YAML 配置、环境变量和验证 | [core-configuration](references/core-configuration.md) |

## 功能

### 交互式界面

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 交互式提示 | 使用 @clack/prompts 构建友好的交互式命令行界面 | [feature-interactive-prompts](references/feature-interactive-prompts.md) |

### 最佳实践

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 错误处理 | CLI 应用程序的错误处理和用户友好的错误消息 | [best-practices-error-handling](references/best-practices-error-handling.md) |
| 测试策略 | CLI 应用程序的测试策略和最佳实践 | [best-practices-testing](references/best-practices-testing.md) |

## 技术栈

- **Commander.js**: 强大的命令行解析框架
- **@clack/prompts**: 现代化的交互式提示库
- **chalk**: 终端字符串样式和颜色
- **ora**: 优雅的终端加载动画
- **Zod**: TypeScript 优先的模式验证
- **Vitest**: 快速的单元测试框架

## 关键特性

- **模块化架构**: 清晰的分层架构，将命令、交互式界面和业务逻辑分离
- **类型安全**: 使用 TypeScript 严格模式，确保代码质量
- **用户友好**: 提供交互式界面和彩色输出，提升用户体验
- **配置灵活**: 支持 YAML 配置文件和环境变量，满足不同场景需求
- **错误处理**: 完善的错误处理机制，提供友好的错误消息
- **测试覆盖**: 完整的测试策略，包括单元测试、集成测试和端到端测试
