"""把 content/wiki/*.md 渲染成 public/wiki.html（索引）与 public/wiki/<slug>.html。

支持 [[双向链接]]（按页面标题解析）并自动生成反向链接；重复运行幂等。
"""
import html
import re
import sys
from pathlib import Path

from site_common import PROJECT_ROOT, render_page
from build_blog import parse_frontmatter, render_blocks, strip_leading_h1

WIKI_SRC = PROJECT_ROOT / "content" / "wiki"
WIKI_OUT = PROJECT_ROOT / "public" / "wiki"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
INDEX_SLUG = "index"


def resolve_wikilinks(rendered_html, title_to_slug, context):
    """把 [[标题]] / [[标题|文字]] 解析成链接；<code> 内的字面量不解析。

    context = "dir"   -> 生成 public/wiki/<slug>.html 时的相对路径
    context = "index" -> 生成 public/wiki.html 时的相对路径
    """
    missing = []

    def repl(m):
        target = m.group(1).strip()
        label = (m.group(2) or target).strip()
        slug = title_to_slug.get(target)
        if slug is None:
            missing.append(target)
            return '<span class="wikilink-missing">{}</span>'.format(label)
        if slug == INDEX_SLUG:
            href = "#" if context == "index" else "../wiki.html"
        else:
            href = slug + ".html" if context == "dir" else "wiki/" + slug + ".html"
        return '<a class="wikilink" href="{}">{}</a>'.format(href, label)

    parts = re.split(r"(<code>.*?</code>)", rendered_html, flags=re.S)
    resolved = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # code 段原样保留
            resolved.append(part)
        else:
            resolved.append(WIKILINK_RE.sub(repl, part))
    return "".join(resolved), missing


def load_pages():
    pages = []
    for path in sorted(WIKI_SRC.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        pages.append({
            "slug": path.stem,
            "title": meta.get("title", path.stem),
            "updated": meta.get("updated", ""),
            "tags": meta.get("tags", []),
            "body_md": body,
        })
    return pages


def backlinks_for(pages, page_slug):
    """扫描所有页面的 [[链接]]，返回链接到 page_slug 的来源页面 slug 列表。"""
    title_to_slug = {p["title"]: p["slug"] for p in pages}
    sources = set()
    for p in pages:
        if p["slug"] in (page_slug, INDEX_SLUG, "README"):
            continue  # 索引页链接到所有页面，不作为反向链接噪音
        for m in WIKILINK_RE.finditer(p["body_md"]):
            slug = title_to_slug.get(m.group(1).strip())
            if slug == page_slug:
                sources.add(p["slug"])
    return sorted(sources)


def article_section(page, body_html):
    tags = "".join('<span class="badge">{}</span>'.format(html.escape(t, quote=False))
                   for t in page["tags"])
    return (
        '<section class="article-header">'
        '<h1>{title}</h1>'
        '<p class="meta">更新于 {updated} {tags}</p>'
        '</section>'
        '<section class="article-body">{body}</section>'
    ).format(title=html.escape(page["title"], quote=False),
             updated=page["updated"], tags=tags, body=strip_leading_h1(body_html))


def page_article(pages, page, slug_to_title):
    body_html, missing = resolve_wikilinks(
        render_blocks(page["body_md"]), {p["title"]: p["slug"] for p in pages}, "dir")

    sources = backlinks_for(pages, page["slug"])
    if sources:
        links = " ".join(
            '<a class="wikilink" href="{}.html">{}</a>'.format(
                s, html.escape(slug_to_title[s], quote=False))
            for s in sources)
        body_html += '<div class="backlinks"><strong>反向链接</strong>：{}</div>'.format(links)
    body_html += '<p><a href="../wiki.html">← 返回 Wiki 索引</a></p>'

    page_html = render_page(
        page["title"] + " · 个人 Wiki",
        "个人 Wiki：" + page["title"],
        "wiki.html", article_section(page, body_html), root="..")
    return page_html, missing


def index_page(pages, index_meta):
    slug_to_title = {p["slug"]: p["title"] for p in pages}
    body_html, missing = resolve_wikilinks(
        render_blocks(index_meta["body_md"]), {p["title"]: p["slug"] for p in pages}, "index")

    items = []
    others = sorted((p for p in pages if p["slug"] != INDEX_SLUG),
                    key=lambda p: p["updated"], reverse=True)
    for p in others:
        items.append(
            '<li><a href="wiki/{slug}.html">{title}</a> '
            '<span class="meta">更新于 {updated}</span></li>'.format(
                slug=p["slug"], title=html.escape(p["title"], quote=False),
                updated=p["updated"]))
    body_html += (
        '<section aria-label="全部页面"><h2>全部页面</h2><ul>{}</ul></section>'
    ).format("".join(items))

    page_html = render_page(
        "Wiki · 刘建阳", "个人 Wiki 索引：课程笔记、概念理解与项目决策",
        "wiki.html", article_section(index_meta, body_html), root=".")
    return page_html, missing


def main():
    if not WIKI_SRC.exists():
        print("BUILD WIKI: 未找到 content/wiki 目录")
        return
    pages = load_pages()
    slug_to_title = {p["slug"]: p["title"] for p in pages}

    WIKI_OUT.mkdir(parents=True, exist_ok=True)
    for old in WIKI_OUT.glob("*.html"):
        old.unlink()

    missing_all = []
    wiki_count = 0
    for page in pages:
        if page["slug"] == INDEX_SLUG:
            continue
        page_html, missing = page_article(pages, page, slug_to_title)
        (WIKI_OUT / (page["slug"] + ".html")).write_text(page_html, encoding="utf-8")
        missing_all.extend(missing)
        wiki_count += 1

    index_meta = next(p for p in pages if p["slug"] == INDEX_SLUG)
    index_html, missing = index_page(pages, index_meta)
    (PROJECT_ROOT / "public" / "wiki.html").write_text(index_html, encoding="utf-8")
    missing_all.extend(missing)

    print("BUILD WIKI: 生成 {} 个 Wiki 页面 + wiki.html".format(wiki_count))
    if missing_all:
        print("BUILD WIKI: 警告，未解析的 [[链接]]：{}".format(sorted(set(missing_all))))


if __name__ == "__main__":
    main()
