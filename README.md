# JupyAI

[![Github Actions Status](https://github.com/ploomber/jupyai/workflows/Build/badge.svg)](https://github.com/ploomber/jupyai/actions/workflows/build.yml)


JupyAI adds AI capabilities to JupyterLab:

- Code generation (generate code based on a prompt)
- Code modifications (update existing code)
- Code fixing (fix broken code)

## Notes

- The prompts are hardcoded, it'd be better to add an option to customize them
- Only OpenAI is supported for now

PRs welcome!

## Requirements

- JupyterLab >= 4.0.0

## Install

```bash
pip install jupyai
```

## Usage

```bash
# set your OpenAI key
export OPENAI_API_KEY=YOURKEY

# start JupyterLab
jupyter lab
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyai
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)