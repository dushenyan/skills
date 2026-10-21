# Shenyan Du 的技能集

一个精心策划的 [Agent Skills](https://agentskills.io/home) 集合，反映了 [Shenyan Du](https://github.com/dushenyan) 的偏好、经验和最佳实践，以及工具的使用文档。

> [!IMPORTANT]
> 这些技能沉淀的是我个人可复用的工作流与约定，尚未经过完整的实践验证，因此非常欢迎反馈和贡献。

## 安装

### 一键安装到本地编辑器

克隆本仓库后，一条命令即可把 `skills/` 下的技能补充到本地各 AI 编辑器 / CLI 的全局技能目录（自动检测 Claude Code、Qoder、Codex、Gemini CLI、Cursor、Windsurf、Cline、OpenCode、CodeBuddy、Trae、TraeWork、WorkBuddy 等 20+ 客户端）：

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
| [cli](skills/cli) | 现代 CLI 应用开发的最佳实践：架构、参数解析、交互式提示、日志、配置、错误处理与测试 |
| [clarify](skills/clarify) | 模糊需求澄清器：一句话式笼统需求先两阶段问清，输出问题重述卡片，确认后直接开工 |
| [project-highlights-extractor](skills/project-highlights-extractor) | 项目素材萃取 + 可控包装：八维提炼事实，再沿项目真实方向补主流技术、显性化术语、合理化量级，输出简历要点与面试答辩清单 |
| [python-project-spec](skills/python-project-spec) | Python 项目规范脚手架：uv 依赖、Makefile、apps/common/tests 目录、docs 模板、Scalar API 文档 |
| [resume](skills/resume) | 7 个 AI 驱动的求职诊断工具，从简历优化到面试通关 |
| [ruanyf-document-style-guide](skills/ruanyf-document-style-guide) | 阮一峰中文技术文档写作规范的代理化改写：排版、句式、标点、数值的硬规则速查与校对工作流 |
| [ruanyf-paper-explainer](skills/ruanyf-paper-explainer) | 把论文或技术长文改写成阮一峰风格的中文解读文章 |
| [runoob-tech-tutorial](skills/runoob-tech-tutorial) | 生成通用、系统、内容充实的中文技术教程：结构对齐菜鸟教程、语气贴近阮一峰，每个知识点按「是什么/为什么/怎么用/常见场景/坑/小结」六要素讲透，重点内容显式标注，配套可运行项目案例 |
| [shenyan](skills/shenyan) | 个人的 JavaScript/TypeScript 项目工具与约定（@antfu/ni、ESLint、pnpm catalogs、monorepo 等） |
| [socratic](skills/socratic) | 苏格拉底式思考伙伴：不直接给答案，通过层层追问引导用户澄清决策、检验理解、打磨论证 |

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
3. 在 `skills/` 下按 [Agent Skills](https://agentskills.io/home) 规范新增技能：每个技能一个目录，并包含 `SKILL.md`
4. 运行 `make skills` 把技能安装到本地编辑器验证效果

请参阅 [AGENTS.md](AGENTS.md) 了解详细的编写指南。
