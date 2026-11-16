---
name: feature-sync
description: 同步检查：README 清单与 skills/ 目录的一致性核对
---

# 同步检查

本仓库没有登记表，`skills/` 目录是唯一事实来源，README.md 的清单靠手工同步——这正是漂移的温床。每次体检的最后一步是核对两边，修复后必须复查。

## 使用

对照规则（目录侧为准）：

| 情况 | 处理 |
|------|------|
| 目录里有、README 没有 | README 补条目：名称 + 一句话描述（与该技能 description 的能力层一致，不必照抄全文） |
| README 有、目录里没有 | 确认技能已删除后，README 移除条目；若是改名的残留，改为指向新名称 |
| 两边描述明显不符 | 以技能当前 description 的能力层为准更新 README |

核对用脚本做，不逐行肉眼比：

```bash
# 目录侧技能名清单
ls -d skills/*/ | xargs -n1 basename | sort > /tmp/dirs.txt
# README 侧按清单格式提取技能名后，与目录侧 diff
```

README 的清单格式可能随时间变化，提取规则以当前文件实际结构为准；提取不出时退回人工逐条核对，并在报告里注明。

## 要点

- 同步是 P1 问题：README 是给人看的入口，漂移会直接误导安装和使用。
- 修复完同步问题后，README 里新增条目的描述若与技能 description 能力层措辞不一致，以技能侧为准再顺一遍。
- AGENTS.md 中的清单描述同样需要核对，规则同 README。
