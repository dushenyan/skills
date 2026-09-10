---
name: best-practices-error-handling
description: CLI 应用程序的错误处理和用户友好的错误消息
---

# 错误处理

此技能涵盖 CLI 应用程序的错误处理策略，包括错误捕获、用户友好的错误消息和恢复机制。

## 错误处理模式

### Try-Catch 包装

使用 try-catch 包装所有可能失败的操作：

```typescript
export async function runOrganizeCommand(path: string, opts: CliOptions): Promise<void> {
  const spinner = ora('正在扫描目录...').start()

  try {
    const config = await loadConfig()
    const files = await scanDirectory(path)
    await organizeFiles(files, opts)

    spinner.succeed('文件整理完成')
  }
  catch (error) {
    spinner.fail('文件整理失败')
    handleError(error)
    process.exitCode = 1
  }
}
```

### 错误处理函数

创建统一的错误处理函数：

```typescript
import chalk from 'chalk'
import process from 'node:process'

export function handleError(error: unknown): void {
  if (error instanceof Error) {
    console.error(chalk.red(`❌ 错误：${error.message}`))

    if (error.stack && process.env.DEBUG) {
      console.error(chalk.gray('\n堆栈跟踪：'))
      console.error(chalk.gray(error.stack))
    }
  }
  else {
    console.error(chalk.red(`❌ 未知错误：${String(error)}`))
  }
}
```

## 自定义错误类

### 基础错误类

创建自定义错误基类：

```typescript
export class CLIError extends Error {
  constructor(
    message: string,
    public code?: string,
    public exitCode: number = 1
  ) {
    super(message)
    this.name = 'CLIError'
  }
}
```

### 配置错误

```typescript
export class ConfigError extends CLIError {
  constructor(message: string) {
    super(message, 'CONFIG_ERROR', 2)
    this.name = 'ConfigError'
  }
}
```

### 验证错误

```typescript
export class ValidationError extends CLIError {
  constructor(message: string, public field?: string) {
    super(message, 'VALIDATION_ERROR', 3)
    this.name = 'ValidationError'
  }
}
```

### 网络错误

```typescript
export class NetworkError extends CLIError {
  constructor(message: string, public url?: string) {
    super(message, 'NETWORK_ERROR', 4)
    this.name = 'NetworkError'
  }
}
```

## 错误消息

### 用户友好的错误消息

提供清晰、可操作的错误消息：

```typescript
function getErrorMessage(error: unknown): string {
  if (error instanceof ConfigError) {
    return `配置错误：${error.message}\n` +
           `请检查配置文件或使用 --help 查看帮助`
  }

  if (error instanceof ValidationError) {
    const field = error.field ? `字段 "${error.field}" ` : ''
    return `验证错误：${field}${error.message}`
  }

  if (error instanceof NetworkError) {
    return `网络错误：${error.message}\n` +
           `请检查网络连接或代理设置`
  }

  if (error instanceof Error) {
    return error.message
  }

  return `未知错误：${String(error)}`
}
```

### 错误上下文

提供错误的上下文信息：

```typescript
export class CLIError extends Error {
  constructor(
    message: string,
    public code?: string,
    public exitCode: number = 1,
    public context?: Record<string, any>
  ) {
    super(message)
    this.name = 'CLIError'
  }

  toString(): string {
    let output = `${this.name}: ${this.message}`

    if (this.code) {
      output += ` [${this.code}]`
    }

    if (this.context) {
      output += `\n上下文：${JSON.stringify(this.context, null, 2)}`
    }

    return output
  }
}
```

## 错误恢复

### 重试机制

为网络请求实现重试机制：

```typescript
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number
    delay?: number
    onRetry?: (error: Error, attempt: number) => void
  } = {}
): Promise<T> {
  const { maxRetries = 3, delay = 1000, onRetry } = options

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    }
    catch (error) {
      if (attempt === maxRetries) {
        throw error
      }

      if (error instanceof Error && onRetry) {
        onRetry(error, attempt)
      }

      await new Promise(resolve => setTimeout(resolve, delay * attempt))
    }
  }

  throw new Error('重试次数已用尽')
}
```

### 回退机制

提供回退选项：

```typescript
export async function withFallback<T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T>,
  options: {
    onFallback?: (error: Error) => void
  } = {}
): Promise<T> {
  try {
    return await primary()
  }
  catch (error) {
    if (error instanceof Error && options.onFallback) {
      options.onFallback(error)
    }
    return await fallback()
  }
}
```

## 输入验证

### 参数验证

在命令处理前验证参数：

```typescript
export async function runCommand(path: string, opts: CliOptions): Promise<void> {
  // 验证路径
  if (path && !existsSync(path)) {
    throw new ValidationError(`路径不存在：${path}`, 'path')
  }

  // 验证选项
  if (opts.category && !['extension', 'date', 'size', 'name'].includes(opts.category)) {
    throw new ValidationError(
      `无效的分类方式：${opts.category}。有效值为：extension, date, size, name`,
      'category'
    )
  }

  // 验证互斥选项
  if (opts.dryRun && opts.force) {
    throw new ValidationError('--dry-run 和 --force 不能同时使用')
  }

  // 执行命令
  await executeCommand(path, opts)
}
```

### 配置验证

验证配置的完整性：

```typescript
export function validateConfig(config: FileWizardConfig): void {
  if (!config.providers[config.app.defaultProvider]) {
    throw new ConfigError(
      `默认 provider "${config.app.defaultProvider}" 未在配置中定义`
    )
  }

  for (const [name, provider] of Object.entries(config.providers)) {
    if (!provider.apiKey) {
      console.warn(`警告：provider "${name}" 的 API Key 未配置`)
    }

    if (provider.temperature !== undefined &&
        (provider.temperature < 0 || provider.temperature > 2)) {
      throw new ValidationError(
        `provider "${name}" 的 temperature 必须在 0 到 2 之间`,
        `providers.${name}.temperature`
      )
    }
  }
}
```

## 全局错误处理

### 未捕获的异常

处理未捕获的异常：

```typescript
process.on('uncaughtException', (error) => {
  console.error(chalk.red('\n❌ 未捕获的异常：'))
  handleError(error)
  process.exit(1)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error(chalk.red('\n❌ 未处理的 Promise 拒绝：'))
  console.error(chalk.gray(`Promise: ${promise}`))
  handleError(reason)
  process.exit(1)
})
```

### 信号处理

处理进程信号：

```typescript
process.on('SIGINT', () => {
  console.log(chalk.yellow('\n\n✋ 收到中断信号，正在退出...'))
  cleanup()
  process.exit(0)
})

process.on('SIGTERM', () => {
  console.log(chalk.yellow('\n\n✋ 收到终止信号，正在退出...'))
  cleanup()
  process.exit(0)
})

function cleanup(): void {
  // 清理资源
  // 关闭连接
  // 保存状态
}
```

## 错误日志

### 错误日志记录

记录错误到日志文件：

```typescript
import { appendFileSync, existsSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'

export function logError(error: unknown): void {
  const logDir = join(process.cwd(), '.logs')
  const logFile = join(logDir, 'error.log')

  if (!existsSync(logDir)) {
    mkdirSync(logDir, { recursive: true })
  }

  const timestamp = new Date().toISOString()
  const errorInfo = error instanceof Error
    ? {
        message: error.message,
        stack: error.stack,
        name: error.name,
      }
    : { message: String(error) }

  const logEntry = `[${timestamp}] ${JSON.stringify(errorInfo)}\n`

  appendFileSync(logFile, logEntry)
}
```

### 错误报告

提供错误报告功能：

```typescript
export function generateErrorReport(error: unknown): string {
  const report = {
    timestamp: new Date().toISOString(),
    platform: process.platform,
    nodeVersion: process.version,
    cliVersion: getVersion(),
    error: error instanceof Error
      ? {
          name: error.name,
          message: error.message,
          stack: error.stack,
        }
      : { message: String(error) },
  }

  return JSON.stringify(report, null, 2)
}
```

## 要点

- 使用 try-catch 包装所有可能失败的操作
- 创建自定义错误类，提供更详细的错误信息
- 提供用户友好的错误消息，包含可操作的建议
- 实现重试机制和回退机制，提高容错性
- 验证输入和配置，防止无效数据导致错误
- 处理未捕获的异常和 Promise 拒绝
- 记录错误日志，便于问题排查
- 生成错误报告，帮助用户报告问题

<!--
来源参考：
- file-wizard 项目源码
- Node.js 错误处理最佳实践
-->
