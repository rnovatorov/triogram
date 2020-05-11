import logging

import attr
import httpx
import trio

from .errors import ApiError, AuthError


logger = logging.getLogger(__name__)


@attr.s
class Updater:

    _api = attr.ib()
    _timeout = attr.ib()
    _retry_interval = attr.ib()
    _offset = attr.ib(default=None)

    @property
    def offset(self):
        return self._offset

    async def get_updates(self):
        while True:
            try:
                return await self._get_updates()
            except AuthError:
                raise
            except ApiError as exc:
                logger.error(
                    "get updates error, will retry after %.1f seconds: %s",
                    self._retry_interval,
                    exc,
                )
                await trio.sleep(self._retry_interval)
            except httpx.TimeoutException as exc:
                logger.warning("get updates timeout, will retry asap: %s", exc)

    async def _get_updates(self):
        updates = await self._api.get_updates(
            params={"offset": self._offset, "timeout": self._timeout}
        )
        if updates:
            self._offset = updates[-1]["update_id"] + 1
        return updates
