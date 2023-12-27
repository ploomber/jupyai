import logging
from enum import Enum
from os import environ

from openai import OpenAI

from jupyai import exceptions

logger = logging.getLogger(__name__)

if environ.get("JUPYAI_DEBUG"):
    # Set the logger's level to DEBUG
    logger.setLevel(logging.DEBUG)

    # Create a console handler with level DEBUG
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)


class TaskType(Enum):
    GENERATE_CODE = "generate_code"
    FIX_CODE = "fix_code"
    MODIFY_CODE = "modify_code"


prompt_generate_code = """
You are a helpful Python code generator. Your job is to generate Python code based on
a command given by the user (wrapped between [COMMAND] [/COMMAND] tags).

You should limit yourself to return Python code, that is,
no markdown and no raw text (Python commends are fine). Your output must be runnable
Python code (comments ok), that is, it should not contain [CODE] or [/CODE] tags.
User's code might refer to existing code. Code that exist in previous lines will
be given between [CODE_PREV] and [/CODE_PREV] tags. Code that exist in following
lines will be given between [CODE_POST] and [/CODE_POST] tags.

When generating output, you must re-use existing variables and only generate new code,
your output should not contain code that already exists in previous lines.
"""

prompt_fix_code = """
You are a helpful Python code fixer. Your job is to fix Python code based on
a command given by the user (wrapped between [COMMAND] [/COMMAND] tags).

You should limit yourself to return a fixed
Python code, that is, no markdown and no raw text (Python commends are fine). The
user code will be given
between [CODE] and [/CODE] tags. While errors produced by the code will be given
between [ERROR] and [/ERROR] tags. There might be more than one error. Your output must
be runnable Python code (comments ok), that is, it should not contain
[CODE] or [/CODE] tags.
User's code might refer to existing code. Code that exist in previous lines will
be given between [CODE_PREV] and [/CODE_PREV] tags. Code that exist in following
lines will be given between [CODE_POST] and [/CODE_POST] tags.

When generating output, you must re-use existing variables and only generate new code,
your output should not contain code that already exists in previous lines.
"""


prompt_modify_code = """
You are a helpful Python code modifier. Your job is to modify Python code based on
a command given by the user  (wrapped between [COMMAND] [/COMMAND] tags).

You should limit yourself to return an updated
Python code, that is, no markdown and no raw text (Python commends are fine). The
user code will be given between [CODE] and [/CODE] tags. While the user command
will be given between [COMMAND] and [/COMMAND] tags. You must update the code
based on the command. Your output must be runnable
Python code (comments ok), that is, it should not contain [CODE] or [/CODE] tags.
User's code might refer to existing code. Code that exist in previous lines will
be given between [CODE_PREV] and [/CODE_PREV] tags. Code that exist in following
lines will be given between [CODE_POST] and [/CODE_POST] tags. 

When generating output, you must re-use existing variables and only generate new code,
your output should not contain code that already exists in previous lines.
"""


def _parse_cell(cell):
    cell_source = cell["source"].strip()

    if not cell_source.replace("#", "").strip():
        raise exceptions.BadInputException("Cell cannot be empty")

    source_lines = cell_source.split("\n")

    # find first line that's not a comment
    for i, line in enumerate(source_lines, start=1):
        if not line.lstrip().startswith("#"):
            break

    # get the top comment (user's command)
    command = " ".join(line.strip()[1:].strip() for line in source_lines[:i])

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


def parse_command(cell, sources):
    command, code, errors = _parse_cell(cell)

    cell_id = cell["id"]
    i = None

    # find the index for the current cell
    for i, source in enumerate(sources):
        if source["id"] == cell_id:
            break

    code_prev = [cell["source"] for cell in sources[:i]]
    code_post = [cell["source"] for cell in sources[i + 1 :]]

    if errors:
        return TaskType.FIX_CODE, Command(command) + str(CodePrev(code_prev)) + str(
            CodePost(code_post)
        ) + str(Errors(errors))

    if code:
        return TaskType.MODIFY_CODE, Command(command) + str(CodePrev(code_prev)) + str(
            CodePost(code_post)
        )

    return TaskType.GENERATE_CODE, Command(command) + str(CodePrev(code_prev)) + str(
        CodePost(code_post)
    )


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


class Error(Component):
    def __init__(self, error: str) -> None:
        self.error = error

    def __str__(self) -> str:
        return f"""
[ERROR]
{self.error}
[/ERROR]
"""


class CodePrev(Component):
    def __init__(self, sources: list[str]) -> None:
        self.sources = sources

    def __str__(self) -> str:
        concatenated = "\n".join(self.sources)
        return f"""
[CODE_PREV]
{concatenated}
[/CODE_PREV]
"""


class CodePost(Component):
    def __init__(self, sources: list[str]) -> None:
        self.sources = sources

    def __str__(self) -> str:
        concatenated = "\n".join(self.sources)
        return f"""
[CODE_POST]
{concatenated}
[/CODE_POST]
"""


class Errors(Component):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors

    def __str__(self) -> str:
        return "\n".join([str(Error(error)) for error in self.errors])


def run_task(system_prompt, command):
    try:
        client = OpenAI()
    except:
        raise exceptions.UnauthorizedException()

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

    output = remove_code_fences(completion.choices[0].message.content)

    return output


def remove_code_fences(code: str) -> str:
    PREFIX, SUFFIX = "```python", "```"

    code = code.strip()

    if code.startswith(PREFIX) and code.endswith(SUFFIX):
        code = code[len(PREFIX) : -len(SUFFIX)]

    return code.strip()


def autocomplete(cell, sources):
    """
    Public API for autocompletion. This is the function that gets called when users
    trigger autocompletion from JupyterLab

    Parameters
    ----------
    cell : dict
        The cell to autocomplete. It must contain a `source` key with the source code
        and an `id` key with the cell's id.

    sources : list[dict]
        The list of all cells in the notebook
    """
    if not sources:
        raise ValueError("Sources cannot be empty")

    task_type, command = parse_command(cell, sources)

    if task_type == TaskType.GENERATE_CODE:
        prompt = prompt_generate_code
    elif task_type == TaskType.FIX_CODE:
        prompt = prompt_fix_code
    elif task_type == TaskType.MODIFY_CODE:
        prompt = prompt_modify_code
    else:
        raise ValueError("Unknown task type: " + task_type)

    logger.debug("Running task %s\nPrompt:\n%sCommand:\n%s", task_type, prompt, command)
    return run_task(prompt, command)
