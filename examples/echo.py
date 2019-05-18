import os

import trio
import triogram


def new_message(update):
    return "message" in update


async def echo(bot):
    """
    Waits for new messages and sends the received text back.
    """
    async with bot.sub(new_message) as updates:
        async for update in updates:
            await bot.api.send_message(
                json={
                    "chat_id": update["message"]["from"]["id"],
                    "text": update["message"]["text"],
                }
            )


async def echo_once(bot):
    """
    Waits for a new message and sends the received text back exactly once.
    """
    update = await bot.wait(new_message)
    await bot.api.send_message(
        json={
            "chat_id": update["message"]["from"]["id"],
            "text": update["message"]["text"],
        }
    )


async def main():
    """
    Starts the bot and event handlers.
    """
    token = os.environ["TOKEN"]
    bot = triogram.make_bot(token)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(echo, bot)
        nursery.start_soon(echo_once, bot)


if __name__ == "__main__":
    trio.run(main)
