from functools import wraps

import trio


def on(exceptions, attempts=2, delay=0):

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None

            for _ in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    await trio.sleep(delay)

            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
