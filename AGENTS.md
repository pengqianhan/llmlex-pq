# Repository Guidelines

## Project Structure & Module Organization
- `llmlex/` hosts the core symbolic-regression toolkit (prompt orchestration, fitting routines, response parsing). Treat it as the only importable package surface.
- `tests/` contains the pytest suite; archived scenarios stay under `tests/archive/` and are ignored by default, while `tests/test_data/` provides generated fixtures.
- Top-level scripts such as `basic_usage.py` and the `Examples/` directory illustrate end-to-end runs; keep new demos beside them.
- Configuration assets (prompts, models, and media) live in `prompts/`, `model/`, and `llm_ha_pipline_html/`. Update references when relocating files to avoid stale paths.

## Build, Test, and Development Commands
- `python -m pip install -e .` installs an editable copy with runtime dependencies; run inside a virtualenv.
- `python basic_usage.py` performs a quick smoke test against the default model pipeline.
- `python tests/run_tests.py --no-api` executes the suite, including fixture generation, while skipping remote API calls.
- `python -m pytest tests/test_fit.py -k kan` targets a focused subset when iterating on regressors.

## Coding Style & Naming Conventions
- Follow PEP 8: four-space indentation, lower_snake_case functions, UpperCamelCase classes, and module-level constants in ALL_CAPS.
- Prefer explicit imports from `llmlex` submodules; avoid star imports to keep prompt and fit logic traceable.
- Add docstrings for public entry points and clarify async helpers with short comments when control flow is non-obvious.
- Use logging via the package logger (`logging.getLogger("LLMLEx...")`) instead of print statements for operational output.

## Testing Guidelines
- Pytest is the test runner; API-dependent tests are marked `@pytest.mark.api` and require `OPENROUTER_API_KEY` (loadable from `.env`).
- Regenerate deterministic fixtures through `tests/run_tests.py`, which calls `tests/test_data/generate_test_data.py` before pytest collection.
- Add new tests alongside the relevant module, name them `test_<feature>.py`, and prefer parametrized cases for coverage.

## Commit & Pull Request Guidelines
- Mirror the existing history: imperative, capitalized subject lines under ~70 characters (e.g., “Add kan optimizer warm-start guard”).
- Include a brief body when behavior changes or new dependencies are introduced; note required environment variables explicitly.
- For pull requests, summarize intent, enumerate major changes, link related issues, and cite manual or automated test commands executed.

## API Keys & Configuration
- Store secrets in a local `.env`; never commit keys. Tests read `OPENROUTER_API_KEY`, while application runs may also consult `model/*.yaml`.
- Document any new configuration flags in `readme.md` and ensure defaults degrade gracefully when keys are absent.
