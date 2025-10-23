import numpy as np
import os
from math import *
import src.DE as DE
import matplotlib.pyplot as plt
from typing import Optional
from src.HybridAutomata import HybridAutomata
import json
from CreatData import plot_fun
# def plot_fun(state_data: np.ndarray,
#              input_data: np.ndarray,
#              dt: float,
#              system_name: str = "System",
#              sample_index: Optional[int] = None,
#              save_path: Optional[str] = None,
#              show: bool = True) -> None:
#     """Plot a 2D trajectory (if available) and the time series for states/inputs."""

#     if state_data.ndim != 2:
#         raise ValueError("state_data must be a 2D array with shape (num_states, num_steps)")

#     num_states, num_steps = state_data.shape

#     if input_data.size == 0:
#         input_series = np.empty((0, num_steps))
#     elif input_data.ndim == 1:
#         input_series = input_data.reshape(1, -1)
#     elif input_data.ndim == 2:
#         input_series = input_data
#     else:
#         raise ValueError("input_data must be empty, 1D, or 2D array")

#     num_inputs = input_series.shape[0]

#     if num_steps == 0:
#         raise ValueError("state_data must contain at least one time step")

#     time = np.arange(num_steps) * dt
#     has_traj = num_states >= 2
#     nrows = 2 if has_traj else 1

#     figsize = (12, 8) if has_traj else (12, 5)
#     fig, axes = plt.subplots(nrows, 1, figsize=figsize, constrained_layout=True)

#     if has_traj:
#         ax_traj, ax_ts = axes
#         ax_traj.plot(state_data[0], state_data[1], color='tab:blue', linewidth=2)
#         ax_traj.scatter(state_data[0, 0], state_data[1, 0], color='green', s=80, zorder=3, label='Start')
#         ax_traj.scatter(state_data[0, -1], state_data[1, -1], color='red', s=80, marker='s', zorder=3, label='End')
#         ax_traj.set_xlabel('x1')
#         ax_traj.set_ylabel('x2')
#         title_suffix = f" Sample {sample_index}" if sample_index is not None else ""
#         ax_traj.set_title(f"{system_name} {title_suffix} - 2D Trajectory".strip())
#         ax_traj.grid(True, linestyle='--', alpha=0.4)
#         ax_traj.legend(loc='best')
#     else:
#         ax_ts = axes

#     total_series = num_states + num_inputs
#     try:
#         cmap = plt.cm.get_cmap('tab20', max(total_series, 1))
#     except (AttributeError, TypeError):
#         # For matplotlib >= 3.7, get_cmap only takes colormap name
#         import matplotlib as mpl
#         cmap = mpl.colormaps['tab20']

#     for idx in range(num_states):
#         ax_ts.plot(time, state_data[idx], label=f"x{idx + 1}", color=cmap(idx), linewidth=2)

#     for idx in range(num_inputs):
#         series_index = num_states + idx
#         ax_ts.plot(time, input_series[idx], label=f"u{idx + 1}", linestyle='--', color=cmap(series_index), linewidth=2)

#     ax_ts.set_xlabel('Time (s)')
#     ax_ts.set_ylabel('Values')
#     title_suffix = f" Sample {sample_index - 1}" if sample_index is not None else ""
#     ax_ts.set_title(f"{system_name} {title_suffix} - Time Series".strip())
#     ax_ts.grid(True, linestyle='--', alpha=0.4)
#     ax_ts.legend(loc='best')

#     if save_path is not None:
#         directory = os.path.dirname(save_path)
#         if directory:
#             os.makedirs(directory, exist_ok=True)
#         fig.savefig(save_path, dpi=150)

#     if show:
#         plt.show()
#     else:
#         plt.close(fig)


def ha_simulation(json_path: str, data_path: str, dT: float, times: float):
    r"""
    :param json_path: File path of automata.
    :param data_path: Data storage path.
    :param dT: Discrete time.
    :param times: Total sampling time.
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(json_path):
        json_path = os.path.join(current_dir, json_path)
    if not os.path.isabs(data_path):
        data_path = os.path.join(current_dir, data_path)

    if not os.path.exists(data_path):
        os.mkdir(data_path)
    else:
        files = os.listdir(data_path)
        for file in files:
            os.remove(os.path.join(data_path, file))

    with open(json_path, 'r') as f:
        data = json.load(f)
        sys = HybridAutomata.from_json(data['automaton'])
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
        
        print('init_state_dict: ', init_state_dict)
        # Use numpy array directly instead of function expression
        init_state_dict['u'] = input_list
        # print('input_list: ', input_list)
        # print('input_list.shape: ', input_list.shape)
        print('init_state_dict with array input: ', {k: v if not isinstance(v, np.ndarray) else f'<array shape={v.shape}>' for k, v in init_state_dict.items()})
        
        
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
            system_title = os.path.splitext(os.path.basename(json_path))[0]
            system_title = 'duffing'
            figure_path = os.path.join(data_path, f"sample_{state_id}.png")
            plot_fun(state_data, input_data, dT, system_name=system_title,
                     sample_index=cnt, save_path=figure_path, show=False)

            # save the data
            np.savez(os.path.join(data_path, "test_data" + str(state_id)),
                     state=state_data, mode=mode_data, input=input_data, change_points=change_points)
            state_id += 1


if __name__ == "__main__":
    ha_simulation('automata/non_linear/duffing_simulation.json', 'data_duffing_simulation', 0.001, 10)
    # ha_simulation('automata/ATVA/ball.json', 'data_ball', 0.001, 10)
