import trio
import triogram


def text_message(update):
    return "message" in update and "text" in update["message"]


async def send_file(bot):
    """
    Waits for new messages and responds with this file.

    Warning:
        If this file contains any sensitive information
        (such as plain-text tokens), it will be sent as is.
    """
    async with bot.sub(text_message) as updates:
        async for update in updates:
            with open(__file__, "rb") as file:
                await bot.api.send_document(
                    params={"chat_id": update["message"]["chat"]["id"]},
                    files={"document": file},
                )


async def main():
    """
    Starts the bot and event handlers.
    """
    bot = triogram.make_bot()

    async with bot, trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(send_file, bot)


if __name__ == "__main__":
    trio.run(main)
