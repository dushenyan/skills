---
name: web-research-report
description: 自主完成「互联网调研 → 交叉验证 → 中文报告」全流程：按问题拆解检索词、优先抓官方与一手材料、过滤营销软文和重复来源、把每条结论落到可点击出处，产出带摘要、证据表、分歧与限制的深度报告。当用户说「调研一下 X」「搜一下最近 Y 的进展」「写一份行业/竞品/技术选型报告」「帮我做市场研究」「这个说法有什么依据」「上网查清楚再写」时使用；如果素材已在本地、只需要整理成文，交给 report-doc-polisher 或 arrange-docs。
metadata:
  author: Shenyan Du
  version: "2026.11.26"
  source: 手写维护，scripts located at https://github.com/dushenyan/skills
---

# 互联网调研报告

把模糊问题变成有出处、能复核的中文报告。核心不是堆链接，而是**问题拆解 → 证据筛选 → 冲突处理 → 成文**。

## 搜索用运行时工具，脚本只下载

搜索一律用当前运行时自带的 web search 工具（跟 baoyu-skills 一样，不自己实现搜索引擎）。Python 脚本只做一件确定性的事：**把选定的远程 URL 下载成干净正文**。这样搜索快，抓取可复查，也不需要 pip / bun / node。

### 第一步：用运行时工具搜索

直接用当前可用的 web search 工具搜。Claude Code 用 `WebSearch`，其它客户端用它自带的搜索工具。**不要在 Python 脚本里做搜索**——那要抓搜索引擎页面，又慢又容易被反爬。

搜索时挑官方文档、论文、项目仓库这类一手来源，记下准备深读的 URL。

### 第二步：用脚本下载选中的 URL

```bash
python3 own/web-research-report/scripts/search_fetch_summarize.py \
  --url "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices" \
  --out-dir research-output
```

可重复 `--url` 一次下载多个网页。脚本给每个 URL 打分、抓正文、去噪、去重复，输出证据包。

### 产物

`research-output/` 下有三个东西：

- `search.json`：下载的 URL 和来源评分
- `pages/*.txt`：从远程网页抓下来的正文
- `summary.md`：人读的初筛清单（标题、URL、抓取状态、摘要）

打开 `summary.md` 判断哪些值得深读，再按下面的规则写报告。脚本只负责下载和初筛，不替 Agent 下结论。

详细流程与报告模板见 [调研流程](references/core-research-workflow.md)。

## 用户输入工具

需要用户做选择时，优先用当前运行时提供的弹窗工具（Claude Code 用 `AskUserQuestion`）。没有弹窗工具时按默认流程走完，不在正文里列编号选项让用户打字回复。

## 工作流

1. **拆问题**：把用户问题拆成 3～5 个可检索子问题（定义 / 现状 / 对比 / 案例 / 限制）。题目太泛时，先按这个框架自行收窄，不停下来问用户。
2. **收集**：每个子问题用运行时 web search 工具搜一次，记下检索词、时间、命中的 URL。搜索结果不足时换同义词，不把同一页面换个域名算两个来源。挑出要深读的 URL，再用脚本批量下载正文。
3. **筛选**：优先官方文档、论文、项目仓库、权威媒体；次优个人博客与社区讨论；营销软文、聚合站、内容农场直接排除。每个子问题至少保留 2 个独立来源，关键数字尽量有 2 处印证。
4. **深读**：打开候选页面读正文，摘录关键句、数字、时间、适用条件。脚本抓取的正文要过质量门禁：检查是否包含真实段落、是否只是导航/推荐/登录提示、是否与搜索目标相关。低质量页面换搜索摘要或 Agent 工具重抓，仍不合格则标注「仅看标题与摘要」，不编造正文细节。
5. **处理冲突**：不同来源说法不一致时，并列呈现分歧，说明分歧原因（时间差、口径差、利益立场），不擅自择一。
6. **成文**：按 [报告模板](references/core-research-workflow.md#报告模板) 写 Markdown，每条事实后面跟可点击链接。结论先写，证据后附，限制单独成节。
7. **自检**：逐条检查数字、日期、产品名、人名是否与来源一致；链接是否可访问；有没有把推测写成事实。交付前按 `humanizer-final-check` 跑去 AI 味终检。

## 输出要求

- 默认单个 Markdown 文件，落位在用户指定位置；未指定时落在当前工作区，文件名 `<主题> 调研报告.md`。
- 报告必须包含：执行摘要、关键结论（带出处）、证据表、分歧与限制、参考来源。
- 没有足够证据支撑的项写「当前材料不足」，不用常识补全。
- 报告中的链接必须来自实际访问过的 URL，禁止拼凑或凭记忆写链接。

## 与其它技能的分工

- 本地素材整理成文 → `report-doc-polisher` / `arrange-docs`
- 单篇论文解读 → `ruanyf-paper-explainer`
- 系统教程 → `tech-tutorial`
- 交付前去 AI 味 → `humanizer-final-check`
