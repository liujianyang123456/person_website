"""共享路径常量与页面模板（博客 / Wiki 生成脚本共用）。"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

NAV_ITEMS = [
    ("index.html", "首页"),
    ("about.html", "关于我"),
    ("blog.html", "博客"),
    ("archive.html", "归档"),
    ("papers.html", "Research Papers"),
    ("wiki.html", "Wiki"),
    ("rss.html", "RSS订阅"),
    ("status.html", "网站状态"),
]

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f8fafc">
  <title>__TITLE__</title>
  <meta name="description" content="__DESCRIPTION__">
  <link rel="stylesheet" href="__ROOT__/styles.css">
</head>
<body>
  <a class="skip-link" href="#main-content">跳到主要内容</a>
  <header class="site-header">
    <p class="brand"><a href="__ROOT__/index.html">person_website</a></p>
    <nav class="site-nav" aria-label="主导航">
      <ul>
__NAV__
      </ul>
    </nav>
  </header>

  <main id="main-content" tabindex="-1">
__BODY__
  </main>

  <footer class="site-footer">
    © 2026 刘建阳 · 用 AI Agent 协作构建 ·
    <a href="__ROOT__/status.html">网站状态</a> ·
    <a href="__ROOT__/feed.xml">RSS</a>
  </footer>
</body>
</html>
"""


def render_nav(active, root):
    lines = []
    for href, label in NAV_ITEMS:
        current = ' aria-current="page"' if href == active else ""
        lines.append('        <li><a href="{}/{}"{}>{}</a></li>'.format(root, href, current, label))
    return "\n".join(lines)


def render_page(title, description, active, body, root="."):
    html = PAGE_TEMPLATE
    html = html.replace("__TITLE__", title)
    html = html.replace("__DESCRIPTION__", description)
    html = html.replace("__NAV__", render_nav(active, root))
    html = html.replace("__BODY__", body)
    html = html.replace("__ROOT__", root)
    return html
