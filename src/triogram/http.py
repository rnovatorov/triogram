import httpx


def http_client(token, base_url="https://api.telegram.org"):
    return httpx.AsyncClient(base_url=f"{base_url}/bot{token}/")
