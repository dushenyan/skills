---
name: core-argument-parsing
description: Commander.js 参数解析和选项处理
---

# 参数解析

此技能涵盖使用 Commander.js 进行命令行参数解析、选项处理和验证的最佳实践。

## 基本命令定义

### 命令注册

使用 Commander.js 注册命令和选项：

```typescript
import { Command } from 'commander'

const program = new Command()

program
  .command('organize')
  .description('按照分类规则整理文件')
  .argument('[path]', '要整理的目录路径，默认为当前目录')
  .option('-c, --category <category>', '分类方式：extension、date、size、name')
  .option('-r, --rule <rule>', '排序规则：asc（升序）、desc（降序）')
  .option('-d, --dry-run', '模拟运行，不实际移动文件')
  .option('-v, --verbose', '输出详细信息')
  .action(runOrganizeCommand)
```

### 参数类型

Commander.js 支持多种参数类型：

```typescript
// 必需参数
.argument('<path>', '必需的路径参数')

// 可选参数
.argument('[path]', '可选的路径参数')

// 可变参数
.argument('[paths...]', '多个路径参数')

// 带默认值的选项
.option('-p, --port <number>', '端口号', '3000')

// 带类型转换的选项
.option('-p, --port <number>', '端口号', parseInt)

// 布尔选项
.option('-v, --verbose', '详细输出')
.option('--no-proxy', '禁用代理')
```

## 选项处理

### 短选项和长选项

同时支持短选项和长选项：

```typescript
.option('-c, --category <type>', '分类方式')
.option('-v, --verbose', '详细输出')
.option('--proxy <url>', '代理地址')
```

### 选项默认值

为选项设置合理的默认值：

```typescript
.option('-c, --category <type>', '分类方式', 'extension')
.option('-r, --rule <rule>', '排序规则', 'asc')
.option('-m, --mode <mode>', '操作模式', 'organize')
```

### 选项验证

在命令处理函数中验证选项：

```typescript
export async function runOrganizeCommand(path: string, opts: CliOptions): Promise<void> {
  const targetPath = path || process.cwd()

  // 验证分类方式
  const validCategories = ['extension', 'date', 'size', 'name']
  if (opts.category && !validCategories.includes(opts.category)) {
    throw new Error(`无效的分类方式：${opts.category}`)
  }

  // 验证排序规则
  const validRules = ['asc', 'desc']
  if (opts.rule && !validRules.includes(opts.rule)) {
    throw new Error(`无效的排序规则：${opts.rule}`)
  }
}
```

## 参数构建工具

### 构建命令行参数

将选项对象转换为命令行参数数组：

```typescript
export function buildCommandArgs(baseArgs: string[], options: Record<string, any>): string[] {
  const args = [...baseArgs]

  for (const [key, value] of Object.entries(options)) {
    if (value === undefined || value === null || value === '') {
      continue
    }

    const optionKey = key.replace(/([A-Z])/g, '-$1').toLowerCase()

    if (Array.isArray(value)) {
      if (value.length > 0) {
        args.push(`--${optionKey}=${value.join(' ')}`)
      }
    }
    else if (typeof value === 'boolean') {
      if (value) {
        args.push(`--${optionKey}`)
      }
    }
    else {
      args.push(`--${optionKey}=${value}`)
    }
  }

  return args
}
```

### 使用示例

```typescript
const args = buildCommandArgs(['/path/to/dir'], {
  category: 'extension',
  rule: 'asc',
  dryRun: true,
  verbose: false
})

// 结果: ['/path/to/dir', '--category=extension', '--rule=asc', '--dry-run']
```

## 选项获取

### 获取全局选项

从 program 实例获取全局选项：

```typescript
const program = new Command()
program.option('-v, --verbose', '详细输出')

const options = program.opts()
const isVerbose = options.verbose
```

### 获取命令特定选项

在命令处理函数中，Commander.js 自动传递选项：

```typescript
export async function runOrganizeCommand(path: string, opts: CliOptions): Promise<void> {
  const { category, rule, dryRun, verbose } = opts

  if (verbose) {
    console.log('详细模式已启用')
  }
}
```

## 高级用法

### 互斥选项

确保某些选项不能同时使用：

```typescript
export async function runCommand(opts: CliOptions): Promise<void> {
  if (opts.dryRun && opts.force) {
    throw new Error('--dry-run 和 --force 不能同时使用')
  }
}
```

### 选项依赖

某些选项需要其他选项存在：

```typescript
export async function runCommand(opts: CliOptions): Promise<void> {
  if (opts.proxy && !opts.provider) {
    throw new Error('使用 --proxy 时必须指定 --provider')
  }
}
```

### 自定义选项解析

使用自定义函数解析选项值：

```typescript
program
  .option('-c, --config <path>', '配置文件路径', (value) => {
    const path = resolve(process.cwd(), value)
    if (!existsSync(path)) {
      throw new Error(`配置文件不存在：${path}`)
    }
    return path
  })
```

## 帮助信息

### 自定义帮助输出

重写 helpInformation 方法：

```typescript
program.helpInformation = function () {
  let output = ''

  output += `${BRAND_LOGO}\nCLI 描述\n\n`

  output += `${chalk.bgWhite('COMMANDS')}\n`
  this.commands.forEach((cmd) => {
    if (cmd.name() !== '*') {
      output += `${chalk.magenta(cmd.name().padEnd(35))}${cmd.description()}\n`
    }
  })

  output += `${chalk.bgWhite('\nOPTIONS')}\n`
  this.options.forEach((opt) => {
    const flags = chalk.magenta(opt.flags.padEnd(35))
    const description = opt.description
    output += `${flags}${description}\n`
  })

  return output
}
```

### 子命令帮助

为子命令自定义帮助：

```typescript
program.commands.forEach((cmd) => {
  cmd.helpInformation = function () {
    let output = ''

    output += `${BRAND_LOGO}\n${this.description()}\n\n`

    if (this.options.length > 0) {
      output += `${chalk.bgWhite('OPTIONS')}\n`
      this.options.forEach((opt) => {
        const flags = chalk.magenta(opt.flags.padEnd(35))
        output += `${flags}${opt.description}\n`
      })
    }

    return output
  }
})
```

## 要点

- 使用 Commander.js 的链式 API 定义命令和选项
- 为选项提供合理的默认值，减少用户输入负担
- 在命令处理函数中验证选项的有效性
- 使用 buildCommandArgs 工具函数构建命令行参数
- 实现选项互斥和依赖检查，防止无效配置
- 自定义帮助输出，提升用户体验
- 支持短选项和长选项，符合 Unix 惯例

<!--
来源参考：
- Commander.js 文档: https://commander.js.org/
- file-wizard 项目源码
- Unix 命令行界面规范
-->
