# 代码注释规范（Google 风格 docstring）

本文件覆盖 Skill 的「四、代码注释规范」。

## 四、代码注释规范

代码注释面向**初学者友好**，遵循以下原则：

1. **函数级别必须有注释** — 解释「为什么这么做」，而不是「做了什么」
2. 关键算法或非直观逻辑处补充行内注释
3. 复杂的业务前置条件、依赖假设要在模块/类注释中说明

### 注释示例（Google 风格）

函数 docstring 统一采用 **Google 风格**，必须包含 `Args` 与 `Returns` 段，必要时补充 `Raises` 段。

```python
def compute_similarity(query: str, candidates: list[str], top_k: int = 5) -> list[float]:
    """计算 query 与候选集合的语义相似度并返回 Top-K 分数。

    选择余弦相似度而非欧氏距离，因为高维词向量空间中
    余弦值对方向差异更敏感，且不受向量长度缩放影响，
    更符合 FAQ 语义匹配「语义方向优先」的业务目标。

    Args:
        query: 用户输入的查询语句，原始字符串，不需要预处理。
        candidates: 候选 FAQ 标准问列表，长度通常为 10~500。
        top_k: 返回的最大相似度条目数，默认 5。超出候选长度时自动截断。

    Returns:
        按相似度降序排列的 Top-K 分数列表，值域为 [0.0, 1.0]，
        长度不超过 min(top_k, len(candidates))。

    Raises:
        ValueError: 当 candidates 为空列表时抛出，避免无意义排序开销。
    """
    if not candidates:
        raise ValueError("candidates 不能为空")
    ...
```

### Google 风格要点速查

| 段落 | 是否必填 | 说明 |
|------|----------|------|
| 功能首句 | 是 | 动词开头，一句话说明「做什么」 |
| 设计说明 | 推荐 | 解释「为什么这么做」，对应业务或技术取舍 |
| `Args:` | 是 | 每个参数一行：`参数名: 中文说明（类型、取值范围、默认值含义）` |
| `Returns:` | 函数非 None 时必填 | 说明返回结构、顺序、值域、单位等 |
| `Raises:` | 有显式抛出异常时必填 | 列出异常类型 + 触发条件 |
