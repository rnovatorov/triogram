import trio

from triogram.utils import aclosed
from triogram.bot import Bot, make_bot
from triogram.dispatcher import Dispatcher


async def test_make_bot():
    token = "123:ABC"
    bot = make_bot(token)
    assert bot.api._session.endpoint == f"/bot{token}"


async def test_bot():
    api = object()
    dispatcher = Dispatcher()

    @aclosed
    async def poller():
        yield 42

    bot = Bot(api=api, poller=poller, dispatcher=dispatcher)

    assert bot.__call__ == bot.run
    assert bot.api == api
    assert bot.pub == dispatcher.pub
    assert bot.sub == dispatcher.sub
    assert bot.wait == dispatcher.wait

    async def subscriber(**kwargs):
        event = await bot.wait(lambda _: True, **kwargs)
        assert event == 42
        nursery.cancel_scope.cancel()

    async with trio.open_nursery() as nursery:
        await nursery.start(subscriber)
        nursery.start_soon(bot)
