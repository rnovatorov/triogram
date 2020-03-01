import json
import functools
from http import server
from urllib import parse

import trio
import pytest

from triogram.api import Api
from triogram.http import http_client


TOKEN = "123:ABC"


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

        _, token, method = url.path.split("/")

        if token != f"bot{TOKEN}":
            response = server.HTTPStatus.UNAUTHORIZED
            content = json.dumps({"ok": False, "description": "Unauthorized"})

        elif "error" in params:
            response = server.HTTPStatus.BAD_REQUEST
            content = json.dumps({"ok": False, "description": "Bad Request"})

        else:
            response = server.HTTPStatus.OK
            result = {"method": method, "params": params}
            content = json.dumps({"ok": True, "result": result})

        self.send_response(response)
        self.send_header("Content-Length", len(content))
        self.send_header("Content-Type", "application/json")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(content.encode())


@pytest.fixture(name="httpd")
async def fixture_httpd(nursery, scope="session"):
    httpd = Server(("", 0), Handler)
    nursery.start_soon(
        functools.partial(
            trio.to_thread.run_sync, httpd.serve_forever, cancellable=True
        )
    )
    await httpd.ready.wait()
    yield httpd


@pytest.fixture(name="make_api")
async def fixture_make_api(httpd):
    host, port = httpd.server_address

    def make_api(auth=True):
        token = TOKEN if auth else "123:INVALID"
        http = http_client(token, f"http://{host}:{port}")
        return Api(http)

    yield make_api
