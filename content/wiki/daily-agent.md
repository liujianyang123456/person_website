---
title: 24 小时个人 Agent：每日自动流水线
updated: 2026-10-07
tags: [agent, automation, 课程笔记]
---

# 24 小时个人 Agent：每日自动流水线

## 我的原话

「网站不该只在我打开电脑时才活着——即使我睡觉，Agent 也应该每天照看它一次。」

## Agent 总结：机制设计

这个网站由一条 GitHub Actions 定时流水线看管（`.github/workflows/daily-agent.yml`），
它把 [[Agent Loop 与我的理解]] 中「接收目标 → 调用工具 → 观察结果」的循环
搬到了每天早上 08:30（北京时间）：

1. **调用工具**：`python scripts/run_daily.py` 依次运行
   `collect_papers.py`（arXiv 论文收集）、`fetch_rss.py`（外部订阅抓取）、
   `build_all.py`（构建 + 全部检查）；
2. **观察结果**：每一步的结果写入 `public/data/last_run.json`，
   status.html 的「最近自动运行」区块展示逐步状态；
3. **决定下一步**：有内容变更 → 自动 commit（`chore: daily agent update`）
   并直接部署 Pages；无变更 → 什么都不做；构建检查失败 → 不提交、不部署，
   Actions 运行标记为红色（问题不会被静默上线）。

## 信任边界（与 [[RAG 与个人 Wiki 问答]] 同源的原则）

- 论文与订阅数据来自外部网络，只作为展示文本（JS 侧 `textContent`）；
- 抓取限定 allowlist、超时与体积上限，失败时保留旧数据；
- `last_run.json` 是每次运行的「经验」：失败原因会被记录并展示，
  形成「运行 → 观察 → 调整」的反馈闭环。

## 怎么验证

- GitHub 仓库的 Actions 页可以看到每日运行的记录（也可手动 workflow_dispatch 触发）；
- status.html 的「最近自动运行」应显示最近一次的时间、触发方式与逐步结果。
