import logging
import itertools
import contextvars

import attr

from .errors import ApiError, AuthError


request_id = contextvars.ContextVar("request_id")

logger = logging.getLogger(__name__)


@attr.s
class Api:

    _http = attr.ib()
    _request_counter = attr.ib(factory=itertools.count)

    async def __call__(self, method_name, **kwargs):
        req_id = self._set_request_id()

        logger.info("> %d %s %s", req_id, method_name, kwargs)
        response = await self._http.post(method_name, **kwargs)
        payload = response.json()

        if payload["ok"]:
            logger.info("< %d %s", req_id, payload)
            return payload["result"]

        logger.error("< %d %s", req_id, payload)
        description = payload["description"]

        if response.status_code == 401:
            raise AuthError(description)

        raise ApiError(description)

    def __getattr__(self, method_name):
        async def method(**kwargs):
            return await self(method_name.replace("_", ""), **kwargs)

        return method

    def _set_request_id(self):
        value = next(self._request_counter)
        request_id.set(value)
        return value
