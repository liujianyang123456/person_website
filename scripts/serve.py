"""本地预览服务器：python scripts/serve.py [端口，默认 8080]

与 `python -m http.server` 等价，但绕开了 Windows 中文主机名环境下
socket.getfqdn 触发 UnicodeDecodeError 的问题（Python 3.8 实测会崩溃）。
"""
import functools
import http.server
import socketserver
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PreviewServer(http.server.ThreadingHTTPServer):
    def server_bind(self):
        # 跳过 http.server.HTTPServer.server_bind 里的 socket.getfqdn
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = "localhost"
        self.server_port = port


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    directory = str(PROJECT_ROOT / "public")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    server = PreviewServer(("127.0.0.1", port), handler)
    print("预览地址: http://localhost:{}/  （Ctrl+C 停止）".format(port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
