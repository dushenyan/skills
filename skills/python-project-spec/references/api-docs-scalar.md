# 服务 API 文档规范（Scalar）

本文件覆盖 Skill 的「六、服务 API 文档规范（Scalar）」。

## 六、服务 API 文档规范（Scalar）

如果项目涉及**启动对外服务**（HTTP API、Web 服务等），API 文档必须使用 **Scalar** 库进行渲染与交互，替代默认的 Swagger UI / ReDoc。

### 6.1 为什么选择 Scalar

- 界面现代化，支持深色模式与响应式布局
- 内置「一键调用」面板，预填参数后可直接发请求
- 支持中文备注、示例值、字段枚举说明，对中文团队更友好
- 基于 OpenAPI 3.x 标准，与 FastAPI / Starlette 等框架无缝对接

### 6.2 接入方式（FastAPI 示例）

```python
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from scalar_fastapi import get_scalar_api_reference

app = FastAPI(
    title="FAQ 语义匹配服务",
    description="提供多租户、多知识库的 FAQ 语义检索与匹配能力",
    version="1.0.0",
    docs_url=None,        # 关闭默认 Swagger UI
    redoc_url=None,       # 关闭默认 ReDoc
)

# 挂载 Scalar 文档页作为主文档入口
@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="FAQ 匹配服务 · API 文档",
    )
```

### 6.3 参数预填与中文备注要求

每个接口的 Pydantic Schema 必须满足以下要求，确保 Scalar 页面打开即可使用：

| 项目 | 要求 | 示例 |
|------|------|------|
| 字段 `title` | 必须使用中文作为字段展示名 | `title="用户查询语句"` |
| 字段 `description` | 解释取值约束、来源、格式 | `description="原始输入字符串，长度 1~500 字符"` |
| 字段 `example` / `examples` | 必须提供**符合业务的真实示例值**，便于在 Scalar 中一键填充 | `example="如何开通会员"` |
| 接口 `summary` | 中文一句话概述功能 | `summary="FAQ 语义匹配"` |
| 接口 `description` | 补充业务场景、调用频率限制等说明 | — |

### 6.4 完整接口示例

```python
from pydantic import BaseModel, Field

class FaqMatchRequest(BaseModel):
    """FAQ 语义匹配请求体。"""

    query: str = Field(
        title="用户查询语句",
        description="用户输入的原始问句，长度范围 1~500 字符，支持中英文混合。",
        example="如何修改收货地址？",
        min_length=1,
        max_length=500,
    )
    knowledge_base_id: str = Field(
        title="知识库 ID",
        description="指定检索的目标知识库，从 /knowledge_bases 接口获取有效值。",
        example="kb_after_sale_001",
    )
    top_k: int = Field(
        title="返回条数",
        description="返回的候选 FAQ 最大数量，超出实际命中数时返回全部。",
        default=5,
        ge=1,
        le=20,
        example=5,
    )

class FaqMatchResponse(BaseModel):
    """FAQ 语义匹配响应体。"""

    matched_questions: list[str] = Field(
        title="匹配到的标准问列表",
        description="按相似度降序排列，长度等于请求 top_k。",
        example=["如何修改收货地址？", "收货地址在哪里改？"],
    )
    scores: list[float] = Field(
        title="对应相似度分数",
        description="值域 [0,1]，下标与 matched_questions 一一对应。",
        example=[0.982, 0.874],
    )

@app.post(
    "/api/v1/faq/match",
    summary="FAQ 语义匹配",
    description="基于向量召回 + 精排两阶段，返回用户问句与目标知识库的 Top-K 匹配结果。\n\n"
                "**调用频率限制**：单租户 QPS 上限 100，超出将返回 429。",
    response_model=FaqMatchResponse,
)
async def faq_match(req: FaqMatchRequest):
    ...
```
