import numpy as np
import os
from math import *
import matplotlib.pyplot as plt
from typing import Optional
from Dainarx_code.src.HybridAutomata import HybridAutomata
import json
import base64
import io

def _plot_trajectory_on_axis(ax, state_data, input_data, dt, title, input_plot, cmap):
    """Helper function to plot trajectory on a given axis.

    Args:
        ax: Matplotlib axis to plot on
        state_data: 2D array with shape (num_states, num_steps)
        input_data: Input data array (processed)
        dt: Time step size
        title: Title for the subplot
        input_plot: Whether to plot input data
        cmap: Colormap for plotting
    """
    num_states, num_steps = state_data.shape
    time = np.arange(num_steps) * dt

    # Process input data
    if input_data.size == 0:
        input_series = np.empty((0, num_steps))
    elif input_data.ndim == 1:
        input_series = input_data.reshape(1, -1)
    elif input_data.ndim == 2:
        input_series = input_data
    else:
        raise ValueError("input_data must be empty, 1D, or 2D array")

    num_inputs = input_series.shape[0]

    # Plot states
    for idx in range(num_states):
        ax.plot(time, state_data[idx], label=f"x{idx + 1}", color=cmap(idx), linewidth=2)

    # Plot inputs if requested
    if input_plot:
        for idx in range(num_inputs):
            series_index = num_states + idx
            ax.plot(time, input_series[idx], label=f"u{idx + 1}", linestyle='--',
                   color=cmap(series_index), linewidth=2)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Values')
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(loc='best', fontsize=16)


def plot_ha(state_data: np.ndarray,
             input_data: np.ndarray,
             dt: float=0.001, # default time step
             save_path: Optional[str] = None,
             input_plot: bool = False,
             return_base64: bool = False,
             plot_mode: str = "single",
             original_state_data: Optional[np.ndarray] = None,
             original_input_data: Optional[np.ndarray] = None,
             **kwargs) -> Optional[str]:
    """Plot the time series for states/inputs.

    Args:
        state_data: 2D array with shape (num_states, num_steps) - simulated data
        input_data: Input data (empty, 1D, or 2D array) - simulated data
        dt: Time step size
        save_path: Path to save the figure
        input_plot: Whether to plot input data
        return_base64: If True, return base64 encoded PNG image instead of None
        plot_mode: Plotting mode - "single", "side_by_side", or "stacked"
        original_state_data: Optional original state data from NPZ file
        original_input_data: Optional original input data from NPZ file
        **kwargs: Additional keyword arguments

    Returns:
        str: Base64 encoded PNG image if return_base64=True, otherwise None
    """

    if state_data.ndim != 2:
        raise ValueError("state_data must be a 2D array with shape (num_states, num_steps)")

    num_states, num_steps = state_data.shape

    if input_data.size == 0:
        input_series = np.empty((0, num_steps))
    elif input_data.ndim == 1:
        input_series = input_data.reshape(1, -1)
    elif input_data.ndim == 2:
        input_series = input_data
    else:
        raise ValueError("input_data must be empty, 1D, or 2D array")

    num_inputs = input_series.shape[0]

    if num_steps == 0:
        raise ValueError("state_data must contain at least one time step")

    # Get colormap
    total_series = num_states + num_inputs
    try:
        cmap = plt.cm.get_cmap('tab20', max(total_series, 1))
    except (AttributeError, TypeError):
        # For matplotlib >= 3.7, get_cmap only takes colormap name
        import matplotlib as mpl
        cmap = mpl.colormaps['tab20']

    # Create figure based on plot mode
    if plot_mode == "single":
        # Mode 1: Single plot (simulated only)
        fig, ax_ts = plt.subplots(1, 1, figsize=(12, 5), constrained_layout=True)
        _plot_trajectory_on_axis(ax_ts, state_data, input_data, dt,
                                "Simulated Trajectory", input_plot, cmap)

    elif plot_mode == "side_by_side":
        # Mode 2: Both trajectories on same plot with distinct markers
        if original_state_data is None:
            raise ValueError("original_state_data must be provided for side_by_side mode")

        fig, ax_ts = plt.subplots(1, 1, figsize=(12, 5), constrained_layout=True)

        num_orig_states = original_state_data.shape[0]
        time = np.arange(num_steps) * dt

        # Plot original data with thick solid lines and large circle markers
        for idx in range(num_orig_states):
            ax_ts.plot(time, original_state_data[idx],
                      label=f"x{idx + 1} (Original)",
                      color=cmap(idx),
                      linewidth=3.5,
                      linestyle='-',
                      marker='o',
                      markersize=6,
                      markevery=max(1, num_steps // 40),  # Show ~40 markers
                      alpha=0.6,
                      zorder=1)  # Draw original data first (behind)

        # Plot simulated data with thin dash-dot lines and triangle markers
        for idx in range(num_states):
            ax_ts.plot(time, state_data[idx],
                      label=f"x{idx + 1} (Simulated)",
                      color=cmap(idx),
                      linewidth=2,
                      linestyle='-.',  # Dash-dot style for more distinction
                      marker='^',  # Triangle marker
                      markersize=5,
                      markevery=max(1, num_steps // 40),
                      alpha=1.0,
                      zorder=2)  # Draw simulated data on top

        # Plot inputs if requested
        if input_plot:
            if original_input_data is not None and original_input_data.size > 0:
                orig_input_series = original_input_data.reshape(1, -1) if original_input_data.ndim == 1 else original_input_data
                for idx in range(orig_input_series.shape[0]):
                    series_index = num_states + idx
                    ax_ts.plot(time, orig_input_series[idx],
                              label=f"u{idx + 1} (Original)",
                              linestyle='-',
                              color=cmap(series_index),
                              linewidth=3.5,
                              marker='o',
                              markersize=6,
                              markevery=max(1, num_steps // 40),
                              alpha=0.6,
                              zorder=1)

            if input_series.shape[0] > 0:
                for idx in range(num_inputs):
                    series_index = num_states + idx
                    ax_ts.plot(time, input_series[idx],
                              label=f"u{idx + 1} (Simulated)",
                              linestyle='-.',
                              color=cmap(series_index),
                              linewidth=2,
                              marker='^',
                              markersize=5,
                              markevery=max(1, num_steps // 40),
                              alpha=1.0,
                              zorder=2)

        ax_ts.set_xlabel('Time (s)', fontsize=14)
        ax_ts.set_ylabel('Values', fontsize=14)
        ax_ts.set_title('Comparison: Original vs Simulated Trajectories', fontsize=16, fontweight='bold')
        ax_ts.grid(True, linestyle='--', alpha=0.4)
        ax_ts.legend(loc='best', fontsize=12, ncol=2)

    elif plot_mode == "stacked":
        # Mode 3: Vertically stacked comparison
        if original_state_data is None:
            raise ValueError("original_state_data must be provided for stacked mode")

        fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(12, 10),
                                                 constrained_layout=True, sharex=True)

        # Top: Simulated data
        _plot_trajectory_on_axis(ax_top, state_data, input_data, dt,
                                "Simulated Trajectory", input_plot, cmap)

        # Bottom: Original data
        _plot_trajectory_on_axis(ax_bottom, original_state_data,
                                original_input_data if original_input_data is not None else np.array([]),
                                dt, "Original Trajectory", input_plot, cmap)

    else:
        raise ValueError(f"Invalid plot_mode: {plot_mode}. Must be 'single', 'side_by_side', or 'stacked'")

    # Save to file if requested
    if save_path is not None:
        directory = os.path.dirname(save_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        fig.savefig(save_path, dpi=150)

    # Return base64 encoded image if requested
    if return_base64:
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
        plt.close(fig)
        return base64_image

    plt.close(fig)
    return None

def ha_evaluation(data: dict, save_path: str, dT: float=0.001, times: float=10.0, plot_mode: str="single"):
    r"""
    :param data: Dictionary containing the hybrid automaton.
    :param save_path: Image save path.
    :param dT: time step, default 0.001.
    :param times: Total sampling time, default 10.0.
    :param plot_mode: Plotting mode - "single", "side_by_side", or "stacked". Default is "single".
    """

    # Use dictionary directly

    sys = HybridAutomata.from_json(data["automaton"])
    dT = data['config']['dt']
    # load npz file, only use the initial state and input
    npz_file = np.load('data_duffing/test_data0.npz')
    state_data_npz = npz_file['state']
    input_data_npz = npz_file['input']
    input_list = input_data_npz
    init_state = state_data_npz[:, :1].tolist()[0]
    init_state = np.float64(init_state)

    # Parse variable names from JSON
    var_names = [v.strip() for v in data['automaton']['var'].split(',')]

    # Convert init_state to dictionary with variable names as keys
    init_state_dict = {'mode': 1}
    if len(var_names) == 1:
        # Single variable case (e.g., "x")
        init_state_dict[var_names[0]] = init_state
    else:
        # Multiple variables case (e.g., "x1, x2, x3, x4")
        for i, var_name in enumerate(var_names):
            init_state_dict[var_name] = [init_state[i]] if i < len(init_state) else [0.0]

    # Use numpy array directly instead of function expression
    # Match the input variable name from automaton definition
    input_var_name = data['automaton']['input']
    init_state_dict[input_var_name] = input_list

    # print('init_state_dict with array input: ', {k: v if not isinstance(v, np.ndarray) else f'<array shape={v.shape}>' for k, v in init_state_dict.items()})


    # data['init_state'] = [{'mode': 1, 'x': [4], 'u': '0.5 * cos(1.2 * t)'}]
    data['init_state'] = [init_state_dict]
    for init_state in data['init_state']:
        state_data = []
        mode_data = []
        input_data = []
        change_points = [0]
        sys.reset(init_state, dt=dT)
        now = 0.
        idx = 0
        while now < times:
            now += dT
            idx += 1
            state, mode, switched = sys.next(dT)
            state_data.append(state)
            mode_data.append(mode)
            input_data.append(sys.getInput())
            if switched:
                change_points.append(idx)
        change_points.append(idx)
        state_data = np.transpose(np.array(state_data))
        input_data = np.transpose(np.array(input_data))
        mode_data = np.array(mode_data)

        # plot data with the specified mode
        mode_suffix_map = {
            "single": "single",
            "side_by_side": "side_by_side",
            "stacked": "stacked"
        }
        filename = f"output_{mode_suffix_map.get(plot_mode, 'single')}.png"
        figure_path = os.path.join(save_path, filename)

        plot_ha(state_data, input_data, dT,
                save_path=figure_path,
                plot_mode=plot_mode,
                original_state_data=state_data_npz,
                original_input_data=input_data_npz)

if __name__ == "__main__":
    data = {
    "automaton": {
        "var": "x1",
        "input": "u1",
        "mode": [
            {
                "id": 1,
                "eq": "x1[2] = -0.5 * x1[1] - 5.0 * x1[0] - 0.5 * x1[0]**3 + u1"
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
    data1 = {
    "automaton": {
        "var": "x1, x2",
        "input": "u1",
        "mode": [
            {
                "id": 1,
                "eq": "x1[1] = x2[0], x2[1] = -0.1 * x2[0] - 1.0 * x1[0] - 1.0 * x1[0]**3 + u1"
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
    # Test all three plotting modes
    print("Generating plots in all three modes...")

    # Mode 1: Single plot (simulated only)
    print("1. Generating single plot (simulated only)...")
    ha_evaluation(data1, 'data_duffing_evaluation', 0.001, 10, plot_mode="single")

    # Mode 2: Side-by-side comparison
    print("2. Generating side-by-side comparison plot...")
    ha_evaluation(data1, 'data_duffing_evaluation', 0.001, 10, plot_mode="side_by_side")

    # Mode 3: Stacked comparison
    print("3. Generating stacked comparison plot...")
    ha_evaluation(data1, 'data_duffing_evaluation', 0.001, 10, plot_mode="stacked")

    print("All plots generated successfully!")
