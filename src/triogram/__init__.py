import logging

from .bot import make_bot
from .errors import ApiError


logging.getLogger(__name__).addHandler(logging.NullHandler())
