# Repository Guidelines

## Project Structure & Module Organization
- `llmlex/` contains the core Python package (symbolic fitting, LLM bridges, image helpers); treat it as the authoritative source for imports exported through `llmlex/__init__.py`.
- `tests/` hosts the pytest suite, with utility runners under `tests/run_tests.py` and archived scenarios in `tests/archive/`.
- `Examples/` provides exploratory notebooks and figures for reproducible case studies; keep heavy assets there instead of the package.
- `model/` stores cached KAN checkpoints referenced by notebook workflows; avoid editing outside controlled experiments.

## Build, Test, and Development Commands
- Create an isolated env and install locally: `python -m venv venv && source venv/bin/activate && pip install -e .`.
- Resolve runtime tooling after edits with `pip install -r requirements.txt` when dependencies change.
- Run the main regression suite via `python tests/run_tests.py --no-api`; drop `--no-api` to exercise OpenRouter calls (requires cost-bearing credentials).
- For quick loops, call `python -m pytest tests -k <pattern> -v`; include `tests/archive/` explicitly when validating legacy behaviors.

## Coding Style & Naming Conventions
- Follow PEP 8: four-space indentation, lowercase_underscore module and function names, CapWords for classes, and descriptive logger names (see `logging.getLogger("LLMLEx.*")`).
- Prefer explicit type hints and docstrings mirroring existing modules such as `llmlex/fit.py`; document non-trivial math steps inline.
- Keep functions pure where possible, favor vectorized NumPy/JAX operations, and guard optional imports or API usage behind feature flags.

## Testing Guidelines
- Pytest drives coverage; new features should land with tests under a mirrored path in `tests/` and a descriptive `test_<feature>.py` filename.
- Regenerate fixtures through `tests/test_data/generate_test_data.py` rather than checking in manual data.
- API-dependent cases must skip automatically when `OPENROUTER_API_KEY` is absent; honor the `--no-api` flag in new parametrizations.

## Commit & Pull Request Guidelines
- Match the existing concise, imperative commit style (e.g., `Add basic usage example for symbolic regression with LLM`).
- Reference related issues in the PR description, summarize functional impact, and note any assets touched in `Examples/` or `model/`.
- Confirm `python tests/run_tests.py --no-api` in the PR checklist, attach screenshots or plots when notebook visuals change, and call out follow-up work explicitly.

## Security & Configuration Tips
- Use `.env` for sensitive settings (OpenRouter keys); rely on `python-dotenv` already wired in `tests/run_tests.py` and never commit secrets.
- Review notebooks before pushing to ensure cached outputs do not leak credentials or proprietary data, and prune large intermediate files from `model/` unless required.
