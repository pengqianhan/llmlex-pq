

### Objective

Your sole objective is to analyze the provided image of a hybrid automaton and generate a single, valid JSON object that represents it. The output must conform EXACTLY to the JSON schema defined below and must be parsable by the provided Python script.

**DO NOT** include any explanatory text, apologies, or conversational filler in your response. The output must be ONLY the raw JSON code block.

### Core Definitions

*   **Hybrid Automaton:** A system with discrete control states (modes) and continuous dynamics.
*   **States (or Modes):** Discrete operating conditions, each with its own set of continuous behaviors (differential equations) and invariants.
*   **Transitions:** Rules that govern the switch from one state to another.
*   **Guard:** A condition on a transition that must be true for the transition to occur.
*   **Reset Map:** An operation that changes the values of continuous variables when a transition occurs.
*   **Invariant:** A condition that must hold true while the system is in a particular state. If the invariant is violated, a transition must occur.
*   **Dynamics:** The set of differential equations (`x'[n] = ...`) that govern the evolution of the continuous variables within a state.

### JSON Schema & Constraints

The output MUST be a valid JSON object with the following structure. Pay close attention to data types (strings, numbers, arrays, objects).

**Derivative Notation:**
*   `xi[0]` refers to the value of the variable `xi`.
*   `xi[1]` refers to the first derivative of `xi`.
*   `xi[2]` refers to the second derivative of `xi`, and so on.

```json
{
  "automaton": {
    "var": "x1, x2，...，xn",
    "mode": [
      {
        "id": 1,
        "eq": "x1[1] = f1(x1[0], x2[0], ...，xn[0],u),x2[1] = f2(x1[0], x2[0], ...，xn[0],u),...，xn[1] = fn(x1[0], x2[0], ...，xn[0],u),..."
      },
      {
        "id": 2,
        "eq": "x1[1] = f1(x1[0], x2[0], ...，xn[0],u),x2[1] = f2(x1[0], x2[0], ...，xn[0],u),...，xn[1] = fn(x1[0], x2[0], ...，xn[0],u),..."
      },
      ...
      {
        "id": m,
        "eq": "x1[1] = f1(x1[0], x2[0], ...，xn[0],u),x2[1] = f2(x1[0], x2[0], ...，xn[0],u),...，xn[1] = fn(x1[0], x2[0], ...，xn[0],u),..."
      }
    ],
    "edge": [
      {
        "direction": "1 -> i",
        "condition": "g1(x1[0], x2[0], ...，xn[0],u) <= 0",
        "reset": {
          "x1": [],
          "x2": [],
          ...
          "xn": []
      },
      "edge": [
        {
          "direction": "1 -> i",
          "condition": "g1(x1[0], x2[0], ...，xn[0],u) <= 0",
          "reset": {
            "x1": [],
            "x2": [],
            ...
            "xn": []
          }
        }
      ]
      }
    ]
  }
}
```

```python
class HybridAutomata:
    LoopWarning = True

    def __init__(self, mode_list, adj, init_mode=None):
        if init_mode is None:
            self.mode_state = None
        else:
            self.mode_state = init_mode
        self.mode_list = mode_list
        self.adj = adj

    @classmethod
    def from_json(cls, info: dict):
        var_list = re.split(r"\s*,\s*", info['var'])
        input_expr = info.get('input')
        if input_expr is None:
            input_list = []
        else:
            input_list = re.split(r"\s*,\s*", info.get('input'))
        mode_list = {}

        adj = {}
        for mode in info['mode']:
            mode_id = mode['id']
            mode_list[mode_id] = ODESystem(mode['eq'], var_list, input_list)
            adj[mode_id] = []
        for edge in info['edge']:
            u_v = re.findall(r'\d+', edge['direction'])
            fun = eval('lambda ' + info['var'] + ':' + edge['condition'])
            reset_val = edge.get("reset", {})
            adj[int(u_v[0])].append((int(u_v[1]), fun, reset_val))
        return cls(mode_list, adj)

    def getInput(self):
        return self.mode_list[self.mode_state].getInput()

    def next(self, *args):
        res = list(self.mode_list[self.mode_state].next(*args))
        mode_state = self.mode_state
        vis = set()
        via_list = []
        is_cycle = False
        switched = False
        while True:
            fl = True
            for to, fun, reset_val in self.adj.get(self.mode_state, {}):
                if fun(*res):
                    # self.mode_list[to].load(self.mode_list[self.mode_state], reset_val)
                    self.mode_state = to
                    switched = True
                    if to in vis:
                        if HybridAutomata.LoopWarning:
                            print("warning: find loop!")
                        is_cycle = True
                    vis.add(to)
                    via_list.append((to, reset_val))
                    fl = False
                    break
            if fl or is_cycle:
                if len(via_list) != 0:
                    to, reset_val = via_list[0] if is_cycle else via_list[-1]
                    self.mode_list[to].load(self.mode_list[mode_state], reset_val)
                    self.mode_state = to
                break
        return res, mode_state, switched

    def reset(self, init_state, *args):
        self.mode_state = init_state.get('mode', self.mode_state)
        self.mode_list[self.mode_state].reset(init_state, *args)
```