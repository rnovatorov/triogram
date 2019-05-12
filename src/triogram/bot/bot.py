class Bot:

    def __init__(self, api, poller, dispatcher):
        self._api = api
        self._poller = poller
        self._dispatcher = dispatcher

    async def run(self):
        async with self._poller() as events:
            async for event in events:
                await self.pub(event)

    __call__ = run

    @property
    def api(self):
        return self._api

    @property
    def pub(self):
        return self._dispatcher.pub

    @property
    def sub(self):
        return self._dispatcher.sub

    @property
    def wait(self):
        return self._dispatcher.wait
