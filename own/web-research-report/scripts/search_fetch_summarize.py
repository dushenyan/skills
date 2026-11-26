#!/usr/bin/env python3
"""Download remote URLs and extract readable text into an evidence pack.

Search is deliberately NOT built in: use the runtime's native web search
(the same approach as baoyu-skills), then pass the chosen URLs here with --url.

Standard library only. Outputs: search.json, summary.md, pages/*.txt in --out-dir.

Typical use:
    python3 scripts/search_fetch_summarize.py \
        --url "https://example.com/article" \
        --out-dir research-output
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

USER_AGENT = "research-script/1.0 (+https://example.org/bot)"
REQUEST_TIMEOUT = 20
MAX_TEXT_CHARS = 12000
MIN_TEXT_CHARS = 200


class TextExtractor(HTMLParser):
    """Extract readable text while skipping script/style/nav-like blocks."""

    SKIP_TAGS = {"script", "style", "nav", "footer", "header", "form", "svg", "noscript"}
    BLOCK_TAGS = {"p", "div", "section", "article", "li", "h1", "h2", "h3", "h4", "tr", "br"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        elif tag in self.BLOCK_TAGS and not self.skip_depth:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif tag in self.BLOCK_TAGS and not self.skip_depth:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts).replace("\xa0", " ")
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


def request(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def normalize_url(url: str) -> str:
    """Strip tracking params and fragments so duplicates collapse."""
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    dropped = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
    kept = [(k, v) for k, v in query if k.lower() not in dropped]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(kept), ""))


def source_score(url: str) -> int:
    """Heuristic source quality. Higher is more likely to be a primary source."""
    host = urllib.parse.urlsplit(url).netloc.lower()
    if re.search(r"(arxiv\.org|rfc-editor\.org|github\.com|gov$|\.gov\.|doi\.org|nature\.com|science\.org)", host):
        return 3
    if re.search(r"(w3\.org|microsoft\.com|anthropic\.com|openai\.com|google\.com|mdn\.|developer\.)", host):
        return 3
    if re.search(r"(platform\.claude\.com|code\.claude\.com|docs\.anthropic\.com)", host):
        return 3
    if re.search(r"(medium\.com|blog\.|news\.|techcrunch\.com|theverge\.com|infoq\.com)", host):
        return 2
    if re.search(r"(pinterest|quora|zhihu|csdn|jianshu|51cto|blogspot)", host):
        return 1
    return 2


def dedupe(results: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    output: list[dict[str, str]] = []
    for item in results:
        key = hashlib.sha256(re.sub(r"\W+", "", item["title"].lower()).encode()).hexdigest()
        url_key = item["url"].rstrip("/")
        if not item["url"].startswith("http") or key in seen or url_key in seen:
            continue
        seen.add(key)
        seen.add(url_key)
        item["source_score"] = source_score(item["url"])
        output.append(item)
    return output


def fetch_page(url: str) -> str:
    raw = request(url)
    match = re.search(r"<meta[^>]+charset=[\"']?([\w-]+)", raw, re.I)
    if match:
        try:
            raw = raw.encode("latin-1", errors="replace").decode(match.group(1), errors="replace")
        except LookupError:
            pass
    parser = TextExtractor()
    parser.feed(raw)
    return parser.text()[:MAX_TEXT_CHARS]


def summarize(text: str, max_sentences: int = 3) -> str:
    sentences = re.split(r"(?<=[。！？.!?])\s+", text)
    picked: list[str] = []
    for sentence in sentences:
        clean = sentence.strip().replace("\n", " ")
        if MIN_TEXT_CHARS > len(clean) > 40:
            picked.append(clean)
        if len(picked) >= max_sentences:
            break
    if not picked:
        picked = [line.strip() for line in text.splitlines() if len(line.strip()) > 30][:max_sentences]
    return " ".join(picked) or "（未提取到足够正文）"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", action="append", required=True, help="Remote URL to download; repeat for multiple URLs")
    ap.add_argument("--out-dir", type=Path, default=Path("research-output"))
    args = ap.parse_args()

    results = dedupe([
        {
            "title": urllib.parse.urlsplit(url).netloc or url,
            "url": normalize_url(url),
            "snippet": "Direct URL input",
        }
        for url in args.url
    ])

    args.out_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = args.out_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    fetched = 0
    for item in results:
        try:
            text = fetch_page(item["url"])
            if len(text) < MIN_TEXT_CHARS:
                item["fetch_status"] = "too_short"
                continue
            fname = hashlib.sha256(item["url"].encode()).hexdigest()[:12] + ".txt"
            (pages_dir / fname).write_text(text, encoding="utf-8")
            item["page_file"] = f"pages/{fname}"
            item["summary"] = summarize(text)
            item["fetch_status"] = "ok"
            fetched += 1
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            item["fetch_status"] = f"error: {exc}"

    (args.out_dir / "search.json").write_text(
        json.dumps({"urls": args.url, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [f"# 远程资料初筛：{', '.join(args.url)}", ""]
    for i, item in enumerate(results, 1):
        lines.extend([
            f"## {i}. {item['title']}",
            "",
            f"- URL: {item['url']}",
            f"- 来源评分: {item['source_score']} | 抓取状态: {item.get('fetch_status', 'not_fetched')}",
            f"- 摘要: {item.get('summary', item['snippet'])}",
            "",
        ])
    (args.out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"urls={len(args.url)} fetched={fetched} out={args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
