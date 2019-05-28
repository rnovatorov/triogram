import os
import random
import operator
import contextlib

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
            await self.send(question)

            if await self.wait_answer() == correct_answer:
                score += 1

        await self.send(f"Your score is {score}/{self.size}.")

    def generate_questions(self):
        questions = []

        for _ in range(self.size):
            a, b = [random.randint(-self.difficulty, self.difficulty) for _ in range(2)]
            op_name, op = random.choice([("+", operator.add), ("-", operator.sub)])
            question = f"{a} {op_name} {b} = ?"
            answer = str(op(a, b))
            questions.append((question, answer))

        return questions

    async def send(self, text):
        await self.bot.api.send_message(params={"chat_id": self.player, "text": text})

    async def wait_answer(self):
        update = await self.bot.wait(
            lambda u: ("message" in u and u["message"]["from"]["id"] == self.player)
        )
        return update["message"]["text"]


@attr.s
class Handler:

    bot = attr.ib()
    command = attr.ib(default="/quiz")
    players = attr.ib(factory=set)

    async def __call__(self):
        async with trio.open_nursery() as nursery:
            async with self.bot.sub(self.predicate) as updates:
                async for update in updates:
                    player = update["message"]["from"]["id"]
                    await nursery.start(self.quiz, player)

    def predicate(self, update):
        if "message" not in update:
            return False

        return (
            update["message"]["text"].startswith(self.command)
            and update["message"]["from"]["id"] not in self.players
        )

    async def quiz(self, player, task_status=trio.TASK_STATUS_IGNORED):
        with self.player_scope(player):
            task_status.started()
            quiz = Quiz(self.bot, player)
            await quiz()

    @contextlib.contextmanager
    def player_scope(self, player):
        self.players.add(player)
        try:
            yield
        finally:
            self.players.remove(player)


async def main():
    """
    Starts the bot and event handlers.
    """
    token = os.environ["TOKEN"]
    bot = triogram.make_bot(token)
    handler = Handler(bot)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(handler)


if __name__ == "__main__":
    trio.run(main)
