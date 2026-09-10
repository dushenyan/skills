# Shenyan Du 的技能集

一个精心策划的 [Agent Skills](https://agentskills.io/home) 集合，反映了 [Shenyan Du](https://github.com/dushenyan) 的偏好、经验和最佳实践，以及工具的使用文档。

> [!IMPORTANT]
> 这些技能沉淀的是我个人可复用的工作流与约定，尚未经过完整的实践验证，因此非常欢迎反馈和贡献。

## 安装

### 一键安装到本地编辑器

克隆本仓库后，一条命令即可把 `skills/` 下的技能补充到本地各 AI 编辑器的全局技能目录（自动检测 Claude Code、CodeBuddy、Trae 等）：

```bash
pnpm install
pnpm skills
```

也可以走 Makefile 入口：`make install && make skills`（`make help` 查看全部命令）。

默认以软链接方式安装，仓库里的改动即时生效，重复执行会更新已安装的技能。常用参数：

| 参数 | 说明 |
|------|------|
| `--target=claude,codebuddy,trae-cn` | 只安装到指定编辑器 |
| `--skill=cli,resume` | 只安装指定技能 |
| `--copy` | 复制文件而不是创建软链接 |
| `--uninstall` | 从各编辑器移除本仓库的技能 |
| `--dry-run` | 只打印将要执行的操作 |

脚本只会操作本仓库中存在的技能名，不会影响编辑器里的其他技能。

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
| [python-project-spec](skills/python-project-spec) | Python 项目规范脚手架：uv 依赖、Makefile、apps/common/tests 目录、docs 模板、Scalar API 文档 |
| [resume](skills/resume) | 7 个 AI 驱动的求职诊断工具，从简历优化到面试通关 |
| [ruanyf-paper-explainer](skills/ruanyf-paper-explainer) | 把论文或技术长文改写成阮一峰风格的中文解读文章 |
| [runoob-tech-tutorial](skills/runoob-tech-tutorial) | 生成菜鸟教程风格、循序渐进的全链路中文技术教程，配套可运行项目案例 |
| [shenyan](skills/shenyan) | 个人的 JavaScript/TypeScript 项目工具与约定（@antfu/ni、ESLint、pnpm catalogs、monorepo 等） |

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

## 许可证

技能和本存储库中的脚本采用 MIT 许可证。

### 致谢

- [antfu](https://github.com/antfu) 对开源做出的卓越贡献
