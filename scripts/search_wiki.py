"""在 content/wiki/ 中检索关键词，返回带片段的结果，供 RAG 问答取证据（SOURCES）。

用法：
    python scripts/search_wiki.py --query "Agent Loop" --top 5
输出 JSON：[{file, title, score, snippet}, ...]（按相关度倒序）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

from site_common import PROJECT_ROOT
from build_blog import parse_frontmatter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WIKI_SRC = PROJECT_ROOT / "content" / "wiki"


def clean_snippet(line):
    text = re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]", r"\2", line)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[#>*`]", "", text)
    return " ".join(text.split())[:160]


def load_wiki():
    pages = []
    for path in sorted(WIKI_SRC.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        pages.append({
            "file": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "title": meta.get("title", path.stem),
            "body": body,
        })
    return pages


def search(query, top):
    terms = [t for t in query.split() if t]
    if not terms:
        return []
    results = []
    for page in load_wiki():
        title = page["title"]
        body = page["body"]
        title_hits = sum(title.lower().count(t.lower()) for t in terms)
        body_hits = sum(body.lower().count(t.lower()) for t in terms)
        if title_hits + body_hits == 0:
            continue
        score = title_hits * 5 + body_hits
        if query.strip().lower() in body.lower():
            score += 10  # 整句命中加权
        snippet = ""
        for line in body.splitlines():
            line_s = line.strip()
            if any(t.lower() in line_s.lower() for t in terms):
                snippet = clean_snippet(line_s)
                break
        results.append({
            "file": page["file"],
            "title": title,
            "score": score,
            "snippet": snippet,
        })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top]


def main():
    parser = argparse.ArgumentParser(description="检索个人 Wiki 内容")
    parser.add_argument("--query", required=True, help="检索词，可用空格分隔多个")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    results = search(args.query, args.top)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if not results:
        print("# 当前 Wiki 中没有足够依据", file=sys.stderr)


if __name__ == "__main__":
    main()
