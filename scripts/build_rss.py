"""根据 content/posts 的博客元数据生成 RSS 2.0 的 public/feed.xml。

Schema：channel 含 title/link/description/language/lastBuildDate；
每个 item 必须有 title、link、guid、pubDate、description；
特殊字符统一 XML 转义，按日期倒序。生成后由 check_feed.py 用解析器验证。
"""
import sys
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

from site_common import PROJECT_ROOT
from build_blog import load_posts, plain_text

# 部署后请替换为 CloudBase 静态托管的实际域名（RSS 里的链接必须是绝对地址）
BASE_URL = "https://person-website.example.com"

FEED_OUT = PROJECT_ROOT / "public" / "feed.xml"
TZ = timezone(timedelta(hours=8))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def rfc822(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=TZ)
    except ValueError:
        dt = datetime.now(TZ)
    return format_datetime(dt)


def item_xml(post):
    link = "{}/posts/{}.html".format(BASE_URL.rstrip("/"), post["slug"])
    summary = plain_text(post["description"])
    return (
        "    <item>\n"
        "      <title>{}</title>\n"
        "      <link>{}</link>\n"
        "      <guid>{}</guid>\n"
        "      <pubDate>{}</pubDate>\n"
        "      <description>{}</description>\n"
        "    </item>\n"
    ).format(escape(post["title"]), escape(link), escape(link),
             escape(rfc822(post["date"])), escape(summary))


def main():
    posts = load_posts()
    now = format_datetime(datetime.now(TZ))
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        "  <channel>",
        "    <title>{}</title>".format(escape("刘建阳的个人网站")),
        "    <link>{}</link>".format(escape(BASE_URL)),
        "    <description>{}</description>".format(
            escape("数据警务专业学生的个人网站：博客、Wiki 与 AI Agent 实践记录")),
        "    <language>zh-CN</language>",
        "    <lastBuildDate>{}</lastBuildDate>".format(now),
    ]
    for post in posts:
        parts.append(item_xml(post))
    parts.extend(["  </channel>", "</rss>", ""])

    FEED_OUT.parent.mkdir(parents=True, exist_ok=True)
    FEED_OUT.write_text("\n".join(parts), encoding="utf-8")
    print("BUILD RSS: feed.xml 生成 {} 条 item".format(len(posts)))


if __name__ == "__main__":
    main()
