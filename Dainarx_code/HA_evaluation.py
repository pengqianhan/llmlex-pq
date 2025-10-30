import numpy as np
import os
from math import *
import matplotlib.pyplot as plt
from typing import Optional
from src.HybridAutomata import HybridAutomata
import json
from CreatData import plot_fun


def ha_evaluation(json_path: str, data_path: str, dT: float, times: float):
    r"""
    :param json_path: File path of automata.
    :param data_path: Data storage path.
    :param dT: Discrete time.
    :param times: Total sampling time.
    """


    data_dict = {
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
    # Use dictionary directly
    data = data_dict
    print('data: ', data)
    
    # Convert automaton to JSON string and back to dict for from_json
    automaton_json = json.dumps(data["automaton"], indent=2, ensure_ascii=False)
    print('automaton_json: ', automaton_json)
    automaton_dict = json.loads(automaton_json)
    print('data["automaton"]: ', automaton_dict)
    sys = HybridAutomata.from_json(automaton_dict)
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
        state_id += 1


if __name__ == "__main__":
    ha_evaluation('automata/non_linear/duffing_simulation.json', 'data_duffing_simulation', 0.001, 10)
