import httpx

from .config import TELEGRAM_API_URL, HTTP_TIMEOUT


def http_client(token, telegram_api_url=TELEGRAM_API_URL, http_timeout=HTTP_TIMEOUT):
    base_url = f"{telegram_api_url}/bot{token}/"
    timeout = httpx.Timeout(http_timeout)
    return httpx.AsyncClient(base_url=base_url, timeout=timeout)
