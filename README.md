[![Build Status](https://travis-ci.com/rnovatorov/triogram.svg?branch=master)](https://travis-ci.com/rnovatorov/triogram)
[![codecov](https://codecov.io/gh/rnovatorov/triogram/branch/master/graph/badge.svg)](https://codecov.io/gh/rnovatorov/triogram)

# Triogram

Async Telegram Bot API built with
[asks](https://github.com/theelous3/asks)
and
[trio](https://github.com/python-trio/trio).

## Installation

Stable from PyPI:
```bash
pip install triogram
```

Latest from Github:
```bash
pip install git+https://github.com/rnovatorov/triogram#egg=triogram
```

## Usage

```python
import os

import trio
import triogram


def new_message(update):
    return 'message' in update


async def echo_once(bot):
    """
    Waits for a new message and sends the received text back exactly once.
    """
    update = await bot.wait(new_message)
    await bot.api.send_message(params={
        'chat_id': update['message']['from']['id'],
        'text': update['message']['text']
    })


async def echo(bot):
    """
    Waits for new messages and sends the received text back.
    """
    async with bot.sub(new_message) as updates:
        async for update in updates:
            await bot.api.send_message(params={
                'chat_id': update['message']['from']['id'],
                'text': update['message']['text']
            })


async def main():
    """
    Starts the bot and event handlers.
    """
    bot = triogram.make_bot(token=os.environ['TOKEN'])
    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(echo_once, bot)
        nursery.start_soon(echo, bot)


if __name__ == '__main__':
    trio.run(main)
```

## Links

  - [Telegram Bot API](https://core.telegram.org/bots/api)
  - [Examples](examples)
