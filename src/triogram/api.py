import logging
import itertools
import contextvars

import attr

from .errors import ApiError
from .logs import ContextVarAdapter


request_id = contextvars.ContextVar("request_id")
logger = ContextVarAdapter(logging.getLogger(__name__), request_id)


@attr.s
class Api:

    _http = attr.ib()
    _request_counter = attr.ib(factory=itertools.count)

    async def __call__(self, method_name, **kwargs):
        self._set_request_id()

        logger.info("> %s %s", method_name, kwargs)
        response = await self._http.post(method_name, **kwargs)
        payload = response.json()

        if payload["ok"]:
            logger.info("< %s", payload)
            return payload["result"]

        logger.error("< %s", payload)
        raise ApiError(payload["description"])

    def __getattr__(self, method_name):
        async def method(**kwargs):
            return await self(method_name.replace("_", ""), **kwargs)

        return method

    def _set_request_id(self):
        request_id.set(next(self._request_counter))
