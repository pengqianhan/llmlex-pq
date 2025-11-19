# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LLM-LEx** (Large Language Models Learning Expressions) is a Python library for symbolic regression using vision-capable LLMs. It finds mathematical formulae to fit data by visualizing them as graphs and using LLMs to suggest equations. The project has been extended to support **Hybrid Automata (HA) extraction** from time-series data.

Paper: https://arxiv.org/abs/2505.07956

## Core Architecture

### Project Root Structure
```
/home/phan635/HybridAutomata/baseline_ha/llmlex-pq/
├── llmlex/                 # Core SR library (importable package)
├── Dainarx_code/           # Traditional HA learning (standalone pipeline)
├── prompts/                # LLM prompts and HA format examples
├── tests/                  # Pytest test suite
├── Examples/               # Demo scripts and notebooks
├── learningnotes/          # Development tutorials
├── basic_usage.py          # Simple SR example
├── basic_usage_ha.py       # Simple HA extraction example
└── setup.py                # Package installation
```

### Two Main Workflows

1. **Symbolic Regression (llmlex/)**: LLM-based symbolic regression for mathematical expressions
2. **Hybrid Automata Learning (Dainarx_code/)**: Traditional change-point detection and clustering approach for learning hybrid automata from time-series data

### Key Modules

**llmlex/** - Core symbolic regression toolkit (importable package):
- `llmlex.py`: Main entry points
  - `single_call(client, base64_img, x, y, model, ...)`: Single symbolic regression call
  - `single_call_ha(client, base64_img, state_data, input_data, model, ...)`: Single HA extraction call
  - `run_genetic(client, base64_img, x, y, population_size, num_of_generations, ...)`: Genetic algorithm for SR
  - `run_genetic_ha(client, base64_img, state_data, input_data, ...)`: Genetic algorithm for HA extraction
  - `kan_to_symbolic(model, client, ...)`: Extract symbolic expressions from KAN models
- `llm.py`: API interaction
  - `call_model(client, prompt, base64_img, model, ...)`: Sync LLM call with rate limiting
  - `async_call_model(...)`: Async version for parallel calls
  - `call_model_ha(client, prompt, base64_img, model, ...)`: HA extraction call
  - `call_model_ha_json(...)`: HA extraction with structured JSON output
  - `get_prompt(parent_ansatzes)`: Generate SR prompt
  - `get_prompt_ha(system_name)`: Generate HA prompt
- `response.py`: Response parsing
  - `extract_ansatz(response_content)`: Extract mathematical expression from LLM response
  - `extract_ha(response_content)`: Extract HA dictionary from LLM response
  - `fun_convert(ansatz, x, y)`: Convert ansatz string to callable lambda function
  - `APICallStats`: Statistics tracker for API calls and processing stages
- `fit.py`: Curve fitting
  - `fit_curve(fun, x, y)`: Fit parameters using curve_fit
  - `get_n_chi_squared(y, y_pred)`: Compute normalized chi-squared score
- `images.py`: Visualization
  - `generate_base64_image(fig, ax, x, y)`: Create base64 image from matplotlib figure
  - `generate_base64_image_ha(state_data, input_data, dt, filename)`: Create HA visualization
  - `generate_base64_image_with_parents(fig, ax, x, y, parent_results)`: Include parent curves
- `json_output.py`: Pydantic schemas for structured JSON output (`HybridAutomatonJSON`)

**Dainarx_code/** - Traditional hybrid automata learning:
- `main.py`: Pipeline orchestration
  - `main(json_path, data_path, need_creat, need_plot)`: Main entry point
  - `run(data_list, input_data, config, evaluation)`: Run full HA learning pipeline
  - `get_config(json_path, evaluation)`: Load configuration from JSON
- `CreatData.py`: Generate training data from JSON specifications
  - `creat_data(json_path, data_path, dt, total_time)`: Create trajectories from HA spec
- `HA_evaluation.py`: Evaluate learned HA against test data
  - `ha_evaluation(ha_dict, test_data, ...)`: Evaluate HA performance
- `src/HybridAutomata.py`: Core HA class with mode switching logic
- `src/ChangePoints.py`: Change-point detection using feature extraction
  - `find_change_point(data, input_val, get_feature, w)`: Detect mode transitions
- `src/Clustering.py`: Mode clustering from segmented trajectories
  - `clustering(slice_data, self_loop)`: Cluster trajectory segments into modes
- `src/GuardLearning.py`: Learning transition guards via SVM
  - `guard_learning(slice_data, get_feature, config)`: Learn guard conditions
- `src/BuildSystem.py`: Constructing the final hybrid automaton
  - `build_system(slice_data, adj, get_feature)`: Assemble final HA
- `src/DEConfig.py`: Differential equation configuration and feature extraction
  - `FeatureExtractor`: Extract features for mode identification

**prompts/** - System prompts and examples:
- `system_prompt.md`: Main LLM guidance for HA extraction
- `prompt_ha.py`: Structured prompt templates
- `dict2json.py`: Reference examples for HA JSON format

**tests/** - Pytest suite:
- Real API tests marked with `@pytest.mark.api` (require `OPENROUTER_API_KEY`)
- Run via `tests/run_tests.py` (includes fixture generation)
- `tests/test_data/generate_test_data.py`: Fixture generation script
- `tests/archive/`: Obsolete tests (excluded by default via conftest.py)

**Dainarx_code/automata/** - HA specifications:
- JSON files defining ground-truth hybrid automata
- See `json_readme.md` for format specification
- Used by `CreatData.py` to generate training/test data

**Dainarx_code/data/** - Generated trajectory data:
- Created by `CreatData.py` from automata JSON specs
- Contains `.npz` files with state/input time series
- Regenerated when JSON specs or config change (hash-based)

**learningnotes/** - Development notebooks and tutorials:
- `async_tutorial/`: Async programming examples
- Various demo scripts for features and API usage
- `learning_utils.py`: Utility functions for tutorials

### Data Flow

**Symbolic Regression**:
1. Generate base64 image from (x, y) data via `images.generate_base64_image()`
2. Create prompt with optional parent functions via `llm.get_prompt()`
3. Call LLM via `llm.call_model()` with rate limiting
4. Extract ansatz from response via `response.extract_ansatz()`
5. Convert to lambda function via `response.fun_convert()`
6. Fit parameters via `fit.fit_curve()` using normalized chi-squared
7. For genetic algorithm: iterate with selection based on scores

**Hybrid Automata (LLM-based)**:
1. Load state/input time-series from `.npz` files
2. Generate visualization via `images.generate_base64_image_ha()`
3. Create HA prompt via `llm.get_prompt_ha()`
4. Call LLM via `llm.call_model_ha()` or `llm.call_model_ha_json()` (structured output)
5. Parse JSON response via `response.extract_ha()`
6. Evaluate HA via `Dainarx_code.HA_evaluation.ha_evaluation()`

**Hybrid Automata (Traditional)**:
1. Load trajectories from `data/` (generated via `CreatData.py` from JSON specs in `automata/`)
2. Detect change points via `ChangePoints.find_change_point()`
3. Segment trajectories and cluster modes via `Clustering.clustering()`
4. Learn transition guards via `GuardLearning.guard_learning()`
5. Build final HA via `BuildSystem.build_system()`
6. Evaluate via simulation against test data

## Typical Usage Patterns

### Basic Symbolic Regression
```python
import llmlex
import openai
import numpy as np
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY")
)

# Generate or load data
x = np.linspace(-1, 1, 50)
y = np.sin(np.pi * x) + 0.1 * np.random.randn(50)

# Create visualization
fig, ax = plt.subplots()
ax.scatter(x, y)
base64_img = llmlex.images.generate_base64_image(fig, ax, x, y)

# Single call
result = llmlex.single_call(client, base64_img, x, y, model="models/gemini-flash-latest")
print(f"Best function: {result['ansatz']}, Score: {result['score']}")

# Genetic algorithm (recommended for better results)
populations = llmlex.run_genetic(
    client, base64_img, x, y,
    population_size=5, num_of_generations=3,
    model="models/gemini-flash-latest"
)
best = populations[0][0]  # First generation, best individual
```

### Hybrid Automata Extraction (LLM-based)
```python
# Load time-series data
npz_file = np.load('data_duffing/test_data0.npz')
state_data = npz_file['state']
input_data = npz_file['input']
dt = 0.001

# Generate HA visualization
base64_img_ha = llmlex.images.generate_base64_image_ha(
    state_data, input_data, dt, 'ha_image.png'
)

# Load system prompt
system_prompt = open('prompts/system_prompt.md', 'r').read()

# Extract HA
result_ha = llmlex.single_call_ha(
    client, base64_img_ha, state_data, input_data,
    model="models/gemini-flash-latest",
    system_prompt=system_prompt
)
print(f"HA dict: {result_ha['ha_dict']}")
```

### Traditional HA Learning
```bash
# Navigate to Dainarx_code directory from project root
cd Dainarx_code
python main.py
```

Or programmatically:
```python
import sys
sys.path.append('Dainarx_code')
from main import main

sys, slice_data = main(
    json_path='automata/example.json',
    data_path='data',
    need_creat=True,  # Generate fresh data
    need_plot=True    # Visualize results
)
```

## Build, Test, and Development Commands

### Installation
```bash
# Editable install for development
pip install -e .

# Standard install
pip install .
```

### Testing
```bash
# Run all tests with summary (recommended)
python tests/run_tests.py

# Skip API tests (no cost)
python tests/run_tests.py --no-api

# Run archived tests (normally excluded)
python tests/run_tests.py --run-archived

# Full unittest with verbose output
python -m unittest discover -s tests

# Run specific test module with pytest
python -m pytest tests/test_fit.py -k kan

# Pass additional pytest arguments
python tests/run_tests.py --pytest-args "tests/test_fit.py -v"
```

### Running Examples
```bash
# From project root (/home/phan635/HybridAutomata/baseline_ha/llmlex-pq/):

# Basic symbolic regression
python basic_usage.py

# Hybrid automata extraction (LLM-based)
python basic_usage_ha.py

# Traditional HA learning (navigate to subdirectory first)
cd Dainarx_code
python main.py
# Return to root with: cd ..
```

### Data Generation
Hybrid automata ground truth data is generated from JSON specifications:
```bash
cd Dainarx_code
python CreatData.py  # Reads automata/*.json, outputs to data/
```

## Environment Variables

- `OPENROUTER_API_KEY`: For OpenRouter API access (supports many models)
- `GEMINI_API_KEY`: For direct Google Gemini API access
- `LLMLEX_LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL; default: INFO)
- `LLMLEx_MAX_CALLS_PER_MINUTE`: API rate limit (default: 120)
- `LLMLEx_TEST_REAL_API`: Set to enable real API tests (default: false)
- `LLMLEx_TEST_MAX_CALLS_PER_MINUTE`: Rate limit for tests (default: 10)

Store secrets in `.env` (never commit). Load via `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### API Provider Setup

**OpenRouter** (multiple models):
```python
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
# Models: "openai/gpt-4", "anthropic/claude-3.5-sonnet", etc.
```

**Google Gemini** (direct):
```python
client = openai.OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY")
)
# Models: "models/gemini-flash-latest", "models/gemini-2.5-pro", etc.
```

## Key Conventions

### Code Organization
- All user-facing functionality is exported via `llmlex/__init__.py`
- Use module-level logger: `logger = logging.getLogger("LLMLEx.<module>")`
- Async functions use `execute_async_in_loop()` helper to handle nested event loops
- Rate limiting is enforced via decorators: `@rate_limit_api_call` (sync) and `@async_rate_limit_api_call` (async)

### Hybrid Automata JSON Format
The standard HA representation (see `Dainarx_code/automata/json_readme.md` and `prompts/dict2json.py`):
```python
{
  "automaton": {
    "var": "x1, x2",           # State variables (comma-separated)
    "input": "u1",             # Input variables (optional, comma-separated)
    "mode": [
      {
        "id": 1,
        "eq": "x1[1] = ..., x2[2] = ..."  # ODEs: x[k] = k-th derivative, comma-separated
      }
    ],
    "edge": [
      {
        "direction": "1 -> 2",
        "condition": "x1 >= 5",  # Guard condition (string or lambda)
        "reset": {"x1": ["", "x1"], "x2": ["", "x2"]}  # Reset map (optional)
      }
    ]
  },
  "init_state": [              # Initial states for trajectory generation
    {
      "mode": 1,
      "x1": [0],               # Initial values: [x1[0], x1[1], ...]
      "x2": [0]
    }
  ],
  "config": {
    "dt": 0.01,                # Discrete time step
    "total_time": 10.0,        # Total simulation time
    "order": 3,                # Differential equation order (dimension for traditional learning)
    "window_size": 10,         # Sliding window size for change-point detection
    "clustering_method": "fit", # Clustering method: "fit" (fitting-based) or "dis" (distance-based)
    "minus": false,            # Minimize order in traditional learning
    "need_bias": true,         # Include constant term in fits
    "kernel": "linear",        # SVM kernel for guard learning ("linear", "rbf", "poly", etc.)
    "other_items": ""          # Additional nonlinear/cross terms (see json_readme.md for syntax)
  }
}
```

### Scoring Function
LLM-LEx uses a robust normalized chi-squared metric that handles noise gracefully:
- See `llmlex/fit.py:get_n_chi_squared()` for implementation
- Balances absolute and relative error regimes
- Prevents collapse to zero via MAD-based scaling

### Async Execution
The genetic algorithm supports async mode for parallel population generation:
- Uses `asyncio.Semaphore(10)` to limit concurrent requests
- Falls back to polling approach if `nest_asyncio` unavailable
- Statistics tracked via shared `APICallStats` object
- Set `use_async=True` in `run_genetic()` for parallel API calls

### Genetic Algorithm Population Structure
The genetic algorithm (`run_genetic`, `run_genetic_ha`) returns nested lists:
- Outer list: generations (length = `num_of_generations`)
- Inner list: individuals in each generation (length = `population_size`)
- Each individual is a dict with keys: `'ansatz'`, `'params'`, `'score'`, `'fun'`
- Populations are sorted by score (best first)
- Example access: `populations[generation_idx][individual_idx]['ansatz']`
- Best overall result: `populations[0][0]` (first generation, best score)

### Statistics Tracking
`response.APICallStats` tracks:
- Success/failure counts per processing stage (API call, ansatz extraction, function conversion, curve fitting)
- Detailed error categorization (rate limit, syntax error, convergence failure, etc.)
- Validation issues (scalar output, shape mismatch, NaN/inf values)
- Fitting warnings (sqrt domain errors, covariance estimation failures)

## Testing Guidelines

- Regenerate fixtures via `tests/test_data/generate_test_data.py` (called automatically by `run_tests.py`)
- API tests check against cached expected outputs; update when prompts/models change
- Use `@pytest.mark.api` for tests requiring real API calls
- Mock API responses for unit tests to avoid costs

## Common Pitfalls

1. **Rate Limiting**: Always use `call_model` wrappers (not raw `client.chat.completions.create`); they enforce rate limits
2. **Async Event Loops**: Use `execute_async_in_loop()` to handle Jupyter/nested contexts; don't call `asyncio.run()` directly
3. **Parameter Extraction**: `extract_ansatz()` expects `params[i]` syntax; validate LLM responses carefully
4. **HA JSON Parsing**: LLMs may wrap JSON in code blocks (` ```json ... ``` `); `extract_ha()` handles this
5. **Logging Levels**: Use `logger.debug()` for trace info, `logger.info()` for progress, `logger.error()` for failures
6. **Data Paths**: `Dainarx_code/main.py` expects data in `data/` relative to script location; adjust paths if running from elsewhere
7. **Test Fixture Generation**: Run `python tests/run_tests.py` instead of calling pytest directly to ensure fixtures are regenerated

## Git Workflow

### Branch Structure
- `main`: Main development branch
- `llm_ha_image`: Current working branch for HA image-based extraction features

### Typical Workflow
```bash
# Check current status
git status

# Create feature branch from main
git checkout main
git pull
git checkout -b feature-name

# After changes, commit with descriptive messages
git add <files>
git commit -m "Add feature: brief description"

# Push and create PR to main
git push -u origin feature-name
```

## Related Files

- **AGENTS.md**: Repository guidelines (project structure, commit conventions, testing practices)
- **researchideas.md**: Research notes on methods and experiments
- **Dainarx_code/automata/json_readme.md**: HA JSON format specification (with Chinese comments)
- **prompts/system_prompt.md**: LLM system prompt for HA extraction
- **prompts/dict2json.py**: Reference examples for HA JSON format conversion
