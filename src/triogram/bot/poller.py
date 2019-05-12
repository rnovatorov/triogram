from urllib.parse import urlencode

from .utils import aclosed


ACT = 'a_check'

ERRNO_HISTORY_OUTDATED = 1
ERRNO_KEY_EXPIRED = 2
ERRNO_DATA_LOST = 3


class Poller:

    def __init__(self, api, session, wait=25):
        self.api = api
        self.session = session
        self.wait = wait

        self.server = None
        self.key = None
        self.ts = None

        self._group_id = None

    @aclosed
    async def poll(self):
        await self._init()

        while True:
            events = await self._wait_events()
            for event in events:
                yield event

    __call__ = poll

    async def _init(self):
        self._group_id = await self._get_group_id()
        config = await self._get_config()

        self.server = config['server']
        self.key = config['key']
        self.ts = config['ts']

    async def _wait_events(self):
        url = self._make_url()
        response = await self.session.get(url)
        payload = response.json()

        try:
            errno = payload['failed']
        except KeyError:
            self.ts = payload['ts']
            return payload['updates']

        if errno == ERRNO_HISTORY_OUTDATED:
            self.ts = payload['ts']

        elif errno == ERRNO_KEY_EXPIRED:
            config = await self._get_config()
            self.key = config['key']

        elif errno == ERRNO_DATA_LOST:
            config = await self._get_config()
            self.key = config['key']
            self.ts = config['ts']

        else:
            raise RuntimeError(f'Unexpected errno: {errno}')

        return []

    async def _get_group_id(self):
        groups = await self.api.groups.getById()
        return groups[0]['id']

    async def _get_config(self):
        assert self._group_id is not None

        return await self.api.groups.getLongPollServer(
            group_id=self._group_id
        )

    def _make_url(self):
        query = urlencode({
            'act': ACT,
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait
        })
        return '?'.join([self.server, query])
