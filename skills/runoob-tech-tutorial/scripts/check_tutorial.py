#!/usr/bin/env python3
"""校验生成的菜鸟风格教程是否符合机械性规范。

用法：
    python3 check_tutorial.py <教程目录或单个 .md 文件>

检查分两组：

1. 教程硬性机械项：分割线、章末指引、配图覆盖、代码块语言标注、文件名与序号。
2. 文字规范提示：标点、字间距、长句、标题层级、被动语态、容易出戏的腔调等。

第 2 组以提醒为目的，多数规则是 WARN 级；只有明确违反中文标点与标题层级的
部分才记 ERROR。语气是否自然、类比是否贴切、指代是否明确、的/地/得是否用对，
脚本判定不了，也不需要为它们反复改稿，写的时候顺手留意即可
（参考 references/narrative-style.md）。

退出码：有 ERROR 时为 1，否则为 0。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CJK = r"\u4e00-\u9fff"
CJK_RE = re.compile(f"[{CJK}]")

# 容易出戏的腔调（见 references/narrative-style.md 第二节），只报 WARN，不阻断交付
BANNED = [
    "综上所述", "由此可见", "总而言之", "本文将详细介绍",
    "作为一个", "所谓",
    "值得我们注意的是", "需要特别强调的是",
    "本教程将带领", "小伙伴们", "老铁们",
    "非常重要！！！", "必看！！！",
]

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

# ------------------------------------------------------------------ 阮一峰规范
# 规则出处：阮一峰《中文技术文档的写作规范》
# https://github.com/ruanyf/document-style-guide
# 只收录能客观判定的条目；每条规则在每个文件里同一行最多报一次，避免刷屏。

# 规则名 -> (级别, 规范章节)
NORM_RULES: dict[str, tuple[str, str]] = {
    # ---- ERROR：明确违反规范 ----
    "正文半角标点": ("error", "标点·原则"),
    "全角数字": ("error", "数值·半角数字"),
    "感叹号连用": ("error", "标点·感叹号"),
    "省略号写法": ("error", "标点·省略号"),
    "括号内句号": ("error", "标点·句号"),
    "标题末尾点号": ("error", "标点·原则"),
    "标题跳级": ("error", "标题·原则"),
    # ---- WARN：提示为主，不阻断交付 ----
    "英数字与全角标点间空格": ("warn", "文本·字间距"),
    "句子过长": ("warn", "文本·句子"),
    "中英之间缺空格": ("warn", "文本·字间距"),
    "数字间距不统一": ("warn", "文本·字间距"),
    "千分号": ("warn", "数值·千分号"),
    "正文感叹号": ("warn", "标点·感叹号"),
    "省略号与等连用": ("warn", "标点·省略号"),
    "句长偏长": ("warn", "文本·句子"),
    "逗号长句过长": ("warn", "文本·句子"),
    "被动语态": ("warn", "文本·写作风格"),
    "父子标题同名": ("warn", "标题·原则"),
    "段落过长": ("warn", "段落·原则"),
}

# 正文里不允许出现的半角标点（紧邻中文时）
HALF_PUNCT = re.compile(f"(?:[{CJK}][,;:!?()]|[,;:!?][{CJK}])")

FULLWIDTH_DIGIT_RE = re.compile(r"[０-９]")
ELLIPSIS_RE = re.compile(r"\.{3,}|。。。")
ELLIPSIS_WITH_DENG_RE = re.compile(r"(?:⋯⋯|…|\.{3,})\s*等")
EXCLAIM_RUN_RE = re.compile(r"[！!]{2,}")
EXCLAIM_RE = re.compile(r"[！!]")
PAREN_PERIOD_RE = re.compile(r"（[^）]{0,60}。）")
PASSIVE_RE = re.compile(f"被(?!动)[{CJK}a-z]{{1,4}}")
CJK_LATIN_RE = re.compile(f"(?:[{CJK}][A-Za-z]|[A-Za-z][{CJK}])")
FULLWIDTH_PUNCT = "，。：；！？、（）“”‘’《》"
SPACE_AROUND_PUNCT_RE = re.compile(
    f"(?:[A-Za-z0-9] +[{FULLWIDTH_PUNCT}]|[{FULLWIDTH_PUNCT}] +[A-Za-z0-9])",
)
DIGIT_TIGHT_RE = re.compile(f"\\d[{CJK}]")
DIGIT_SPACED_RE = re.compile(f"\\d [{CJK}]")
THOUSAND_RE = re.compile(r"(?<![\d,.])\d{5,}(?![\d,.])")
SENTENCE_SPLIT_RE = re.compile(r"[。！？；]")
CLAUSE_SPLIT_RE = re.compile(r"[，、]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BLOCK_ITEM_RE = re.compile(r"(?:[-*+]\s+|\d+\.\s+|>|\|)")
TITLE_TAIL_PUNCT = "，。、；：,.;:"

# 句子长度阈值（阮一峰：20 字以内最好，20~29 可接受，30~39 需语义明确，40 以上不可接受）
CLAUSE_LIMIT = 40
CLAUSE_SUGGEST = 30
COMMA_SENTENCE_LIMIT = 100
# 段落长度上限（阮一峰：不能超过七行，最佳小于等于四行）
MAX_PARA_LINES = 7
# 每条规则最多展示的样例数
NORM_SAMPLE_LIMIT = 3


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        # 规则名 -> [(位置, 说明), ...]
        self.norms: dict[str, list[tuple[str, str]]] = {}

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")

    def norm(self, rule: str, where: str, detail: str) -> None:
        """记一条阮一峰规范命中项；同一规则同一行只记一次。"""
        bucket = self.norms.setdefault(rule, [])
        if any(item_where == where for item_where, _ in bucket):
            return
        bucket.append((where, detail))

    def norm_errors(self) -> set[str]:
        return {
            rule
            for rule, (level, _) in NORM_RULES.items()
            if level == "error" and self.norms.get(rule)
        }


def snippet(text: str, start: int, end: int, width: int = 10) -> str:
    """截取命中处上下文，方便定位。"""
    return text[max(0, start - width):min(len(text), end + width)].strip()


def strip_non_prose(line: str) -> str:
    """去掉行内代码、链接目标、URL 与占位符，只留下需要检查标点的正文。"""
    line = MD_LINK_RE.sub(r"\1", line)
    line = URL_RE.sub("", line)
    line = INLINE_CODE_RE.sub("", line)
    line = PLACEHOLDER_RE.sub("", line)
    return line


def strip_for_spacing(line: str) -> str:
    """字间距检查用：连链接文字一起去掉，避免文件名式的链接文字误报。"""
    line = MD_LINK_RE.sub("", line)
    line = URL_RE.sub("", line)
    line = INLINE_CODE_RE.sub("", line)
    line = PLACEHOLDER_RE.sub("", line)
    return line


def check_line_norms(rel: str, lineno: int, raw: str, report: Report) -> None:
    """逐行的阮一峰规范机械项。"""
    if TABLE_SEP_RE.match(raw):
        return

    where = f"{rel}:{lineno}"
    prose = strip_non_prose(raw)
    spacing = strip_for_spacing(raw)

    # 标点·原则：中文语句一律全角标点
    if hit := HALF_PUNCT.search(prose):
        report.norm(
            "正文半角标点",
            where,
            f"正文出现半角标点 `{hit.group()}`，应改用全角（，；：！？（）） → {prose.strip()[:50]}",
        )

    # 数值·半角数字
    if m := FULLWIDTH_DIGIT_RE.search(prose):
        report.norm("全角数字", where, f"「{snippet(prose, m.start(), m.end())}」应改用半角数字")

    # 标点·感叹号：不得连用，尽量不用
    if EXCLAIM_RUN_RE.search(prose):
        report.norm("感叹号连用", where, "感叹号不得连用（`！！`、`!!!`），改成平静语气")
    elif m := EXCLAIM_RE.search(prose):
        report.norm(
            "正文感叹号",
            where,
            f"正文出现感叹号：「{snippet(prose, m.start(), m.end())}」，尽量改为陈述语气",
        )

    # 标点·省略号
    if m := ELLIPSIS_RE.search(prose):
        report.norm("省略号写法", where, f"「{m.group()}」不是规范省略号，中文应写作「⋯⋯」")
    if m := ELLIPSIS_WITH_DENG_RE.search(prose):
        report.norm("省略号与等连用", where, f"「{m.group()}」中省略号与「等」重复，留一个即可")

    # 标点·句号：括号加注时句号在括号之外
    if m := PAREN_PERIOD_RE.search(prose):
        report.norm("括号内句号", where, f"句号应写在括号外：「{m.group()}」")

    # 文本·字间距：半角英数字与全角标点之间不留空格
    if m := SPACE_AROUND_PUNCT_RE.search(spacing):
        report.norm(
            "英数字与全角标点间空格",
            where,
            f"「{snippet(spacing, m.start(), m.end())}」中英数字与全角标点之间不留空格",
        )

    # 文本·字间距：中文与半角英文之间应有一个半角空格
    if m := CJK_LATIN_RE.search(spacing):
        pair = m.group()
        report.norm(
            "中英之间缺空格",
            where,
            f"「{pair}」→「{pair[0]} {pair[1]}」，中文与半角英文之间应有一个半角空格",
        )

    # 数值·千分号
    if m := THOUSAND_RE.search(prose):
        report.norm("千分号", where, f"「{m.group()}」超过千位，应写成「{int(m.group()):,}」")

    # 文本·写作风格：尽量用主动语态
    if m := PASSIVE_RE.search(prose):
        report.norm("被动语态", where, f"「{m.group()}」建议改为主动语态")

    # 文本·句子：构件长度与逗号长句
    for sentence in SENTENCE_SPLIT_RE.split(prose):
        for clause in CLAUSE_SPLIT_RE.split(sentence):
            compact = re.sub(r"\s+", "", clause)
            if not CJK_RE.search(compact):
                continue
            length = len(compact)
            if length > CLAUSE_LIMIT:
                report.norm(
                    "句子过长",
                    where,
                    f"{length} 字的句子构件超过 {CLAUSE_LIMIT} 字上限，必须拆句：{compact[:25]}…",
                )
                break
            if length >= CLAUSE_SUGGEST:
                report.norm(
                    "句长偏长",
                    where,
                    f"{length} 字的句子构件偏长（建议 {CLAUSE_SUGGEST} 字以内）：{compact[:25]}…",
                )
        plain_sentence = re.sub(r"\s+", "", sentence)
        if len(plain_sentence) > COMMA_SENTENCE_LIMIT:
            report.norm(
                "逗号长句过长",
                where,
                f"逗号长句共 {len(plain_sentence)} 字，超过 {COMMA_SENTENCE_LIMIT} 字上限",
            )


def check_heading_norms(rel: str, headings: list[tuple[int, str, int]], report: Report) -> None:
    """标题层级相关的阮一峰规范。"""
    prev_level = 0
    ancestors: list[tuple[int, str]] = []

    for level, text, lineno in headings:
        where = f"{rel}:{lineno}"

        if prev_level and level > prev_level + 1:
            report.norm(
                "标题跳级",
                where,
                f"「{'#' * prev_level}」下直接出现「{'#' * level}」，中间缺了一级标题",
            )
        if text and text[-1] in TITLE_TAIL_PUNCT:
            report.norm("标题末尾点号", where, f"标题「{text}」末尾不应出现点号")

        while ancestors and ancestors[-1][0] >= level:
            ancestors.pop()
        if ancestors and ancestors[-1][1] == text:
            report.norm("父子标题同名", where, f"「{text}」与上一级标题同名，换个说法更清楚")

        ancestors.append((level, text))
        prev_level = level


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
    headings: list[tuple[int, str, int]] = []
    prose_lines: list[str] = []

    in_code = False
    fence_char = ""
    fence_open_line = 0
    dividers = 0
    para_len = 0

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

        if not stripped:
            para_len = 0
            continue

        # 分割线（只算独立的 ---）
        if re.fullmatch(r"-{3,}", stripped):
            dividers += 1
            report.warn(rel, f"第 {i} 行：出现分割线 `---`，确认是否真的需要视觉断点")
            para_len = 0
            continue

        # 段落长度（阮一峰：不超过七行）
        if stripped.startswith("#"):
            stats["headings"] += 1
            if m := HEADING_RE.match(stripped):
                headings.append((len(m.group(1)), m.group(2), i))
            para_len = 0
        elif BLOCK_ITEM_RE.match(stripped):
            # 列表、引用块、表格各自成块，不与上下正文算同一段
            para_len = 0
        else:
            para_len = para_len + 1 if para_len else 1
            if para_len == MAX_PARA_LINES + 1:
                report.norm(
                    "段落过长",
                    f"{rel}:{i - MAX_PARA_LINES}",
                    f"该段落超过 {MAX_PARA_LINES} 行（最佳 {MAX_PARA_LINES - 3} 行以内），拆成几段更好读",
                )

        # 章末"下一站建议"
        if "下一站建议" in raw:
            stats["has_next_stop"] = True

        # 配图建议
        if "配图建议" in raw:
            stats["has_illustration"] = True

        # 类比
        if "类比理解" in raw:
            stats["has_analogy"] = True

        # 容易出戏的腔调（提示级，不必为此回扫全文）
        for word in BANNED:
            if word in raw:
                report.warn(rel, f"第 {i} 行：出现容易出戏的腔调「{word}」，建议换个说法")

        # 阮一峰规范的逐行机械项
        check_line_norms(rel, i, raw, report)
        prose_lines.append(strip_non_prose(raw))

    if in_code:
        report.error(rel, f"第 {fence_open_line} 行：代码块未闭合")

    # 分割线上限按「单篇文档」判定（见 references/formatting.md 第一节）
    if dividers > 2:
        report.error(rel, f"分割线 `---` 共 {dividers} 处，单篇文档上限为 2 处")

    # 与中文相邻的数字：加不加空格必须全文统一
    tight = [m.group() for line in prose_lines if (m := DIGIT_TIGHT_RE.search(line))]
    spaced = [m.group() for line in prose_lines if (m := DIGIT_SPACED_RE.search(line))]
    if tight and spaced:
        report.norm(
            "数字间距不统一",
            rel,
            f"同一文档里既有「{tight[0]}」也有「{spaced[0]}」，与中文相邻的数字要么全部加空格，要么全不加",
        )

    check_heading_norms(rel, headings, report)

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


def print_norms(report: Report) -> None:
    """按规则聚合输出阮一峰规范的检查结果。"""
    if not report.norms:
        return

    print("== 文字规范提示（参考，不阻断交付） ==")
    for rule, (level, source) in NORM_RULES.items():
        hits = report.norms.get(rule)
        if not hits:
            continue
        mark = "✗" if level == "error" else "!"
        print(f"  {mark} {rule}（{source}） {len(hits)} 处")
        for where, detail in hits[:NORM_SAMPLE_LIMIT]:
            print(f"      {where}  {detail}")
        if len(hits) > NORM_SAMPLE_LIMIT:
            print(f"      …另有 {len(hits) - NORM_SAMPLE_LIMIT} 处")
    print()


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

    norm_total = sum(len(hits) for hits in report.norms.values())
    shown = [p for p in paths if p.name != "README.md"]
    print(f"检查文件：{len(paths)} 个（其中章节文件 {len(shown)} 个）")
    print(
        f"ERROR {len(report.errors)} 项，WARN {len(report.warnings)} 项，"
        f"文字规范提示 {norm_total} 处（{len(report.norms)} 类，"
        f"其中 {len(report.norm_errors())} 类需修正）\n",
    )

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

    print_norms(report)

    if not report.errors and not report.warnings and not report.norms:
        print("机械项全部通过。")
    if report.norms:
        print("以上只是提醒；语气是否自然、类比是否贴切，写的时候留意即可，")
        print("不必为这些提示反复改稿。参考 references/narrative-style.md。")

    return 1 if report.errors or report.norm_errors() else 0


if __name__ == "__main__":
    sys.exit(main())
