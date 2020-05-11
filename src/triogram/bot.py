import os

import attr

from .api import Api
from .dispatcher import Dispatcher
from .poller import Poller
from .http import make_http


def make_bot(
    token=None,
    token_env_var="TRIOGRAM_TOKEN",
    telegram_api_url="https://api.telegram.org",
    http_timeout=50.0,
    poller_timeout=25.0,
    poller_retry_interval=1.0,
):
    if token is None:
        token = os.environ[token_env_var]

    http = make_http(
        token=token, telegram_api_url=telegram_api_url, http_timeout=http_timeout
    )
    api = Api(http=http)
    poller = Poller(
        api=api, timeout=poller_timeout, retry_interval=poller_retry_interval
    )
    dispatcher = Dispatcher()

    return Bot(http=http, api=api, poller=poller, dispatcher=dispatcher)


@attr.s
class Bot:

    _http = attr.ib()
    api = attr.ib()
    _poller = attr.ib()
    _dispatcher = attr.ib()

    async def run(self):
        while True:
            for update in await self._poller.get_updates():
                await self._dispatcher.pub(update)

    __call__ = run

    @property
    def sub(self):
        return self._dispatcher.sub

    async def wait(self, *args, **kwargs):
        async with self.sub(*args, **kwargs) as updates:
            return await updates.receive()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.aclose()

    async def aclose(self):
        await self._http.aclose()
