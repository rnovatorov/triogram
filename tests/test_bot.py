import os
import contextlib
from unittest import mock

import trio

from triogram.bot import Bot, make_bot
from triogram.dispatcher import Dispatcher
from triogram.config import TOKEN_ENV_VAR


async def test_make_bot():
    token = "123:ABC"
    bot = make_bot(token)
    assert bot.api._http.base_url.path == f"/bot{token}/"


async def test_make_bot_token_from_env():
    token = "123:ABC"
    with mock.patch.dict(os.environ, {TOKEN_ENV_VAR: token}):
        bot = make_bot()
    assert bot.api._http.base_url.path == f"/bot{token}/"


async def test_wait():
    async def get_updates():
        return [42]

    http = contextlib.AsyncExitStack()
    api = None
    poller = mock.Mock(get_updates=get_updates)
    dispatcher = Dispatcher()
    bot = Bot(http=http, api=api, poller=poller, dispatcher=dispatcher)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)

        async def waiter(**kwargs):
            assert await bot.wait(**kwargs) == 42
            nursery.cancel_scope.cancel()

        await nursery.start(waiter)
