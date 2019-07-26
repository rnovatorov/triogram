import attr

from triogram.poller import Poller


@attr.s
class MockApi:

    _updates = attr.ib()

    async def get_updates(self, *_, **__):
        return next(self._updates)


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
