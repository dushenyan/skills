---
name: skill-polisher
description: 体检并打磨技能文件：按 frontmatter 合规、description 三要素与字数区间、SKILL.md 索引结构、references 命名与孤儿文件、技能间引用网络、README 同步六个维度先出诊断报告，确认后逐项修复；为相邻技能补分工引用，阮一峰等风格锚点词重点保护不误删。当用户要求检查、格式化、规范化或打磨技能文件，抱怨技能描述太长、太薄、触发不准、不合规范、技能间缺少互相引用，或在新增/修改技能后想统一风格时使用。不用于从零创建新技能（交给 skill-creator），也不改写技能的实质技术内容——只动结构与表述。
metadata:
  author: Shenyan Du
  version: "2026.11.16"
  source: 手写维护，scripts located at https://github.com/dushenyan/skills
---

# 技能文件打磨器

对本仓库 `own/` 与 `external/` 下的技能做**结构与表述层面的体检和修复**，让每个技能文件做到三点：描述通用（能力用类别词，不绑定特定例子）、信息立体（做什么/何时触发/边界三要素齐全）、字数适中（description 300~700 字符，要素优先于字数）。诊断先行，改什么、怎么改都先过用户确认。

定稿前必须走「终检：去 AI 味」，见本文同名章节。

## 工作流

1. **扫描**：遍历 `own/*/` 与 `external/*/`，收集每个技能的结构数据——SKILL.md 行数、description 字符数、references 文件清单、GENERATION.md 有无。
2. **诊断**：按六个维度逐项检查，问题分三级——P0 结构缺失（影响可用）、P1 description 不达标（影响触发）、P2 风格与命名（影响维护）。
3. **报告**：输出体检报告，按严重度排列，每条问题给出定位、判定依据和建议修法，等用户圈定修复范围。
4. **修复**：逐项修复；改完更新受影响技能的 `version` 与 README 清单，再复扫一次确认清零。

**边界**：只动结构与表述，不动技能的实质技术判断（某技能的教学法、评分量表本身不在打磨范围）；阮一峰等风格锚点信息是保护对象，只突出、不削弱，细则见 [core-description](references/core-description.md)。description 改写遵循三要素优先——先齐全，再控字数，不为一刀切砍掉边界层。

## 核心参考

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 诊断清单 | 五维度的检查项与 P0/P1/P2 判级标准 | [core-checklist](references/core-checklist.md) |
| description 打磨 | 三要素结构、300~700 字数的拿捏、通用性与立体度 | [core-description](references/core-description.md) |

## 功能

| 主题 | 描述 | 参考 |
|-------|-------------|-----------|
| 修复手法 | 补薄描述、给重描述瘦身、补结构、更新版本号 | [feature-repair](references/feature-repair.md) |
| 同步检查 | README 清单与 own/、external/ 目录的一致性核对 | [feature-sync](references/feature-sync.md) |

## 终检：去 AI 味（流程的最后一步）

这不是可跳过的附录。定稿前先跑扫描，再逐条过人工清单，两条都过才算交付。

`humanizer-zh` 在仓库里位于 `external/`，安装到编辑器后与其他技能平铺在同一 `skills/` 下，相对路径随布局变化。先定位脚本再跑，两种布局都覆盖：

```bash
SCAN=$(ls ../humanizer-zh/scripts/scan-ai-tone.mjs ../../external/humanizer-zh/scripts/scan-ai-tone.mjs 2>/dev/null | head -1)

node "$SCAN" 稿件.md   # 稿件已落盘
node "$SCAN" -         # 从标准输入读
```

扫描只负责把候选捞出来，判定标准在 `humanizer-zh/SKILL.md` 的 A–F 检查点（仓库内为 `external/humanizer-zh/SKILL.md`）。命中不等于必须改，承载实际信息的句子照原样保留。

必须清掉的六处：

- 空泛高频词：「赋能」「闭环」「显著提升」换成具体动作或数据
- 强凑三段式：有几项写几项，不为节奏删项或凑项
- 万能破折号：每处问一句「换成逗号或句号是否更清楚」
- 句尾拔高：结论停在事实上，不追加「这标志着……」
- 套话收尾：删掉「综上所述」「未来可期」「希望对你有帮助」
- 客服腔与免责填充：「值得注意的是」「需要指出的是」

底线是保留事实、否定、条件、归因、时间与完成状态，润色不许改变原意。
