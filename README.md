# Shenyan Du 的技能集

一个精心策划的 [Agent Skills](https://agentskills.io/home) 集合，反映了 [Shenyan Du](https://github.com/dushenyan) 的偏好、经验和最佳实践，以及工具的使用文档。

> [!IMPORTANT]
> 这些技能沉淀的是我个人可复用的工作流与约定，尚未经过完整的实践验证，因此非常欢迎反馈和贡献。

## 安装

### 一键安装到本地编辑器

克隆本仓库后，一条命令即可把 `own/`（自维护）与 `external/`（外部引入）下的技能补充到本地各 AI 编辑器 / CLI 的全局技能目录（自动检测 Claude Code、Qoder、Codex、Gemini CLI、Cursor、Windsurf、Cline、OpenCode、CodeBuddy、Trae、TraeWork、WorkBuddy 等 20+ 客户端）：

```bash
pnpm install
pnpm skills
```

也可以走 Makefile 入口：`make install && make skills`（`make help` 查看全部命令）。

默认以软链接方式安装，仓库里的改动即时生效，重复执行会更新已安装的技能。不带参数时执行**全量对齐**：每个技能都会装到每个已检测到的编辑器，编辑器里指向本仓库但已从仓库删除的技能会被清理，因此不会出现「某个工具有这个技能、另一个没有」。

| 参数 | 说明 |
|------|------|
| `--target=claude,qoder` | 只安装到指定编辑器 |
| `--skill=cli,resume` | 只安装指定技能（跳过清理，其余技能与编辑器不动） |
| `--copy` | 复制文件而不是创建软链接 |
| `--force` | 覆盖/移除编辑器里的同名技能（默认跳过非本仓库安装的技能） |
| `--uninstall` | 从各编辑器移除本仓库的技能 |
| `--dry-run` | 只打印将要执行的操作 |

支持的编辑器（配置目录存在即视为已安装，技能目录统一为 `<配置目录>/skills`）：

| `--target` | 客户端 | 技能目录 |
|------------|--------|----------|
| `claude` | Claude Code | `~/.claude/skills` |
| `agents`（别名 `universal`） | Cline / Zed / Warp / Kimi Code 等共用目录 | `~/.agents/skills` |
| `config-agents`（别名 `amp`、`replit`） | Amp / Replit 共用目录 | `~/.config/agents/skills` |
| `qoder` | Qoder | `~/.qoder/skills` |
| `qoder-cn` | Qoder CN | `~/.qoder-cn/skills` |
| `codex` | Codex | `~/.codex/skills` |
| `gemini` | Gemini CLI | `~/.gemini/skills` |
| `antigravity` | Antigravity | `~/.gemini/antigravity/skills` |
| `cursor` | Cursor | `~/.cursor/skills` |
| `windsurf` | Windsurf | `~/.codeium/windsurf/skills` |
| `copilot` | GitHub Copilot CLI | `~/.copilot/skills` |
| `opencode` | OpenCode | `~/.config/opencode/skills` |
| `qwen` | Qwen Code | `~/.qwen/skills` |
| `iflow` | iFlow CLI | `~/.iflow/skills` |
| `kilo` | Kilo Code | `~/.kilo/skills` |
| `roo` | Roo Code | `~/.roo/skills` |
| `codebuddy` | CodeBuddy | `~/.codebuddy/skills` |
| `codebuddy-cn` | CodeBuddy CN | `~/.codebuddycn/skills` |
| `trae` | Trae | `~/.trae/skills` |
| `trae-cn`（别名 `traework-cn`） | Trae CN / TraeWork CN | `~/.trae-cn/skills` |
| `trae-plugin`（别名 `marscode`） | Trae 插件（VS Code / JetBrains） | `~/.marscode/skills` |
| `workbuddy` | WorkBuddy | `~/.workbuddy/skills` |

路径以 [vercel-labs/skills](https://github.com/vercel-labs/skills) 的支持列表为准，需要更多客户端可在 `scripts/install.ts` 的 `EDITORS` 里追加一行。

脚本只会操作本仓库装出去的技能（指向仓库的软链接，或与仓库内容一致的副本）；编辑器里已有的同名技能会被跳过并提示，加 `--force` 才会覆盖，其他技能更不会碰到。

### 终端速览技能

`skill` 命令在终端里一屏列出所有技能，每个技能一行「名称 + 一句话用途」，按来源分组，方便快速分辨。完整触发条件与边界说明来自各技能 `SKILL.md` 的 `description`，用 `--verbose` 查看。

```bash
make link                      # 首次：等价于 pnpm link --global，注册全局 skill 命令
skill                          # 速览全部技能
skill --verbose                # 查看完整触发/边界描述
skill --source=own             # 只看自维护技能
skill --search=面试             # 按名称或描述搜索
skill --skill=clarify          # 只看指定技能
skill --json                   # JSON 输出，便于脚本消费
skill --help                   # 查看全部参数
```

仓库内也可直接运行 `make skill` 或 `pnpm skill`。`pnpm link --global` 注册后，命令指向仓库里的脚本，改动即时生效。

### 通过 skills CLI 安装

```bash
pnpx skills add dushenyan/skills --skill='*'
```

或全局安装所有技能：

```bash
pnpx skills add dushenyan/skills --skill='*' -g
```

在 [skills](https://github.com/vercel-labs/skills) 了解更多 CLI 使用方法。

## 技能

全部技能由 Shenyan Du 手动维护，包含他偏好的工具、设置约定和最佳实践。

| 技能 | 描述 |
|-------|-------------|
| [web-research-report](own/web-research-report) | 自主互联网调研报告：拆问题、搜索抓取、来源分级、交叉验证、带证据表成文；自带纯标准库远程正文下载脚本 |
| [report-doc-polisher](own/report-doc-polisher) | 把调研初稿、网页摘录、聊天记录合并成正式报告：事实盘点、删重复、按读者顺序重组、风格与终检 |
| [doc-workflow](own/doc-workflow) | 文档任务总编排：按教程目录、Markdown 文件、链接三条路线分流到对应技能，成文先看再问配图，配图看完再问上传图床 |
| [article-readability-rewriter](own/article-readability-rewriter) | 诊断并改写不好读的文章：先判断吸引力来源，再按顺序、形态、密度、语气四类杠杆逐条改写 |
| [article-illustrations](own/article-illustrations) | 为文章规划并生成配图：通读全文找需要画面的位置、定图型与风格基线、复用 image-prompt-designer 出图、写图注并落回文章 |
| [arrange-docs](own/arrange-docs) | 把零散收集的文档初稿规整成正式稿件：删除对话残留与重复内容、逐张看图图文对应配注、按阮一峰规范润色并去 AI 味，排版与去味复用现有技能不自造 |
| [ruanyf-answer-style](own/ruanyf-answer-style) | 用阮一峰风格为题目写备考答案：术语先落地、短句白话、按需控制篇幅 |
| [ruanyf-document-style-guide](own/ruanyf-document-style-guide) | 阮一峰中文技术文档写作规范的代理化改写：排版、句式、标点、数值的硬规则速查与校对工作流 |
| [ruanyf-paper-explainer](own/ruanyf-paper-explainer) | 把论文或技术长文变成中文可读材料：深度解读、精读笔记、摘要卡片、汇报稿、综述，默认阮一峰风格且可整体覆盖 |
| [image-prompt-designer](own/image-prompt-designer) | 通用图片生成方案：先判表达型还是信息型，再按可裁剪骨架写提示词——摄影、插画、产品图、封面与信息图、架构图、流程图都走同一套判断，生成后分层校验 |
| [tech-tutorial](own/tech-tutorial) | 生成通用、系统、内容充实的中文技术教程：结构对齐菜鸟教程、语气贴近阮一峰，先列知识点清单确保覆盖齐全，每个知识点按「是什么/为什么/怎么用/常见场景/坑/小结」六要素讲透，重点内容显式标注，按需配套可运行示例脚本与项目案例（先判必要性，不默认产出） |
| [interactive-concept-visual](own/interactive-concept-visual) | 一页单文件交互式概念讲解页：版式按概念本身的难点选，读者能亲手操作、看见概念如何运作 |
| [inspect-resume](own/inspect-resume) | 7 个 AI 驱动的求职诊断工具，从简历审查到面试通关 |
| [project-highlights-extractor](own/project-highlights-extractor) | 项目素材萃取 + 可控包装：八维提炼事实，再沿项目真实方向补主流技术、显性化术语、合理化量级，输出简历要点与面试答辩清单 |
| [socratic](own/socratic) | 苏格拉底式思考伙伴：不直接给答案，通过层层追问引导用户澄清决策、检验理解、打磨论证 |
| [clarify](own/clarify) | 模糊需求澄清器：一句话式笼统需求先两阶段问清，输出问题重述卡片，确认后直接开工 |
| [skill-polisher](own/skill-polisher) | 技能文件体检与打磨：六维度诊断报告、description 三要素与字数区间、技能间引用网络与风格锚点词保护 |
| [picgo-upload](external/picgo-upload) | 用 PicGo 把本地图片或文件传到图床拿回公开链接：优先复用已开着的 PicGo 客户端，其次走 CLI，最后才推荐 PicGo Cloud |
| [interview-simulator](own/interview-simulator) | 连续多轮深度模拟面试：基于简历针对性提问，给三段式结构化反馈与理想回答范例 |
| [makefile-style](own/makefile-style) | Makefile 组织规范：编号章节分类、每个分类收敛出总命令、统一排版与自动 help |
| [python-project-spec](own/python-project-spec) | Python 项目规范脚手架：uv 依赖、Makefile、apps/common/tests 目录、docs 模板、Scalar API 文档 |
| [shenyan](own/shenyan) | 个人的 JavaScript/TypeScript 项目工具与编码约定：代码组织、@antfu/eslint-config、pnpm catalogs、monorepo 别名、tsdown 发库 |
| [humanizer-zh](external/humanizer-zh) | 中文文本润色：清理空话、重复与模板化表达，保留事实、确定程度和作者声音，31 个检查点按 A–F 分类 |
| [humanizer-final-check](own/humanizer-final-check) | 中文文本交付前的去 AI 味终检：跑扫描脚本定位候选，按 humanizer-zh 的 A–F 检查点逐条判定，供各写作技能统一调用 |
| [skill-creator](external/skill-creator) | 从零创建或更新 Agent Skill：判定写/装与项目/全局范围，按规范生成 SKILL.md 并校验 |
| [baoyu-image-gen](external/baoyu-image-gen) | 调用多家图像 API 生成图片：文生图、参考图、比例尺寸与批量生成，是写作配图链路的出图执行层 |
| [baoyu-article-illustrator](external/baoyu-article-illustrator) | 分析文章结构定位配图位置，按类型×风格×配色批量生成插图；与 article-illustrations 的设计规划不同，偏上游整套成稿配图执行 |
| [baoyu-slide-deck](external/baoyu-slide-deck) | 从内容生成可发布风格的逐页图片幻灯片，支持风格维度配置并合并为 PPTX/PDF |
| [script-cli](own/script-cli) | 现代 CLI 应用开发的最佳实践：架构、参数解析、交互式提示、日志、配置、错误处理与测试 |



## 常见问题

### 这个集合有什么不同之处？

这个集合有个人观点，关键在于它沉淀的是一套可复用的工作流与约定，而不是零散的提示词。技能以纯 Markdown 组织，可以用 `pnpm skills` 一键安装到本地各编辑器，也可以发布出去供他人安装。

### Skills vs llms.txt vs AGENTS.md

对我来说，技能的价值在于它的**可共享性**和**按需使用**。

可共享性使提示更容易在项目之间管理和重用。按需使用意味着技能可以根据需要被引入，其规模远远超出了任何代理的上下文窗口一次可以容纳的范围。

你可能会听到人们说 "AGENTS.md 优于技能"。我认为这是真的 —— AGENTS.md 预先加载所有内容，所以代理总是尊重它，而技能可能会有假阴性，即代理在你期望的时候没有引入它们。也就是说，我认为这更多是工具和集成方面的差距，随着时间的推移会改进。技能实际上只是代理消费的标准化格式 —— 归根结底是纯 Markdown 文件。把它们看作是代理的知识库。如果你希望某些技能始终适用，你可以在你的 AGENTS.md 中直接引用它们。

## 生成你自己的技能

fork 这个项目来创建你自己的定制技能集合。

1. fork 或克隆这个存储库
2. 安装依赖：`make install`（或 `pnpm install`）
3. 在 `own/`（自维护）或 `external/`（外部引入）下按 [Agent Skills](https://agentskills.io/home) 规范新增技能：每个技能一个目录，并包含 `SKILL.md`
4. 运行 `make skills` 把技能安装到本地编辑器验证效果

请参阅 [AGENTS.md](AGENTS.md) 了解详细的编写指南。
