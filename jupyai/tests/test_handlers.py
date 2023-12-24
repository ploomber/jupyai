import json


async def test_get_example(jp_fetch):
    # When
    response = await jp_fetch("jupyai", "get-example")

    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "data": "This is /jupyai/get-example endpoint!"
    }