# Contributing

Thanks for helping improve Deep Research Agent.

## Local setup

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Run `pip install -e ".[dev]"`.
4. Copy `.env.example` to `.env` and configure provider keys for end-to-end use.

## Before opening a pull request

- Keep provider calls behind the service layer so they can be mocked.
- Add or update tests for behavior changes.
- Run `ruff check .`, `ruff format --check .`, and `pytest -q`.
- Never include API keys, real user research, or generated database files.
- Describe user-visible changes and new configuration in the README.

## Pull requests

Keep changes focused. Include the motivation, implementation summary, and validation performed. For UI changes, include a screenshot when practical.
