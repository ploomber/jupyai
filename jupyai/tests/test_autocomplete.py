from unittest.mock import Mock

import pytest

from jupyai import autocomplete


@pytest.mark.parametrize(
    "cell, expected_command, expected_code, expected_errors",
    [
        [
            {"source": "# generate some code", "id": "first"},
            "generate some code",
            "",
            [],
        ],
        [
            {
                "source": "# generate some code\n # that does something cool",
                "id": "first",
            },
            "generate some code that does something cool",
            "",
            [],
        ],
    ],
)
def test_parse_cell(cell, expected_command, expected_code, expected_errors):
    command, code, errors = autocomplete._parse_cell(cell)

    assert command == expected_command
    assert code == expected_code
    assert errors == expected_errors


@pytest.mark.parametrize(
    "openai_response, expected_output",
    [
        ["x + y", "x + y"],
        ["\n```python\nx + y\n```", "x + y"],
    ],
)
def test_generate_code(monkeypatch, openai_response, expected_output):
    mock_client = Mock()
    mock_completion = Mock(choices=[Mock(message=Mock(content=openai_response))])
    mock_client.chat.completions.create.return_value = mock_completion

    monkeypatch.setattr(autocomplete, "OpenAI", lambda: mock_client)

    response = autocomplete.autocomplete(
        cell={
            "source": "# generate code to add x and y",
            "id": "third",
        },
        sources=[
            {
                "source": "x = 1",
                "id": "first",
                "source": "y = 1",
                "id": "second",
                "source": "# generate code to add x and y",
                "id": "third",
            }
        ],
        model_name="gpt-4",
    )

    assert response == expected_output
    msg_system, msg_user = mock_client.chat.completions.create.call_args.kwargs[
        "messages"
    ]
    assert "code generator" in msg_system["content"]
    assert "generate code to add x and y" in msg_user["content"]
