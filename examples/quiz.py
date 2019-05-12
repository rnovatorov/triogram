import os
import random
import operator

import trio
import triogram


class Quiz:

    def __init__(self, bot, player, size=5, difficulty=10):
        self.bot = bot
        self.player = player
        self.size = size
        self.difficulty = difficulty

    async def __call__(self):
        score = 0
        for question, correct_answer in self.generate_questions():
            await self.send(question)
            if await self.wait_answer() == correct_answer:
                score += 1
        await self.send(f'Your score is {score}/{self.size}.')

    def generate_questions(self):
        questions = []

        for _ in range(self.size):
            a = random.randint(-self.difficulty, self.difficulty)
            b = random.randint(-self.difficulty, self.difficulty)
            op_name, op = random.choice([
                ('+', operator.add),
                ('-', operator.sub)
            ])
            question = f'{a} {op_name} {b} = ?'
            answer = str(op(a, b))
            questions.append((question, answer))

        return questions

    async def send(self, text):
        await self.bot.api.sendMessage(params={
            'chat_id': self.player,
            'text': text
        })

    async def wait_answer(self):
        update = await self.bot.wait(lambda u: (
            'message' in u
            and
            u['message']['from']['id'] == self.player
        ))
        return update['message']['text']


async def handler(bot, command='/quiz'):
    players = set()

    async with trio.open_nursery() as nursery:
        async with bot.sub(lambda u: (
            'message' in u
            and
            u['message']['text'] == command
            and
            u['message']['from']['id'] not in players
        )) as updates:
            async for update in updates:
                player = update['message']['from']['id']

                async def quiz(task_status=trio.TASK_STATUS_IGNORED):
                    players.add(player)
                    task_status.started()
                    await Quiz(bot, player)()
                    players.remove(player)

                await nursery.start(quiz)


async def main():
    token = os.environ['TOKEN']
    bot = triogram.make_bot(token)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        nursery.start_soon(handler, bot)


if __name__ == '__main__':
    trio.run(main)
