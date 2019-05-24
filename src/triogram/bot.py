import attr

from .api import Api
from .dispatcher import Dispatcher
from .poller import Poller
from .session import make_session


def make_bot(token):
    session = make_session(token=token)
    api = Api(session=session)
    poller = Poller(api=api)
    dispatcher = Dispatcher()
    return Bot(api=api, poller=poller, dispatcher=dispatcher)


@attr.s
class Bot:

    _api = attr.ib()
    _poller = attr.ib()
    _dispatcher = attr.ib()

    async def run(self):
        async with self._poller() as updates:
            async for update in updates:
                await self.pub(update)

    __call__ = run

    @property
    def api(self):
        return self._api

    @property
    def pub(self):
        return self._dispatcher.pub

    @property
    def sub(self):
        return self._dispatcher.sub

    @property
    def wait(self):
        return self._dispatcher.wait
