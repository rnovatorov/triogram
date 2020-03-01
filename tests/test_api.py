import pytest

from triogram.errors import ApiError, AuthError


async def test_response_ok(make_api):
    api = make_api()
    response = await api.get_chat_member(params={"chat_id": "@foo", "user_id": 42})
    assert response["method"] == "getchatmember"
    assert response["params"]["chat_id"] == "@foo"
    assert response["params"]["user_id"] == "42"


async def test_response_error(make_api):
    api = make_api()
    with pytest.raises(ApiError) as exc:
        await api.send_message(params={"error": True, "chat_id": 43, "text": "bar"})
    assert exc.value.args[0] == "Bad Request"


async def test_auth_error(make_api):
    api = make_api(auth=False)
    with pytest.raises(AuthError):
        await api.get_me()
