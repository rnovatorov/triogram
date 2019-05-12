from contextlib import asynccontextmanager

import trio

from .utils import aclosed


class Dispatcher:

    def __init__(self):
        self._lock = trio.Lock()
        self._send_channels = set()

    async def pub(self, event):
        async with self._lock:
            for send_channel in self._send_channels:
                await send_channel.send(event)

    @aclosed
    async def sub(self, predicate, task_status=trio.TASK_STATUS_IGNORED):
        async with self._open_channel() as recv_channel:
            task_status.started()

            async for event in recv_channel:
                if predicate(event):
                    yield event

    async def wait(self, predicate, **kwargs):
        async with self.sub(predicate, **kwargs) as events:
            async for event in events:
                return event

    @property
    def has_subs(self):
        return len(self._send_channels) != 0

    @asynccontextmanager
    async def _open_channel(self):
        send_channel, recv_channel = trio.open_memory_channel(0)

        async with send_channel, recv_channel:
            async with self._lock:
                self._send_channels.add(send_channel)

            try:
                yield recv_channel

            finally:
                with trio.CancelScope(shield=True):
                    async with self._lock:
                        self._send_channels.remove(send_channel)
