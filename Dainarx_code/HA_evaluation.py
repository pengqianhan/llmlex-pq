import numpy as np
import os
from math import *
import matplotlib.pyplot as plt
from typing import Optional
from Dainarx_code.src.HybridAutomata import HybridAutomata
import json

def plot_ha(state_data: np.ndarray,
             input_data: np.ndarray,
             dt: float,
             system_name: str = "System",
             sample_index: Optional[int] = None,
             save_path: Optional[str] = None,
             show: bool = True,
             input_plot: bool = False) -> None:
    """Plot the time series for states/inputs."""

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

    time = np.arange(num_steps) * dt

    fig, ax_ts = plt.subplots(1, 1, figsize=(12, 5), constrained_layout=True)

    total_series = num_states + num_inputs
    try:
        cmap = plt.cm.get_cmap('tab20', max(total_series, 1))
    except (AttributeError, TypeError):
        # For matplotlib >= 3.7, get_cmap only takes colormap name
        import matplotlib as mpl
        cmap = mpl.colormaps['tab20']

    for idx in range(num_states):
        ax_ts.plot(time, state_data[idx], label=f"x{idx + 1}", color=cmap(idx), linewidth=2)

    if input_plot:
        for idx in range(num_inputs):
            series_index = num_states + idx
            ax_ts.plot(time, input_series[idx], label=f"u{idx + 1}", linestyle='--', color=cmap(series_index), linewidth=2)

    ax_ts.set_xlabel('Time (s)')
    ax_ts.set_ylabel('Values')
    title_suffix = f" Sample {sample_index - 1}" if sample_index is not None else ""
    ax_ts.set_title(f"{system_name} {title_suffix} - Time Series".strip())
    ax_ts.grid(True, linestyle='--', alpha=0.4)
    ax_ts.legend(loc='best')

    if save_path is not None:
        directory = os.path.dirname(save_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        fig.savefig(save_path, dpi=150)

    if show:
        plt.show()
    else:
        plt.close(fig)

def ha_evaluation(data: dict, data_path: str, dT: float, times: float):
    r"""
    :param data: Dictionary containing the hybrid automaton.
    :param data_path: Data storage path.
    :param dT: Discrete time.
    :param times: Total sampling time.
    """


    
    # Use dictionary directly

    sys = HybridAutomata.from_json(data["automaton"])
    dT = data['config']['dt']
    state_id = 0
    cnt = 0
    # load npz file
    npz_file = np.load('data_duffing/test_data0.npz')
    state_data_npz = npz_file['state']
    input_list = npz_file['input']
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
        cnt += 1
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
        # plot data
        system_title = 'duffing'
        figure_path = os.path.join(data_path, f"sample_{state_id}.png")
        plot_ha(state_data, input_data, dT, system_name=system_title,
                    sample_index=cnt, save_path=figure_path, show=False)
        state_id += 1


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
    ha_evaluation(data1, 'data_duffing_evaluation', 0.001, 10)
