# HA_evaluation.py - Hybrid Automaton Evaluation Module

## Overview

The `HA_evaluation.py` module provides a comprehensive framework for evaluating hybrid automata (HA) against ground truth data. It supports simulation, metric computation, and visualization with multiple plotting modes.

**Key Features:**
- **Object-Oriented Design**: Clean class-based architecture for modularity and reusability
- **Comprehensive Metrics**: Both absolute error metrics (RMSE, MAE) and normalized metrics for comparison
- **Flexible Visualization**: Three plotting modes (single, side-by-side, stacked) for trajectory comparison
- **Backward Compatibility**: Original function interfaces preserved for existing code

---

## Architecture

### Class Hierarchy

```
HA_evaluation.py
│
├── TrajectoryPlotter        # Handles all plotting operations
│   ├── plot_single()        # Plot simulated trajectory only
│   ├── plot_side_by_side()  # Overlay original vs simulated
│   ├── plot_stacked()       # Vertically stacked comparison
│   ├── save()               # Save figure to file
│   └── to_base64()          # Convert to base64 string
│
├── HAEvaluator              # Main evaluation orchestrator
│   ├── load_ground_truth()  # Load NPZ data
│   ├── simulate()           # Run HA simulation
│   ├── compute_metrics()    # Calculate error metrics
│   ├── plot()               # Generate visualizations
│   └── evaluate()           # Complete evaluation pipeline
│
└── Wrapper Functions        # Backward-compatible API
    ├── plot_ha()            # Legacy plotting function
    └── ha_evaluation()      # Legacy evaluation function
```

---

## Quick Start

### Basic Usage (New Class-Based API)

```python
import sys
sys.path.insert(0, 'Dainarx_code')
from HA_evaluation import HAEvaluator

# Define hybrid automaton
ha_dict = {
    "automaton": {
        "var": "x1, x2",
        "input": "u1",
        "mode": [
            {
                "id": 1,
                "eq": "x1[1] = x2[0], x2[1] = -0.1*x2[0] - x1[0] - x1[0]**3 + u1"
            }
        ],
        "edge": []
    },
    "config": {
        "dt": 0.001,
        "total_time": 10.0,
        "dim": 2,
        "other_items": ""
    }
}

# Create evaluator
evaluator = HAEvaluator(
    ha_dict=ha_dict,
    npz_file_path='data_duffing/test_data0.npz',
    dt=0.001,
    total_time=10.0
)

# Run complete evaluation
results = evaluator.evaluate(
    save_path='output_dir',
    plot_mode='side_by_side',
    compute_metrics=True,
    return_results=True
)

# Access results
print(f"State RMSE: {results['state_rmse']:.6f}")
print(f"Mode Accuracy: {results['mode_accuracy']:.2%}")
```

### Legacy API (Backward Compatible)

```python
from HA_evaluation import ha_evaluation

# Same ha_dict as above...

results = ha_evaluation(
    data=ha_dict,
    save_path='output_dir',
    dT=0.001,
    times=10.0,
    plot_mode='side_by_side',
    npz_file_path='data_duffing/test_data0.npz',
    compute_metrics=True,
    return_results=True
)
```

---

## Class Reference

### 1. TrajectoryPlotter

**Purpose**: Handles plotting of hybrid automaton trajectories with multiple visualization modes.

#### Constructor

```python
TrajectoryPlotter(
    state_data: np.ndarray,           # Simulated state data (num_states, num_steps)
    input_data: np.ndarray,           # Simulated input data (num_inputs, num_steps)
    dt: float = 0.001,                # Time step size
    original_state_data: Optional[np.ndarray] = None,  # Ground truth states
    original_input_data: Optional[np.ndarray] = None,  # Ground truth inputs
    input_plot: bool = False          # Whether to plot inputs
)
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `plot_single()` | Plot simulated trajectory only | `matplotlib.figure.Figure` |
| `plot_side_by_side()` | Overlay original and simulated on same axes | `matplotlib.figure.Figure` |
| `plot_stacked()` | Vertically stacked comparison plots | `matplotlib.figure.Figure` |
| `plot(mode)` | Generate plot based on mode string | `matplotlib.figure.Figure` |
| `save(save_path, dpi)` | Save current figure to file | `None` |
| `to_base64(dpi)` | Convert figure to base64 PNG string | `str` |
| `close()` | Close figure and free memory | `None` |

#### Example: Custom Plotting

```python
from HA_evaluation import TrajectoryPlotter
import numpy as np

# Create dummy data
state_data = np.random.randn(2, 1000)
input_data = np.random.randn(1, 1000)
original_state = np.random.randn(2, 1000)

# Create plotter
plotter = TrajectoryPlotter(
    state_data=state_data,
    input_data=input_data,
    dt=0.01,
    original_state_data=original_state,
    input_plot=True
)

# Generate side-by-side comparison
plotter.plot_side_by_side()
plotter.save('comparison.png', dpi=300)

# Or get base64 for web display
base64_img = plotter.to_base64()
print(f"data:image/png;base64,{base64_img}")

plotter.close()
```

---

### 2. HAEvaluator

**Purpose**: Evaluates a hybrid automaton against ground truth data through simulation and metric computation.

#### Constructor

```python
HAEvaluator(
    ha_dict: Dict[str, Any],          # HA specification with 'automaton' and 'config'
    npz_file_path: str,               # Path to ground truth NPZ file
    dt: Optional[float] = None,       # Time step (uses config['dt'] if None)
    total_time: float = 10.0          # Total simulation time
)
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `load_ground_truth()` | Load ground truth from NPZ file | `Dict[str, np.ndarray]` |
| `simulate()` | Run HA simulation | `Dict[str, np.ndarray]` |
| `compute_metrics()` | Calculate evaluation metrics | `Dict[str, Any]` |
| `plot(plot_mode, save_path, ...)` | Generate visualization | `Optional[str]` |
| `evaluate(save_path, plot_mode, ...)` | Complete evaluation pipeline | `Optional[Dict[str, Any]]` |

#### Example: Step-by-Step Evaluation

```python
# Initialize evaluator
evaluator = HAEvaluator(
    ha_dict=ha_dict,
    npz_file_path='data_duffing/test_data0.npz'
)

# Step 1: Load ground truth
gt_data = evaluator.load_ground_truth()
print(f"Ground truth has {gt_data['state'].shape[1]} time steps")

# Step 2: Run simulation
sim_data = evaluator.simulate()
print(f"Simulated {sim_data['state'].shape[1]} time steps")
print(f"Number of mode switches: {len(sim_data['change_points']) - 2}")

# Step 3: Compute metrics
metrics = evaluator.compute_metrics()
print(f"State RMSE: {metrics['state_rmse']:.6f}")
print(f"State MAE: {metrics['state_mae']:.6f}")
print(f"Mode Accuracy: {metrics['mode_accuracy']:.2%}")

# Step 4: Generate plots
evaluator.plot(
    plot_mode='stacked',
    save_path='output/comparison.png'
)
```

---

## Plotting Modes

### Mode 1: Single (Simulated Only)

Shows only the simulated trajectory without ground truth comparison.

```python
evaluator.plot(plot_mode='single', save_path='output_single.png')
```

**Use Case**: When you only want to visualize the HA simulation results.

**Output**: Single plot with state variables and optionally input variables.

---

### Mode 2: Side-by-Side (Overlay)

Overlays original and simulated trajectories on the same axes with distinct visual styles.

```python
evaluator.plot(plot_mode='side_by_side', save_path='output_comparison.png')
```

**Visual Encoding**:
- **Original Data**: Thick solid lines (─) with circle markers (○), 60% opacity
- **Simulated Data**: Thin dash-dot lines (─·─) with triangle markers (△), 100% opacity

**Use Case**: Direct visual comparison to see how closely simulation matches ground truth.

**Output**: Single plot with both trajectories overlaid.

---

### Mode 3: Stacked (Separate Subplots)

Displays simulated and original trajectories in vertically stacked subplots.

```python
evaluator.plot(plot_mode='stacked', save_path='output_stacked.png')
```

**Layout**:
- **Top subplot**: Simulated trajectory
- **Bottom subplot**: Original (ground truth) trajectory

**Use Case**: Detailed comparison when overlay becomes cluttered, or to analyze each trajectory independently.

**Output**: Figure with two vertically aligned subplots.

---

## Evaluation Metrics

The `compute_metrics()` method returns a comprehensive dictionary with the following metrics:

### Absolute Error Metrics (Interpretability)

| Metric | Description | Unit |
|--------|-------------|------|
| `state_rmse` | Root Mean Square Error of state variables | Same as state units |
| `state_max_error` | Maximum absolute error across all states and time | Same as state units |
| `state_mae` | Mean Absolute Error of state variables | Same as state units |
| `mode_accuracy` | Fraction of time steps with correct mode | [0, 1] |
| `change_point_error` | Maximum temporal error in detecting mode switches | Seconds |
| `input_mse` | Mean Squared Error of input tracking | Input units² |

### Normalized Metrics (Comparison with Traditional HA Learning)

| Metric | Description | Range |
|--------|-------------|-------|
| `normalized_max_diff` | Max state error normalized by ground truth range | [0, ∞) |
| `normalized_mean_diff` | Mean state error normalized by ground truth range | [0, ∞) |
| `train_tc` | Training temporal correspondence (change-point error) | Seconds |
| `clustering_error` | Absolute difference in number of modes | Integer |

### Data Dictionaries

| Key | Description |
|-----|-------------|
| `simulated_data` | Dict with keys: `'state'`, `'input'`, `'mode'`, `'change_points'` |
| `ground_truth_data` | Dict with keys: `'state'`, `'input'`, `'mode'`, `'change_points'` |

### Example: Accessing Metrics

```python
results = evaluator.compute_metrics()

# Print absolute errors
print(f"State RMSE: {results['state_rmse']:.6f}")
print(f"Max Error: {results['state_max_error']:.6f}")
print(f"Mean Abs Error: {results['state_mae']:.6f}")

# Print mode tracking performance
if results['mode_accuracy'] is not None:
    print(f"Mode Accuracy: {results['mode_accuracy':.2%}")

# Print change-point detection performance
if results['change_point_error'] is not None:
    print(f"Change-Point Error: {results['change_point_error']:.3f} seconds")

# Access raw data for custom analysis
sim_states = results['simulated_data']['state']
gt_states = results['ground_truth_data']['state']
print(f"Simulated state shape: {sim_states.shape}")
```

---

## Input Data Format

### Hybrid Automaton Dictionary

```python
ha_dict = {
    "automaton": {
        "var": "x1, x2, ...",           # Comma-separated state variable names
        "input": "u1, u2, ...",         # Comma-separated input variable names
        "mode": [                       # List of modes
            {
                "id": 1,                 # Unique mode ID (integer)
                "eq": "x1[1] = ..., x2[1] = ..."  # ODEs (comma-separated)
            },
            ...
        ],
        "edge": [                       # List of transitions
            {
                "direction": "1 -> 2",   # Source mode -> Target mode
                "condition": "x1 >= 5",  # Guard condition (Python expression)
                "reset": {               # Optional reset map
                    "x1": ["", "x1"],    # Format: ["const_term", "linear_term"]
                    "x2": ["", "x2"]
                }
            },
            ...
        ]
    },
    "config": {
        "dt": 0.001,                    # Time step for simulation
        "total_time": 10.0,             # Total simulation duration
        "dim": 2,                       # State space dimension
        "other_items": ""               # Additional config (see json_readme.md)
    }
}
```

### NPZ File Format

Ground truth data should be stored in NumPy `.npz` format with the following arrays:

| Array Name | Shape | Description |
|------------|-------|-------------|
| `state` | `(num_states, num_steps)` | State trajectory |
| `input` | `(num_inputs, num_steps)` or `(num_steps,)` | Input trajectory |
| `mode` (optional) | `(num_steps,)` | Mode sequence |
| `change_points` (optional) | `(num_transitions,)` | Indices where mode switches occur |

**Example**: Loading NPZ file
```python
import numpy as np

npz_file = np.load('data_duffing/test_data0.npz')
print(f"State shape: {npz_file['state'].shape}")
print(f"Input shape: {npz_file['input'].shape}")
if 'mode' in npz_file:
    print(f"Mode shape: {npz_file['mode'].shape}")
    print(f"Unique modes: {np.unique(npz_file['mode'])}")
```

---

## Constants and Configuration

The module defines plotting constants at the top of the file (lines 32-49):

```python
DEFAULT_TIME_STEP = 0.001
DEFAULT_FIGURE_WIDTH = 12
DEFAULT_FIGURE_HEIGHT = 5
DEFAULT_STACKED_HEIGHT = 10
DEFAULT_DPI = 150
DEFAULT_BASE64_DPI = 100
DEFAULT_LINEWIDTH = 2.0
DEFAULT_LINEWIDTH_THICK = 3.5
DEFAULT_LINEWIDTH_THIN = 2.0
DEFAULT_MARKER_SIZE = 6
DEFAULT_MARKER_SIZE_SMALL = 5
DEFAULT_MARKER_INTERVAL = 40  # Show ~40 markers per plot
DEFAULT_FONT_SIZE = 14
DEFAULT_LEGEND_FONT_SIZE = 16
DEFAULT_TITLE_FONT_SIZE = 16
```

You can modify these constants to customize the appearance of plots.

---

## Advanced Usage

### Custom Initial Conditions

The evaluator automatically extracts initial conditions from the ground truth NPZ file. However, you can modify the HA dictionary to use different initial states:

```python
# Modify before creating evaluator
ha_dict['init_state'] = [
    {
        'mode': 1,
        'x1': [0.5],  # Initial value for x1
        'x2': [0.0],  # Initial value for x2
        'u1': input_array  # Input time series
    }
]
```

### Handling Dimension Mismatch

When the simulated state dimension doesn't match the ground truth:

```python
results = evaluator.compute_metrics()

# Check if full metrics were computed
if results['normalized_max_diff'] is None:
    print("Warning: Dimension mismatch detected")
    print(f"Limited metrics available")
    print(f"State RMSE (partial): {results['state_rmse']:.6f}")
else:
    print("Full metric suite available")
```

### Batch Evaluation

Evaluate multiple HA configurations:

```python
ha_configs = [ha_dict_1, ha_dict_2, ha_dict_3]
npz_files = ['test_data0.npz', 'test_data1.npz', 'test_data2.npz']

results_list = []
for ha_dict, npz_path in zip(ha_configs, npz_files):
    evaluator = HAEvaluator(ha_dict, npz_path)
    results = evaluator.evaluate(
        save_path=f'output/{npz_path.replace(".npz", "")}',
        compute_metrics=True
    )
    results_list.append(results)

# Compare results
for i, res in enumerate(results_list):
    print(f"Config {i+1}: RMSE = {res['state_rmse']:.6f}")
```

### Using Base64 Images for Web Display

```python
# Generate base64 image without saving to disk
base64_img = evaluator.plot(
    plot_mode='side_by_side',
    return_base64=True
)

# Use in HTML
html = f'''
<html>
<body>
    <h1>HA Evaluation Results</h1>
    <img src="data:image/png;base64,{base64_img}" />
</body>
</html>
'''
```

---

## Error Handling

### Common Issues

#### 1. Missing NPZ File

```python
FileNotFoundError: [Errno 2] No such file or directory: 'data_duffing/test_data0.npz'
```

**Solution**: Ensure the NPZ file path is correct and the file exists.

#### 2. Invalid State Data Dimensions

```python
ValueError: state_data must be a 2D array with shape (num_states, num_steps)
```

**Solution**: Check that state data has shape `(num_states, num_steps)`, not `(num_steps, num_states)`.

#### 3. Missing Original Data for Comparison Plots

```python
ValueError: original_state_data must be provided for side_by_side mode
```

**Solution**: Use `plot_mode='single'` or ensure ground truth data is loaded.

#### 4. Invalid Plot Mode

```python
ValueError: Invalid plot mode: xyz. Must be 'single', 'side_by_side', or 'stacked'
```

**Solution**: Use one of the three supported plot modes.

---

## Performance Considerations

### Memory Management

- Always call `plotter.close()` when done plotting to free memory
- The `evaluate()` method stores results in instance variables; create new evaluators for batch processing to avoid accumulation

### Large Datasets

For very long time series (> 100k steps):

```python
# Downsample for plotting while keeping full data for metrics
downsampled_state = state_data[:, ::10]  # Every 10th point
downsampled_input = input_data[:, ::10]

# Plot with downsampled data
plotter = TrajectoryPlotter(downsampled_state, downsampled_input, dt=0.01)
plotter.plot_single()
plotter.save('plot.png')
plotter.close()
```

---

## Testing

Run the built-in test by executing the module directly:

```bash
cd Dainarx_code
python HA_evaluation.py
```

This will generate three test plots in `data_duffing_evaluation/`:
- `output_single.png` - Single trajectory plot
- `output_side_by_side.png` - Overlay comparison
- `output_stacked.png` - Stacked comparison

And print evaluation metrics to console.

---

## Dependencies

```python
numpy>=1.20.0
matplotlib>=3.3.0
```

**Optional** (for parent modules):
```python
scipy>=1.6.0  # For curve fitting in fit.py
```

---

## Input Data Flow in Simulation

Understanding how input data flows through the HA simulation is crucial for debugging and extending the evaluation framework.

### Overview

The input data follows this path during simulation:

```
NPZ File (Ground Truth)
    ↓
HAEvaluator._prepare_initial_state()
    ↓
HybridAutomata.reset()
    ↓
ODESystem.analyticalInput() → Creates time-indexed function
    ↓
ODESystem.getInput(t) → Retrieves value at time t
    ↓
Used in ODE evaluation at each simulation step
```

### Detailed Flow

#### 1. Loading Ground Truth Data

When `load_ground_truth()` is called ([HA_evaluation.py:457-473](HA_evaluation copy.py#L457-L473)):

```python
def load_ground_truth(self):
    npz_file = np.load(self.npz_file_path)

    self.ground_truth = {
        'state': npz_file['state'],      # Shape: (num_states, num_steps)
        'input': npz_file['input'],      # Shape: (num_inputs, num_steps) or (num_steps,)
        'mode': npz_file['mode'],        # Shape: (num_steps,)
        'change_points': npz_file['change_points']
    }
```

The **entire input time series** is loaded into memory from the NPZ file.

#### 2. Preparing Initial State

The `_prepare_initial_state()` method ([HA_evaluation.py:475-511](HA_evaluation copy.py#L475-L511)) creates an initial state dictionary:

```python
def _prepare_initial_state(self):
    # Extract initial state values from first time step
    state_data_npz = self.ground_truth['state']
    input_data_npz = self.ground_truth['input']

    init_state = state_data_npz[:, 0].tolist()  # First column

    # Build initial state dictionary
    init_state_dict = {'mode': 1}

    # Add state variables
    for i, var_name in enumerate(var_names):
        init_state_dict[var_name] = [init_state[i]]

    # KEY STEP: Pass entire input array (not just initial value)
    input_var_name = self.ha_dict['automaton']['input']
    init_state_dict[input_var_name] = input_data_npz  # Full array!

    return init_state_dict
```

**Critical Point**: The entire input time series array is passed, not just the initial value.

#### 3. Converting Array to Time-Indexed Function

When `reset()` is called ([ODE_System.py:152-159](src/ODE_System.py#L152-L159)):

```python
def reset(self, init_state, dt=None):
    if dt is not None:
        self.dt = dt  # Store time step for indexing

    # ... reset state variables ...

    # Convert input data to callable functions
    self.input_fun_list = self.analyticalInput(init_state)
```

The `analyticalInput()` method ([ODE_System.py:38-89](src/ODE_System.py#L38-L89)) detects the input type and creates appropriate functions:

```python
def analyticalInput(self, input_expr=None):
    res = []
    for var in self.input_list:  # e.g., ['u1']
        expr = input_expr.get(var)  # Get input for 'u1'

        if isinstance(expr, (np.ndarray, list)):
            # Input is an array - create time-indexed function
            input_array = np.asarray(expr)

            def make_input_func(arr, dt):
                def input_func(t):
                    # Convert time to array index
                    # Note: array[i] corresponds to time (i+1)*dt
                    idx = int(round(t / dt - 1))
                    idx = max(0, min(idx, len(arr) - 1))  # Clamp to bounds
                    return arr[idx]
                return input_func

            res.append(make_input_func(input_array, self.dt))

        elif isinstance(expr, str):
            # Input is a mathematical expression (e.g., "sin(t)")
            res.append(eval("lambda t: " + expr))

        else:
            # No input specified - return zero
            res.append(lambda t: 0)

    return res
```

**Key Insight**: The input array is wrapped in a **closure** that captures both the array and the time step `dt`. This creates a function `input_func(t)` that maps simulation time to array indices.

#### 4. Time Indexing Convention

The indexing formula `idx = int(round(t / dt - 1))` accounts for how data was collected:

```python
# During data collection (in CreatData.py or similar):
for i in range(num_steps):
    state, mode, switched = sys.next(dt)  # Advances time by dt
    state_data.append(state)              # Recorded AFTER next()
    input_data.append(sys.getInput())     # Also recorded AFTER next()
    # At this point: current_time = (i+1) * dt
```

So `input_data[i]` corresponds to time `t = (i+1) * dt`, which means:
- For time `t`, we need index `i` where `(i+1) * dt ≈ t`
- Solving: `i ≈ t/dt - 1`

**Example**:
- At `t = 0.001` (first time step after initialization)
- Index: `i = 0.001/0.001 - 1 = 0`
- Returns `input_array[0]` ✓

#### 5. Retrieving Input During Simulation

At each simulation step ([ODE_System.py:96-100, 130-134](src/ODE_System.py#L96-L100)):

```python
def getInput(self, t=None):
    if t is None:
        t = self.now_time  # Use current simulation time
    res = [fun(t) for fun in self.input_fun_list]  # Call indexed function
    return res

def rk_fun(self, y, t):
    # Runge-Kutta integration step
    res = np.roll(y, -1, axis=1)
    for idx in range(self.var_num):
        # Evaluate ODE with current input value
        res[idx][self.order_list[idx] - 1] = self.eq_list[idx](y, *self.getInput(t))
    return res
```

**Flow at time `t = 0.005`**:
1. `getInput(0.005)` is called
2. Calls `input_func(0.005)`
3. Computes `idx = int(round(0.005/0.001 - 1)) = 4`
4. Returns `input_array[4]`
5. This value is used in the ODE evaluation

#### 6. Complete Simulation Loop

Putting it all together ([HA_evaluation.py:513-559](HA_evaluation copy.py#L513-L559)):

```python
def simulate(self):
    init_state_dict = self._prepare_initial_state()
    self.ha_system.reset(init_state_dict, dt=self.dt)

    state_data = []
    mode_data = []
    input_data = []

    current_time = 0.0
    time_step_idx = 0

    while current_time < self.total_time:
        current_time += self.dt
        time_step_idx += 1

        # Advance simulation by one time step
        # Internally: getInput(current_time) retrieves input_array[time_step_idx-1]
        state, mode, switched = self.ha_system.next(self.dt)

        state_data.append(state)
        mode_data.append(mode)
        input_data.append(self.ha_system.getInput())  # For recording

        if switched:
            change_points.append(time_step_idx)

    # Convert to numpy arrays
    self.simulation_results = {
        'state': np.transpose(np.array(state_data)),
        'input': np.transpose(np.array(input_data)),
        'mode': np.array(mode_data),
        'change_points': change_points
    }
```

### Input Types Supported

The `analyticalInput()` method supports three input types:

#### 1. **Array/List (Most Common for Evaluation)**

```python
# 1D array
init_state_dict['u1'] = np.array([1.0, 1.5, 2.0, ...])  # Shape: (num_steps,)

# 2D array (will be flattened to 1D)
init_state_dict['u1'] = np.array([[1.0, 1.5, 2.0, ...]])  # Shape: (1, num_steps)
```

→ Creates time-indexed function using array indexing

#### 2. **String Expression (For Analytical Inputs)**

```python
init_state_dict['u1'] = "sin(t)"
init_state_dict['u2'] = "5 * cos(2 * pi * t)"
```

→ Creates function using `eval("lambda t: " + expr)`

#### 3. **No Input (Default to Zero)**

```python
# Don't specify input in init_state_dict
```

→ Creates function that always returns 0

### Debugging Tips

#### Check Input Alignment

```python
evaluator = HAEvaluator(ha_dict, npz_file_path)
evaluator.load_ground_truth()
evaluator.simulate()

# Compare input tracking
gt_input = evaluator.ground_truth['input']
sim_input = evaluator.simulation_results['input']

print(f"Ground truth input shape: {gt_input.shape}")
print(f"Simulated input shape: {sim_input.shape}")

# Should be nearly identical (within floating point precision)
input_diff = np.max(np.abs(gt_input[:, :min(gt_input.shape[1], sim_input.shape[1])] -
                            sim_input[:, :min(gt_input.shape[1], sim_input.shape[1])]))
print(f"Max input difference: {input_diff}")  # Should be ~0
```

#### Verify Time Indexing

```python
# Test time indexing directly
from Dainarx_code.src.ODE_System import ODESystem

input_array = np.array([10, 20, 30, 40, 50])
dt = 0.001

ode_sys = ODESystem("x1[1] = u1", ["x1"], ["u1"])
ode_sys.reset({"x1": [0], "u1": input_array}, dt=dt)

# At t = 0.001 (first step), should get input_array[0] = 10
print(ode_sys.getInput(0.001))  # [10]

# At t = 0.002 (second step), should get input_array[1] = 20
print(ode_sys.getInput(0.002))  # [20]

# At t = 0.003 (third step), should get input_array[2] = 30
print(ode_sys.getInput(0.003))  # [30]
```

### Common Pitfalls

#### Pitfall 1: Off-by-One Errors

**Problem**: Forgetting that `input_array[i]` corresponds to time `(i+1)*dt`, not `i*dt`.

**Solution**: The indexing formula `idx = t/dt - 1` handles this automatically.

#### Pitfall 2: Time Step Mismatch

**Problem**: Using different `dt` for simulation vs. data collection.

```python
# Data collected with dt=0.001
# But simulation uses dt=0.01
evaluator = HAEvaluator(ha_dict, npz_file_path, dt=0.01)  # Wrong!
```

**Solution**: Always use the same `dt` as the ground truth data:

```python
evaluator = HAEvaluator(ha_dict, npz_file_path, dt=0.001)  # Correct
# Or let it auto-detect from ha_dict['config']['dt']
```

#### Pitfall 3: Input Array Length Too Short

**Problem**: Simulation runs longer than available input data.

```python
# Input has 1000 time steps (covers t=0 to t=1.0)
# But simulation runs for t=2.0
evaluator = HAEvaluator(ha_dict, npz_file_path, total_time=2.0)  # May extrapolate
```

**Solution**: The indexing function clamps to array bounds:

```python
idx = max(0, min(idx, len(arr) - 1))  # Repeats last value if beyond bounds
```

But it's better to ensure `total_time <= len(input_array) * dt`.

### Summary

The input data flow is designed to:

1. **Support multiple input types**: Arrays (for real data), expressions (for analytical functions), or zeros (for autonomous systems)
2. **Preserve exact input values**: Simulation uses the same input time series as ground truth
3. **Handle time alignment**: Automatic indexing accounts for how data was collected
4. **Enable reproducibility**: Using identical inputs ensures fair comparison between simulation and ground truth

This architecture allows the evaluator to accurately assess how well a learned HA can reproduce the original system's behavior when driven by the **same inputs**.

---

## Related Documentation

- **[CLAUDE.md](../CLAUDE.md)**: Project overview and architecture
- **[Dainarx_code/automata/json_readme.md](automata/json_readme.md)**: HA JSON format specification
- **[prompts/system_prompt.md](../prompts/system_prompt.md)**: LLM prompt for HA extraction
- **[src/Evaluation.py](src/Evaluation.py)**: Evaluation class used for normalized metrics

---

## Changelog

### Version 2.0 (Current Refactoring)

- **Added**: `TrajectoryPlotter` class for modular plotting
- **Added**: `HAEvaluator` class for streamlined evaluation workflow
- **Added**: Comprehensive docstrings and type hints throughout
- **Added**: Constants section for easy customization
- **Improved**: Error handling and validation
- **Improved**: Code organization with private helper methods
- **Maintained**: Full backward compatibility with legacy API

### Version 1.0 (Original)

- Basic `ha_evaluation()` and `plot_ha()` functions
- Three plotting modes
- Metric computation using Evaluation class

---

## Contributing

When extending this module:

1. **Add type hints** to all new methods
2. **Write comprehensive docstrings** in English
3. **Extract magic numbers** to constants section
4. **Maintain backward compatibility** with wrapper functions
5. **Add tests** in `__main__` block for new features

---

## License

This module is part of the LLM-LEx project. See parent directory for license information.

---

## Contact

For questions or issues related to this module, please refer to the main project repository or contact the development team.

**Last Updated**: 2025-01-20
