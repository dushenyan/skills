---
name: core-project-layout
description: 目录结构与 PEP 8 命名规范：apps/common/tests 目录划分、文件/类/函数命名与名实相符检查，划分目录或命名文件时读取。
---

# 目录结构与命名规范

本文件覆盖 Skill 的「三、目录结构规范（必须）」，含命名规范与文件一致性要求。

## 三、目录结构规范（必须）

当项目包含多个业务模块时，采用 **apps 包裹 + 子模块划分** 的结构：

```
<project-root>/
├── apps/                          # 多业务逻辑模块
│   ├── <business_a>/              # 业务模块 A
│   │   ├── __init__.py
│   │   ├── models.py              # 数据模型
│   │   ├── services.py            # 业务逻辑
│   │   ├── routers.py             # 路由/入口
│   │   └── schemas.py             # 数据结构定义
│   └── <business_b>/              # 业务模块 B
│       └── ...
├── common/                        # 公共组件（配置、工具、中间件等）
│   ├── config.py
│   ├── utils.py
│   └── ...
├── tests/                         # 测试目录，与 apps 结构对应
├── docs/                          # 项目文档（见 core-docs-templates.md）
├── Makefile
├── pyproject.toml                 # uv 依赖配置
├── README.md
└── .gitignore
```

### 目录设计思路

- **apps/** 将不同业务域隔离，每个子模块自包含 models/services/routers/schemas，降低耦合
- **common/** 存放跨模块复用的能力，避免循环依赖
- **tests/** 镜像 apps 结构，便于按模块定位用例

### 3.1 文件与代码命名规范（PEP 8）

Python 最主流的命名规范是 **PEP 8**，文件与代码命名必须遵循：

| 对象 | 规范 | 正例 | 反例 |
|------|------|------|------|
| 包 / 模块 / 文件名 | 全小写 snake_case，简短明确 | `api_client.py`、`logging_config.py` | ~~`Home.py`~~、~~`APIClient.py`~~ |
| 类名 | PascalCase（大驼峰） | `FaqMatchRequest`、`ESIndexService` | ~~`faq_match_request`~~ |
| 函数 / 方法 / 变量 | snake_case（小写下划线） | `compute_similarity` | ~~`computeSimilarity`~~ |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` | ~~`maxRetryCount`~~ |
| 受保护成员 | 前置单下划线 | `_internal_cache` | — |
| 私有成员 | 前置双下划线 | `__secret_key` | — |

补充约束：

- **禁止单字符命名**（循环计数器 `i`、`j` 与异常 `e` 除外）
- **禁止覆盖内置名**：不使用 `list`、`dict`、`type`、`id` 等作为变量/函数名
- 文件名中的数字前缀仅在框架约定要求时使用（如 Streamlit `pages/` 目录的 `1_category.py` 排序前缀）

### 3.2 文件名与代码内容一致性（必须）

文件名是代码的「目录索引」，必须满足：

1. **名实相符**：文件名必须准确描述内部全部代码的职责。例如 `logging_config.py` 只放日志配置；若文件内出现与文件名无关的代码，说明归属错误
2. **单一主题**：一个模块只承载一个主题；超过单一主题时拆分为子模块或包
3. **改名优先于将就**：发现名不符实的文件，重命名文件（或移动代码），而不是让名字继续撒谎
4. **入口文件命名**：应用入口统一 `main.py`；Streamlit 主页面用 `home.py`（不使用 `Home.py`）
