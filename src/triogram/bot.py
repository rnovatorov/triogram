import attr

from .api import Api
from .dispatcher import Dispatcher
from .poller import Poller
from .http import http_client


def make_bot(token):
    http = http_client(token=token)
    api = Api(http=http)
    poller = Poller(api=api)
    dispatcher = Dispatcher()
    return Bot(http=http, api=api, poller=poller, dispatcher=dispatcher)


@attr.s
class Bot:

    _http = attr.ib()
    api = attr.ib()
    _poller = attr.ib()
    _dispatcher = attr.ib()

    async def run(self):
        async with self._http:
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
