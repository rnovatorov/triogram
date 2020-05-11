import contextlib

import attr
import trio


@attr.s
class Fanout:

    _lock = attr.ib(factory=trio.Lock)
    _send_channels = attr.ib(factory=dict)

    async def pub(self, update):
        async with self._lock, trio.open_nursery() as nursery:
            for send_channel, predicate in self._send_channels.items():
                if predicate is None or predicate(update):
                    nursery.start_soon(send_channel.send, update)

    @contextlib.asynccontextmanager
    async def sub(self, predicate=None, buffer=0, task_status=trio.TASK_STATUS_IGNORED):
        async with self._open_channel(predicate, buffer) as recv_channel:
            task_status.started()
            yield recv_channel

    @property
    def has_subs(self):
        return len(self._send_channels) != 0

    @contextlib.asynccontextmanager
    async def _open_channel(self, predicate, buffer):
        send_channel, recv_channel = trio.open_memory_channel(buffer)

        async with send_channel, recv_channel:
            async with self._lock:
                self._send_channels[send_channel] = predicate

            try:
                yield recv_channel

            finally:
                with trio.CancelScope(shield=True):
                    async with self._lock:
                        del self._send_channels[send_channel]
