"""抓取 config/feeds.json 中的订阅源，规范化为 public/data/rss-items.json。

信任边界：
- 只抓取 HTTPS 且域名在 allowlist 中的地址；
- 限制超时（15s）与体积（2MB）；
- 标题/摘要去除 HTML 标签后仅作为纯文本存储，页面侧也只用 textContent 展示；
- 任何抓取或解析失败都不写文件（保留旧数据），并以非零码退出。
"""
import json
import re
import sys
import html as htmllib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG = PROJECT_ROOT / "config" / "feeds.json"
OUTPUT = PROJECT_ROOT / "public" / "data" / "rss-items.json"

TIMEOUT = 15
MAX_BYTES = 2 * 1024 * 1024
MAX_SUMMARY = 300
MAX_ITEMS = 200
UA = "student-agent-course/1.0"
ATOM = {"a": "http://www.w3.org/2005/Atom"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def strip_tags(text):
    """外部内容一律去标签、解实体，只保留纯文本（信任边界）。"""
    text = re.sub(r"<[^>]+>", " ", text or "")
    return " ".join(htmllib.unescape(text).split())


def fetch_bytes(url):
    request = Request(url, headers={"User-Agent": UA})
    with urlopen(request, timeout=TIMEOUT) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("响应超过 {} 字节限制".format(MAX_BYTES))
    return data


def make_item(feed, feed_url, item_id, title, link, pub_raw, summary):
    published_sort = ""
    if pub_raw:
        try:
            published_sort = parsedate_to_datetime(pub_raw).astimezone(
                timezone.utc).isoformat()
        except (TypeError, ValueError):
            published_sort = pub_raw  # Atom 日期本身就是 ISO 格式
    return {
        "id": item_id,
        "feed": feed,
        "feed_url": feed_url,
        "title": title,
        "link": link,
        "published": pub_raw,
        "published_sort": published_sort,
        "summary": summary,
    }


def parse_items(data, feed_meta):
    root = ET.fromstring(data)
    feed_title = feed_meta.get("title") or ""
    items = []

    channel = root.find("channel")  # RSS 2.0
    if channel is not None:
        feed_title = feed_title or strip_tags(channel.findtext("title") or "")
        for node in channel.findall("item"):
            title = strip_tags(node.findtext("title"))
            link = (node.findtext("link") or "").strip()
            guid = (node.findtext("guid") or link or title).strip()
            pub_raw = (node.findtext("pubDate") or "").strip()
            summary = strip_tags(node.findtext("description"))[:MAX_SUMMARY]
            if title or link:
                items.append(make_item(feed_title, feed_meta["url"],
                                       guid, title, link, pub_raw, summary))

    if root.tag == "{http://www.w3.org/2005/Atom}feed":  # Atom 1.0
        feed_title = feed_title or strip_tags(
            root.findtext("a:title", namespaces=ATOM) or "")
        for node in root.findall("a:entry", ATOM):
            title = strip_tags(node.findtext("a:title", namespaces=ATOM))
            link = ""
            for link_node in node.findall("a:link", ATOM):
                if link_node.get("rel") in (None, "alternate"):
                    link = link_node.get("href") or ""
                    break
            guid = (node.findtext("a:id", namespaces=ATOM) or link or title).strip()
            pub_raw = (node.findtext("a:published", namespaces=ATOM)
                       or node.findtext("a:updated", namespaces=ATOM) or "").strip()
            summary = strip_tags(node.findtext("a:summary", namespaces=ATOM))[:MAX_SUMMARY]
            if title or link:
                items.append(make_item(feed_title, feed_meta["url"],
                                       guid, title, link, pub_raw, summary))

    return feed_title, items


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    allowlist = [h.lower() for h in config.get("allowlist", [])]

    old = []
    if OUTPUT.exists():
        try:
            old = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except ValueError:
            old = []

    all_items = []
    fetched = 0
    for feed_meta in config.get("feeds", []):
        url = feed_meta.get("url", "")
        host = (urlparse(url).hostname or "").lower()
        if not url.startswith("https://"):
            print("SKIP（非 HTTPS）: {}".format(url))
            continue
        if allowlist and host not in allowlist:
            print("SKIP（域名不在 allowlist）: {}".format(url))
            continue
        data = fetch_bytes(url)
        feed_title, items = parse_items(data, feed_meta)
        fetched += len(items)
        all_items.extend(items)

    by_id = {}
    for item in old:
        by_id.setdefault(item.get("id", item.get("link", "")), item)
    for item in all_items:
        by_id[item["id"]] = item

    merged = sorted(by_id.values(),
                    key=lambda it: it.get("published_sort", ""), reverse=True)
    merged = merged[:MAX_ITEMS]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(json.dumps({"feeds": len(config.get("feeds", [])),
                      "fetched": fetched, "total": len(merged)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("FETCH RSS FAILED: {}（已保留旧数据，文件未改动）".format(exc))
        sys.exit(1)
