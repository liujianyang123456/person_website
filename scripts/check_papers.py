"""校验 public/data/papers.json：必填字段、URL scheme、id 去重。"""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from site_common import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PAPERS = PROJECT_ROOT / "public" / "data" / "papers.json"
REQUIRED = {"id", "title", "authors", "published", "summary", "url", "source"}


def run():
    if not PAPERS.exists():
        return True, "未运行", "papers.json 不存在；可运行 scripts/collect_papers.py 收集论文"
    try:
        papers = json.loads(PAPERS.read_text(encoding="utf-8"))
        ids = set()
        for index, paper in enumerate(papers):
            missing = REQUIRED - set(paper.keys())
            if missing:
                raise ValueError("paper {} 缺少字段: {}".format(index, sorted(missing)))
            if paper["id"] in ids:
                raise ValueError("重复 id: {}".format(paper["id"]))
            if urlparse(paper["url"]).scheme != "https":
                raise ValueError("非 HTTPS 链接: {}".format(paper["url"]))
            ids.add(paper["id"])
        return True, "通过", "{} 篇论文通过校验".format(len(papers))
    except Exception as exc:
        return False, "失败", "papers.json 校验失败：{}".format(exc)


def main():
    ok, word, detail = run()
    print("CHECK PAPERS [{}] {}".format(word, detail))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
