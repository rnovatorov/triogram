import contextlib

import attr
import trio

from .utils import aclosed


@attr.s
class Dispatcher:

    _lock = attr.ib(factory=trio.Lock)
    _send_channels = attr.ib(factory=set)

    async def pub(self, update):
        async with self._lock:
            for send_channel in self._send_channels:
                await send_channel.send(update)

    @aclosed
    async def sub(self, predicate, task_status=trio.TASK_STATUS_IGNORED):
        async with self._open_channel() as recv_channel:
            task_status.started()

            async for update in recv_channel:
                if predicate(update):
                    yield update

    async def wait(self, predicate, **kwargs):
        async with self.sub(predicate, **kwargs) as updates:
            async for update in updates:
                return update

    @property
    def has_subs(self):
        return len(self._send_channels) != 0

    @contextlib.asynccontextmanager
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
