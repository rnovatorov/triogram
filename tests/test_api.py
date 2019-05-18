import pytest

from triogram.errors import ApiError


async def test_api(api):
    # Response OK
    response = await api.get_chat_member(
        json={"_ok": True, "chat_id": "@foo", "user_id": 42}
    )
    assert response["method_name"] == "getchatmember"
    assert response["json"]["chat_id"] == "@foo"
    assert response["json"]["user_id"] == 42

    # Response error
    try:
        await api.send_message(json={"_ok": False, "chat_id": 43, "text": "bar"})
    except ApiError as exc:
        response = exc.args[0]
        assert response["method_name"] == "sendmessage"
        assert response["json"]["chat_id"] == 43
        assert response["json"]["text"] == "bar"
    else:
        pytest.fail()
