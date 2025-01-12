import attr
import httpx
import pytest
import trio
import triogram


@attr.s
class MockApi:

    _updates = attr.ib()

    async def get_updates(self, *_, **__):
        u = next(self._updates)
        if isinstance(u, Exception):
            raise u
        return u


def make_updater(api, retry_interval=1.0):
    return triogram.Updater(api=api, timeout=25.0, retry_interval=retry_interval)


async def test_auth_error():
    api = MockApi(iter([triogram.AuthError()]))
    updater = make_updater(api)

    with pytest.raises(triogram.AuthError):
        await updater.get_updates()


async def test_retry_on_error(autojump_clock):
    api = MockApi(
        iter(
            [
                httpx.NetworkError("network error occurred"),
                [{"update_id": 0, "message": "A"}],
                triogram.ApiError(),
                [{"update_id": 1, "message": "B"}],
            ]
        )
    )
    retry_interval = 1.0
    updater = make_updater(api, retry_interval=retry_interval)

    start_time = trio.current_time()
    updates = await updater.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "A"
    assert updater.offset == 1
    end_time = trio.current_time()
    assert end_time - start_time == pytest.approx(retry_interval)

    start_time = trio.current_time()
    updates = await updater.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "B"
    assert updater.offset == 2
    end_time = trio.current_time()
    assert end_time - start_time == pytest.approx(retry_interval)


async def test_timeout():
    api = MockApi(
        iter(
            [
                httpx.ConnectTimeout("connection timed out"),
                [{"update_id": 0, "message": "A"}],
                httpx.ReadTimeout("read timed out"),
                httpx.WriteTimeout("write timed out"),
                [{"update_id": 1, "message": "B"}],
            ]
        )
    )
    updater = make_updater(api)

    updates = await updater.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "A"
    assert updater.offset == 1

    updates = await updater.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "B"
    assert updater.offset == 2


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
    updater = make_updater(api)

    updates = await updater.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "A"
    assert updater.offset == 1

    updates = await updater.get_updates()
    assert len(updates) == 2
    assert updates[0]["message"] == "B"
    assert updates[1]["message"] == "B"
    assert updater.offset == 3

    updates = await updater.get_updates()
    assert len(updates) == 0
    assert updater.offset == 3

    updates = await updater.get_updates()
    assert len(updates) == 1
    assert updates[0]["message"] == "C"
    assert updater.offset == 4
