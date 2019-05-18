from triogram.factories import make_bot


async def test_make_bot():
    token = "123:ABC"
    bot = make_bot(token)
    assert bot.api._session.endpoint == f"/bot{token}"
