from functools import wraps

from async_generator import aclosing


def aclosed(async_gen_func):

    @wraps(async_gen_func)
    def wrapper(*args, **kwargs):
        return aclosing(async_gen_func(*args, **kwargs))

    return wrapper
