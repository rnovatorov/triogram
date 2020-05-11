from unittest import mock

import trio
import pytest

import triogram


TEST_UPDATE = {"type": "test_type", "object": "test_object"}


@pytest.fixture()
async def fanout():
    return triogram.Fanout()


async def test_one_subscriber(fanout, autojump_clock):
    predicate = mock.Mock()

    async def subscriber(**kwargs):
        async with fanout.sub(predicate, **kwargs) as updates:
            assert await updates.receive() == TEST_UPDATE

    async with trio.open_nursery() as nursery:
        await nursery.start(subscriber)
        assert fanout.has_subs
        await fanout.pub(TEST_UPDATE)

    assert not fanout.has_subs

    predicate.assert_called_once_with(TEST_UPDATE)


async def test_multiple_subscribers(fanout, autojump_clock):
    predicate = mock.Mock()
    n_subscribers = 4

    async def subscriber(**kwargs):
        async with fanout.sub(predicate, **kwargs) as updates:
            assert await updates.receive() == TEST_UPDATE

    async with trio.open_nursery() as nursery:
        for _ in range(n_subscribers):
            await nursery.start(subscriber)

        assert fanout.has_subs
        await fanout.pub(TEST_UPDATE)

    assert not fanout.has_subs

    predicate.assert_called_with(TEST_UPDATE)
    assert predicate.call_count == n_subscribers


async def test_buffering(fanout, autojump_clock):
    predicate = mock.Mock()

    async def subscriber(**kwargs):
        async with fanout.sub(predicate, buffer=1, **kwargs) as updates:
            await trio.sleep(3)
            assert await updates.receive() == TEST_UPDATE

    async with trio.open_nursery() as nursery:
        await nursery.start(subscriber)
        assert fanout.has_subs

        with trio.fail_after(1):
            await fanout.pub(TEST_UPDATE)

        with trio.move_on_after(1):
            await fanout.pub(TEST_UPDATE)
            pytest.fail()

    assert not fanout.has_subs


async def test_sub_cancellation(fanout, autojump_clock):
    predicate = lambda _: False
    timeout = 4

    async def subscriber(**kwargs):
        with trio.move_on_after(timeout):
            async with fanout.sub(predicate, **kwargs) as updates:
                await updates.receive()
                pytest.fail()

    async with trio.open_nursery() as nursery:
        await nursery.start(subscriber)
        await fanout.pub(TEST_UPDATE)

    assert not fanout.has_subs


async def test_blocking_subscriber(fanout, autojump_clock):
    predicate = mock.Mock()
    event = trio.Event()

    async def blocking_subscriber(**kwargs):
        async with fanout.sub(predicate, **kwargs) as updates:
            await trio.sleep(1)
            event.set()
            assert await updates.receive() == TEST_UPDATE

    async def non_blocking_subscriber(**kwargs):
        async with fanout.sub(predicate, **kwargs) as updates:
            assert await updates.receive() == TEST_UPDATE
            assert not event.is_set()

    async with trio.open_nursery() as nursery:
        await nursery.start(blocking_subscriber)
        await nursery.start(non_blocking_subscriber)
        await fanout.pub(TEST_UPDATE)

    assert not fanout.has_subs


async def test_no_predicate(fanout, autojump_clock):
    predicate = mock.Mock()

    async def subscriber_with_predicate(**kwargs):
        async with fanout.sub(predicate, **kwargs) as updates:
            assert await updates.receive() == TEST_UPDATE

    async def subscriber_without_predicate(**kwargs):
        async with fanout.sub(**kwargs) as updates:
            assert await updates.receive() == TEST_UPDATE

    async with trio.open_nursery() as nursery:
        await nursery.start(subscriber_with_predicate)
        await nursery.start(subscriber_without_predicate)
        await fanout.pub(TEST_UPDATE)

    assert not fanout.has_subs
    assert predicate.call_count == 1
