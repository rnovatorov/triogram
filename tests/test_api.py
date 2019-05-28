import pytest

from triogram.errors import ApiError


async def test_api(api):
    # Response OK
    response = await api.get_chat_member(params={"chat_id": "@foo", "user_id": 42})
    assert response["method_name"] == "getchatmember"
    assert response["params"]["chat_id"] == "@foo"
    assert response["params"]["user_id"] == "42"

    # Response error
    try:
        await api.send_message(params={"_error": True, "chat_id": 43, "text": "bar"})
    except ApiError as exc:
        response = exc.args[0]
        assert response["method_name"] == "sendmessage"
        assert response["params"]["chat_id"] == "43"
        assert response["params"]["text"] == "bar"
    else:
        pytest.fail()
