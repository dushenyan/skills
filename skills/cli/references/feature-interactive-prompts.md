---
name: feature-interactive-prompts
description: 使用 @clack/prompts 构建友好的交互式命令行界面
---

# 交互式提示

此技能涵盖使用 @clack/prompts 构建现代化、用户友好的交互式命令行界面。

## 基本提示类型

### 文本输入

收集用户文本输入：

```typescript
import * as prompts from '@clack/prompts'

const path = await prompts.text({
  message: '请输入要整理的目录路径：',
  placeholder: process.cwd(),
  validate: (value) => {
    if (!value) {
      return '路径不能为空'
    }
    if (!existsSync(value)) {
      return '路径不存在'
    }
  }
})
```

### 选择提示

从预定义选项中选择：

```typescript
const category = await prompts.select({
  message: '请选择分类方式：',
  options: [
    { value: 'extension', label: 'extension - 按扩展名' },
    { value: 'date', label: 'date - 按日期' },
    { value: 'size', label: 'size - 按大小' },
    { value: 'name', label: 'name - 按名称首字母' },
  ],
  initialValue: 'extension'
})
```

### 确认提示

获取用户确认：

```typescript
const dryRun = await prompts.confirm({
  message: '是否模拟运行？（不实际移动文件）',
  initialValue: true
})
```

### 多选提示

允许用户选择多个选项：

```typescript
const features = await prompts.multiselect({
  message: '选择要启用的功能：',
  options: [
    { value: 'lint', label: '代码检查' },
    { value: 'format', label: '代码格式化' },
    { value: 'test', label: '运行测试' },
    { value: 'build', label: '构建项目' },
  ],
  required: false
})
```

## 取消处理

### 检测取消操作

使用 prompts.isCancel 检测用户取消：

```typescript
const path = await prompts.text({
  message: '请输入路径：'
})

if (prompts.isCancel(path)) {
  console.log(chalk.yellow('\n✋ 操作已取消'))
  return
}
```

### 全局取消监听

监听键盘快捷键取消操作：

```typescript
let isCancelled = false

process.stdin.on('keypress', (_, key) => {
  if (key && key.name === 'q') {
    isCancelled = true
    console.log(chalk.yellow('\n✋ 操作已取消'))
    process.exit(0)
  }
})

readline.emitKeypressEvents(process.stdin)
if (process.stdin.isTTY) {
  process.stdin.setRawMode(true)
}

try {
  const result = await prompts.text({ message: '输入：' })
  if (isCancelled) return
}
finally {
  if (process.stdin.isTTY) {
    process.stdin.setRawMode(false)
  }
  process.stdin.removeAllListeners('keypress')
}
```

## 输入验证

### 同步验证

使用 validate 函数验证输入：

```typescript
const path = await prompts.text({
  message: '请输入目录路径：',
  validate: (value) => {
    if (!value) {
      return '路径不能为空'
    }
    if (!existsSync(value)) {
      return '路径不存在'
    }
    if (!statSync(value).isDirectory()) {
      return '必须是目录'
    }
  }
})
```

### 异步验证

对于需要异步检查的验证：

```typescript
const url = await prompts.text({
  message: '请输入 API URL：',
  validate: async (value) => {
    if (!value) {
      return 'URL 不能为空'
    }
    try {
      new URL(value)
      await checkUrlAccessible(value)
    }
    catch {
      return 'URL 无效或无法访问'
    }
  }
})
```

## 复杂交互流程

### 多步骤交互

构建多步骤交互流程：

```typescript
export async function runOrganizeInteractive(): Promise<void> {
  const path = await prompts.text({
    message: '请输入要整理的目录路径：',
    placeholder: process.cwd()
  })

  const category = await prompts.select({
    message: '请选择分类方式：',
    options: [
      { value: 'extension', label: 'extension - 按扩展名' },
      { value: 'date', label: 'date - 按日期' },
    ]
  })

  const rule = await prompts.select({
    message: '请选择排序规则：',
    options: [
      { value: 'asc', label: 'asc - 升序' },
      { value: 'desc', label: 'desc - 降序' },
    ]
  })

  const dryRun = await prompts.confirm({
    message: '是否模拟运行？',
    initialValue: true
  })

  if (prompts.isCancel(path) || prompts.isCancel(category) ||
      prompts.isCancel(rule) || prompts.isCancel(dryRun)) {
    console.log(chalk.yellow('\n✋ 操作已取消'))
    return
  }

  // 执行命令
  await executeOrganize({ path, category, rule, dryRun })
}
```

### 条件交互

根据前序输入决定是否显示后续提示：

```typescript
const useProxy = await prompts.confirm({
  message: '是否使用代理？',
  initialValue: false
})

let proxyUrl
if (useProxy) {
  proxyUrl = await prompts.text({
    message: '请输入代理地址：',
    placeholder: 'http://127.0.0.1:7890',
    validate: (value) => {
      if (!value) return '代理地址不能为空'
      try {
        new URL(value)
      }
      catch {
        return '无效的 URL 格式'
      }
    }
  })
}
```

## 交互式模式集成

### 主循环

创建交互式主循环：

```typescript
async function runInteractiveMode(): Promise<void> {
  let continueRunning = true

  while (continueRunning) {
    console.clear()
    console.log(chalk.cyan.bold(`${BRAND_LOGO}`))
    console.log(chalk.blue('🪄 My CLI'))

    const commands = [
      { name: 'organize', description: '整理文件' },
      { name: 'build', description: '构建项目' },
      { name: 'test', description: '运行测试' },
    ]

    const selectedCommand = await prompts.select({
      message: '请选择要执行的命令：',
      options: commands.map(cmd => ({
        value: cmd.name,
        label: `${cmd.name} - ${cmd.description}`
      }))
    })

    if (prompts.isCancel(selectedCommand)) {
      continueRunning = false
      break
    }

    try {
      switch (selectedCommand) {
        case 'organize':
          await runOrganizeInteractive()
          break
        case 'build':
          await runBuildInteractive()
          break
        case 'test':
          await runTestInteractive()
          break
      }
    }
    catch (error) {
      console.error(chalk.red(`\n❌ 执行失败: ${error.message}`))
    }

    const shouldContinue = await prompts.confirm({
      message: '是否继续？',
      initialValue: true
    })

    if (!shouldContinue || prompts.isCancel(shouldContinue)) {
      continueRunning = false
    }
  }
}
```

### 命令转换

将交互式输入转换为命令行参数：

```typescript
import { buildCli } from '../cli'
import { buildCommandArgs } from '../utils/command-utils'

const args = buildCommandArgs([path], {
  category,
  rule,
  dryRun,
  verbose
})

displayFinalCommand('organize', args)
await buildCli().parseAsync(['node', 'my-cli', 'organize', ...args])
```

## 用户体验优化

### 进度提示

使用 ora 显示进度：

```typescript
import ora from 'ora'

const spinner = ora('正在扫描目录...').start()

try {
  const files = await scanDirectory(path)
  spinner.text = `找到 ${files.length} 个文件，正在处理...`

  await processFiles(files)

  spinner.succeed('处理完成')
}
catch (error) {
  spinner.fail('处理失败')
  console.error(error)
}
```

### 彩色输出

使用 chalk 增强输出：

```typescript
import chalk from 'chalk'

console.log(chalk.green('✅ 成功'))
console.log(chalk.red('❌ 失败'))
console.log(chalk.yellow('⚠️ 警告'))
console.log(chalk.blue('ℹ️ 信息'))
console.log(chalk.gray('详细日志'))
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

## 要点

- 使用 @clack/prompts 提供现代化的交互式界面
- 始终检查 prompts.isCancel 处理用户取消
- 为所有输入提供验证，防止无效数据
- 使用 ora spinner 显示长时间操作进度
- 使用 chalk 增强输出的可读性和美观性
- 将交互式输入转换为命令行参数，复用命令逻辑
- 实现主循环，支持连续执行多个命令
- 添加键盘快捷键（如 'q' 退出）提升用户体验

<!--
来源参考：
- @clack/prompts 文档: https://github.com/natemoo-re/clack
- ora 文档: https://github.com/sindresorhus/ora
- chalk 文档: https://github.com/chalk/chalk
- file-wizard 项目源码
-->
