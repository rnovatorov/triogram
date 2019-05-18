import os
import logging

import trio
import triogram


def configure_logging():
    logger = logging.getLogger("triogram")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(request_id)s %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)


async def get_me(bot):
    """
    Gets info about the bot every 5 seconds.
    """
    while True:
        await bot.api.get_me()
        await trio.sleep(5)


async def main():
    """
    Starts the bot and event handlers.
    """
    configure_logging()
    token = os.environ["TOKEN"]
    bot = triogram.make_bot(token)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(get_me, bot)


if __name__ == "__main__":
    trio.run(main)
