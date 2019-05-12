from .errors import ApiError


class Api:

    def __init__(self, access_token, version, session, throttler,
                 request_wrapper=None):
        self._access_token = access_token
        self._version = version
        self._session = session
        self._throttler = throttler
        self._request_wrapper = request_wrapper

    async def __call__(self, method_name, **params):
        async def make_request():
            async with self._throttler():
                return await self._session.get(
                    path=f'/{method_name}',
                    params={**self._meta_params, **params}
                )

        if self._request_wrapper is not None:
            make_request = self._request_wrapper(make_request)

        response = await make_request()
        payload = response.json()

        try:
            return payload['response']
        except KeyError:
            raise ApiError(payload['error']) from None

    def __getattr__(self, key):
        return MethodGroup(name=key, api=self)

    @property
    def _meta_params(self):
        return {
            'access_token': self._access_token,
            'v': self._version,
        }


class MethodGroup:

    def __init__(self, name, api):
        self.name = name
        self.api = api

    def __getattr__(self, key):
        return Method(name=key, group=self)


class Method:

    def __init__(self, name, group):
        self.name = name
        self.group = group

    @property
    def full_name(self):
        return f'{self.group.name}.{self.name}'

    async def __call__(self, **params):
        return await self.group.api(self.full_name, **params)
