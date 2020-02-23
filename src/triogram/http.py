import logging

import httpx

from .config import TELEGRAM_API_URL, HTTP_TIMEOUT


logger = logging.getLogger(__name__)


class RetryingClient(httpx.AsyncClient):
    async def send(self, *args, **kwargs):
        try:
            return await super().send(*args, **kwargs)
        except KeyError:
            logger.exception("See: https://github.com/encode/httpx/issues/817")
            return await super().send(*args, **kwargs)


def http_client(token, telegram_api_url=TELEGRAM_API_URL, http_timeout=HTTP_TIMEOUT):
    base_url = f"{telegram_api_url}/bot{token}/"
    timeout = httpx.Timeout(http_timeout)
    return RetryingClient(base_url=base_url, timeout=timeout)
