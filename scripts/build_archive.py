"""把博客文章按年份归档，生成 public/archive.html。

数据来自 build_blog.load_posts（content/posts/*.md，已按日期倒序）；
只用 Python 标准库；重复运行结果一致（幂等，整体重写而不是追加）。
"""
import html
import sys

from build_blog import load_posts
from site_common import PROJECT_ROOT, render_page

ARCHIVE_OUT = PROJECT_ROOT / "public" / "archive.html"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def archive_page(posts):
    by_year = {}
    for post in posts:
        year = post["date"][:4] or "未知"
        by_year.setdefault(year, []).append(post)

    sections = []
    for year in sorted(by_year, reverse=True):
        year_posts = by_year[year]
        items = "".join(
            '<article class="item">'
            '<h2><a href="posts/{slug}.html">{title}</a></h2>'
            '<p class="meta">{date}</p>'
            '<p class="summary">{description}</p>'
            '</article>'.format(slug=post["slug"],
                                title=html.escape(post["title"], quote=False),
                                date=post["date"],
                                description=html.escape(post["description"], quote=False))
            for post in year_posts)
        sections.append(
            '<section aria-labelledby="year-{year}">'
            '<h2 id="year-{year}">{year} 年（{count} 篇）</h2>'
            '{items}'
            '</section>'.format(year=year, count=len(year_posts), items=items))

    body = (
        '<section class="hero">'
        '<h1>归档</h1>'
        '<p class="meta">本页由构建脚本从 <code>content/posts/</code> 生成，按年份汇总全部文章；'
        '订阅更新请使用 <a href="feed.xml">feed.xml</a>。</p>'
        '</section>'
        '{}'
    ).format("".join(sections) or '<p class="empty-tip">暂无文章。</p>')
    return render_page("归档 · 刘建阳", "博客文章归档：按年份浏览全部文章",
                       "archive.html", body, root=".")


def main():
    posts = load_posts()
    ARCHIVE_OUT.write_text(archive_page(posts), encoding="utf-8")
    print("BUILD ARCHIVE: 归档页生成 {} 篇文章的归档".format(len(posts)))


if __name__ == "__main__":
    main()
