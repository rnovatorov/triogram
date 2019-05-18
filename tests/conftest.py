import functools

import trio
import pytest
import flask
from werkzeug import serving

from triogram.factories import make_session
from triogram.api import Api


server_ready = trio.Event()


class Handler(serving.WSGIRequestHandler):

    protocol_version = "HTTP/1.1"


class Server(serving.BaseWSGIServer):
    def server_activate(self):
        super().server_activate()
        server_ready.set()


@pytest.fixture(name="api")
async def fixture_api(nursery):
    app = flask.Flask(__name__)
    token = "123:ABC"

    @app.route(f"/bot{token}/<name>", methods=["POST"])
    def method(name):
        json = flask.request.get_json()
        return flask.jsonify(
            {
                "ok": json["_ok"],
                "result"
                if json["_ok"]
                else "description": {
                    "method_name": name,
                    "json": flask.request.get_json(),
                },
            }
        )

    server = Server(host="localhost", port=0, app=app, handler=Handler)

    nursery.start_soon(
        functools.partial(
            trio.run_sync_in_worker_thread, server.serve_forever, cancellable=True
        )
    )
    await server_ready.wait()

    base_location = f"http://{server.host}:{server.port}"
    session = make_session(token, base_location=base_location)
    api = Api(session=session)

    yield api
