# person_website —— 用 AI Agent 逐步构建的个人网站

数据警务课程作业：从一个最小首页开始，按课程 Step 1~12 逐步演化出博客、RSS、
论文订阅、个人 Wiki、Wiki 问答、状态面板、归档页和 24 小时自动流水线。
所有页面只使用原生 HTML/CSS/JavaScript，所有构建脚本只使用 Python 标准库。

线上地址：https://liujianyang123456.github.io/person_website/
（GitHub Pages + GitHub Actions 自动构建部署，不使用任何云厂商密钥）

## 课程路线图对照表

| 课程 Step | 功能 | 关键 commit | 线上验证方式 |
|---|---|---|---|
| Step 1–2 | 最小首页；纳入 Git 管理；远程托管自动部署上线 | `a5b4b3d` `150cfd8` `23708cf` | 打开首页；仓库 Actions 页看 Deploy to GitHub Pages 全绿 |
| Step 3 | 菜单栏与多页面互跳（现 8 个入口） | `150cfd8` | 点导航在 首页/关于我/博客/归档/论文/Wiki/RSS/状态 间跳转，当前页高亮 |
| Step 4 | Markdown 博客（content/posts 自动生成） | `bad93d4` | 打开 /blog/ 任一文章；新增 md 后 push，页面自动出现 |
| Step 5 | 发布 RSS 2.0 订阅源 | `3d915dc` | 打开 /feed.xml，或把地址粘进任一 RSS 阅读器订阅成功 |
| Step 6 | RSS 阅读器（allowlist + 信任边界） | `b0fae87` | 打开 RSS订阅 页，看到腾讯安全中心外部内容按来源分组展示 |
| Step 7 | 论文 Skill（arXiv 收集） | `b8a41a0` | 打开 Research Papers 页，论文按提交时间倒序、带原文链接 |
| Step 8 | 文件化个人 Wiki（[[双向链接]]） | `fa08339` | 打开 Wiki，页底可见「反向链接」，链接互相可达 |
| Step 9 | Wiki 检索问答（RAG，有据回答） | `085e7e6` | 问答由 Skill 离线使用；本地 `python scripts/search_wiki.py --query "…"` 复现 |
| Step 10 | 网站状态面板（可观测） | `b9372a2` | 打开 网站状态，站点数据与三项自动检查结果一目了然 |
| Step 11 | Multi-Agent 分工协同（归档页） | `01e4635` | 打开 归档 页，按年份分组浏览全部博文 |
| Step 12 | 24 小时个人 Agent（定时流水线） | `14f1f19` | Actions 页 Daily agent run 定时/手动运行；网站状态页看「最近自动运行」 |

## 目录结构

```
person_website/
├── AGENTS.md            # 项目长期规则（Agent 必读）
├── PLAN.md              # 全阶段执行计划与审查记录（唯一事实来源）
├── .github/workflows/
│   ├── deploy.yml       # push main -> 构建检查 -> GitHub Pages 部署
│   └── daily-agent.yml  # 每日 08:30 定时流水线（论文/订阅/构建/提交/部署）
├── config/
│   └── feeds.json       # RSS 阅读器订阅配置（含 allowlist）
├── content/
│   ├── posts/           # 博客 Markdown 源文件
│   └── wiki/            # Wiki Markdown 源文件（[[双向链接]]）
├── scripts/             # 构建 / 抓取 / 检查脚本（仅标准库）
│   ├── build_all.py     # 统一构建入口（生成 + 全部检查 + 状态数据）
│   ├── build_blog.py    # content/posts -> public/blog.html + public/posts/
│   ├── build_wiki.py    # content/wiki  -> public/wiki.html + public/wiki/
│   ├── build_archive.py # 按年份归档 -> public/archive.html
│   ├── build_rss.py     # content/posts -> public/feed.xml（RSS 2.0）
│   ├── fetch_rss.py     # config/feeds.json -> public/data/rss-items.json
│   ├── collect_papers.py# arXiv API -> public/data/papers.json
│   ├── run_daily.py     # 每日流水线：collect_papers + fetch_rss + build_all -> last_run.json
│   ├── search_wiki.py   # Wiki 关键词检索（供 RAG 问答取证据）
│   ├── check_feed.py    # feed.xml 结构校验
│   ├── check_links.py   # 全站内部死链检查
│   ├── check_papers.py  # papers.json 字段校验
│   ├── serve.py         # 本地预览服务器
│   └── build_status.py  # 汇总站点数据 -> public/data/status.json
├── public/              # 唯一被部署的目录
│   ├── index.html       # 首页
│   ├── about.html       # 关于我
│   ├── blog.html        # 博客列表（生成）
│   ├── archive.html     # 博客归档（生成）
│   ├── papers.html      # Research Papers
│   ├── wiki.html        # Wiki 索引（生成）
│   ├── rss.html         # RSS 订阅阅读器
│   ├── status.html      # 网站状态面板
│   ├── styles.css
│   ├── feed.xml         # 生成的 RSS 源
│   ├── data/            # 生成的数据 JSON（status / papers / rss-items / last_run）
│   ├── posts/           # 生成的文章页
│   └── wiki/            # 生成的 Wiki 页面
└── .opencode/skills/    # Agent 技能
    ├── research-paper-collector/
    └── search-wiki/
```

## 本地使用

```bash
# 1. 生成博客/Wiki/归档/RSS/状态数据并执行全部检查
python scripts/build_all.py

# 2. 本地预览（推荐，自动指向 public 目录）
python scripts/serve.py 8080
# 浏览器访问 http://localhost:8080

# 等价写法：cd public && python -m http.server 8080
# （注：中文主机名的 Windows 上 http.server 可能在 socket.getfqdn 处
#   抛 UnicodeDecodeError，此时请改用 scripts/serve.py）
```

常用脚本：

```bash
python scripts/collect_papers.py --query "all:\"AI agent\"" --limit 10   # 收集最新论文
python scripts/fetch_rss.py                                             # 抓取订阅源
python scripts/search_wiki.py --query "Agent Loop"                      # Wiki 检索
python scripts/run_daily.py                                             # 手动跑一次每日流水线
```

## 部署（GitHub Pages + GitHub Actions）

1. 在 GitHub 创建空仓库 `person_website`（Public、不初始化 README）并推送本仓库；
2. 仓库 Settings -> Pages -> Source 选 **GitHub Actions**（首次部署后自动配置）；
3. push 到 `main` 分支触发 `deploy.yml`：构建 -> 全部检查（任一失败中止部署）
   -> actions/deploy-pages 上线；
4. `daily-agent.yml` 每天 08:30（北京时间）自动跑论文收集 + 订阅抓取 + 构建，
   有内容变更自动 commit 并部署，结果见网站状态页「最近自动运行」；
   也可在 Actions 页手动 workflow_dispatch 触发；
5. 全程不使用任何用户密钥（Pages 部署走仓库内置 OIDC）。

## 常见问题

**论文 / RSS / 状态页面提示“数据加载失败”？**
先看是不是用双击方式打开的 html（地址栏以 `file://` 开头）。浏览器出于安全策略
禁止 `file://` 页面用 `fetch()` 读取本地数据文件，即使文件就在旁边。这不是数据缺失，
请改用 `python scripts/serve.py 8080` 并访问 `http://localhost:8080`；
页面检测到 `file://` 时也会直接显示这条提示。

**`python -m http.server 8080` 报 `UnicodeDecodeError`？**
中文主机名的 Windows 上 Python 3.8 的已知问题（`socket.getfqdn` 解码失败），
改用 `python scripts/serve.py 8080` 即可。

## 个性化修改点

- 姓名 / 学校 / 专业 / 邮箱：`public/index.html`、`public/about.html`；
- RSS 里的文章链接域名：`scripts/build_rss.py` 顶部的 `BASE_URL`
  （已配置为 GitHub Pages 地址，换仓库/用户名时同步修改）；
- 兴趣方向与自我介绍文案：`public/index.html`；
- 订阅源：`config/feeds.json`（注意 allowlist 同步添加域名）；
- 每日流水线的论文查询词与抓取时间：`scripts/run_daily.py`、
  `.github/workflows/daily-agent.yml` 的 cron。
