import trio
import triogram


def text_message(update):
    return "message" in update and "text" in update["message"]


async def echo(bot):
    """
    Waits for new messages and sends the received text back.
    """
    async with bot.sub(text_message) as updates:
        async for update in updates:
            await bot.api.send_message(
                params={
                    "chat_id": update["message"]["chat"]["id"],
                    "text": update["message"]["text"],
                }
            )


async def echo_once(bot):
    """
    Waits for a new message and sends the received text back exactly once.
    """
    update = await bot.wait(text_message)
    await bot.api.send_message(
        params={
            "chat_id": update["message"]["chat"]["id"],
            "text": update["message"]["text"],
        }
    )


async def main():
    """
    Starts the bot and event handlers.
    """
    bot = triogram.make_bot()
    async with bot, trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(echo, bot)
        nursery.start_soon(echo_once, bot)


if __name__ == "__main__":
    trio.run(main)
