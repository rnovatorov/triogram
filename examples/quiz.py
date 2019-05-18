import os
import random
import operator

import attr
import trio
import triogram


@attr.s
class Quiz:

    bot = attr.ib()
    player = attr.ib()
    size = attr.ib(default=5)
    difficulty = attr.ib(default=10)

    async def __call__(self):
        score = 0

        for (question, correct_answer) in self.generate_questions():
            await self._send(question)

            if await self._wait_answer() == correct_answer:
                score += 1

        await self._send(f"Your score is {score}/{self.size}.")

    def generate_questions(self):
        questions = []

        for _ in range(self.size):
            a, b = [random.randint(-self.difficulty, self.difficulty) for _ in range(2)]
            op_name, op = random.choice([("+", operator.add), ("-", operator.sub)])
            question = f"{a} {op_name} {b} = ?"
            answer = str(op(a, b))
            questions.append((question, answer))

        return questions

    async def _send(self, text):
        await self.bot.api.send_message(params={"chat_id": self.player, "text": text})

    async def _wait_answer(self):
        update = await self.bot.wait(
            lambda u: ("message" in u and u["message"]["from"]["id"] == self.player)
        )
        return update["message"]["text"]


async def handler(bot, command="/quiz"):
    players = set()

    async with trio.open_nursery() as nursery:
        async with bot.sub(
            lambda u: (
                "message" in u
                and u["message"]["text"] == command
                and u["message"]["from"]["id"] not in players
            )
        ) as updates:
            async for update in updates:
                player = update["message"]["from"]["id"]

                async def quiz(task_status=trio.TASK_STATUS_IGNORED):
                    players.add(player)
                    task_status.started()
                    await Quiz(bot, player)()
                    players.remove(player)

                await nursery.start(quiz)


async def main():
    token = os.environ["TOKEN"]
    bot = triogram.make_bot(token)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(handler, bot)


if __name__ == "__main__":
    trio.run(main)
