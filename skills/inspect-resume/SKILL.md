---
name: inspect-resume
description: 以资深技术面试官视角审查简历并做求职全链路诊断：简历体检（淘汰红线、6 秒初筛、分层排查）、目标赛道锚定、投放策略系统、冷邮件外联、带评分量表的模拟面试、求职全案复盘。适用于需要检查或优化简历、提高技术岗求职成功率、准备面试的用户。边界：简历要点深加工与 STAR 改写交给 project-highlights-extractor；连续多轮深度模拟面试与理想回答范例交给 interview-simulator，本技能的模拟面试工具只做求职诊断链路内的评分摸底。
metadata:
  author: Shenyan Du
  version: "2026.11.16"
  source: 手写维护，scripts located at https://github.com/dushenyan/skills
---

# 简历审查与求职诊断技能

以**资深技术面试官的评判标准**串起一条求职流水线：定位 → 简历 → 策略 → 外联 → 面试 → 复盘。每个工具都给出「面试官凭什么判断」的标准、可执行流程与输出模板，而不只是名字。面向技术岗。

> 与 `project-highlights-extractor` 分工：那个技能负责把项目素材深加工成分档简历要点与 STAR 故事；本技能负责诊断、定位、投放策略、外联与模拟面试。需要改写具体 bullet 时交叉引用，不在此重复。

## 核心参考

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 求职诊断工具 | 7 个工具，含淘汰红线、6 秒视线落点、L1~L5 下钻、1~5 评分量表、外联骨架 | [core-tools](references/core-tools.md) |

## 功能

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 提示词模板 | 7 个内嵌面试官评判口径的技术岗模板，可直接复制 | [feature-prompt-templates](references/feature-prompt-templates.md) |
| 最佳实践 | 使用流程、技术岗误区、与同类技能的分工 | [best-practices](references/best-practices.md) |