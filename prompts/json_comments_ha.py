dim_diff_eq = 'k'
automaton_comments = {
    "var": "// variables list, separated by ','",
    "input": "// input variables list, separated by ','",
    "mode": [
        {
            "id": "// mode id",
            "eq": f"// {dim_diff_eq}-th order differential equation in the mode, separated by ','\n// cannot contain variables that are not defined in var, x[k] represents the k-th derivative of x\n// the left side of the equal sign is the highest order derivative, the right side is the expression, does not support implicit functions\n// must provide ode for each variable"
        }
    ],
    "edge": [
        {
            "direction": "// edge from mode u to mode v, represented as 'u -> v'",
            "condition": "// transition condition, cannot contain variables that are not defined in var",
            "reset": "// reset mapping for each variable, each variable has a list of reset values"
        }
    ],
    "config": {
        "dt": "// discrete time step",
        "total_time": "// total sampling time",
        "dim": "// dimension of differential equation",
        # "window_size": "// sliding window size (default 10)",
        # "clustering_method": "// clustering method, 'fit' or 'dis' (default 'fit')",
        # "minus": "// whether to minimize order (default false)",
        # "need_bias": "// whether to include constant term (default true)",
        # "kernel": "// SVM kernel function (default 'linear')",
        "other_items": "// additional nonlinear or cross terms"
    }
}