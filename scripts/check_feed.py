"""校验 public/feed.xml：用 XML 解析器验证结构与必填字段，解析失败视为失败。"""
import sys
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

from site_common import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FEED = PROJECT_ROOT / "public" / "feed.xml"
REQUIRED_ITEM = ("title", "link", "guid", "pubDate", "description")


def run():
    try:
        root = ET.parse(FEED).getroot()
        channel = root.find("channel")
        if channel is None:
            raise ValueError("缺少 channel 元素")
        for tag in ("title", "link", "description"):
            if not (channel.findtext(tag) or "").strip():
                raise ValueError("channel 缺少 {}".format(tag))
        items = channel.findall("item")
        if not items:
            raise ValueError("没有任何 item")
        for i, item in enumerate(items):
            for tag in REQUIRED_ITEM:
                if item.findtext(tag) is None:
                    raise ValueError("item {} 缺少 <{}>".format(i, tag))
            parsedate_to_datetime(item.findtext("pubDate"))
        return True, "通过", "feed.xml 有效，共 {} 条 item".format(len(items))
    except FileNotFoundError:
        return False, "失败", "feed.xml 不存在，请先运行 scripts/build_rss.py"
    except Exception as exc:
        return False, "失败", "feed.xml 校验失败：{}".format(exc)


def main():
    ok, word, detail = run()
    print("CHECK FEED [{}] {}".format(word, detail))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
