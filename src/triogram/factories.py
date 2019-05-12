import asks
import asks.errors as asks_errors

from . import retry
from .api import Api
from .bot import Bot
from .dispatcher import Dispatcher
from .poller import Poller
from .throttler import Throttler


def make_bot(token):
    session = make_session(token=token)
    api = make_api(session=session)
    poller = make_poller(api=api)
    dispatcher = make_dispatcher()
    return Bot(api=api, poller=poller, dispatcher=dispatcher)


def make_session(
    token,
    base_location='https://api.telegram.org',
    connections=1,
    **kwargs
):
    return asks.Session(
        base_location=base_location,
        endpoint=f'/bot{token}',
        connections=connections,
        **kwargs
    )


def make_api(
    session,
    throttler=None,
    request_wrapper=None
):
    if throttler is None:
        throttler = make_throttler()

    if request_wrapper is None:
        request_wrapper = make_request_wrapper()

    return Api(
        session=session,
        throttler=throttler,
        request_wrapper=request_wrapper
    )


def make_throttler(frequency=3):
    return Throttler(frequency=frequency)


def make_request_wrapper(
    exceptions=asks_errors.BadHttpResponse,
    attempts=2,
    delay=0
):
    return retry.on(
        exceptions=exceptions,
        attempts=attempts,
        delay=delay
    )


def make_poller(api):
    return Poller(api=api)


def make_dispatcher():
    return Dispatcher()
