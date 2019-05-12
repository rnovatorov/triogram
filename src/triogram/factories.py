import asks

from .api import Api
from .bot import Bot
from .dispatcher import Dispatcher
from .poller import Poller


def make_bot(token):
    session = make_session(token=token)
    api = Api(session=session)
    poller = Poller(api=api)
    dispatcher = Dispatcher()
    return Bot(api=api, poller=poller, dispatcher=dispatcher)


def make_session(
    token,
    base_location='https://api.telegram.org',
    connections=2
):
    return asks.Session(
        base_location=base_location,
        endpoint=f'/bot{token}',
        connections=connections
    )
