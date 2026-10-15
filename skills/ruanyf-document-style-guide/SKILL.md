---
name: ruanyf-document-style-guide
description: 阮一峰中文技术文档写作规范：字间距、句子、段落、标点、数值、标题层级的硬规则清单，外加阮一峰叙事风格（问题驱动、短句口语、生活化类比）。当用户要求检查或优化中文文档的排版与写作风格（如「检查一下这段中文的排版」「按写作规范改写」「这段话读起来不像人话」「写得像阮一峰一点」）时调用，用于生成或修改面向中文读者的技术文档。
metadata:
  author: Shenyan Du
  version: "2026.10.14"
  source: 手写维护，scripts located at https://github.com/dushenyan/skills
---

# 阮一峰中文技术文档写作规范

本技能是 [ruanyf/document-style-guide](https://github.com/ruanyf/document-style-guide) 的代理化改写：把写作规范压缩成可执行的硬规则清单，用于生成和校对中文技术文档。排版管「看起来」，叙事风格管「读起来」，两者都在本技能覆盖范围内。

## 核心速查（先看这一节）

排版硬规则，写完逐条对照：

- **中英文之间加半角空格**：`启动 Windows 系统`，不是 `启动Windows系统`。数字与中文之间加不加皆可，但全篇统一。
- **全角标点**：`，。：；？！（）「」`。整句英文时才用半角标点。行内代码、URL、命令行内保持半角。
- **顿号分隔并列词**：`Google、Facebook、腾讯和阿里`，不用逗号。最后一个用「和」连接。
- **句号在括号外**：`请参照第 1.3 节（见第 26 页）。`
- **短句**：一句话 ≤20 字最好，40 字以上任何情况不允许。逗号分割的长句不超过 100 字或 3 行。
- **段落**：一个段落一个主题，中心句放段首，不超过七行（最佳 ≤4 行）。
- **数值用半角**：`1000 元`，不是 `１０００元`。千位以上加千分号。
- **避免感叹号**，禁止连用（`！！`）。

风格三句话（细节见 core-narrative-style）：

- 先讲痛点，再给方案，不直接甩定义。
- 短句口语，多用「你」「我们」；抽象概念配一个「贴、准、短」的类比。
- 避开学术腔、官腔、卖课腔和空泛形容。

## 参考索引

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 叙事风格 | 问题驱动、短句口语、类比、作者视角、禁用腔调清单 | [core-narrative-style](references/core-narrative-style.md) |
| 标题 | 四级标题层级与结构规则 | [core-title](references/core-title.md) |
| 文本 | 字间距、句子、写作风格、英文处理 | [core-text](references/core-text.md) |
| 段落 | 段落原则与引用格式 | [core-paragraph](references/core-paragraph.md) |
| 标点符号 | 各标点的全半角用法与易错点 | [core-marks](references/core-marks.md) |
| 数值 | 半角数字、千分号、货币、范围、增减 | [core-number](references/core-number.md) |
| 文档体系 | 软件手册的章节结构与文件命名 | [feature-document-structure](references/feature-document-structure.md) |
| 参考链接 | 引用第三方内容的标注规范 | [best-practices-references](references/best-practices-references.md) |

## 校对工作流

1. **写前**：先过一遍核心速查，硬规则入脑。
2. **写中**：涉及具体类别（如数值范围、英文处理）时，按需加载对应参考；讲解性文字先加载 core-narrative-style 找手感。
3. **写后**：逐条对照核心速查清单，重点查中英文空格、全半角混用、超长句；再过一遍风格四问——开头在讲问题吗？有类比吗？有一句「我」的观察吗？避开禁用腔调了吗？
