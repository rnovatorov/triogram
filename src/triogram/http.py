import httpx


def make_http(token, telegram_api_url, http_timeout):
    base_url = f"{telegram_api_url}/bot{token}/"
    timeout = httpx.Timeout(http_timeout)
    return httpx.AsyncClient(base_url=base_url, timeout=timeout)
