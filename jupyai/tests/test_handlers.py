import json


import pytest
from tornado.httpclient import HTTPClientError


async def test_autocomplete(jp_fetch):
    with pytest.raises(HTTPClientError) as e:
        await jp_fetch(
            "jupyai",
            "autocomplete",
            method="POST",
            body=json.dumps(
                {
                    "cell": {
                        "source": "print('hello')",
                        "id": "cellid",
                    },
                    "sources": [
                        {"source": "print('hello')", "id": "cellid"},
                        {"source": "x = 1", "id": "anotherid"},
                    ],
                    "model_name": "gpt-4",
                }
            ),
        )

    assert e.value.code == 401
