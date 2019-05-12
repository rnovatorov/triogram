import functools

import async_generator


def aclosed(async_gen_func):

    @functools.wraps(async_gen_func)
    def wrapper(*args, **kwargs):
        return async_generator.aclosing(async_gen_func(*args, **kwargs))

    return wrapper
