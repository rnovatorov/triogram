import attr

from .api import Api
from .config import Config
from .fanout import Fanout
from .updater import Updater
from .http import make_http


def make_bot(*args, **kwargs):
    config = Config(*args, **kwargs)

    http = make_http(
        token=config.get_token(),
        telegram_api_url=config.telegram_api_url,
        http_timeout=config.http_timeout,
    )
    api = Api(http=http)
    updater = Updater(
        api=api,
        timeout=config.updater_timeout,
        retry_interval=config.updater_retry_interval,
    )
    fanout = Fanout()

    return Bot(http=http, api=api, updater=updater, fanout=fanout)


@attr.s
class Bot:

    _http = attr.ib()
    api = attr.ib()
    _updater = attr.ib()
    _fanout = attr.ib()

    async def run(self):
        while True:
            for update in await self._updater.get_updates():
                await self._fanout.pub(update)

    __call__ = run

    @property
    def sub(self):
        return self._fanout.sub

    async def wait(self, *args, **kwargs):
        async with self.sub(*args, **kwargs) as updates:
            return await updates.receive()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.aclose()

    async def aclose(self):
        await self._http.aclose()
