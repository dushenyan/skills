---
name: core-architecture
description: CLI 应用程序的核心架构设计模式和最佳实践
---

# CLI 核心架构

此技能涵盖构建现代 CLI 应用程序的核心架构设计原则，包括模块化、可扩展性和可维护性。

## 架构原则

### 分层架构

采用清晰的分层架构，将关注点分离：

```typescript
src/
├── cli.ts              # CLI 入口和命令注册
├── commands/           # 命令实现（命令式）
│   ├── organize.ts
│   ├── smart-organize.ts
│   └── ...
├── interactive/        # 交互式命令实现
│   ├── organize.ts
│   ├── smart-organize.ts
│   └── ...
├── utils/              # 工具函数
│   ├── logger.ts
│   ├── command-utils.ts
│   └── ...
├── config.ts           # 配置管理
├── types.ts            # 类型定义
└── services/           # 业务逻辑服务
```

### 命令模块化

每个命令独立实现，通过 Commander.js 注册：

```typescript
import { Command } from 'commander'
import { runOrganizeCommand } from './commands/organize'

export function buildCli(): Command {
  const program = new Command()

  program
    .name('my-cli')
    .description('CLI 描述')

  program
    .command('organize')
    .description('命令描述')
    .argument('[path]', '可选参数')
    .option('-c, --category <type>', '选项描述')
    .option('-v, --verbose', '详细输出')
    .action(runOrganizeCommand)

  return program
}
```

### 命令与交互分离

将命令式（CLI 参数）和交互式（UI 提示）实现分离：

```typescript
// commands/organize.ts - 命令式实现
export async function runOrganizeCommand(path: string, opts: CliOptions): Promise<void> {
  // 直接执行命令逻辑
}

// interactive/organize.ts - 交互式实现
export async function runOrganizeInteractive(): Promise<void> {
  // 使用 @clack/prompts 收集用户输入
  // 构建命令参数
  // 调用命令式实现
}
```

## 入口点设计

### 条件执行

确保 CLI 只在直接执行时启动，避免被 import 时重复触发：

```typescript
const isEntryPoint = process.argv[1]?.endsWith('cli.js') || process.argv[1]?.endsWith('cli.ts')

if (isEntryPoint) {
  const cli = buildCli()
  cli.parseAsync(process.argv)
}
```

### 默认行为

当没有提供命令时，显示帮助信息或进入交互模式：

```typescript
program.action(() => {
  program.help()
})

// 或者进入交互模式
if (!hasCommand) {
  runInteractiveMode()
}
```

## 类型系统

### 统一类型定义

在 `types.ts` 中定义所有接口：

```typescript
export interface CliOptions {
  path?: string
  category?: string
  rule?: string
  dryRun?: boolean
  verbose?: boolean
  provider?: string
  proxy?: string
}

export interface AppConfig {
  defaultProvider: string
  proxy?: string
  ignoreList?: string[]
}
```

### 类型安全

使用 TypeScript 严格模式，确保类型安全：

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

## 可扩展性

### 插件系统

设计插件接口，支持功能扩展：

```typescript
interface Plugin {
  name: string
  register(program: Command): void
}

export function registerPlugins(program: Command, plugins: Plugin[]): void {
  plugins.forEach(plugin => plugin.register(program))
}
```

### 中间件模式

支持命令执行前后的中间件：

```typescript
type Middleware = (ctx: CommandContext, next: () => Promise<void>) => Promise<void>

export async function executeCommand(
  command: Command,
  middlewares: Middleware[],
  handler: () => Promise<void>
): Promise<void> {
  const ctx: CommandContext = { command, options: command.opts() }

  const chain = middlewares.reduce(
    (next, middleware) => () => middleware(ctx, next),
    handler
  )

  await chain()
}
```

## 要点

- 使用 Commander.js 作为 CLI 框架，提供强大的命令解析和帮助生成
- 将命令实现与交互式界面分离，提高代码复用性
- 采用分层架构，将业务逻辑与 CLI 层解耦
- 使用 TypeScript 严格类型检查，确保代码质量
- 设计可扩展的插件系统，支持功能扩展
- 条件执行入口点，避免重复初始化

<!--
来源参考：
- file-wizard 项目源码
- Commander.js 文档: https://commander.js.org/
- TypeScript 最佳实践
-->
