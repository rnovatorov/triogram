from .errors import ApiError


class Api:

    def __init__(self, session, throttler, request_wrapper=None):
        self._session = session
        self._throttler = throttler
        self._request_wrapper = request_wrapper

    async def __call__(self, method_name, **kwargs):
        async def make_request():
            async with self._throttler():
                return await self._session.post(
                    path=f'/{method_name}',
                    **kwargs
                )

        if self._request_wrapper is not None:
            make_request = self._request_wrapper(make_request)

        response = await make_request()
        payload = response.json()

        if payload['ok']:
            return payload['result']

        raise ApiError(payload['description'])

    def __getattr__(self, method_name):
        async def method(**kwargs):
            return await self(method_name, **kwargs)

        return method
