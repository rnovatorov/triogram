import logging

import httpx


logger = logging.getLogger(__name__)


class RetryingClient(httpx.AsyncClient):
    async def send(self, *args, **kwargs):
        try:
            return await super().send(*args, **kwargs)
        except KeyError:
            logger.exception("See: https://github.com/encode/httpx/issues/817")
            return await super().send(*args, **kwargs)


def make_http(token, telegram_api_url, http_timeout):
    base_url = f"{telegram_api_url}/bot{token}/"
    timeout = httpx.Timeout(http_timeout)
    return RetryingClient(base_url=base_url, timeout=timeout)
