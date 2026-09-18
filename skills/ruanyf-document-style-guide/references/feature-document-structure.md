---
name: feature-document-structure
description: 软件手册的章节结构与文档文件命名规则
---

# 文档体系

完整的软件手册建议采用的结构，以及文档文件命名规则。

## 使用

**章节结构**

- **简介**（Introduction）：[必备] 对产品和文档的总体说明
- **快速上手**（Getting Started）：[可选] 最快用起来的路径
- **入门篇**（Basics）：[必备] 初级使用教程，含环境准备、设置
- **进阶篇**（Advanced）：[可选] 中高级开发教程
- **API**（Reference）：[可选] API 逐一介绍
- **FAQ**：[可选] 常见问题
- **附录**（Appendix）：[可选] Glossary、Recipes、Troubleshooting、ChangeLog

真实范例：[Redux 手册](https://redux.js.org/introduction/getting-started)、[Atom 手册](http://flight-manual.atom.com/)。

**文件命名**

- 不含空格，只用半角字符（文件名不用中文）。
- 只用小写字母，多个单词用半角连词线 `-` 分隔：`advanced-usage.md`，不是 `advanced_usage.md`。
- `README`、`LICENSE` 等说明文件可以大写。

## 要点

- 这套结构适用于完整的手册类文档；单篇文章只需要它的精神：简介 → 上手 → 深入 → 参考。
- 中文文件名是常见反例，新建文档文件时第一个检查项。

<!--
来源参考：
- https://github.com/ruanyf/document-style-guide/blob/master/docs/structure.md
-->
