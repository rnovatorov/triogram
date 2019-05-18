import os

import trio
import triogram


def new_message(update):
    return "message" in update


async def send_file(bot):
    """
    Waits for new messages and responds with this file.

    Warning:
        If this file contains any sensitive information
        (such as plain-text tokens), it will be sent as is.
    """
    async with bot.sub(new_message) as updates:
        async for update in updates:
            await bot.api.send_document(
                params={"chat_id": update["message"]["chat"]["id"]},
                files={"document": __file__},
            )


async def main():
    """
    Starts the bot and event handlers.
    """
    token = os.environ["TOKEN"]
    bot = triogram.make_bot(token)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(send_file, bot)


if __name__ == "__main__":
    trio.run(main)
