### Objective

Your sole objective is to analyze the provided image of a hybrid automaton and generate a single, valid JSON object that represents it. The output must conform EXACTLY to the JSON schema defined below.

{
  "automaton": { // automaton
    "var": "x1, x2, ... , xn", // variables list, separated by ','
    "input": "u1, u2, ... , un", // input variables list, separated by ','
    "mode": [ // mode list
      {
        "id": 1, // mode id
        "eq": "x1[1] = 1, x2[2] = -3 * x2[1] - 25 * x2[0] + 25"
        // ode of each variable in the mode, separated by ','
        // cannot contain variables that are not defined in var, x[k] represents the k-th derivative of x
        // the left side of the equal sign is the highest order derivative, the right side is the expression, does not support implicit functions
        // must provide ode for each variable
      },
      {
        "id": 2,
        "eq": "x1[1] = -1, x2[2] = -3 * x2[1] - 25 * x2[0]"
      }
    ],
    "edge": [
      {
        "direction": "1 -> 2", // edge from mode u to mode v, represented as "u -> v"
        "condition": "x1 >= 5" // transition condition, cannot contain variables that are not defined in var
      },
      {
        "direction": "2 -> 1",
        "condition": "x1 <= 0"
      }
    ]
  },
  "init_state": [ // initial state list, generate as many trajectories as there are initial states
    {
      "mode": 1, // initial mode
      "x1": [0], // initial state of x1, [a, b, c, ...] are the initial states of x1[0], x1[1], x1[2], ...
      "x2": [0]  // if no initial state is provided, or the number of initial states is less than the order of the equation + 1, it will be automatically padded with 0
    },
    {
      "mode": 1,
      "x1": [2],
      "x2": [3]
    }
  ],
  "config": {                   // parameters for fitting the difference equation
    "dt": 0.001,                 // discrete time, default 0.001
    "total_time": 10.0,         // sampling total time, default 10
    "dim": 3,                   // dimension of the difference equation, default 3
  }
}

