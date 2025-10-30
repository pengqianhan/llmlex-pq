prompt = """
# Hybrid Automaton v0
PROMPT_HA_v0 = {
    "automaton": {  # automaton
        "var": "x1",  # variables list, separated by ','
        "input": "u1",  # input variables list, separated by ','
        "mode": [  # mode list
            {
                "id": 1,  # mode id
                "eq": "x1[1] = x1[0] + u1"
                # k-th order differential equation in the mode, separated by ','
                # cannot contain variables that are not defined in var, x[k] represents the k-th derivative of x
                # the left side of the equal sign is the highest order derivative, the right side is the expression, does not support implicit functions
                # must provide ode for each variable
            }
        ],

        "edge": [
            {
                "direction": "1 -> 1",  # edge from mode u to mode v, represented as 'u -> v'
                "condition": "x1 >= 5",  # transition condition, cannot contain variables that are not defined in var
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
        "dt": 0.001,  # discrete time step
        "total_time": 10.0,  # total sampling time 
        "dim": 1,  # dimension of differential equation 
        "other_items": ""  # additional nonlinear or cross terms
    }
}

# Hybrid Automaton v1
"""