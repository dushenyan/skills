---
name: feature-code-examples
description: engineering_examples 示例库落位规范：目录与命名、脚本骨架、高亮/下划线标记、LLM 主题复用 utils 与运行验证，抽配套脚本时读取。
---

# 配套代码示例（engineering_examples 示例库）

教程正文里的代码块是给"读"的，示例库里的脚本是给"跑"的。整份教程写完后，把最重要、最能帮读者建立手感的 **2~5 个示例**抽成编号可运行脚本，落到 `~/Desktop/engineering_examples/` 下的新主题目录。动笔前先翻一眼仓库里的既有脚本（如 `context/01_context_slots.py`、`utils.py`），照它的手感写。

## 一、仓库结构与落位规则

```
engineering_examples/
├── config.py            # 服务商与显示配置（环境变量切 Mock / Ollama / 远程 API），不要改
├── utils.py             # 显示层与 LLM 调用辅助（calc 下划线、ai_text 高亮等），不要改
├── pyproject.toml       # uv 管理依赖
├── context/             # 一个主题一个目录
│   ├── 01_context_slots.py
│   └── Context-Engineering学习指南.md
└── harness/ ...
```

- 每份教程开一个**新主题目录**，目录名用小写（如 `milvus/`、`fastapi/`），与教程技术名对应。
- 文件命名 `NN_主题.py`，序号从 `01` 起，顺序对齐脚本在教程正文出现的次序；一个脚本只讲一个主题。
- **只新增目录，不改仓库既有文件**：`config.py`、`utils.py` 和其它主题的脚本一律不动。
- 大文件（数据集、模型权重）不入库，脚本里用链接或小样本代替。

## 二、脚本骨架（对照既有脚本的四段式）

头部 docstring → 常量与函数 → `__main__` 演示 → 要点总结，四段缺一不可：

```python
"""
03 - 分区键与数据分区

核心思想：查询性能高度依赖分区键的选择，本示例对比两种分区策略的差别。
适合场景：设计 Collection Schema、需要大规模过滤检索时。

学习要点：
- 分区键决定写入路由，不要把高基数字段设成分区键
- 单分区 vs 多分区的延迟对比，用数据说话

运行: python3 milvus/03_partition.py
"""
```

- docstring 五要素（编号标题 / 核心思想 / 适合场景 / 学习要点 / 运行命令）必写；运行命令直接照抄可跑。
- 函数一律 Google 风格 docstring；关键行注释解释**为什么这么做**，不解释在做什么。
- `__main__` 末尾打一个「要点总结」块，回扣本脚本对应的教程知识点——与教程里「六要素」的最后一项呼应。

## 三、高亮与下划线（示例库的视觉约定）

仓库既有脚本用 ANSI 转义序列让关键信息一眼可分，新脚本必须沿用同一套约定：

| 标记 | 含义 | LLM 主题：复用仓库 helper | 非 LLM 主题：脚本自带等价 helper |
|---|---|---|---|
| 下划线 | 本次运行**算出来的值**（数量、占比、延迟），与输入参数、固定文案区分 | `from utils import calc` | 头部定义同款 `calc()`（`\033[4m{value}\033[0m`） |
| 粗体亮青 / 深灰底整块衬底 | 关键结论、模型回复，从普通输出里跳出来 | `ai_text()` / `print_response()` | 对「重点结论」输出段用同样的粗体亮青 |
| 双线 / 单线标题框 | 章节标题、要点总结块 | `print_header()` / `print_response()` | 等价实现或复用 |

- 下划线**只标计算值**，不要给输入参数、装饰性文字加——全标等于没标。
- 非 LLM 主题的脚本不硬依赖 `from utils import ...`（那些 helper 绑着 LLM 配置），在文件头部抄几行等价实现即可，保持终端观感一致。

## 四、LLM 相关主题的额外约定

教程本身讲 LLM / Agent 时，脚本必须走仓库现成通道，不要自己搭调用层：

- 模型调用统一用 `chat_completion()` / `chat_with_tools()` / `stream_completion()`，服务商由 `config.py` 环境变量切换：`USE_MOCK=1`（离线演示）、`USE_OLLAMA=1`（本地）、`LLM_API_KEY` + `LLM_BASE_URL` + `LLM_MODEL`（DeepSeek / 通义 / 豆包 / GLM 等国产 OpenAI 兼容网关开箱即用）。
- 每个脚本要保证 **Mock 模式也能跑通**：主流程别硬编码真实 API 的返回内容，关键词能命中 `utils.py` 的响应池或走兜底回复即可。

## 五、运行与验证

- 零第三方依赖：`python3 <主题>/<脚本>.py` 直接跑（LLM 主题加 `PYTHONPATH=.`）。
- 需要额外依赖：在仓库根 `uv add <包>`，并在脚本「运行」行注明 `uv run python <主题>/<脚本>.py`。
- 写完**逐个实际运行一遍**（LLM 主题用 `USE_MOCK=1 PYTHONPATH=. python3 ...` 验证），确认不报错、下划线和高亮效果正常，再进教程自查。
- 教程正文对应小节末尾标注脚本路径，让读者能从「读」跳到「跑」：

  ```markdown
  > 可运行示例：`engineering_examples/milvus/03_partition.py`
  ```
