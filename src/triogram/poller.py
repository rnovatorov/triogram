import attr

from .utils import aclosed


@attr.s
class Poller:

    _api = attr.ib()
    _offset = attr.ib(default=None)
    _timeout = attr.ib(default=25)

    @aclosed
    async def poll(self):
        while True:
            updates = await self._get_updates()
            for update in updates:
                yield update
                self._offset = update['update_id'] + 1

    __call__ = poll

    async def _get_updates(self):
        return await self._api.get_updates(json={
            'offset': self._offset,
            'timeout': self._timeout
        })
