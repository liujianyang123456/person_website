"""汇总站点状态到 public/data/status.json：构建时间 + 各类计数 + 检查结果。

日志不含任何密钥或敏感信息（可观测性规则）。
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from site_common import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def count_papers():
    data = load_json(PROJECT_ROOT / "public" / "data" / "papers.json")
    return len(data) if isinstance(data, list) else None


def count_rss_items():
    data = load_json(PROJECT_ROOT / "public" / "data" / "rss-items.json")
    return len(data) if isinstance(data, list) else None


def count_feeds():
    data = load_json(PROJECT_ROOT / "config" / "feeds.json")
    return len(data.get("feeds", [])) if isinstance(data, dict) else 0


def main(checks=None):
    public = PROJECT_ROOT / "public"
    status = {
        "build_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "counts": {
            "pages": len(list(public.rglob("*.html"))),
            "posts": len(list((PROJECT_ROOT / "content" / "posts").glob("*.md"))),
            "wiki": len([p for p in (PROJECT_ROOT / "content" / "wiki").glob("*.md")
                         if p.name != "README.md"]),
            "papers": count_papers(),
            "rss_feeds": count_feeds(),
            "rss_items": count_rss_items(),
        },
        "checks": checks or {},
    }
    out = public / "data" / "status.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print("BUILD STATUS: 构建时间 {}，页面 {}，文章 {}，Wiki {}".format(
        status["build_time"], status["counts"]["pages"],
        status["counts"]["posts"], status["counts"]["wiki"]))


if __name__ == "__main__":
    main()
