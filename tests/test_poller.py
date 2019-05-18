from triogram.poller import Poller


class MockApi:
    def __init__(self, updates):
        self._updates = iter(updates)

    async def get_updates(self, *_, **__):
        return next(self._updates)


async def test_sanity():
    api = MockApi(
        updates=[
            [{"update_id": 0, "message": "A"}],
            [{"update_id": 1, "message": "B"}, {"update_id": 2, "message": "B"}],
            [{"update_id": 3, "message": "C"}],
        ]
    )
    poller = Poller(api=api)

    async with poller() as updates:
        assert (await updates.__anext__())["message"] == "A"
        assert poller._offset is None

        assert (await updates.__anext__())["message"] == "B"
        assert poller._offset == 1

        assert (await updates.__anext__())["message"] == "B"
        assert poller._offset == 2

        assert (await updates.__anext__())["message"] == "C"
        assert poller._offset == 3
