import json

# Prompt template for hybrid automaton specification
PROMPT_HA = {
    "automaton": {  # automaton
        "var": "x1",  # variables list, separated by ','
        "mode": [  # mode list
            {
                "id": 1,  # mode id
                "eq": "x1[k] = lambda x1, *params: "
                # k-th order differential equation in the mode, separated by ','
                # cannot contain variables that are not defined in var, x[k] represents the k-th derivative of x
                # the left side of the equal sign is the highest order derivative, the right side is the expression, does not support implicit functions
                # must provide ode for each variable
            }
        ],
        "input": "u1",  # input variables list, separated by ','
        "edge": [
            {
                "direction": "1 -> 1",  # edge from mode u to mode v, represented as 'u -> v'
                "condition": "lambda x1, u1, *params: f(x1, u1, params) > 0",  # transition condition, cannot contain variables that are not defined in var
                "reset": {  # reset mapping for each variable, each variable has a list of reset values
                    "x1": [
                        "",
                        "x[1]"
                    ]
                }
            }
        ]
    },
    "config": {  # configuration parameters
        "dt": 0.001,  # discrete time step (default 0.001)
        "total_time": 10.0,  # total sampling time (default 10.0)
        "dim": "k",  # dimension of differential equation (default 1)
        "other_items": ""  # additional nonlinear or cross terms (default empty string)
    }
}


def to_json(indent=2):
    """
    Convert PROMPT_HA dictionary to JSON string.
    
    Args:
        indent (int): Number of spaces for indentation (default: 2)
    
    Returns:
        str: JSON formatted string
    """
    return json.dumps(PROMPT_HA, indent=indent, ensure_ascii=False)


def save_json(filepath, indent=2):
    """
    Save PROMPT_HA dictionary to a JSON file.
    
    Args:
        filepath (str): Path to save the JSON file
        indent (int): Number of spaces for indentation (default: 2)
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(PROMPT_HA, f, indent=indent, ensure_ascii=False)


# Example usage (uncomment to test):
if __name__ == "__main__":
    # Print as JSON string
    print(to_json())
    
    # Save to file
    save_json("prompt_ha_output.json")