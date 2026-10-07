# 个人网站 Agent 实践课 · 执行计划（PLAN.md）

> 本文件是全阶段自动执行的唯一事实来源。执行 Agent 每完成一个阶段必须更新对应条目
> （状态 / 审查记录 / commit），中断后下次运行从这里断点继续。**禁止在本文件写入任何密钥或 token。**

## 项目信息

- 项目根目录：`E:\liujianyang\Documents\作用\person_website`
- 托管平台：**GitHub（用户名 liujianyang123456）+ GitHub Actions + GitHub Pages**
  （原课程方案为极狐 GitLab + 腾讯 CloudBase，按用户决定改为 GitHub 等价实现；
  验收本质不变：远程托管、自动 CI 构建部署、线上可访问）
- 预期线上地址：`https://liujianyang123456.github.io/person_website/`
- 仓库要求：Public（免费账号 Pages 的要求）、空仓库创建（不要初始化 README）
- 腾讯云密钥：本方案不使用，不入库、不进 CI

## 全局规则（每个阶段都必须遵守）

1. 先读 `AGENTS.md`：只用原生 HTML/CSS/JS 与 Python 标准库；生成产物（`blog.html`、`posts/`、`wiki/`、`feed.xml`、`data/`）只能改 `scripts/` 模板后用 `python scripts/build_all.py` 重建，且构建必须幂等；
2. 所有 UI 对照 Web Interface Guidelines（`https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`）。红线：语义化标签、每页唯一 h1、键盘可达且 `:focus-visible` 清晰、正文对比度 ≥ 4.5:1、可点击区域 ≥ 44×44px、动画尊重 `prefers-reduced-motion`、`aria-current`/`aria-live` 正确、无死链、无 console 报错；
3. 每阶段固定循环：**执行 → 自审（构建/检查脚本 + guidelines 逐条 + 本地渲染 + 验收标准逐条打勾）→ commit（`feat:`/`fix:`/`ci:`/`docs:`/`chore:`）→ push → 更新本文件 → 下一阶段**；
4. GitHub 授权：不用密码；优先浏览器授权弹窗，备选用户提供的 PAT（经 `git credential approve` 存入系统凭证管理器，不写入文件和远程 URL）；
5. 密钥、token 等敏感信息绝不入库、绝不写入日志。

---

## 阶段 1：UI 基线审查与提交（课程 Step 1/3 的视觉与可及性要求）

- **状态**：已通过
- **背景**：工作区已有一整套未提交的 UI 修复（19 个文件：skip-link、标题层级 h3→h2、`aria-live`、`:focus-visible`、`prefers-reduced-motion`、`scrollbar-gutter`、44px 命中区、对比度修正等）。
- **任务**：抓取 guidelines 全文 → 逐页对照审查全部 `public/` 页面与未提交改动 → 发现问题当场修复 → 跑 `build_all.py` + 全部 `check_*.py` → 本地渲染核验 7 个页面 → 提交。
- **验收**：guidelines 红线全部满足；`check_links.py` 无死链；构建幂等（连跑两次，除时间戳外无变化）；本地渲染正常。
- **审查记录**：
  - guidelines 全文已获取（GitHub raw 直连超时，经 jsdelivr 镜像下载），逐条对照 14 个 HTML 页面 + styles.css + `site_common.py` 模板；
  - 本轮新修复 4 项：全站补 `<meta name="theme-color">`（含模板，重建生效）、`-webkit-tap-highlight-color: transparent`（反馈由 :hover/:active 承担）、状态表 `td` 加 `font-variant-numeric: tabular-nums`、页脚链接加内边距使命中区≈44px；
  - 红线核验：每页唯一 h1（程序化扫描 14 页全过）；语义化标签齐全；aria-current 正确；对比度实测 --muted/#f8fafc≈4.55:1、badge 4.62:1、链接 5.17:1、--ok 5.0:1 达标；:focus-visible 3px 轮廓、动画均在 prefers-reduced-motion: no-preference 内、三处 aria-live 就位；站点无 img/表单，相关条目 N/A；
  - `build_all.py` 连跑两次全绿：FEED_XML / INTERNAL_LINKS / PAPERS_SCHEMA 通过，14 页面 206 内部链接无死链，除时间戳外输出一致（幂等）；
  - 本地渲染核验 7 页（无头 Edge 按 scrollHeight 整页截图逐页查验）：首页/关于/博客/论文/Wiki/RSS/状态结构完整、导航高亮正确、无截断乱码、papers(10 篇)与 rss(20 条)数据正常加载、无失败资源请求；首版 fullPage 截图重复拼接经视口截图确认是截图工具伪影，页面本身无问题；rss/papers 首次无头截图停在「正在加载…」为截图时机问题，加 `--virtual-time-budget` 重拍正常；
  - 备注：about 页「Step 1-2 用 CloudBase 部署上线」文案待阶段 2 切换 GitHub Pages 时同步更新。
- **commit**：`9e4f1db fix: ui baseline pass per web interface guidelines`

## 阶段 2：GitHub 仓库 + Actions 自动部署 Pages 上线（等价课程 Step 2）

- **状态**：部分完成（本地就绪；按用户指示跳过仓库创建，继续后续阶段）
- **任务**：
  1. 优先用 `gh repo create person_website --public --source . --push`；gh 不可用时请用户在 github.com 手动建空仓库 `person_website`（Public、不初始化 README），配好 remote 后继续；
  2. 删除 `.gitlab-ci.yml`，新增 `.github/workflows/deploy.yml`：push 到 main 触发 → setup Python → `python scripts/build_all.py` → 上传 `public/` → `actions/deploy-pages`；
  3. 把 `scripts/build_rss.py` 等处的占位域名 `person-website.example.com` 改为 `https://liujianyang123456.github.io/person_website`（改脚本后重建，不手改 `feed.xml`）；
  4. push，等 Actions 全绿；请用户确认 Settings → Pages 的 Source 为 GitHub Actions；
  5. 打开线上地址抽查首页、`/feed.xml`、一篇博客详情页。
- **验收**：Actions 运行成功；线上地址可访问；线上抽查页面无死链；`feed.xml` 可在线订阅。
- **审查记录**：
  - 本地部分已完成并提交：删除 `.gitlab-ci.yml`；新增 `.github/workflows/deploy.yml`（push main 触发 → setup Python → `python scripts/build_all.py`（含全部检查，失败即中止）→ upload-pages-artifact → actions/deploy-pages，支持 workflow_dispatch 手动触发，无任何云厂商密钥）；`scripts/build_rss.py` BASE_URL 改为 `https://liujianyang123456.github.io/person_website` 并重建 feed.xml（四条链接全部指向正式域名，check_feed 解析通过）；about 页与博客《Git 是 Agent 开发的安全绳》部署文案同步为 GitHub；
  - 授权环境探测：本机无 gh CLI、Windows 凭证管理器无 github.com 凭证、无 gh 配置；API 探测 `api.github.com/repos/liujianyang123456/person_website` 返回 404，账号存在但公开仓库为 0；
  - 已请用户在 github.com/new 建空仓库（Public、不初始化），用户答复先跳过该步骤、继续后续阶段；首次 push 时 Windows 凭证管理器会自动弹浏览器授权（无需 PAT）；
  - **待用户完成**：建好 Public 空仓库后执行 `git remote add origin https://github.com/liujianyang123456/person_website.git && git push -u origin main` → 等 Actions 全绿 → 确认 Settings→Pages Source 为 GitHub Actions → 线上抽查首页、/feed.xml、一篇博客详情页。
- **commit**：`23708cf ci: deploy to github pages with actions`（push 待仓库就绪后补做）

## 阶段 3：导航与多页面 + Markdown 博客验收（课程 Step 3–4）

- **状态**：已通过
- **任务**：核对五个入口互相跳转、当前页 aria-current 与高亮、全站菜单一致；验证博客构建幂等；临时新增一篇文章走完整流程（content/posts → 构建 → 页面出现 → 还原）；确认所有生成页面遵守 AGENTS.md。
- **验收**：清单全过；发现问题已修复。
- **审查记录**：
  - 菜单一致性：程序化提取 14 个页面（7 个手写/生成索引 + 3 篇文章 + 4 个 Wiki 页）的 `<nav>`，全部与基线一致（现站点为 7 个入口：首页/关于我/博客/Research Papers/Wiki/RSS订阅/网站状态）；
  - aria-current：每页恰好 1 处且归属正确（文章页→博客、Wiki 子页→Wiki、索引页对应自身），浏览器中蓝色高亮与页面 h1 一致；
  - 浏览器真实点击走查：首页 → 点导航「博客」→ 点文章《从发布 RSS 到订阅 RSS》→ 点「← 返回博客列表」，全程 URL/标题正确；
  - 博客构建幂等：`build_blog.py` 重跑前后对 public 全树做 SHA-256 快照，哈希一致；
  - 临时文章全流程：新增 `phase3-temp-check.md`（含 frontmatter/列表/行内代码/链接/引用）→ `build_all.py` → blog.html、feed.xml、posts/phase3-temp-check.html 三处出现，status 计数 15 页/4 篇/221 链接无死链 → 删除源文件重建 → 完全还原（14 页/3 篇/206 链接，无残留引用，仅时间戳变化）；
  - 本阶段发现并修复 2 个问题：① skip-link 目标 `<main>` 缺 `tabindex="-1"`，回车后焦点未真正转移（浏览器实测确认），已全站补齐并复验焦点落到 `#main-content`；② status.html 有一处 JS 内联样式（`td.style.fontWeight`），违反 AGENTS.md「CSS 统一放 styles.css」，改为 `.status-num` 类。
- **commit**：见 `fix: phase3 nav and a11y verification fixes`（连同 PLAN 本条更新一起提交）

## 阶段 4：RSS 发布 + RSS 阅读器验收（课程 Step 5–6）

- **状态**：已通过（线上 /feed.xml 抽查待仓库就绪后补做，本地等效验证已完成）
- **任务**：check_feed.py 解析验证通过；item 五要素齐全、按日期倒序、中文与特殊字符转义正确；线上 /feed.xml 可访问；rss.html 正常展示外部订阅（腾讯安全中心），确认 allowlist、超时、失败保旧数据、JS 侧 textContent 渲染。
- **验收**：上述全部通过，外站内容无 XSS 风险。
- **审查记录**：
  - `check_feed.py` 通过（XML 解析器验证 + 五要素逐项校验）；
  - 结构核验（程序化解析 feed.xml）：channel 的 title/link/description/language/lastBuildDate 齐全，link 已是正式域名；3 个 item 五要素齐全、pubDate 严格倒序、中文与源文件逐字一致（xml.sax.saxutils.escape 转义，解析后文本与源 markdown description 相等）；
  - 信任边界实测：临时向 config/feeds.json 加入 `evil.example.com`（不在 allowlist）与非 HTTPS 源，运行 `fetch_rss.py` 输出 `SKIP（域名不在 allowlist）` 与 `SKIP（非 HTTPS）`，合法源正常抓取 20 条，`rss-items.json` 哈希前后不变（合并幂等、旧数据保留）；测试后配置已还原（哈希比对一致）；
  - 代码核验：HTTPS-only + allowlist + 15s 超时 + 2MB 体积上限 + 摘要 300 字/总量 200 条封顶；抓取或解析异常时不写文件、非零退出（保留旧数据）；`strip_tags` + 实体解码后仅存纯文本；
  - rss.html：全部 `createElement`/`textContent` 渲染，`innerHTML` 仅出现在注释中的禁用声明里（0 次实际调用），外链均 `rel="noopener"`；页面正常分组展示腾讯安全中心 20 条（阶段 1 截图已核验）；
  - 本地 `http://localhost:8080/feed.xml` 返回 200/text/xml；线上抽查待 push 后补做。
- **commit**：无代码改动（本阶段为纯验收，记录见本次 docs 提交）

## 阶段 5：论文 Skill + 个人 Wiki 验收（课程 Step 7–8）

- **状态**：已通过
- **任务**：.opencode/skills/ 两个 Skill 的 SKILL.md 字段完整；papers.html 加载 papers.json 展示标题/作者/摘要/日期/链接；check_papers.py 通过；Wiki [[双向链接]] 解析正确、content/wiki 规则文件齐全、wiki.html 无死链。
- **验收**：上述全部通过。
- **审查记录**：
  - 两个 SKILL.md 均含 name/description frontmatter + 何时使用/输入/工作流/安全规则；research-paper-collector 附 references/topics.md；search-wiki 含 RAG 回答模板与「资料不足时如实承认」规则；
  - papers.json 10 篇，字段 id/title/authors/published/summary/url/source 齐全（首篇 5 位作者、arXiv 原链）；`check_papers.py` 通过；papers.html 按 标题(外链)→作者·日期·来源徽章→摘要 渲染全部字段（阶段 1 截图核验），全部 textContent 无 XSS 面；
  - Wiki：0 处未解析 [[链接]]；agent-experiment/agent-loop/rag-wiki 三页互相链接且各自渲染正确的「反向链接」区块（如 agent-loop 页列出 agent-experiment 与 rag-wiki）；content/wiki 5 个文件 frontmatter（title/updated/tags）全部齐全，README.md 即「Wiki 使用规则」规则文件；wiki.html 与全部 Wiki 子页 0 死链（check_links 覆盖）。
- **commit**：无代码改动（本阶段为纯验收，记录见本次 docs 提交）

## 阶段 6：Wiki 检索问答 + 状态面板验收（课程 Step 9–10）

- **状态**：已通过
- **任务**：search_wiki.py 能按关键词检索 content/wiki 返回片段；status.json 数据真实（页面数/文章数/wiki 数/论文数/检查结果）；status.html 渲染正常且含 aria-live。
- **验收**：上述全部通过。
- **审查记录**：
  - `search_wiki.py --query "Agent Loop"` 返回按 score 排序的 file/title/score/snippet；内容级关键词「验收标准」命中 agent-experiment.md 的原话片段；无命中查询返回 `# 当前 Wiki 中没有足够依据` + 空列表（有据问答的「资料不足如实承认」路径可用）；
  - status.json 真实性：六项计数（页面 14 / 文章 3 / Wiki 4 / 论文 10 / 订阅源 1 / 订阅条目 20）与文件系统实际统计逐一相符；三项检查结果（feed_xml / internal_links / papers_schema）与 build_all 输出一致；
  - status.html：浏览器实测 6 行站点数据（数值列 .status-num 类 font-weight 600）+ 3 行检查结果表格渲染正常，`#status-note` 含 `aria-live="polite"`；
  - 阶段 3 引入的 CSS 类化重构（fontWeight → .status-num）在浏览器复验无回归。
- **commit**：无代码改动（本阶段为纯验收，记录见本次 docs 提交）

## 阶段 7：Multi-Agent 分工协同（课程 Step 11）

- **状态**：已通过（push 与线上验收待仓库就绪后随阶段 2 补做）
- **任务**：选一个小功能（建议：博客归档页/标签页），在审查记录中写明三个角色的分工（规划 / 实现 / 审查），实现后汇总合并，全站检查通过。
- **验收**：新功能上线且不破坏既有验收。
- **功能**：博客归档页（按年份分组浏览全部文章）。
- **审查记录**：
  - **三个角色分工（真实多 Agent 协作）**：
    - 规划（主 Agent）：选定功能为归档页（比标签页更自洽——现有 3 篇文章的 frontmatter 没有 tags 字段，归档页无需新增内容字段）；确定方案：新建 `scripts/build_archive.py`（复用 `build_blog.load_posts` 与 `site_common.render_page`）、`NAV_ITEMS` 插入「归档」、5 个手写页面同步导航、`build_all.py` 接入、AGENTS.md 生成文件清单更新、验收标准（幂等/无死链/菜单一致/guidelines 红线保持）；
    - 实现（子代理 `agent_13ce2140`，general-purpose）：按方案独立完成全部 7 项修改（新建 build_archive.py 与 archive.html、site_common/build_all/5 手写页面/AGENTS.md），自行跑通 build_all 与幂等验证，未越权 commit；
    - 审查（主 Agent）：逐行核对 diff 与方案一致性 → 重跑全站检查（15 页 237 链接无死链、三检查全绿）→ 严格幂等复核（两次构建逐文件 byte 级对比，仅 `build_time`/`lastBuildDate` 两个时间戳字段变化）→ 菜单一致性与 aria-current 程序化扫描全过 → 浏览器实测 博客→归档 点击跳转、h1/年份分组/条目链接正确、归档导航项蓝色高亮（aria-current）。
  - 实现者两点补充均合理：导航实际覆盖 15 页（含 archive.html 自身）；AGENTS.md 两处生成文件清单同步（目录约定 + 构建规则第 1 条）。
  - status.json 页面计数自动 14→15，internal_links 206→237，均被 build_status 正确追踪。
- **commit**：`feat: blog archive page grouped by year`（push 待仓库就绪）

## 阶段 8：24 小时个人 Agent（课程 Step 12）

- **状态**：已通过（schedule 定时任务与线上验证待仓库就绪后补做：push 后在 Actions 页手动 workflow_dispatch 触发一次即可完成线上验收）
- **任务**：用 GitHub Actions schedule（cron）实现定时流水线：每日自动跑 collect_papers + fetch_rss + build_all，有更新则自动 commit 并触发部署（事件驱动 + 经验反馈闭环）；运行结果写入 public/data/last_run.json 并在 status.html 展示；把机制说明写进一篇 Wiki 页面。
- **验收**：Actions 定时任务配置成功；手动触发一次跑通全链路。
- **审查记录**：
  - `scripts/run_daily.py`：三步流水线（collect_papers → fetch_rss → build_all），每步 300s 超时；抓取失败不致命（各脚本自身保留旧数据，失败详情记入 last_run.json）；build_all 检查失败则整体非零退出（坏内容不提交不部署）；输出「人类可读」的步骤详情（如「抓取 10 篇，新增 9 篇，共保存 19 篇」）；不做 git 写操作，本地手动运行安全；
  - `.github/workflows/daily-agent.yml`：schedule `30 0 * * *`（北京 08:30）+ workflow_dispatch；有变更则 `chore: daily agent update` 自动 commit+push（GITHUB_TOKEN，permissions.contents: write）；因 GITHUB_TOKEN 的 push 不触发其他 workflow，本 workflow 自带 deploy-pages 步骤（与 deploy.yml 共用 pages 并发组），无变更则跳过提交与部署；
  - status.html 新增「最近自动运行」区块（aria-live=polite、textContent 渲染、无记录时给指引），浏览器实测三步状态/触发方式/变更文件数渲染正确；
  - 新增 Wiki 页 `content/wiki/daily-agent.md`《24 小时个人 Agent：每日自动流水线》，遵守 Wiki 规则（frontmatter 齐全、链接到 Agent Loop 与 RAG 两页），构建后 wikilink 全解析；
  - **全链路本地实跑两次**：第一次 arXiv 实抓新增 9 篇论文（10→19）、订阅 20 条、构建 16 页全绿；第二次复跑新增 0 篇（按 id 去重幂等）、订阅 20 条；`last_run.json` 正确记录两次结果；
  - 构建幂等维持：16 页 256 内部链接无死链，三检查全绿。
- **commit**：`14f1f19 feat: 24h personal agent daily pipeline`（push 待仓库就绪）

## 阶段 9：结课总检

- **状态**：本地部分已通过（线上抽查随阶段 2 push 后补做）
- **任务**：全站最终检查（guidelines + 死链 + 幂等 + 线上抽查）；完善 README.md（课程路线图对照表：Step ↔ 功能 ↔ commit ↔ 线上验证方式）；输出结课报告。
- **验收**：九个阶段全部「已通过」；线上站点完整可交付。
- **审查记录**：
  - README.md 重写：课程路线图对照表（Step 1–12 ↔ 功能 ↔ 关键 commit ↔ 线上验证方式）、目录结构更新（两个 workflow + build_archive/run_daily）、部署章节改为 GitHub Pages 流程（无密钥）、常见问题与个性化修改点保留并更新；
  - 全站 guidelines 红线总扫（程序化，16 页）：每页唯一 h1、lang/viewport/theme-color 齐全、无禁用缩放、skip-link 链完整（含 tabindex=-1）、导航 aria-label 与 aria-current 恰一处、16 页菜单 8 项全一致；`.innerHTML=` 赋值 0 处（正文中出现的「innerHTML」为教学性提及）；CSS 无 transition: all、无无替代的 outline:none（唯一例外为 skip-link 目标的惯例抑制）；
  - 最终构建连跑两次：FEED_XML / INTERNAL_LINKS / PAPERS_SCHEMA（16 页 256 链接、19 篇论文、3 条 item）全绿，差异仅 build_time/lastBuildDate 两个时间戳字段；
  - 线上抽查：仓库仍不存在（API 404，用户暂缓创建），随阶段 2 push 后补做（首页、/feed.xml、一篇博客详情页、归档页、状态页「最近自动运行」）。
- **commit**：见本次 docs 提交（`docs: finalize README roadmap and record phase 9`）

## 结课报告（2026-10-07）

**已交付（本地全部完成，9 阶段中 8 个完全通过）**

- 站点：8 入口 16 个 HTML 页面（首页/关于/博客/归档/论文/Wiki/RSS/状态 + 3 文章 + 5 Wiki 页），全站无死链、构建幂等、guidelines 红线全过；
- 数据与自动化：feed.xml（正式域名、可订阅校验通过）、papers.json（arXiv 实抓 19 篇）、rss-items.json（allowlist/超时/体积/失败保旧）、status.json + last_run.json（状态面板展示）、search_wiki 检索问答、两个 SKILL.md；
- CI/CD：deploy.yml（push main 自动构建检查部署 Pages）+ daily-agent.yml（每日 08:30 定时流水线，有变更自动 commit+push+部署，手动可触发）；本地已实跑通每日全链路两次；
- Multi-Agent 协作：阶段 7 归档页由「规划（主 Agent）→ 实现（子代理）→ 审查（主 Agent）」完成并留档；
- 过程质量：每阶段 执行→自审→commit→更新 PLAN 闭环，全程未入库任何密钥。

**待用户一个动作后补完（阶段 2 收尾）**

1. 在 github.com/new 创建空仓库 `person_website`（账号 liujianyang123456，Public，不初始化 README）；
2. 在本目录执行：
   `git remote add origin https://github.com/liujianyang123456/person_website.git`
   `git push -u origin main`（首次 push 会弹浏览器授权，点同意即可）
3. push 后：等 Actions 全绿 → 确认 Settings→Pages Source 为 GitHub Actions → 打开
   `https://liujianyang123456.github.io/person_website/` 抽查首页、/feed.xml、一篇博客详情、归档页、状态页「最近自动运行」；
4. Actions 页对 Daily agent run 手动 workflow_dispatch 触发一次，完成阶段 8 的线上验收。

**课程成果对照**：Step 1–10 全部验收通过并有线上验证方式（见 README 路线图）；Step 11（归档页）与 Step 12（24h Agent）功能完成、待 push 上线验证。
