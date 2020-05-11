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


async def main():
    """
    Gets info about the bot every 5 seconds.
    """
    configure_logging()

    async with triogram.make_bot() as bot:
        while True:
            await bot.api.get_me()
            await trio.sleep(5)


if __name__ == "__main__":
    trio.run(main)
