import attr
import httpx
import pytest
import trio

from triogram.errors import ApiError, AuthError
from triogram.poller import Poller


@attr.s
class MockApi:

    _updates = attr.ib()

    async def get_updates(self, *_, **__):
        u = next(self._updates)
        if isinstance(u, Exception):
            raise u
        return u


async def test_auth_error():
    api = MockApi(iter([AuthError()]))
    poller = Poller(api=api)

    with pytest.raises(AuthError):
        await poller.get_updates()


async def test_api_error(autojump_clock):
    api = MockApi(
        iter(
            [
                [{"update_id": 0, "message": "A"}],
                ApiError(),
                [{"update_id": 1, "message": "B"}],
            ]
        )
    )
    poller = Poller(api=api, retry_interval=2)

    updates = await poller.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "A"
    assert poller._offset == 1

    start_time = trio.current_time()

    updates = await poller.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "B"
    assert poller._offset == 2

    end_time = trio.current_time()

    assert 1 < end_time - start_time < 3


async def test_timeout():
    api = MockApi(
        iter(
            [
                [{"update_id": 0, "message": "A"}],
                httpx.TimeoutException(),
                [{"update_id": 1, "message": "B"}],
            ]
        )
    )
    poller = Poller(api=api)

    updates = await poller.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "A"
    assert poller._offset == 1

    updates = await poller.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "B"
    assert poller._offset == 2


async def test_sanity():
    api = MockApi(
        iter(
            [
                [{"update_id": 0, "message": "A"}],
                [{"update_id": 1, "message": "B"}, {"update_id": 2, "message": "B"}],
                [],
                [{"update_id": 3, "message": "C"}],
            ]
        )
    )
    poller = Poller(api=api)

    updates = await poller.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "A"
    assert poller._offset == 1

    updates = await poller.get_updates()
    assert len(updates) == 2
    assert updates[0]["message"] == "B"
    assert updates[1]["message"] == "B"
    assert poller._offset == 3

    updates = await poller.get_updates()
    assert len(updates) == 0
    assert poller._offset == 3

    updates = await poller.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "C"
    assert poller._offset == 4
