import asks

from .bot import Bot
from .poller import Poller
from .dispatcher import Dispatcher


def make_bot(api, poller=None, dispatcher=None):
    if poller is None:
        poller = make_poller(api=api)

    if dispatcher is None:
        dispatcher = make_dispatcher()

    return Bot(api=api, poller=poller, dispatcher=dispatcher)


def make_poller(api, session=None, **kwargs):
    if session is None:
        session = make_session()

    return Poller(api=api, session=session, **kwargs)


def make_session(**kwargs):
    return asks.Session(**kwargs)


def make_dispatcher():
    return Dispatcher()
