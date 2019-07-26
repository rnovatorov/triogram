import attr


@attr.s
class Poller:

    _api = attr.ib()
    _offset = attr.ib(default=None)
    _timeout = attr.ib(default=25)

    async def get_updates(self):
        updates = await self._api.get_updates(
            params={"offset": self._offset, "timeout": self._timeout}
        )
        if updates:
            self._offset = updates[-1]["update_id"] + 1
        return updates
