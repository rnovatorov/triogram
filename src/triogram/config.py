import os
from typing import Optional

import attr


@attr.s(auto_attribs=True)
class Config:

    token: Optional[str] = None
    token_env_var: str = "TRIOGRAM_TOKEN"
    telegram_api_url: str = "https://api.telegram.org"
    http_timeout: float = 50.0
    updater_timeout: float = 25.0
    updater_retry_interval: float = 1.0

    def get_token(self):
        if self.token is not None:
            return self.token
        return os.environ[self.token_env_var]
