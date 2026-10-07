"""统一构建入口：生成博客 / Wiki / RSS -> 执行全部检查 -> 生成状态数据。

任何检查失败都以非零码退出（本地提示、CI 中止部署）。
"""
import sys

import build_blog
import build_rss
import build_status
import build_wiki
import check_feed
import check_links
import check_papers

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    build_blog.main()
    build_wiki.main()
    build_rss.main()

    checks = {}
    failed = False
    for name, module in (("feed_xml", check_feed),
                         ("internal_links", check_links),
                         ("papers_schema", check_papers)):
        ok, word, detail = module.run()
        checks[name] = {"status": word, "detail": detail}
        print("CHECK {} [{}] {}".format(name.upper(), word, detail))
        if not ok:
            failed = True

    build_status.main(checks=checks)

    if failed:
        print("BUILD ALL: 存在失败的检查")
        sys.exit(1)
    print("BUILD ALL: 完成")


if __name__ == "__main__":
    main()
