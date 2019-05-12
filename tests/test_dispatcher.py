from unittest.mock import Mock

import trio
import pytest

from triogram.dispatcher import Dispatcher


TEST_EVENT = {
    'type': 'test_type',
    'object': 'test_object'
}


@pytest.fixture()
async def dispatcher():
    return Dispatcher()


async def test_one_waiter(dispatcher, autojump_clock):
    predicate = Mock()

    async def subscriber(**kwargs):
        event = await dispatcher.wait(predicate, **kwargs)
        assert event == TEST_EVENT

    async with trio.open_nursery() as nursery:
        await nursery.start(subscriber)
        assert dispatcher.has_subs
        await dispatcher.pub(TEST_EVENT)

    assert not dispatcher.has_subs

    predicate.assert_called_once_with(TEST_EVENT)


async def test_multiple_waiters(dispatcher, autojump_clock):
    predicate = Mock()
    n_subscribers = 4

    async def subscriber(**kwargs):
        event = await dispatcher.wait(predicate, **kwargs)
        assert event == TEST_EVENT

    async with trio.open_nursery() as nursery:
        for _ in range(n_subscribers):
            await nursery.start(subscriber)

        assert dispatcher.has_subs
        await dispatcher.pub(TEST_EVENT)

    assert not dispatcher.has_subs

    predicate.assert_called_with(TEST_EVENT)
    assert predicate.call_count == n_subscribers


async def test_wait_cancellation(dispatcher, autojump_clock):
    predicate = lambda _: False
    timeout = 4

    async def subscriber(**kwargs):
        with trio.move_on_after(timeout):
            await dispatcher.wait(predicate, **kwargs)

    async with trio.open_nursery() as nursery:
        await nursery.start(subscriber)
        assert dispatcher.has_subs
        await dispatcher.pub(TEST_EVENT)

    assert not dispatcher.has_subs


async def test_one_subscriber(dispatcher, autojump_clock):
    predicate = Mock()

    async def subscriber(**kwargs):
        async with dispatcher.sub(predicate, **kwargs) as events:
            async for event in events:
                assert event == TEST_EVENT
                return

    async with trio.open_nursery() as nursery:
        await nursery.start(subscriber)
        assert dispatcher.has_subs
        await dispatcher.pub(TEST_EVENT)

    assert not dispatcher.has_subs

    predicate.assert_called_once_with(TEST_EVENT)


async def test_multiple_subscribers(dispatcher, autojump_clock):
    predicate = Mock()
    n_subscribers = 4

    async def subscriber(**kwargs):
        async with dispatcher.sub(predicate, **kwargs) as events:
            async for event in events:
                assert event == TEST_EVENT
                return

    async with trio.open_nursery() as nursery:
        for _ in range(n_subscribers):
            await nursery.start(subscriber)

        assert dispatcher.has_subs
        await dispatcher.pub(TEST_EVENT)

    assert not dispatcher.has_subs

    predicate.assert_called_with(TEST_EVENT)
    assert predicate.call_count == n_subscribers


async def test_sub_cancellation(dispatcher, autojump_clock):
    predicate = lambda _: False
    timeout = 4

    async def subscriber(**kwargs):
        with trio.move_on_after(timeout):
            async with dispatcher.sub(predicate, **kwargs) as events:
                async for _ in events:
                    pytest.fail()

    async with trio.open_nursery() as nursery:
        await nursery.start(subscriber)
        await dispatcher.pub(TEST_EVENT)

    assert not dispatcher.has_subs
