---
name: core-logging-output
description: 实现结构化日志和美观的命令行输出
---

# 日志和输出

此技能涵盖实现结构化日志系统、进度显示和美观的命令行输出。

## 日志系统设计

### 日志级别

定义清晰的日志级别：

```typescript
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}
```

### Logger 类实现

创建统一的日志工具类：

```typescript
import type { Command } from 'commander'
import chalk from 'chalk'

export class Logger {
  private static isVerbose = false

  /**
   * 初始化日志工具，检测是否启用了verbose模式
   */
  static initialize(program: Command): void {
    const options = program.opts()
    Logger.isVerbose = !!options.verbose
  }

  /**
   * 检测是否启用了verbose模式
   */
  static getVerbose(): boolean {
    return Logger.isVerbose
  }

  /**
   * 输出调试日志
   */
  static debug(message: string, data?: any): void {
    if (Logger.isVerbose) {
      Logger.log(LogLevel.DEBUG, message, data)
    }
  }

  /**
   * 输出信息日志
   */
  static info(message: string, data?: any): void {
    Logger.log(LogLevel.INFO, message, data)
  }

  /**
   * 输出警告日志
   */
  static warn(message: string, data?: any): void {
    Logger.log(LogLevel.WARN, message, data)
  }

  /**
   * 输出错误日志
   */
  static error(message: string, data?: any): void {
    Logger.log(LogLevel.ERROR, message, data)
  }

  /**
   * 核心日志输出方法
   */
  private static log(level: LogLevel, message: string, data?: any): void {
    const timestamp = new Date().toISOString()
    let logLine = `${timestamp} [${level.toUpperCase()}] ${message}`

    if (data !== undefined) {
      try {
        const dataStr = typeof data === 'string' ? data : JSON.stringify(data, null, 2)
        logLine += `\n${dataStr}`
      }
      catch (e) {
        logLine += `\n[ERROR] 无法序列化数据: ${e}`
      }
    }

    // 根据日志级别添加颜色
    switch (level) {
      case LogLevel.DEBUG:
        logLine = chalk.gray(logLine)
        break
      case LogLevel.INFO:
        logLine = chalk.green(logLine)
        break
      case LogLevel.WARN:
        logLine = chalk.yellow(logLine)
        break
      case LogLevel.ERROR:
        logLine = chalk.red(logLine)
        break
    }

    const consoleMethod = Logger.getConsoleMethod(level)
    consoleMethod(logLine)
  }

  /**
   * 根据日志级别获取对应的console方法
   */
  private static getConsoleMethod(level: LogLevel): (...args: any[]) => void {
    switch (level) {
      case LogLevel.DEBUG:
        return console.debug
      case LogLevel.INFO:
        return console.log
      case LogLevel.WARN:
        return console.warn
      case LogLevel.ERROR:
        return console.error
      default:
        return console.log
    }
  }
}
```

### 使用示例

```typescript
import { Logger } from './utils/logger'

Logger.initialize(program)

Logger.info('开始处理')
Logger.debug('调试信息', { data: 'value' })
Logger.warn('警告信息')
Logger.error('错误信息', new Error('Something went wrong'))
```

## 进度显示

### 使用 ora

使用 ora 显示加载动画：

```typescript
import ora from 'ora'

const spinner = ora('正在扫描目录...').start()

try {
  const files = await scanDirectory(path)
  spinner.text = `找到 ${files.length} 个文件，正在分类...`

  const categorized = await categorizeFiles(files)
  spinner.text = '正在整理文件...'

  await organizeFiles(categorized)

  spinner.succeed('文件整理完成')
  console.log(chalk.green(`✅ 已成功整理 ${files.length} 个文件`))
}
catch (error) {
  spinner.fail('文件整理失败')
  console.error(chalk.red(`❌ 错误详情：${error.message}`))
  process.exitCode = 1
}
```

### 进度更新

动态更新进度信息：

```typescript
spinner.text = `正在处理文件 ${current}/${total}...`

spinner.text = `已处理 ${completed} 个文件，剩余 ${remaining} 个`

spinner.text = `进度：${Math.round((completed / total) * 100)}%`
```

### 状态控制

控制 spinner 的不同状态：

```typescript
spinner.succeed('操作成功')  // 显示成功图标
spinner.fail('操作失败')    // 显示失败图标
spinner.warn('警告信息')     // 显示警告图标
spinner.info('信息提示')     // 显示信息图标
spinner.stop()              // 停止但不显示图标
spinner.start('新任务')     // 重新开始
```

## 彩色输出

### 使用 chalk

使用 chalk 增强输出：

```typescript
import chalk from 'chalk'

// 基本颜色
console.log(chalk.red('错误信息'))
console.log(chalk.green('成功信息'))
console.log(chalk.yellow('警告信息'))
console.log(chalk.blue('信息提示'))
console.log(chalk.gray('详细日志'))

// 背景色
console.log(chalk.bgRed('错误'))
console.log(chalk.bgGreen('成功'))

// 样式
console.log(chalk.bold('粗体文本'))
console.log(chalk.italic('斜体文本'))
console.log(chalk.underline('下划线'))
console.log(chalk.strikethrough('删除线'))

// 组合样式
console.log(chalk.bold.red('粗体红色'))
console.log(chalk.bgBlue.white('蓝色背景白色文字'))
```

### 表情符号

使用表情符号增强可读性：

```typescript
console.log(chalk.green('✅ 成功'))
console.log(chalk.red('❌ 失败'))
console.log(chalk.yellow('⚠️ 警告'))
console.log(chalk.blue('ℹ️ 信息'))
console.log(chalk.cyan('🔧 配置'))
console.log(chalk.magenta('📦 依赖'))
console.log(chalk.gray('📄 文件'))
console.log(chalk.white('🚀 启动'))
```

### 分隔线

使用分隔线组织输出：

```typescript
console.log(chalk.green('══════════════════════════════════════════════════════'))
console.log(chalk.cyan('操作选项：'))
console.log(chalk.cyan('  r - 重新运行'))
console.log(chalk.cyan('  q - 退出'))
console.log(chalk.green('══════════════════════════════════════════════════════'))
```

## 输出格式化

### 表格输出

使用表格格式化输出：

```typescript
function formatTable(headers: string[], rows: string[][]): string {
  const columnWidths = headers.map((header, i) => {
    const maxWidth = Math.max(
      header.length,
      ...rows.map(row => row[i]?.length || 0)
    )
    return maxWidth + 2
  })

  const separator = columnWidths.map(width => '─'.repeat(width)).join('┼')
  const headerRow = headers.map((header, i) => header.padEnd(columnWidths[i] - 1)).join('│')
  const dataRows = rows.map(row =>
    row.map((cell, i) => (cell || '').padEnd(columnWidths[i] - 1)).join('│')
  )

  return [separator, headerRow, separator, ...dataRows, separator].join('\n')
}

console.log(formatTable(
  ['名称', '大小', '修改时间'],
  [
    ['file1.txt', '1.2KB', '2024-01-01'],
    ['file2.txt', '2.4KB', '2024-01-02'],
  ]
))
```

### 树形结构

使用树形结构显示层级：

```typescript
function formatTree(items: Array<{ name: string, children?: any[] }>, indent = 0): string {
  return items.map((item, index) => {
    const isLast = index === items.length - 1
    const prefix = indent === 0 ? '' : (isLast ? '└─ ' : '├─ ')
    const childPrefix = indent === 0 ? '' : (isLast ? '   ' : '│  ')
    const line = '  '.repeat(indent) + prefix + item.name

    if (item.children && item.children.length > 0) {
      return line + '\n' + formatTree(item.children, indent + 1)
    }

    return line
  }).join('\n')
}

console.log(formatTree([
  { name: 'src', children: [
    { name: 'cli.ts' },
    { name: 'commands', children: [
      { name: 'organize.ts' },
      { name: 'build.ts' },
    ]},
  ]},
]))
```

### 列表输出

格式化列表输出：

```typescript
function formatList(items: string[], prefix = '• '): string {
  return items.map(item => `${prefix}${item}`).join('\n')
}

console.log(formatList([
  '项目文件',
  '配置文件',
  '文档',
]))
```

## 命令显示

### 显示最终命令

显示用户执行的最终命令：

```typescript
export function displayFinalCommand(command: string, args: string[]): void {
  console.log(chalk.cyan('\n📋 最终执行的命令：'))
  console.log(chalk.white(`my-cli ${command} ${args.join(' ')}`))
}
```

### 显示配置

显示当前配置：

```typescript
function displayConfig(config: Config): void {
  console.log(chalk.gray('\n🔧 配置信息：'))
  console.log(chalk.gray(`  提供商：${config.provider}`))
  console.log(chalk.gray(`  模型：${config.model}`))
  console.log(chalk.gray(`  代理：${config.proxy || '未配置'}`))
  console.log(chalk.gray(`  详细模式：${config.verbose ? '是' : '否'}`))
}
```

## 要点

- 使用 Logger 类统一管理日志，支持不同级别和颜色
- 使用 ora spinner 显示长时间操作的进度
- 使用 chalk 增强输出的可读性和美观性
- 使用表情符号和分隔线组织输出结构
- 实现表格、树形等格式化输出，提升信息展示效果
- 在 verbose 模式下输出详细调试信息
- 显示最终执行的命令，方便用户复用

<!--
来源参考：
- ora 文档: https://github.com/sindresorhus/ora
- chalk 文档: https://github.com/chalk/chalk
- file-wizard 项目源码
-->
