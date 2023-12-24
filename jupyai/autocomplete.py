from enum import Enum

from openai import OpenAI


class TaskType(Enum):
    GENERATE_CODE = "generate_code"
    FIX_CODE = "fix_code"
    MODIFY_CODE = "modify_code"


client = OpenAI()

prompt_generate_code = """
You are a helpful Python code generator. Your job is to generate Python code based on
a command given by the user. You should limit yourself to return Python code, that is,
no markdown and no raw text (Python commends are fine). Your output must be runnable
Python code (comments ok), that is, it should not contain [CODE] or [/CODE] tags.
"""

prompt_fix_code = """
You are a helpful Python code fixer. Your job is to fix Python code based on
a command given by the user. You should limit yourself to return a fixed
Python code, that is, no markdown and no raw text (Python commends are fine). The
user code will be given
between [CODE] and [/CODE] tags. While errors produced by the code will be given
between [ERROR] and [/ERROR] tags. There might be more than one error. Your output must
be runnable Python code (comments ok), that is, it should not contain
[CODE] or [/CODE] tags.
"""


prompt_modify_code = """
You are a helpful Python code modifier. Your job is to modify Python code based on
a command given by the user. You should limit yourself to return an updated
Python code, that is, no markdown and no raw text (Python commends are fine). The
user code will be given between [CODE] and [/CODE] tags. While the user command
will be given between [COMMAND] and [/COMMAND] tags. You must update the code
based on the command. Your output must be runnable
Python code (comments ok), that is, it should not contain [CODE] or [/CODE] tags.
"""


# TODO: pass context from previous cells
# TODO: sanitize output in case it's wrapped into ```
# TODO: handle cases when there is nothing to do:
# - empty cell
# - cell with no command and no errors


def _parse_cell(cell):
    source_lines = cell["source"].split("\n")

    # find first line that's not a comment
    for i, line in enumerate(source_lines):
        if not line.startswith("#"):
            break

    # get the top comment (user's command)
    command = "\n".join(line[1:] for line in source_lines[:i])

    # get remaining lines
    code = "\n".join(source_lines[i:])

    errors = _get_output_errors(cell)

    return command, code, errors


def _get_output_errors(cell):
    return [
        "\n".join(output["traceback"])
        for output in cell.get("output", {}).get("outputs", [])
        if output["output_type"] == "error"
    ]


def parse_command(cell):
    command, code, errors = _parse_cell(cell)

    if errors:
        return TaskType.FIX_CODE, Command(command) + Code(code) + str(Errors(errors))

    if code:
        return TaskType.MODIFY_CODE, Command(command) + Code(code)

    return TaskType.GENERATE_CODE, command


class Component:
    def __add__(self, other):
        return str(self) + "\n" + str(other)


class Command(Component):
    def __init__(self, command: str) -> None:
        self.command = command

    def __str__(self) -> str:
        return f"""
[COMMAND]
{self.command}
[/COMMAND]
"""


class Code(Component):
    def __init__(self, code: str) -> None:
        self.code = code

    def __str__(self) -> str:
        return f"""
[COMMAND]
{self.code}
[/COMMAND]
"""


class Error(Component):
    def __init__(self, error: str) -> None:
        self.error = error

    def __str__(self) -> str:
        return f"""
[ERROR]
{self.error}
[/ERROR]
"""


class Errors(Component):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors

    def __str__(self) -> str:
        return "\n".join([str(Error(error)) for error in self.errors])


def autocomplete(cell):
    print("cell:", cell)
    task_type, command = parse_command(cell)

    if task_type == TaskType.GENERATE_CODE:
        return run_task(prompt_generate_code, command)
    elif task_type == TaskType.FIX_CODE:
        return run_task(prompt_fix_code, command)
    elif task_type == TaskType.MODIFY_CODE:
        return run_task(prompt_modify_code, command)
    else:
        raise ValueError("Unknown task type: " + task_type)


def run_task(system_prompt, command):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": command},
        ],
    )

    output = completion.choices[0].message.content

    return output