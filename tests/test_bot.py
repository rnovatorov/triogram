from unittest import mock

import trio

from triogram.bot import Bot, make_bot
from triogram.dispatcher import Dispatcher


async def test_make_bot():
    token = "123:ABC"
    bot = make_bot(token)
    assert bot.api._session.endpoint == f"/bot{token}"


async def test_bot():
    async def get_updates():
        return [42]

    poller = mock.Mock(get_updates=get_updates)
    dispatcher = Dispatcher()
    bot = Bot(api=None, poller=poller, dispatcher=dispatcher)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)

        async def subscriber(**kwargs):
            async with bot.sub(lambda _: True, **kwargs) as updates:
                assert await updates.receive() == 42
            nursery.cancel_scope.cancel()

        await nursery.start(subscriber)
