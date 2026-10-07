"""每日自动流水线：collect_papers + fetch_rss + build_all，结果写入 public/data/last_run.json。

设计（事件驱动 + 经验反馈闭环）：
- 论文/订阅抓取失败不致命：脚本自身会保留旧数据，失败原因记入 last_run.json；
- build_all（含全部检查）失败则整体失败并以非零码退出，不产生可部署内容；
- 本脚本不做 git 提交：本地手动运行安全；CI 中由 workflow 判断变更后提交并部署。
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from site_common import PROJECT_ROOT

SCRIPTS = PROJECT_ROOT / "scripts"
OUTPUT = PROJECT_ROOT / "public" / "data" / "last_run.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

STEP_TIMEOUT = 300
DETAIL_LIMIT = 300


def human_detail(script, output):
    """把步骤输出整理成一句人类可读的说明（解析失败则回退到原始尾部）。"""
    lines = [l for l in output.splitlines() if l.strip()]
    last = lines[-1] if lines else ""
    try:
        data = json.loads(last)
    except ValueError:
        return " … ".join(lines[-3:])[:DETAIL_LIMIT] or "完成"
    if script == "collect_papers.py":
        return "抓取 {fetched} 篇，新增 {new} 篇，共保存 {saved} 篇（查询词 {query}）".format(**data)
    if script == "fetch_rss.py":
        return "{feeds} 个订阅源，本次抓取 {fetched} 条，合并后共 {total} 条".format(**data)
    return " … ".join(lines[-3:])[:DETAIL_LIMIT]


def run_step(script, args):
    """运行一个步骤脚本，返回 (ok, detail)。失败不中断后续步骤。"""
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / script)] + args,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=STEP_TIMEOUT, cwd=str(PROJECT_ROOT))
        output = ((proc.stdout or "") + (proc.stderr or "")).strip()
        if proc.returncode == 0:
            return True, human_detail(script, output)
        tail = " … ".join(output.splitlines()[-3:])[:DETAIL_LIMIT]
        return False, "exit {}: {}".format(proc.returncode, tail or "无输出")
    except subprocess.TimeoutExpired:
        return False, "超时（超过 {} 秒）".format(STEP_TIMEOUT)
    except OSError as exc:
        return False, "无法启动：{}".format(exc)


def changed_files():
    """只读的 git status，列出将要产生的变更（本地无 git 时返回空）。"""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--", "public"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30, cwd=str(PROJECT_ROOT))
        if proc.returncode != 0:
            return []
        return [line[3:].strip() for line in (proc.stdout or "").splitlines()
                if line.strip()][:50]
    except (OSError, subprocess.TimeoutExpired):
        return []


def main():
    parser = argparse.ArgumentParser(description="运行每日自动流水线")
    parser.add_argument("--trigger", default="manual",
                        help="触发方式（manual / schedule / workflow_dispatch）")
    args = parser.parse_args()

    steps = {}

    ok, detail = run_step("collect_papers.py",
                          ["--query", 'all:"AI agent"', "--limit", "10"])
    steps["collect_papers"] = {"ok": ok, "detail": detail}
    print("DAILY collect_papers [{}] {}".format("通过" if ok else "失败", detail))

    ok, detail = run_step("fetch_rss.py", [])
    steps["fetch_rss"] = {"ok": ok, "detail": detail}
    print("DAILY fetch_rss [{}] {}".format("通过" if ok else "失败", detail))

    ok, detail = run_step("build_all.py", [])
    steps["build"] = {"ok": ok, "detail": detail}
    print("DAILY build [{}] {}".format("通过" if ok else "失败", detail))

    record = {
        "run_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "trigger": args.trigger,
        "steps": steps,
        "changed_files": changed_files(),
        "ok": steps["build"]["ok"],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("DAILY: last_run.json 已写入（整体{}）".format(
        "通过" if record["ok"] else "失败"))

    if not record["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
