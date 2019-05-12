import asks

from .errors import ApiError
from .factories import make_api


asks.init('trio')
