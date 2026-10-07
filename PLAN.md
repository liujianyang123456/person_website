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

- **状态**：待执行
- **任务**：
  1. 优先用 `gh repo create person_website --public --source . --push`；gh 不可用时请用户在 github.com 手动建空仓库 `person_website`（Public、不初始化 README），配好 remote 后继续；
  2. 删除 `.gitlab-ci.yml`，新增 `.github/workflows/deploy.yml`：push 到 main 触发 → setup Python → `python scripts/build_all.py` → 上传 `public/` → `actions/deploy-pages`；
  3. 把 `scripts/build_rss.py` 等处的占位域名 `person-website.example.com` 改为 `https://liujianyang123456.github.io/person_website`（改脚本后重建，不手改 `feed.xml`）；
  4. push，等 Actions 全绿；请用户确认 Settings → Pages 的 Source 为 GitHub Actions；
  5. 打开线上地址抽查首页、`/feed.xml`、一篇博客详情页。
- **验收**：Actions 运行成功；线上地址可访问；线上抽查页面无死链；`feed.xml` 可在线订阅。
- **审查记录**：（待填）
- **commit**：（待填，建议 `ci: deploy to github pages with actions`）

## 阶段 3：导航与多页面 + Markdown 博客验收（课程 Step 3–4）

- **状态**：待执行
- **任务**：核对五个入口互相跳转、当前页 `aria-current` 与高亮、全站菜单一致；验证博客构建幂等；临时新增一篇文章走完整流程（`content/posts` → 构建 → 页面出现 → 还原）；确认所有生成页面遵守 AGENTS.md。
- **验收**：清单全过；发现问题已修复。
- **审查记录**：（待填）
- **commit**：（待填）

## 阶段 4：RSS 发布 + RSS 阅读器验收（课程 Step 5–6）

- **状态**：待执行
- **任务**：`check_feed.py` 解析验证通过；item 五要素齐全、按日期倒序、中文与特殊字符转义正确；线上 `/feed.xml` 可访问；`rss.html` 正常展示外部订阅（腾讯安全中心），确认 allowlist、超时、失败保旧数据、JS 侧 `textContent` 渲染。
- **验收**：上述全部通过，外站内容无 XSS 风险。
- **审查记录**：（待填）
- **commit**：（待填）

## 阶段 5：论文 Skill + 个人 Wiki 验收（课程 Step 7–8）

- **状态**：待执行
- **任务**：`.opencode/skills/` 两个 Skill 的 SKILL.md 字段完整；`papers.html` 加载 `papers.json` 展示标题/作者/摘要/日期/链接；`check_papers.py` 通过；Wiki `[[双向链接]]` 解析正确、`content/wiki` 规则文件齐全、`wiki.html` 无死链。
- **验收**：上述全部通过。
- **审查记录**：（待填）
- **commit**：（待填）

## 阶段 6：Wiki 检索问答 + 状态面板验收（课程 Step 9–10）

- **状态**：待执行
- **任务**：`search_wiki.py` 能按关键词检索 `content/wiki` 返回片段；`status.json` 数据真实（页面数/文章数/wiki 数/论文数/检查结果）；`status.html` 渲染正常且含 `aria-live`。
- **验收**：上述全部通过。
- **审查记录**：（待填）
- **commit**：（待填）

## 阶段 7：Multi-Agent 分工协同（课程 Step 11）

- **状态**：待执行
- **任务**：选一个小功能（建议：博客归档页/标签页），在审查记录中写明三个角色的分工（规划 / 实现 / 审查），实现后汇总合并，全站检查通过。
- **验收**：新功能上线且不破坏既有验收。
- **审查记录**：（待填）
- **commit**：（待填）

## 阶段 8：24 小时个人 Agent（课程 Step 12）

- **状态**：待执行
- **任务**：用 GitHub Actions `schedule`（cron）实现定时流水线：每日自动跑 `collect_papers` + `fetch_rss` + `build_all`，有更新则自动 commit 并触发部署（事件驱动 + 经验反馈闭环）；运行结果写入 `public/data/last_run.json` 并在 `status.html` 展示；把机制说明写进一篇 Wiki 页面。
- **验收**：Actions 定时任务配置成功；手动触发一次跑通全链路。
- **审查记录**：（待填）
- **commit**：（待填）

## 阶段 9：结课总检

- **状态**：待执行
- **任务**：全站最终检查（guidelines + 死链 + 幂等 + 线上抽查）；完善 `README.md`（课程路线图对照表：Step ↔ 功能 ↔ commit ↔ 线上验证方式）；输出结课报告。
- **验收**：九个阶段全部「已通过」；线上站点完整可交付。
- **审查记录**：（待填）
- **commit**：（待填）
