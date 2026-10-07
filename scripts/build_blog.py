"""把 content/posts/*.md 渲染成 public/blog.html 与 public/posts/<slug>.html。

只用 Python 标准库；重复运行结果一致（幂等，整体重写而不是追加）。
"""
import html
import re
import sys
from pathlib import Path

from site_common import PROJECT_ROOT, render_page

POSTS_SRC = PROJECT_ROOT / "content" / "posts"
POSTS_OUT = PROJECT_ROOT / "public" / "posts"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_frontmatter(text):
    """返回 (meta: dict, body: str)。支持 key: value 与 [a, b] 列表。"""
    meta = {}
    body = text
    stripped = text.lstrip("\ufeff")
    lines = stripped.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                body = "\n".join(lines[i + 1:])
                break
            if ":" in lines[i]:
                key, _, value = lines[i].partition(":")
                value = value.strip()
                if value.startswith("[") and value.endswith("]"):
                    value = [v.strip() for v in value[1:-1].split(",") if v.strip()]
                meta[key.strip()] = value
    return meta, body


def render_inline(text):
    s = html.escape(text, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: '<a href="{}">{}</a>'.format(html.escape(m.group(2), quote=True), m.group(1)),
        s,
    )
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def render_blocks(text):
    """极简 Markdown 渲染：标题、段落、列表、引用、围栏代码块、行内格式。"""
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # 跳过结束围栏
            out.append("<pre><code>" + html.escape("\n".join(buf), quote=False) + "</code></pre>")
            continue

        if not stripped:
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append("<h{0}>{1}</h{0}>".format(level, render_inline(m.group(2))))
            i += 1
            continue

        if stripped.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + "".join(
                "<p>{}</p>".format(render_inline(b)) for b in buf if b) + "</blockquote>")
            continue

        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(
                "<li>{}</li>".format(render_inline(it)) for it in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(
                "<li>{}</li>".format(render_inline(it)) for it in items) + "</ol>")
            continue

        buf = [stripped]
        i += 1
        while i < len(lines):
            t = lines[i].strip()
            if (not t or t.startswith(("#", ">", "```")) or re.match(r"^[-*]\s+", t)
                    or re.match(r"^\d+\.\s+", t)):
                break
            buf.append(t)
            i += 1
        out.append("<p>" + render_inline(" ".join(buf)) + "</p>")

    return "\n".join(out)


def plain_text(markdown_text):
    """提取纯文本（去掉行内标记与链接），用于 description 兜底。"""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", markdown_text)
    text = re.sub(r"[#>*`]", "", text)
    return " ".join(text.split())


def first_paragraph(body):
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith(("#", ">", "```")) and not re.match(r"^[-*]\s+", s):
            return plain_text(s)
    return ""


def strip_leading_h1(html_text):
    """去掉正文开头的第一个 <h1>（页面头部已展示标题，避免重复）。"""
    return re.sub(r"^\s*<h1>.*?</h1>\s*", "", html_text, count=1)


def load_posts():
    posts = []
    for path in sorted(POSTS_SRC.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        posts.append({
            "slug": path.stem,
            "title": meta.get("title", path.stem),
            "date": meta.get("date", ""),
            "description": meta.get("description") or first_paragraph(body),
            "tags": meta.get("tags", []),
            "html": render_blocks(body),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def article_page(post):
    tags = "".join('<span class="badge">{}</span>'.format(html.escape(t, quote=False))
                   for t in post["tags"])
    body = (
        '<section class="article-header">'
        '<h1>{}</h1>'
        '<p class="meta">{} {}</p>'
        '</section>'
        '<section class="article-body">{}</section>'
        '<p><a href="../blog.html">← 返回博客列表</a></p>'
    ).format(html.escape(post["title"], quote=False), post["date"], tags,
             strip_leading_h1(post["html"]))
    return render_page(post["title"], post["description"], "blog.html", body, root="..")


def blog_index_page(posts):
    items = []
    for post in posts:
        items.append(
            '<article class="item">'
            '<h3><a href="posts/{slug}.html">{title}</a></h3>'
            '<p class="meta">{date}</p>'
            '<p class="summary">{description}</p>'
            '</article>'.format(slug=post["slug"],
                                title=html.escape(post["title"], quote=False),
                                date=post["date"],
                                description=html.escape(post["description"], quote=False)))
    body = (
        '<section class="hero">'
        '<h1>博客</h1>'
        '<p class="meta">文章源文件在 <code>content/posts/</code>，由构建脚本生成本页；'
        '订阅更新请使用 <a href="feed.xml">RSS 订阅源 feed.xml</a>。</p>'
        '</section>'
        '<section aria-label="文章列表">{}</section>'
    ).format("".join(items) or '<p class="empty-tip">暂无文章。</p>')
    return render_page("博客 · 刘建阳", "刘建阳的博客文章列表", "blog.html", body, root=".")


def main():
    if not POSTS_SRC.exists():
        print("BUILD BLOG: 未找到 content/posts 目录")
        return
    posts = load_posts()
    POSTS_OUT.mkdir(parents=True, exist_ok=True)

    for old in POSTS_OUT.glob("*.html"):
        old.unlink()

    for post in posts:
        (POSTS_OUT / (post["slug"] + ".html")).write_text(
            article_page(post), encoding="utf-8")

    (PROJECT_ROOT / "public" / "blog.html").write_text(
        blog_index_page(posts), encoding="utf-8")

    print("BUILD BLOG: 生成 {} 篇文章页面 + blog.html".format(len(posts)))


if __name__ == "__main__":
    main()
