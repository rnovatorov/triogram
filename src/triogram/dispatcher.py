import contextlib

import attr
import trio


@attr.s
class Dispatcher:

    _lock = attr.ib(factory=trio.Lock)
    _send_channels = attr.ib(factory=dict)

    async def pub(self, update):
        async with self._lock:
            for send_channel, predicate in self._send_channels.items():
                if predicate(update):
                    try:
                        send_channel.send_nowait(update)
                    except trio.WouldBlock:
                        pass

    @contextlib.asynccontextmanager
    async def sub(self, predicate, task_status=trio.TASK_STATUS_IGNORED):
        async with self._open_channel(predicate) as recv_channel:
            task_status.started()
            yield recv_channel

    @property
    def has_subs(self):
        return len(self._send_channels) != 0

    @contextlib.asynccontextmanager
    async def _open_channel(self, predicate):
        send_channel, recv_channel = trio.open_memory_channel(0)

        async with send_channel, recv_channel:
            async with self._lock:
                self._send_channels[send_channel] = predicate

            try:
                yield recv_channel

            finally:
                with trio.CancelScope(shield=True):
                    async with self._lock:
                        del self._send_channels[send_channel]
