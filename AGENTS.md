# 技能仓库维护指南

本仓库是一个手工维护的 [Agent Skills](https://agentskills.io/home) 集合。技能由 Shenyan Du 根据个人偏好、经验、品味和最佳实践编写，或从本地工具实践中整理而来。

请严格遵循技能的最佳实践：<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>

- 专注于代理的能力和实际使用模式。
- 忽略面向用户的指南、介绍、入门、安装指南等。
- 忽略 LLM 代理在其训练数据中已经确信的内容。
- 使技能尽可能简洁，避免创建太多引用。

## 存储库结构

```
.
├── Makefile                  # 常用命令入口（make help）
├── README.md                 # 面向使用者的技能清单与安装说明
├── scripts/
│   └── install.ts            # 把 own/ 与 external/ 安装到本地各 AI 编辑器的全局技能目录
├── own/                      # 自己维护的技能集合，目录名即技能名
│   └── {skill}/
└── external/                 # 外部引入的技能，原样保留上游文件
    └── {skill}/
        ├── SKILL.md          # 必需：索引 + 工作流
        ├── GENERATION.md     # 来源追踪元数据
        ├── references/
        │   └── *.md          # 按需加载的细节文档
        └── scripts/          # 技能自带的可执行脚本（可选）
```

没有额外的登记表或清单文件：**`own/` 与 `external/` 下的目录就是唯一事实来源**。`scripts/install.ts` 扫描这两个目录自动发现技能（目录需含 `SKILL.md`），安装时统一平铺到编辑器的 `skills/`，两处技能不得重名。`AGENTS.md` 与 `README.md` 中的清单需手工保持同步。

## 技能规范

### `SKILL.md`

技能的入口文件，只承载**工作流与索引**，细节拆到 `references/` 按需加载。名称使用 `kebab-case`，版本号用最后一次修改的日期。

```markdown
---
name: {name}
description: {description}
metadata:
  author: Shenyan Du
  version: "2026.9.10"
  source: 手写维护，scripts located at https://github.com/dushenyan/skills
---

# {技能标题}

一段话说明该技能解决什么问题、何时使用。

## 核心参考

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 主题 A | 一句话说明 | [core-topic-a](references/core-topic-a.md) |

## 功能

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 功能 A | 一句话说明 | [feature-a](references/feature-a.md) |
```

`description` 要同时写清「做什么」和「何时触发」，可以列出触发关键词——代理主要靠它决定是否加载技能。

### `references/*.md`

每个文件只讲一个概念，文件名以类别前缀开头（`core-`、`feature-`、`best-practices-`、`advanced-` 等）：

```markdown
---
name: {name}
description: {description}
---

# {概念名称}

此技能涵盖内容的简要描述。

## 使用

代码示例和实际模式。

## 要点

- 重要细节 1
- 重要细节 2
```

### `GENERATION.md`

记录技能来源，便于日后判断是否需要重新整理：

```markdown
# 生成信息

- **来源：** `手动创建` 或 `{项目名}`
- **Git SHA：** `abc123def456...`（无上游仓库时省略此行）
- **生成时间：** 2026-09-10
```

## 编写指南

1. **为代理重写** - 不要逐字复制文档；为 LLM 消费进行综合
2. **实用** - 专注于使用模式和代码示例
3. **简洁** - 移除 fluff，保留基本信息
4. **每个文件一个概念** - 将大主题拆分为单独的技能文件
5. **包含代码** - 始终提供工作代码示例
6. **解释原因** - 不仅说明如何使用，还说明何时和为什么使用

## 常用命令

见 `make help`：

```bash
make install                       # 安装依赖
make skills                        # 软链接安装到所有已检测到的编辑器
make skills ARGS="--target=claude" # 透传 install.ts 参数
make check                         # lint + typecheck
```

默认软链接安装，仓库里的技能改动即时生效；`make skills-copy` 改为复制文件。
