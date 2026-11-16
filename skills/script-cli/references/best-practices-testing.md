---
name: best-practices-testing
description: CLI 应用程序的测试策略和最佳实践
---

# 测试策略

此技能涵盖 CLI 应用程序的测试策略，包括单元测试、集成测试和端到端测试。

## 测试框架

### Vitest 配置

使用 Vitest 作为测试框架：

```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.test.ts',
        '**/*.spec.ts',
      ],
    },
  },
})
```

### package.json 脚本

配置测试脚本：

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest watch",
    "test:coverage": "vitest run --coverage"
  }
}
```

## 单元测试

### 测试工具函数

测试纯函数和工具类：

```typescript
import { describe, it, expect } from 'vitest'
import { buildCommandArgs } from './command-utils'

describe('buildCommandArgs', () => {
  it('应该构建基本参数', () => {
    const args = buildCommandArgs(['/path'], {
      category: 'extension',
      verbose: true,
    })

    expect(args).toEqual(['/path', '--category=extension', '--verbose'])
  })

  it('应该忽略空值', () => {
    const args = buildCommandArgs(['/path'], {
      category: '',
      verbose: false,
    })

    expect(args).toEqual(['/path'])
  })

  it('应该处理数组参数', () => {
    const args = buildCommandArgs(['/path'], {
      patterns: ['*.js', '*.ts'],
    })

    expect(args).toEqual(['/path', '--patterns=*.js *.ts'])
  })
})
```

### 测试 Logger 类

测试日志功能：

```typescript
import { describe, it, expect, vi } from 'vitest'
import { Logger } from './logger'

describe('Logger', () => {
  beforeEach(() => {
    vi.spyOn(console, 'log').mockImplementation(() => {})
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('应该在 verbose 模式下输出 debug 日志', () => {
    Logger.initialize({ opts: { verbose: true } })
    Logger.debug('调试信息')

    expect(console.log).toHaveBeenCalled()
  })

  it('应该在非 verbose 模式下不输出 debug 日志', () => {
    Logger.initialize({ opts: { verbose: false } })
    Logger.debug('调试信息')

    expect(console.log).not.toHaveBeenCalled()
  })
})
```

## 集成测试

### 测试命令执行

测试命令的完整执行流程：

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { Command } from 'commander'
import { buildCli } from '../cli'
import { runOrganizeCommand } from '../commands/organize'

describe('organize 命令', () => {
  let cli: Command

  beforeEach(() => {
    cli = buildCli()
  })

  it('应该成功执行 organize 命令', async () => {
    const testDir = '/tmp/test-organize'

    await runOrganizeCommand(testDir, {
      category: 'extension',
      dryRun: true,
    })

    // 验证结果
  })

  it('应该在路径不存在时抛出错误', async () => {
    await expect(
      runOrganizeCommand('/nonexistent/path', {})
    ).rejects.toThrow()
  })
})
```

### 测试配置加载

测试配置加载和验证：

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { loadConfig, validateConfig } from '../config'

describe('配置管理', () => {
  beforeEach(() => {
    // 设置测试配置文件
  })

  it('应该成功加载配置', async () => {
    const config = await loadConfig({ configPath: '/tmp/test-config.yaml' })

    expect(config).toBeDefined()
    expect(config.app).toBeDefined()
    expect(config.providers).toBeDefined()
  })

  it('应该验证配置的完整性', () => {
    const config = {
      app: { defaultProvider: 'groq' },
      providers: { groq: { apiKey: 'test' } },
    }

    expect(() => validateConfig(config)).not.toThrow()
  })

  it('应该在配置无效时抛出错误', () => {
    const config = {
      app: { defaultProvider: 'nonexistent' },
      providers: {},
    }

    expect(() => validateConfig(config)).toThrow()
  })
})
```

## 端到端测试

### 测试 CLI 入口

测试完整的 CLI 执行流程：

```typescript
import { describe, it, expect } from 'vitest'
import { execSync } from 'node:child_process'

describe('CLI 端到端测试', () => {
  it('应该显示帮助信息', () => {
    const output = execSync('node dist/cli.js --help', {
      encoding: 'utf-8',
    })

    expect(output).toContain('用法')
    expect(output).toContain('选项')
    expect(output).toContain('命令')
  })

  it('应该显示版本信息', () => {
    const output = execSync('node dist/cli.js --version', {
      encoding: 'utf-8',
    })

    expect(output).toMatch(/\d+\.\d+\.\d+/)
  })

  it('应该执行 organize 命令', () => {
    const output = execSync(
      'node dist/cli.js organize /tmp/test --dry-run',
      { encoding: 'utf-8' }
    )

    expect(output).toContain('模拟运行')
  })
})
```

### 测试交互式模式

测试交互式命令：

```typescript
import { describe, it, expect } from 'vitest'
import { spawn } from 'node:child_process'

describe('交互式模式测试', () => {
  it('应该进入交互式模式', async () => {
    const child = spawn('node', ['dist/cli.js', '-u'])

    child.stdin.write('\n') // 选择默认选项
    child.stdin.write('q\n') // 退出

    const output = await new Promise<string>((resolve) => {
      let data = ''
      child.stdout.on('data', (chunk) => {
        data += chunk.toString()
      })
      child.on('close', () => resolve(data))
    })

    expect(output).toContain('请选择要执行的命令')
  })
})
```

## Mock 和 Stub

### Mock 文件系统

使用 vi.mock 模拟文件系统：

```typescript
import { describe, it, expect, vi } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { loadConfig } from '../config'

vi.mock('node:fs', () => ({
  existsSync: vi.fn(),
  readFileSync: vi.fn(),
}))

describe('配置加载', () => {
  it('应该在配置文件不存在时抛出错误', async () => {
    vi.mocked(existsSync).mockReturnValue(false)

    await expect(loadConfig()).rejects.toThrow('配置文件缺失')
  })

  it('应该成功加载配置文件', async () => {
    vi.mocked(existsSync).mockReturnValue(true)
    vi.mocked(readFileSync).mockReturnValue(`
app:
  default_provider: groq
providers:
  groq:
    api_key: test
`)

    const config = await loadConfig()
    expect(config.app.defaultProvider).toBe('groq')
  })
})
```

### Mock 外部服务

模拟外部 API 调用：

```typescript
import { describe, it, expect, vi } from 'vitest'
import { callAPI } from '../api'

vi.mock('../api', () => ({
  callAPI: vi.fn(),
}))

describe('API 调用', () => {
  it('应该成功调用 API', async () => {
    vi.mocked(callAPI).mockResolvedValue({ data: 'success' })

    const result = await callAPI('/test')
    expect(result).toEqual({ data: 'success' })
  })

  it('应该在 API 调用失败时抛出错误', async () => {
    vi.mocked(callAPI).mockRejectedValue(new Error('API 错误'))

    await expect(callAPI('/test')).rejects.toThrow('API 错误')
  })
})
```

## 测试覆盖率

### 配置覆盖率

配置测试覆盖率目标：

```typescript
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      statements: 80,
      branches: 80,
      functions: 80,
      lines: 80,
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.test.ts',
        '**/*.spec.ts',
        '**/cli.ts', // 排除入口文件
      ],
    },
  },
})
```

### 生成覆盖率报告

运行测试并生成覆盖率报告：

```bash
npm run test:coverage
```

## 测试最佳实践

### 测试命名

使用清晰的测试命名：

```typescript
describe('buildCommandArgs', () => {
  it('应该构建基本参数', () => {})
  it('应该忽略空值', () => {})
  it('应该处理数组参数', () => {})
  it('应该在参数无效时抛出错误', () => {})
})
```

### 测试隔离

确保测试之间相互独立：

```typescript
describe('测试套件', () => {
  beforeEach(() => {
    // 每个测试前重置状态
  })

  afterEach(() => {
    // 每个测试后清理
  })
})
```

### 测试数据

使用固定的测试数据：

```typescript
const testConfig = {
  app: { defaultProvider: 'groq' },
  providers: {
    groq: {
      apiKey: 'test-key',
      model: 'llama-3.1-8b-instant',
    },
  },
}
```

## 要点

- 使用 Vitest 作为测试框架，配置合理的覆盖率目标
- 编写单元测试测试工具函数和纯函数
- 编写集成测试测试命令的完整执行流程
- 编写端到端测试测试 CLI 的实际使用场景
- 使用 vi.mock 模拟外部依赖，提高测试可靠性
- 确保测试之间相互独立，避免测试污染
- 使用清晰的测试命名和固定的测试数据
- 定期运行测试并检查覆盖率报告
