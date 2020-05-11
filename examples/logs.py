import logging

import trio
import triogram


def configure_logging():
    """
    Configures `triogram` to log API requests and responses.
    """
    logger = logging.getLogger("triogram")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

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
    bot = triogram.make_bot()

    async with bot, trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(get_me, bot)


if __name__ == "__main__":
    trio.run(main)
