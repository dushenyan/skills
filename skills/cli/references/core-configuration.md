---
name: core-configuration
description: CLI 应用程序的配置管理，包括 YAML 配置、环境变量和验证
---

# 配置管理

此技能涵盖 CLI 应用程序的配置管理，包括配置文件加载、环境变量处理和验证。

## 配置文件结构

### YAML 配置

使用 YAML 作为配置文件格式：

```yaml
app:
  default_provider: groq
  proxy: ""
  ignoreList:
    - node_modules
    - .git
    - dist
  exclude_patterns:
    - "*.log"
    - ".DS_Store"

providers:
  groq:
    api_key: ""
    model: llama-3.1-8b-instant
    temperature: 0.7
    top_k: 40
    base_url: ""

  deepseek:
    api_key: ""
    model: deepseek-chat
    temperature: 0.7
    top_k: 40

  gemini:
    api_key: ""
    model: models/gemini-2.0-flash
    temperature: 0.7
    top_k: 40
```

## 类型定义

### 配置接口

定义配置类型：

```typescript
export interface ProviderConfig {
  apiKey: string
  model: string
  temperature?: number
  topK?: number
  baseUrl?: string
  proxy?: string
}

export interface AppConfig {
  defaultProvider: string
  proxy?: string
  ignoreList?: string[]
  excludePatterns?: string[]
}

export interface FileWizardConfig {
  app: AppConfig
  providers: Record<string, ProviderConfig>
}
```

## 配置验证

### Zod Schema

使用 Zod 进行配置验证：

```typescript
import { z } from 'zod'

const appSchema = z.object({
  default_provider: z.string().default('gemini'),
  proxy: z.string().optional(),
  ignoreList: z.array(z.string()).optional(),
  exclude_patterns: z.array(z.string()).optional(),
})

const providerSchema = z.object({
  api_key: z.string().default(''),
  model: z.string().default('models/gemini-2.0-flash'),
  temperature: z.number().min(0).max(2).optional(),
  top_k: z.number().int().positive().optional(),
  base_url: z.string().optional(),
})

const configSchema = z.object({
  app: appSchema,
  providers: z.record(z.string(), providerSchema),
})
```

## 配置加载

### 异步加载

支持异步配置加载和代理检测：

```typescript
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import process from 'node:process'
import { parse } from 'yaml'
import { z } from 'zod'

export async function loadConfig(params?: {
  configPath?: string
  autoDetectProxy?: boolean
}): Promise<FileWizardConfig> {
  const configPath = resolve(process.cwd(), params?.configPath ?? 'mycli.config.yaml')

  if (!existsSync(configPath)) {
    throw new Error(`配置文件缺失：${configPath}`)
  }

  const raw = readFileSync(configPath, 'utf-8')
  const parsed = parse(raw)
  const data = configSchema.parse(parsed)

  // 获取配置文件中的代理设置
  let configuredProxy = data.app.proxy

  // 如果启用自动检测代理，且当前没有配置代理，则自动检测
  if (params?.autoDetectProxy !== false && !configuredProxy) {
    try {
      const detectedProxy = await detectProxy()
      if (detectedProxy) {
        configuredProxy = detectedProxy
      }
    }
    catch {
      // 忽略自动代理检测失败，继续使用无代理模式
    }
  }

  const normalized: FileWizardConfig = {
    app: {
      defaultProvider: data.app.default_provider,
      proxy: configuredProxy,
      ignoreList: data.app.ignoreList,
      excludePatterns: data.app.exclude_patterns,
    },
    providers: Object.entries(data.providers).reduce<Record<string, ProviderConfig>>(
      (acc, [key, value]) => {
        acc[key] = {
          apiKey: value.api_key,
          model: value.model,
          temperature: value.temperature,
          topK: value.top_k,
          baseUrl: value.base_url,
        }
        return acc
      },
      {},
    ),
  }

  return normalized
}
```

### 同步加载

提供同步版本的配置加载：

```typescript
export function loadConfigSync(params?: { configPath?: string }): FileWizardConfig {
  const configPath = resolve(process.cwd(), params?.configPath ?? 'mycli.config.yaml')

  if (!existsSync(configPath)) {
    throw new Error(`配置文件缺失：${configPath}`)
  }

  const raw = readFileSync(configPath, 'utf-8')
  const parsed = parse(raw)
  const data = configSchema.parse(parsed)

  const normalized: FileWizardConfig = {
    app: {
      defaultProvider: data.app.default_provider,
      proxy: data.app.proxy,
      ignoreList: data.app.ignoreList,
      excludePatterns: data.app.exclude_patterns,
    },
    providers: Object.entries(data.providers).reduce<Record<string, ProviderConfig>>(
      (acc, [key, value]) => {
        acc[key] = {
          apiKey: value.api_key,
          model: value.model,
          temperature: value.temperature,
          topK: value.top_k,
          baseUrl: value.base_url,
        }
        return acc
      },
      {},
    ),
  }

  return normalized
}
```

## 环境变量

### 环境变量支持

支持通过环境变量覆盖配置：

```typescript
export function loadConfigWithEnv(params?: {
  configPath?: string
  autoDetectProxy?: boolean
}): FileWizardConfig {
  const config = loadConfigSync(params)

  // 从环境变量覆盖配置
  if (process.env.MYCLI_PROVIDER) {
    config.app.defaultProvider = process.env.MYCLI_PROVIDER
  }

  if (process.env.MYCLI_PROXY) {
    config.app.proxy = process.env.MYCLI_PROXY
  }

  // 覆盖 provider 配置
  for (const [key, provider] of Object.entries(config.providers)) {
    const envKey = `MYCLI_${key.toUpperCase()}_API_KEY`
    if (process.env[envKey]) {
      provider.apiKey = process.env[envKey]
    }
  }

  return config
}
```

### 环境变量优先级

定义配置优先级：命令行参数 > 环境变量 > 配置文件 > 默认值

```typescript
export function resolveConfig(
  config: FileWizardConfig,
  cliOptions: Partial<FileWizardConfig>
): FileWizardConfig {
  return {
    app: {
      defaultProvider: cliOptions.app?.defaultProvider || config.app.defaultProvider,
      proxy: cliOptions.app?.proxy || config.app.proxy,
      ignoreList: cliOptions.app?.ignoreList || config.app.ignoreList,
      excludePatterns: cliOptions.app?.excludePatterns || config.app.excludePatterns,
    },
    providers: {
      ...config.providers,
      ...cliOptions.providers,
    },
  }
}
```

## 代理检测

### 自动代理检测

自动检测系统代理配置：

```typescript
async function detectProxy(): Promise<string | null> {
  // 检查环境变量
  const envProxies = [
    process.env.HTTP_PROXY,
    process.env.HTTPS_PROXY,
    process.env.http_proxy,
    process.env.https_proxy,
  ]

  for (const proxy of envProxies) {
    if (proxy) {
      return proxy
    }
  }

  // 检查 macOS 系统代理
  if (process.platform === 'darwin') {
    try {
      const { execSync } = await import('node:child_process')
      const result = execSync('scutil --proxy', { encoding: 'utf-8' })

      if (result.includes('HTTPEnable : 1')) {
        const match = result.match(/HTTPProxy\s*:\s*([^\n]+)/)
        if (match) {
          const portMatch = result.match(/HTTPPort\s*:\s*(\d+)/)
          const port = portMatch ? portMatch[1] : '80'
          return `http://${match[1].trim()}:${port}`
        }
      }
    }
    catch {
      // 忽略错误
    }
  }

  return null
}
```

## 配置验证

### 配置完整性检查

验证配置的完整性：

```typescript
export function validateConfig(config: FileWizardConfig): void {
  // 检查默认 provider 是否存在
  if (!config.providers[config.app.defaultProvider]) {
    throw new Error(
      `默认 provider "${config.app.defaultProvider}" 未在配置中定义`
    )
  }

  // 检查 provider 配置
  for (const [name, provider] of Object.entries(config.providers)) {
    if (!provider.apiKey) {
      console.warn(`警告：provider "${name}" 的 API Key 未配置`)
    }

    if (provider.temperature !== undefined &&
        (provider.temperature < 0 || provider.temperature > 2)) {
      throw new Error(
        `provider "${name}" 的 temperature 必须在 0 到 2 之间`
      )
    }
  }
}
```

### 配置默认值

为配置提供合理的默认值：

```typescript
export function applyDefaults(config: Partial<FileWizardConfig>): FileWizardConfig {
  return {
    app: {
      defaultProvider: config.app?.defaultProvider || 'gemini',
      proxy: config.app?.proxy,
      ignoreList: config.app?.ignoreList || ['node_modules', '.git', 'dist'],
      excludePatterns: config.app?.excludePatterns || ['*.log', '.DS_Store'],
    },
    providers: {
      groq: {
        apiKey: config.providers?.groq?.apiKey || '',
        model: config.providers?.groq?.model || 'llama-3.1-8b-instant',
        temperature: config.providers?.groq?.temperature ?? 0.7,
        topK: config.providers?.groq?.topK ?? 40,
      },
      ...config.providers,
    },
  }
}
```

## 配置热重载

### 监听配置变化

监听配置文件变化并重新加载：

```typescript
import { watch } from 'node:fs'

export function watchConfig(
  configPath: string,
  callback: (config: FileWizardConfig) => void
): () => void {
  const watcher = watch(configPath, async (eventType) => {
    if (eventType === 'change') {
      try {
        const config = await loadConfig({ configPath })
        callback(config)
      }
      catch (error) {
        console.error('重新加载配置失败:', error)
      }
    }
  })

  return () => watcher.close()
}
```

## 要点

- 使用 YAML 作为配置文件格式，易于阅读和编辑
- 使用 Zod 进行配置验证，确保配置的正确性
- 支持环境变量覆盖配置，提高灵活性
- 实现自动代理检测，简化用户配置
- 提供同步和异步两种配置加载方式
- 定义配置优先级：命令行参数 > 环境变量 > 配置文件 > 默认值
- 验证配置完整性，防止运行时错误
- 为配置提供合理的默认值，减少用户配置负担
