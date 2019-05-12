from .utils import aclosed


class Poller:

    def __init__(self, api, offset=None, timeout=3):
        self.api = api
        self.offset = offset
        self.timeout = timeout

    @aclosed
    async def poll(self):
        while True:
            updates = await self._get_updates()
            for update in updates:
                yield update
                self.offset = update['update_id'] + 1

    __call__ = poll

    async def _get_updates(self):
        return await self.api.getUpdates(json={
            'offset': self.offset,
            'timeout': self.timeout
        })
