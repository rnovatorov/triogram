import attr

from .errors import ApiError


@attr.s
class Api:

    _session = attr.ib()

    async def __call__(self, method_name, **kwargs):
        response = await self._session.post(path=f'/{method_name}', **kwargs)
        payload = response.json()

        if payload['ok']:
            return payload['result']

        raise ApiError(payload['description'])

    def __getattr__(self, method_name):
        async def method(**kwargs):
            return await self(method_name.replace('_', ''), **kwargs)

        return method
