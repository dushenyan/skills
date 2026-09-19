#!/usr/bin/env python3
"""校验生成的教程是否满足协作必需的基础格式（宽松版）。

用法：
    python3 check_tutorial.py <教程目录或单个 .md 文件>

只检查影响协作与阅读的机械项：

1. 文件命名：`<序号>-<中文标题>.md`，序号连续、不重复（ERROR）。
2. 代码块：围栏闭合（ERROR）；语言标注缺失只提醒（WARN）。
3. 章末「下一站建议」：除最后一章外建议都有（WARN，不阻断）。

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

    stats = {"has_next_stop": False}

    in_code = False
    fence_char = ""
    fence_open_line = 0

    for i, raw in enumerate(text.splitlines(), start=1):
        fence = FENCE_RE.match(raw)

        if fence:
            char, info = fence.group(1), fence.group(2).strip()
            if not in_code:
                in_code = True
                fence_char = char
                fence_open_line = i
                if not info:
                    report.warn(rel, f"第 {i} 行：代码块缺少语言标注（```python / ```bash ...）")
            elif char == fence_char and not info:
                # 按 CommonMark，闭合围栏不能带 info string。
                # 带 info string 的围栏即使出现在代码块内，也只是代码内容。
                in_code = False
            continue

        if in_code:
            continue

        if "下一站建议" in raw:
            stats["has_next_stop"] = True

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
