# 生成信息

- **来源：** `手动创建`
- **生成时间：** 2026-11-14
- **说明：** 2026-11-18 固化国内外视频必须汲取内容反哺教程正文的规则，视频反哺不随篇幅压缩。2026-11-16 name 字段由 `runoob-tech-tutorial` 改为 `tech-tutorial`，与目录名对齐。同日经 skill-polisher 体检修复：description 压缩手法细节并补与 ruanyf-paper-explainer / ruanyf-answer-style 的分工句（单向引用改双向）；示例对话拆到 `references/feature-workflow-examples.md`，正文留索引行。
- **打磨记录：** 2026-11-18 经 skill-polisher 二次体检修复：README 清单描述与技能行为对齐（示例脚本由默认产出改为按需产出）；description 去除 frontmatter 内的 Markdown 加粗符号；「三、引用文件」表头改为「三、核心参考」以对齐仓库模板；清理 scripts/__pycache__ 编译缓存。
- **脚本降级：** `scripts/check_tutorial.py` 从「2 类 ERROR 阻断 + 5 类 WARN 提示」改为全部机械项只提示、不阻断，退出码恒为 0；同步清理 SKILL.md Step 5 与 `references/feature-workflow-examples.md` 中的「ERROR 清零」表述。动机：用户认为脚本做严格卡控无必要，保留机械兜底的提示价值即可。
