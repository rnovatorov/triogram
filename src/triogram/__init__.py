import logging

from .errors import ApiError
from .factories import make_bot


logging.getLogger(__name__).addHandler(logging.NullHandler())
