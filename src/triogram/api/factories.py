import asks
import asks.errors as asks_errors

from . import retry
from .api import Api
from .throttler import Throttler


def make_api(
    access_token,
    version,
    session=None,
    throttler=None,
    request_wrapper=None
):
    if session is None:
        session = make_session()

    if throttler is None:
        throttler = make_throttler()

    if request_wrapper is None:
        request_wrapper = make_request_wrapper()

    return Api(
        access_token=access_token,
        version=version,
        session=session,
        throttler=throttler,
        request_wrapper=request_wrapper
    )


def make_session(
    base_location='https://api.vk.com',
    endpoint='/method',
    connections=1,
    **kwargs
):
    return asks.Session(
        base_location=base_location,
        endpoint=endpoint,
        connections=connections,
        **kwargs
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
