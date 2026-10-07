"""从 arXiv API 收集论文，按 id 去重后合并进 public/data/papers.json。

网络失败时保留旧数据并以非零码退出（Skill 安全规则）。
"""
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from site_common import PROJECT_ROOT

API = "https://export.arxiv.org/api/query"
OUTPUT = PROJECT_ROOT / "public" / "data" / "papers.json"
ATOM = {"atom": "http://www.w3.org/2005/Atom"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def clean(text):
    return " ".join((text or "").split())


def fetch(query, limit):
    params = urlencode({
        "search_query": query,
        "start": 0,
        "max_results": limit,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    request = Request("{0}?{1}".format(API, params),
                      headers={"User-Agent": "student-agent-course/1.0"})
    with urlopen(request, timeout=20) as response:
        root = ET.fromstring(response.read())

    papers = []
    for entry in root.findall("atom:entry", ATOM):
        raw_id = clean(entry.findtext("atom:id", namespaces=ATOM))
        paper_id = raw_id.rsplit("/", 1)[-1]
        papers.append({
            "id": paper_id,
            "title": clean(entry.findtext("atom:title", namespaces=ATOM)),
            "authors": [clean(a.findtext("atom:name", namespaces=ATOM))
                        for a in entry.findall("atom:author", ATOM)],
            "published": clean(entry.findtext("atom:published", namespaces=ATOM))[:10],
            "summary": clean(entry.findtext("atom:summary", namespaces=ATOM)),
            # arXiv API 返回的 id 是 http://，统一升级为 https://（check_papers 要求）
            "url": "https://" + raw_id.split("://", 1)[1] if "://" in raw_id else raw_id,
            "source": "arXiv",
        })
    return papers


def main():
    parser = argparse.ArgumentParser(description="收集 arXiv 最新论文")
    parser.add_argument("--query", default='all:"AI agent"')
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    old = []
    if OUTPUT.exists():
        old = json.loads(OUTPUT.read_text(encoding="utf-8"))

    fetched = fetch(args.query, args.limit)  # 失败会抛异常，不会动旧数据
    by_id = {paper["id"]: paper for paper in old}
    before = len(by_id)
    for paper in fetched:
        by_id[paper["id"]] = paper

    result = sorted(by_id.values(), key=lambda p: p["published"], reverse=True)[:50]
    if result != old:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"fetched": len(fetched), "new": len(by_id) - before,
                      "saved": len(result), "query": args.query}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("COLLECT PAPERS FAILED: {}（已保留旧数据，文件未改动）".format(exc))
        sys.exit(1)
