"""全站内部死链检查：扫描 public 下所有 HTML 的 href/src，验证本地目标存在。"""
import re
import sys
from pathlib import Path

from site_common import PROJECT_ROOT

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PUBLIC = PROJECT_ROOT / "public"
ATTR_RE = re.compile(r'(?:href|src)="([^"]+)"')
SKIP_PREFIXES = ("http://", "https://", "mailto:", "data:", "javascript:", "tel:", "//")


def check_target(raw_target, page_path):
    """返回 (ok, 描述)。raw_target 已去掉引号，可能是相对路径或锚点。"""
    target = raw_target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return True, None  # 纯锚点
    if target.startswith(SKIP_PREFIXES):
        return True, None  # 外部链接不检查可达性
    if target.startswith("/"):
        resolved = PUBLIC / target.lstrip("/")
    else:
        resolved = (page_path.parent / target)
    resolved = Path(str(resolved).replace("\\", "/"))
    try:
        resolved = resolved.resolve()
    except OSError:
        return False, raw_target
    if resolved.exists():
        return True, None
    return False, raw_target


def run():
    pages = sorted(PUBLIC.rglob("*.html"))
    broken = []
    checked = 0
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for match in ATTR_RE.finditer(text):
            ok, bad = check_target(match.group(1).strip(), page)
            checked += 1
            if not ok:
                broken.append("{} -> {}".format(page.relative_to(PUBLIC), bad))
    detail = "{} 个页面、{} 个内部链接".format(len(pages), checked)
    if broken:
        return False, "失败", detail + "；死链：" + "; ".join(broken[:10])
    return True, "通过", detail + "，无死链"


def main():
    ok, word, detail = run()
    print("CHECK LINKS [{}] {}".format(word, detail))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
