---
name: python-project-spec
description: Python 项目规范脚手架：统一的目录结构、uv 依赖环境、Makefile、docs 文档模板、PEP 8 命名、Google 风格 docstring 与 Scalar API 文档。创建或初始化 Python 项目、要求规范/改造既有 Python 代码结构时调用；用户提到「项目初始化/脚手架/目录结构/Makefile/uv/docs 规范/PEP 8 命名/Google 风格 docstring/Scalar API 文档」时也应使用，即使没有明确说出「规范」二字。不用于写技术教程（交 tech-tutorial），本技能只落地项目脚手架与代码规范。
metadata:
  author: Shenyan Du
  version: "2026.11.16"
  source: 手写维护，scripts located at https://github.com/dushenyan/skills
---

# Python 项目规范脚手架

本 Skill 定义 Python 项目的标准化开发规范，用于在创建或初始化项目时自动应用统一的目录结构、构建方式、文档模板和代码风格要求。

本文件只承载**工作流与索引**。各主题的细节分散在 `references/` 下，按需读取，不要一次性全部加载。

定稿前必须走「终检：去 AI 味」，见本文同名章节。

## 何时触发

- 用户要求创建新的 Python 项目
- 用户要求为现有 Python 项目补齐 / 改造规范结构
- 用户提到「项目初始化」「脚手架」「目录结构」「Makefile」「uv」「docs」「PEP 8」「docstring」「Scalar」等关键词
- 需要生成符合规范的 Makefile、目录划分或文档模板时

## 使用方式

1. 先看下方「应用流程（Checklist）」，确定当前任务涉及哪些步骤。
2. 对照「references 索引」，**只打开当前步骤需要的 reference 文件**，不要全量加载。
3. 严格按 reference 中的规则生成或改造项目。

## references 索引

| 主题 | 文件 | 何时读取 |
|------|------|----------|
| uv 依赖环境 + Makefile 规范 | `references/core-dependency-and-makefile.md` | 初始化依赖、编写 Makefile（端口清理、注释位置、推荐结构）时 |
| 目录结构 + PEP 8 命名 + 文件一致性 | `references/core-project-layout.md` | 划分 apps/common/tests 目录、命名文件/类/函数、发现名实不符文件时 |
| 代码注释规范（Google 风格 docstring） | `references/core-code-comments.md` | 编写或审查 docstring、需要 Args/Returns/Raises 示例时 |
| docs 目录 7 份文档规范 | `references/core-docs-templates.md` | 创建 `docs/` 骨架、补齐项目文档时 |
| 服务 API 文档（Scalar） | `references/feature-api-docs-scalar.md` | 项目对外提供 HTTP/Web 服务、需要接入交互式 API 文档时 |
| 主语言标识（写入 `.trae/rules.md`） | `references/feature-language-rules.md` | 初始化项目规则、声明中文为主语言时 |

## 应用流程（Checklist）

在生成或改造项目时，按以下顺序逐一落实相应步骤，并读取右侧对应的 reference：

| 步骤 | 检查项 | 参考文档 | 完成标记 |
|------|--------|----------|----------|
| 1 | 使用 `uv init` 或补齐 `pyproject.toml` | `references/core-dependency-and-makefile.md` | ☐ |
| 2 | 按 apps/common/tests 划分目录结构，文件命名符合 PEP 8 且名实相符 | `references/core-project-layout.md` | ☐ |
| 3 | 创建 Makefile，注释在命令上方，服务启动前清理端口 | `references/core-dependency-and-makefile.md` | ☐ |
| 4 | 补齐 `docs/` 下 7 份文档骨架（01~07） | `references/core-docs-templates.md` | ☐ |
| 5 | 核心函数 docstring 采用 Google 风格，含 Args / Returns / Raises，注释解释「为什么」 | `references/core-code-comments.md` | ☐ |
| 6 | 若对外提供 HTTP 服务：接入 Scalar 文档，字段配置中文 title/description/example 预填 | `references/feature-api-docs-scalar.md` | ☐ |
| 7 | 在 `.trae/rules.md` 中写入中文主语言全局规则声明 | `references/feature-language-rules.md` | ☐ |

## 终检：去 AI 味（流程的最后一步）

这不是可跳过的附录。定稿前先跑扫描，再逐条过人工清单，两条都过才算交付。

`humanizer-zh` 在仓库里位于 `external/`，安装到编辑器后与其他技能平铺在同一 `skills/` 下，相对路径随布局变化。先定位脚本再跑，两种布局都覆盖：

```bash
SCAN=$(ls ../humanizer-zh/scripts/scan-ai-tone.mjs ../../external/humanizer-zh/scripts/scan-ai-tone.mjs 2>/dev/null | head -1)

node "$SCAN" 稿件.md   # 稿件已落盘
node "$SCAN" -         # 从标准输入读
```

扫描只负责把候选捞出来，判定标准在 `humanizer-zh/SKILL.md` 的 A–F 检查点（仓库内为 `external/humanizer-zh/SKILL.md`）。命中不等于必须改，承载实际信息的句子照原样保留。

必须清掉的六处：

- 空泛高频词：「赋能」「闭环」「显著提升」换成具体动作或数据
- 强凑三段式：有几项写几项，不为节奏删项或凑项
- 万能破折号：每处问一句「换成逗号或句号是否更清楚」
- 句尾拔高：结论停在事实上，不追加「这标志着……」
- 套话收尾：删掉「综上所述」「未来可期」「希望对你有帮助」
- 客服腔与免责填充：「值得注意的是」「需要指出的是」

底线是保留事实、否定、条件、归因、时间与完成状态，润色不许改变原意。
