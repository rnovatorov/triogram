import os
import contextlib
from unittest import mock

import trio

import triogram


async def test_make_bot():
    token = "123:ABC"
    bot = triogram.make_bot(token)
    assert bot.api._http.base_url.path == f"/bot{token}/"


async def test_make_bot_token_from_env():
    token = "123:ABC"
    with mock.patch.dict(os.environ, {"TOKEN": token}):
        bot = triogram.make_bot(token_env_var="TOKEN")
    assert bot.api._http.base_url.path == f"/bot{token}/"


async def test_wait():
    async def aclose():
        pass

    http = mock.Mock(aclose=aclose)
    api = None

    async def get_updates():
        return [42]

    updater = mock.Mock(get_updates=get_updates)

    fanout = triogram.Fanout()
    bot = triogram.Bot(http=http, api=api, updater=updater, fanout=fanout)

    async with bot, trio.open_nursery() as nursery:
        nursery.start_soon(bot)

        async def waiter(**kwargs):
            assert await bot.wait(**kwargs) == 42
            nursery.cancel_scope.cancel()

        await nursery.start(waiter)
