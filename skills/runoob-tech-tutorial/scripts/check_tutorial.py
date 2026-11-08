#!/usr/bin/env python3
"""校验生成的教程是否满足协作必需的基础格式（宽松版）。

用法：
    python3 check_tutorial.py <教程目录或单个 .md 文件>

只检查影响协作与阅读的机械项：

1. 文件命名：`<序号>-<中文标题>.md`，序号连续、不重复（ERROR）。
2. 代码块：围栏闭合（ERROR）；语言标注缺失只提醒（WARN）。
3. 章末「下一站建议」：除最后一章外建议都有（WARN，不阻断）。
4. 重点标注覆盖度：每章建议出现 `> 学习重点 ⭐` 与 `> 注意`（WARN，不阻断）。
5. `_meta.yaml` 目录树清单：建议存在，且节点与实际文件/目录一致、UUID 不重复（WARN，不阻断）。
6. 命令占位符：`bash` / `sh` 代码块里出现独立 `...` 或 `xxx` 时提醒（WARN，不阻断）。

标点、字间距、句长、语气、分割线、配图覆盖等写作风格一律不查：
这些交给写作时的判断，不在校验范围内。

退出码：有 ERROR 时为 1，否则为 0。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
FENCE_RE = re.compile(r"^\s*(```|~~~)(.*)$")
# 章节文件：<序号>-<标题>.md
CHAPTER_RE = re.compile(r"^(\d+)-(.+)\.md$")
# 只在这些 shell 类代码块里查占位符，避免误伤 SQL 的 `...` 与 Python 的 Ellipsis
SHELL_LANGS = {"bash", "sh", "shell", "zsh"}
# 独立出现的三点或 xxx 才算占位，`../data`、`a...b` 不匹配
PLACEHOLDER_ELLIPSIS_RE = re.compile(r"(?:^|\s)\.\.\.(?:\s|$)")
PLACEHOLDER_XXX_RE = re.compile(r"(?:^|\s)xxx(?:\s|$)", re.IGNORECASE)
# _meta.yaml 节点：- name: xxx（顶层 name: xxx 不带列表符，不匹配）
META_NAME_RE = re.compile(r"^\s*-\s+name:\s*(.+?)\s*$")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def chapter_files(paths: list[Path]) -> list[Path]:
    """筛出章节文件：排除 README，按序号排序。"""
    numbered = [(int(m.group(1)), p) for p in paths if (m := CHAPTER_RE.match(p.name))]
    numbered.sort(key=lambda x: x[0])
    return [p for _, p in numbered]


def scan_file(path: Path, report: Report) -> dict:
    """逐行扫描单个文件，返回供全局统计用的信息。"""
    text = path.read_text(encoding="utf-8")
    rel = str(path)

    stats = {"has_next_stop": False, "has_key_point": False, "has_caution": False}

    in_code = False
    fence_char = ""
    code_lang = ""
    fence_open_line = 0

    for i, raw in enumerate(text.splitlines(), start=1):
        fence = FENCE_RE.match(raw)

        if fence:
            char, info = fence.group(1), fence.group(2).strip()
            if not in_code:
                in_code = True
                fence_char = char
                code_lang = info.split()[0].lower() if info else ""
                fence_open_line = i
                if not info:
                    report.warn(rel, f"第 {i} 行：代码块缺少语言标注（```python / ```bash ...）")
            elif char == fence_char and not info:
                # 按 CommonMark，闭合围栏不能带 info string。
                # 带 info string 的围栏即使出现在代码块内，也只是代码内容。
                in_code = False
                code_lang = ""
            continue

        if in_code:
            # 注释里的省略号是说明文字，不算命令占位；只查真正会执行的行
            if (
                code_lang in SHELL_LANGS
                and not raw.lstrip().startswith("#")
                and (
                    PLACEHOLDER_ELLIPSIS_RE.search(raw)
                    or PLACEHOLDER_XXX_RE.search(raw)
                )
            ):
                report.warn(
                    rel,
                    f"第 {i} 行：命令含占位符，请写成完整可执行版本（不要用 `...` / `xxx`）",
                )
            continue

        if "下一站建议" in raw:
            stats["has_next_stop"] = True

        if "学习重点" in raw and "⭐" in raw:
            stats["has_key_point"] = True

        if "**注意**" in raw or "**踩坑提醒**" in raw:
            stats["has_caution"] = True

    if in_code:
        report.error(rel, f"第 {fence_open_line} 行：代码块未闭合")

    return stats


def check_names(paths: list[Path], report: Report) -> None:
    """检查文件命名：中文标题 + 序号连续。"""
    numbered: list[tuple[int, Path]] = []

    for p in paths:
        if p.name == "README.md":
            continue
        m = re.match(r"^(\d+)-(.+)\.md$", p.name)
        if not m:
            report.error(str(p), "文件名不符合 `<序号>-<中文标题>.md` 格式")
            continue
        title = m.group(2)
        if not CJK_RE.search(title):
            report.error(str(p), f"文件名缺少中文标题：「{title}」")
        numbered.append((int(m.group(1)), p))

    if not numbered:
        return

    numbered.sort(key=lambda x: x[0])
    seen: dict[int, Path] = {}
    for num, p in numbered:
        if num in seen:
            report.error(str(p), f"序号 {num} 与 {seen[num]} 重复")
        seen[num] = p

    nums = sorted(seen)
    expected = list(range(1, len(nums) + 1))
    if nums != expected:
        missing = sorted(set(expected) - set(nums))
        report.error(
            "章节目录",
            f"序号不连续，期望 1~{len(nums)}，实际 {nums}"
            + (f"，缺失 {missing}" if missing else ""),
        )


def check_next_stop(paths: list[Path], flags: dict, report: Report) -> None:
    """除最后一章外，每章都应有"下一站建议"（仅提醒）。"""
    chapters = chapter_files(paths)
    if len(chapters) < 2:
        return
    for p in chapters[:-1]:
        if not flags[str(p)]["has_next_stop"]:
            report.warn(str(p), "缺少章末「下一站建议」引用块（协作导航用，建议补上）")


def check_highlights(paths: list[Path], flags: dict, report: Report) -> None:
    """每个章节文件都建议至少一处「学习重点 ⭐」与一处「注意 / 踩坑提醒」（仅提醒）。

    参考资源、README 这类纯链接章自动跳过；其它章没命中时给 WARN，让作者回到
    该章把常见 / 易错点显式标注一下，不阻断交付。
    """
    for p in chapter_files(paths):
        if "参考资源" in p.name or "资源" in p.name:
            continue
        f = flags[str(p)]
        if not f["has_key_point"]:
            report.warn(str(p), "未出现 `> 学习重点 ⭐`：核心概念建议显式标注一下")
        if not f["has_caution"]:
            report.warn(str(p), "未出现 `> 注意` 或 `> **踩坑提醒**`：建议补一个易错点")


def check_meta_yaml(target: Path, report: Report) -> None:
    """校验教程根目录的 _meta.yaml 目录树清单（仅提醒，不阻断）。

    规范见 references/tutorial-structure.md 第五节第 4 小节：文件节点带不重复
    UUID，目录节点以 children 嵌套。这里只兜底机械项：存在性、节点覆盖、
    UUID 格式与去重；层级顺序不做深校验。
    """
    meta = target / "_meta.yaml"
    if not meta.exists():
        report.warn(str(meta), "教程根目录缺少 `_meta.yaml` 目录树清单（知识库导航依赖，建议补上）")
        return

    meta_names: set[str] = set()
    ids: list[str] = []
    pending_name = False
    for raw in meta.read_text(encoding="utf-8").splitlines():
        if m := META_NAME_RE.match(raw):
            meta_names.add(m.group(1))
            pending_name = True
            continue
        if pending_name and raw.strip().startswith("id:"):
            ids.append(raw.split(":", 1)[1].strip())
        pending_name = False

    for uid in ids:
        if not UUID_RE.match(uid):
            report.warn(str(meta), f"UUID 格式不合法：{uid}")
    if len(ids) != len(set(ids)):
        report.warn(str(meta), "存在重复 UUID，每个文件节点应独立生成")

    actual = {p.name for p in target.rglob("*.md")}
    actual |= {p.name for p in target.iterdir() if p.is_dir()}
    if missing := sorted(actual - meta_names):
        report.warn(str(meta), f"目录树缺少节点：{'、'.join(missing)}")
    if extra := sorted(meta_names - actual):
        # 根节点 name 不带列表符不会进 meta_names，这里只可能是不再存在的文件/目录节点
        report.warn(str(meta), f"目录树存在实际不存在的节点：{'、'.join(extra)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验教程目录的协作格式（宽松版）")
    parser.add_argument("target", help="教程目录或单个 .md 文件")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        print(f"路径不存在：{target}", file=sys.stderr)
        return 2

    paths = [target] if target.is_file() else sorted(target.rglob("*.md"))
    if not paths:
        print(f"没有找到 .md 文件：{target}", file=sys.stderr)
        return 2

    report = Report()
    flags: dict[str, dict] = {}
    for p in paths:
        flags[str(p)] = scan_file(p, report)

    check_names(paths, report)
    check_next_stop(paths, flags, report)
    check_highlights(paths, flags, report)
    if target.is_dir():
        check_meta_yaml(target, report)

    shown = [p for p in paths if p.name != "README.md"]
    print(f"检查文件：{len(paths)} 个（其中章节文件 {len(shown)} 个）")
    print(f"ERROR {len(report.errors)} 项，WARN {len(report.warnings)} 项\n")

    if report.errors:
        print("== ERROR ==")
        for msg in report.errors:
            print(f"  ✗ {msg}")
        print()
    if report.warnings:
        print("== WARN ==")
        for msg in report.warnings:
            print(f"  ! {msg}")
        print()

    if not report.errors and not report.warnings:
        print("协作格式检查全部通过。")

    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
