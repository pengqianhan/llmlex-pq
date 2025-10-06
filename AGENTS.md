# Repository Guidelines

## Project Structure & Module Organization
- `llmlex/`: core Python package (symbolic fitting, LLM bridges, image helpers). Public imports are exported via `llmlex/__init__.py`.
- `tests/`: pytest suite and runners (see `tests/run_tests.py`); legacy scenarios in `tests/archive/`.
- `Examples/`: notebooks and figures for reproducible case studies; store heavy assets here, not in the package.
- `model/`: cached KAN checkpoints used by notebooks; avoid edits outside controlled experiments.

## Build, Test, and Development Commands
- Create env and install locally: `python -m venv venv && source venv/bin/activate && pip install -e .`.
- Update dependencies after edits: `pip install -r requirements.txt`.
- Run main regression suite (no API): `python tests/run_tests.py --no-api`. Drop `--no-api` to exercise OpenRouter calls (requires `OPENROUTER_API_KEY`).
- Quick test loops: `python -m pytest tests -k "<pattern>" -v`. Include `tests/archive/` when validating legacy behaviors.

## Coding Style & Naming Conventions
- Follow PEP 8: 4-space indentation, `lowercase_underscore` for modules/functions, `CapWords` for classes.
- Prefer explicit type hints and docstrings mirroring `llmlex/fit.py`; document non-trivial math inline.
- Favor pure functions and vectorized NumPy/JAX operations; guard optional imports and API usage behind feature flags.
- Use descriptive logger names, e.g., `logging.getLogger("LLMLEx.fit")`.
- No enforced formatter is configured; match existing style and keep diffs minimal.

## Testing Guidelines
- Pytest drives coverage. Place new tests under a mirrored path in `tests/` and name files `test_<feature>.py`.
- Regenerate fixtures via `tests/test_data/generate_test_data.py` instead of checking in manual data.
- API-dependent cases must skip automatically when `OPENROUTER_API_KEY` is absent; always honor the `--no-api` flag.

## Commit & Pull Request Guidelines
- Commit messages: concise, imperative (e.g., `Add basic usage example for symbolic regression with LLM`).
- PRs: link related issues, summarize functional impact, and note assets touched in `Examples/` or `model/`.
- Confirm `python tests/run_tests.py --no-api` before requesting review; attach screenshots/plots when notebook visuals change; call out follow-ups explicitly.

## Security & Configuration Tips
- Use a `.env` for secrets (OpenRouter keys). `python-dotenv` is wired in `tests/run_tests.py`; never commit secrets.
- Review notebooks to ensure outputs don’t leak credentials; prune large intermediates from `model/` unless required.

