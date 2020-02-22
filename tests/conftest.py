import json
import functools
from http import server
from urllib import parse

import trio
import pytest

from triogram.api import Api
from triogram.http import http_client


class Server(server.HTTPServer):
    def __init__(self, *args, **kwargs):
        self.ready = trio.Event()
        super().__init__(*args, **kwargs)

    def server_activate(self):
        super().server_activate()
        self.ready.set()


class Handler(server.BaseHTTPRequestHandler):
    def do_POST(self):
        url = parse.urlparse(self.path)
        params = dict(parse.parse_qsl(url.query))
        method = url.path.split("/")[-1]
        ok = "error" not in params
        content = json.dumps(
            {
                "ok": ok,
                "result" if ok else "description": {"method": method, "params": params},
            }
        )
        self.send_response(server.HTTPStatus.OK)
        self.send_header("Content-Length", len(content))
        self.send_header("Content-Type", "application/json")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(content.encode())


@pytest.fixture(name="api")
async def fixture_api(nursery):
    httpd = Server(("", 0), Handler)
    nursery.start_soon(
        functools.partial(
            trio.to_thread.run_sync, httpd.serve_forever, cancellable=True
        )
    )
    await httpd.ready.wait()
    host, port = httpd.server_address
    http = http_client("123:ABC", f"http://{host}:{port}")
    yield Api(http)
