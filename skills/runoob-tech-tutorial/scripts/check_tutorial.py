#!/usr/bin/env python3
"""校验生成的菜鸟风格教程是否符合机械性规范。

用法：
    python3 check_tutorial.py <教程目录或单个 .md 文件>

只检查能客观判定的项目（标点、分割线、禁用词、章末指引、配图覆盖、
代码块语言标注、文件名）。风格是否到位、类比是否贴切，仍需人工对照
references/narrative-style.md 的自检清单。

退出码：有 ERROR 时为 1，否则为 0。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CJK = r"\u4e00-\u9fff"
CJK_RE = re.compile(f"[{CJK}]")

# 禁用写法清单（见 references/narrative-style.md 第二节）
BANNED = [
    "综上所述", "由此可见", "总而言之", "本文将详细介绍",
    "作为一个", "所谓",
    "值得我们注意的是", "需要特别强调的是",
    "本教程将带领", "小伙伴们", "老铁们",
    "非常重要！！！", "必看！！！",
]

# 正文里不允许出现的半角标点（紧邻中文时）
HALF_PUNCT = re.compile(f"(?:[{CJK}][,;:!?()]|[,;:!?][{CJK}])")

FENCE_RE = re.compile(r"^\s*(```|~~~)(.*)$")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
URL_RE = re.compile(r"https?://\S+")
TABLE_SEP_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
# 占位符写法（如 {维度下标: 权重}），内部按代码习惯用半角标点，不算违规
PLACEHOLDER_RE = re.compile(r"\{[^{}]*\}")
# Markdown 链接：[文字](目标) → 只保留文字，链接目标里的标点不参与检查
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
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


def strip_non_prose(line: str) -> str:
    """去掉行内代码、链接目标、URL 与占位符，只留下需要检查标点的正文。"""
    line = MD_LINK_RE.sub(r"\1", line)
    line = URL_RE.sub("", line)
    line = INLINE_CODE_RE.sub("", line)
    line = PLACEHOLDER_RE.sub("", line)
    return line


def chapter_files(paths: list[Path]) -> list[Path]:
    """筛出章节文件：排除 README，按序号排序。"""
    numbered = [(int(m.group(1)), p) for p in paths if (m := CHAPTER_RE.match(p.name))]
    numbered.sort(key=lambda x: x[0])
    return [p for _, p in numbered]


def scan_file(path: Path, report: Report) -> dict:
    """逐行扫描单个文件，返回供全局统计用的信息。"""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    rel = str(path)

    stats = {
        "has_next_stop": False,
        "has_illustration": False,
        "has_analogy": False,
        "headings": 0,
    }

    in_code = False
    fence_char = ""
    fence_open_line = 0
    dividers = 0

    for i, raw in enumerate(lines, start=1):
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

        stripped = raw.strip()

        # 分割线（只算独立的 ---）
        if re.fullmatch(r"-{3,}", stripped):
            dividers += 1
            report.warn(rel, f"第 {i} 行：出现分割线 `---`，确认是否真的需要视觉断点")
            continue

        if stripped.startswith("#"):
            stats["headings"] += 1

        # 章末"下一站建议"
        if "下一站建议" in raw:
            stats["has_next_stop"] = True

        # 配图建议
        if "配图建议" in raw:
            stats["has_illustration"] = True

        # 类比
        if "类比理解" in raw:
            stats["has_analogy"] = True

        # 禁用写法
        for word in BANNED:
            if word in raw:
                report.error(rel, f"第 {i} 行：出现禁用写法「{word}」")

        # 中文夹半角标点
        if TABLE_SEP_RE.match(raw):
            continue
        prose = strip_non_prose(raw)
        hit = HALF_PUNCT.search(prose)
        if hit:
            report.error(
                rel,
                f"第 {i} 行：正文出现半角标点 `{hit.group()}`，应改用全角（，；：！？（）） → {stripped[:60]}",
            )

    if in_code:
        report.error(rel, f"第 {fence_open_line} 行：代码块未闭合")

    # 分割线上限按「单篇文档」判定（见 references/formatting.md 第一节）
    if dividers > 2:
        report.error(rel, f"分割线 `---` 共 {dividers} 处，单篇文档上限为 2 处")

    stats["dividers"] = dividers
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


def check_illustration_coverage(paths: list[Path], flags: dict, report: Report) -> None:
    """配图建议：每 2~3 章至少 1 处，即连续未配图的章节不超过 3 章。"""
    chapters = chapter_files(paths)
    if not chapters:
        return

    gap: list[Path] = []
    reported = False
    for p in chapters:
        if flags[str(p)]["has_illustration"]:
            gap, reported = [], False
            continue
        gap.append(p)
        if len(gap) >= 4 and not reported:
            report.error(
                "配图建议",
                "连续 %d 章没有配图建议：%s" % (len(gap), "、".join(q.name for q in gap)),
            )
            reported = True

    if gap and not reported:
        report.warn(
            "配图建议",
            "结尾连续 %d 章没有配图建议：%s" % (len(gap), "、".join(q.name for q in gap)),
        )


def check_next_stop(paths: list[Path], flags: dict, report: Report) -> None:
    """除最后一章外，每章都应有"下一站建议"。"""
    chapters = chapter_files(paths)
    if len(chapters) < 2:
        return
    for p in chapters[:-1]:
        if not flags[str(p)]["has_next_stop"]:
            report.error(str(p), "缺少章末「下一站建议」引用块")


def check_header_reference(paths: list[Path], report: Report) -> None:
    """禁止在文件开头加"参考来源"引用行。"""
    for p in paths:
        head = p.read_text(encoding="utf-8").splitlines()[:6]
        for line in head:
            if re.match(r"^>\s*(参考|参考来源|Reference)", line.strip(), re.IGNORECASE):
                report.error(str(p), "文件开头出现「参考来源」引用行，应删掉并统一放到最后一章")
                break


def main() -> int:
    parser = argparse.ArgumentParser(description="校验菜鸟风格教程的机械性规范")
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
    check_illustration_coverage(paths, flags, report)
    check_header_reference(paths, report)

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
        print("机械项全部通过。风格与类比质量请对照 references/narrative-style.md 自检清单过一遍。")

    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
