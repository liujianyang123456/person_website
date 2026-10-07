# person_website —— 用 AI Agent 逐步构建的个人网站

数据警务课程作业：从一个最小首页开始，按 Step 1~10 逐步演化出博客、RSS、论文订阅、
个人 Wiki、Wiki 问答和网站状态面板。所有页面只使用原生 HTML/CSS/JavaScript，
所有构建脚本只使用 Python 标准库。

## 目录结构

```
person_website/
├── AGENTS.md            # 项目长期规则（Agent 必读）
├── .gitlab-ci.yml       # CloudBase 部署流水线
├── .gitignore
├── README.md
├── config/
│   └── feeds.json       # RSS 阅读器订阅配置（含 allowlist）
├── content/
│   ├── posts/           # 博客 Markdown 源文件
│   └── wiki/            # Wiki Markdown 源文件（[[双向链接]]）
├── scripts/             # 构建 / 抓取 / 检查脚本（仅标准库）
│   ├── build_all.py     # 统一构建入口（生成 + 全部检查 + 状态数据）
│   ├── build_blog.py    # content/posts -> public/blog.html + public/posts/
│   ├── build_rss.py     # content/posts -> public/feed.xml（RSS 2.0）
│   ├── build_wiki.py    # content/wiki  -> public/wiki.html + public/wiki/
│   ├── fetch_rss.py     # config/feeds.json -> public/data/rss-items.json
│   ├── collect_papers.py# arXiv API -> public/data/papers.json
│   ├── search_wiki.py   # Wiki 关键词检索（供 RAG 问答取证据）
│   ├── check_feed.py    # feed.xml 结构校验
│   ├── check_links.py   # 全站内部死链检查
│   ├── check_papers.py  # papers.json 字段校验
│   └── build_status.py  # 汇总站点数据 -> public/data/status.json
├── public/              # 唯一被部署的目录
│   ├── index.html       # 首页
│   ├── about.html       # 关于我
│   ├── blog.html        # 博客列表（生成）
│   ├── papers.html      # Research Papers
│   ├── wiki.html        # Wiki 索引（生成）
│   ├── rss.html         # RSS 订阅阅读器
│   ├── status.html      # 网站状态面板
│   ├── styles.css
│   ├── feed.xml         # 生成的 RSS 源
│   ├── data/            # 生成的数据 JSON
│   ├── posts/           # 生成的文章页
│   └── wiki/            # 生成的 Wiki 页面
└── .opencode/skills/    # Agent 技能
    ├── research-paper-collector/
    └── search-wiki/
```

## 本地使用

```bash
# 1. 生成博客/Wiki/RSS/状态数据并执行全部检查
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
```

## 常见问题

**论文 / RSS / 状态页面提示“数据加载失败”？**
先看是不是用双击方式打开的 html（地址栏以 `file://` 开头）。浏览器出于安全策略
禁止 `file://` 页面用 `fetch()` 读取本地数据文件，即使文件就在旁边。这不是数据缺失，
请改用 `python scripts/serve.py 8080` 并访问 `http://localhost:8080`；
页面检测到 `file://` 时也会直接显示这条提示。

**`python -m http.server 8080` 报 `UnicodeDecodeError`？**
中文主机名的 Windows 上 Python 3.8 的已知问题（`socket.getfqdn` 解码失败），
改用 `python scripts/serve.py 8080` 即可。

## 部署（GitLab + 腾讯云 CloudBase）

1. 在极狐 GitLab 创建空项目并推送本仓库；
2. 注册腾讯云，创建 CloudBase 环境（免费体验版即可），
   在“密钥管理”创建 `TCB_SECRET_ID` / `TCB_SECRET_KEY`；
3. GitLab 仓库 -> 设置 -> CI/CD -> 变量，添加
   `TCB_SECRET_ID`、`TCB_SECRET_KEY`、`TCB_ENV_ID`；
4. push 到 `main` 分支后流水线自动执行：构建 -> 全部检查 -> `tcb hosting deploy ./public`；
   检查失败会直接中止部署。

## 个性化修改点

- 姓名 / 学校 / 专业 / 邮箱：`public/index.html`、`public/about.html`；
- RSS 里的文章链接域名：`scripts/build_rss.py` 顶部的 `BASE_URL`（部署后替换为 CloudBase 托管域名）；
- 兴趣方向与自我介绍文案：`public/index.html`；
- 订阅源：`config/feeds.json`（注意 allowlist 同步添加域名）。
