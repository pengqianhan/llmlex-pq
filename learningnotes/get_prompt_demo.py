"""
get_prompt Function Demonstration
===================================

This example file demonstrates how the get_prompt function works in llmlex/llm.py,
with a detailed focus on the function_list and imports parameters.

The get_prompt function generates prompts that are sent to LLMs for symbolic regression.
It creates lambda function definitions that serve as "parent functions" to guide the LLM
in suggesting improved mathematical expressions.
"""

# Standalone implementation of get_prompt to avoid dependency issues
# This is a copy from llmlex/llm.py:267-300

def get_prompt(function_list=None, imports=None):
    """
    Generates the user prompt given a list of functions.

    This is a standalone copy of the function from llmlex/llm.py for demonstration purposes.

    Args:
        function_list (list, optional): A list of tuples where each tuple contains:
            - [0]: A string representing a mathematical expression (function body)
            - [1]: An integer (tracking info, typically 1)
            If None, defaults to [("params[0]", 1)].
        imports (list, optional): A list of import statements to include at the beginning.
                                  If None, defaults to ["import numpy as np"].
    Returns:
        str: A string containing the generated user prompt with lambda function definitions.
    """
    # Use default if no function list provided
    if function_list is None:
        function_list = [("params[0]", 1)]

    # Use default imports if none provided
    if imports is None:
        imports = ["import numpy as np"]

    # Build the prompt
    prompt = ""
    for import_stmt in imports:
        prompt += f"{import_stmt}\n"

    for n in range(len(function_list)):
        prompt += f"curve_{n} = lambda x, *params: {function_list[n][0]} \n"
    prompt += f"curve_{len(function_list)} = lambda x, *params:"

    return prompt


def example_1_default_behavior():
    """
    Example 1: Default behavior (no arguments provided)

    When called without arguments, get_prompt uses:
    - Default function_list: [("params[0]", 1)]
    - Default imports: ["import numpy as np"]
    """
    print("=" * 70)
    print("Example 1: Default Behavior")
    print("=" * 70)

    prompt = get_prompt()

    print("\nGenerated Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)

    print("\nExplanation:")
    print("- Single import statement: 'import numpy as np'")
    print("- Single parent function: curve_0 = lambda x, *params: params[0]")
    print("- Final incomplete lambda: curve_1 = lambda x, *params:")
    print("- The LLM will complete the final lambda with a new expression")
    print()


def example_2_custom_function_list():
    """
    Example 2: Custom function_list parameter

    The function_list parameter is a list of tuples where each tuple contains:
    - [0]: A string representing the mathematical expression (the function body)
    - [1]: An integer (currently used for tracking, typically set to 1)

    These become "parent functions" that guide the LLM's suggestions.
    """
    print("=" * 70)
    print("Example 2: Custom Function List (Single Parent)")
    print("=" * 70)

    # Define a parent function: quadratic form
    function_list = [("params[0] * x**2 + params[1] * x + params[2]", 1)]

    prompt = get_prompt(function_list=function_list)

    print("\nInput function_list:")
    print(f"  {function_list}")
    print("\nGenerated Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)

    print("\nExplanation:")
    print("- curve_0 shows the quadratic parent function")
    print("- curve_1 is left incomplete for the LLM to fill in")
    print("- The LLM will build upon or modify the quadratic form")
    print()


def example_3_multiple_parent_functions():
    """
    Example 3: Multiple parent functions

    You can provide multiple parent functions to show evolution of expressions
    in a genetic algorithm or iterative refinement process.
    """
    print("=" * 70)
    print("Example 3: Multiple Parent Functions")
    print("=" * 70)

    # Define multiple parent functions showing progression
    function_list = [
        ("params[0] * x", 1),                                    # Linear
        ("params[0] * x**2 + params[1]", 1),                   # Quadratic
        ("params[0] * np.exp(params[1] * x) + params[2]", 1),  # Exponential
    ]

    prompt = get_prompt(function_list=function_list)

    print("\nInput function_list:")
    for i, (expr, _) in enumerate(function_list):
        print(f"  [{i}]: {expr}")

    print("\nGenerated Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)

    print("\nExplanation:")
    print("- curve_0, curve_1, curve_2 show the evolution of parent functions")
    print("- curve_3 is left incomplete for the LLM to suggest the next generation")
    print("- The LLM can see the progression and suggest improvements")
    print()


def example_4_custom_imports():
    """
    Example 4: Custom imports parameter

    The imports parameter allows you to specify which Python libraries
    the LLM can use in its mathematical expressions.
    """
    print("=" * 70)
    print("Example 4: Custom Imports")
    print("=" * 70)

    # Custom imports for special functions
    custom_imports = [
        "import numpy as np",
        "from scipy.special import erf, gamma",
        "import math"
    ]

    function_list = [("params[0] * erf(params[1] * x)", 1)]

    prompt = get_prompt(function_list=function_list, imports=custom_imports)

    print("\nInput imports:")
    for imp in custom_imports:
        print(f"  {imp}")

    print("\nInput function_list:")
    print(f"  {function_list}")

    print("\nGenerated Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)

    print("\nExplanation:")
    print("- All import statements appear at the top")
    print("- The parent function uses erf (error function) from scipy.special")
    print("- The LLM knows it can use numpy, scipy.special, and math functions")
    print()


def example_5_complex_expressions():
    """
    Example 5: Complex mathematical expressions

    Demonstrates how to use numpy functions and complex mathematical forms
    in the function_list.
    """
    print("=" * 70)
    print("Example 5: Complex Mathematical Expressions")
    print("=" * 70)

    function_list = [
        ("params[0] * np.sin(params[1] * x) + params[2] * np.cos(params[3] * x)", 1),
        ("params[0] * np.exp(-params[1] * x**2) * np.sin(params[2] * x)", 1),
        ("params[0] / (1 + np.exp(-params[1] * (x - params[2])))", 1),  # Sigmoid
    ]

    prompt = get_prompt(function_list=function_list)

    print("\nInput function_list (complex forms):")
    for i, (expr, _) in enumerate(function_list):
        print(f"  [{i}]: {expr}")

    print("\nGenerated Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)

    print("\nExplanation:")
    print("- Trigonometric functions (sin, cos)")
    print("- Gaussian envelope with oscillation")
    print("- Sigmoid/logistic function")
    print("- All use numpy (np) prefix for functions")
    print()


def example_6_genetic_algorithm_workflow():
    """
    Example 6: Simulating a genetic algorithm workflow

    This shows how get_prompt would be used in an iterative genetic algorithm
    where parent functions evolve over generations.
    """
    print("=" * 70)
    print("Example 6: Genetic Algorithm Workflow Simulation")
    print("=" * 70)

    print("\n--- Generation 1 ---")
    gen1_parents = [("params[0] * x + params[1]", 1)]
    prompt1 = get_prompt(function_list=gen1_parents)
    print("Parent functions:", [p[0] for p in gen1_parents])
    print("\nPrompt for LLM:")
    print(prompt1)

    print("\n--- Generation 2 ---")
    # Simulating that LLM suggested: params[0] * x**2 + params[1] * x + params[2]
    gen2_parents = [
        ("params[0] * x + params[1]", 1),
        ("params[0] * x**2 + params[1] * x + params[2]", 1),
    ]
    prompt2 = get_prompt(function_list=gen2_parents)
    print("Parent functions:", [p[0] for p in gen2_parents])
    print("\nPrompt for LLM:")
    print(prompt2)

    print("\n--- Generation 3 ---")
    # Simulating evolution with exponential term
    gen3_parents = [
        ("params[0] * x**2 + params[1] * x + params[2]", 1),
        ("params[0] * np.exp(params[1] * x) + params[2]", 1),
    ]
    prompt3 = get_prompt(function_list=gen3_parents)
    print("Parent functions:", [p[0] for p in gen3_parents])
    print("\nPrompt for LLM:")
    print(prompt3)

    print("\nExplanation:")
    print("- Each generation builds on previous parent functions")
    print("- The LLM sees the evolution and can suggest improvements")
    print("- Better-fitting expressions survive to the next generation")
    print()


def example_7_understanding_params():
    """
    Example 7: Understanding the params mechanism

    Explains how params[0], params[1], etc. work in the expressions.
    """
    print("=" * 70)
    print("Example 7: Understanding params[]")
    print("=" * 70)

    function_list = [
        ("params[0] * x**2 + params[1] * x + params[2]", 1),
    ]

    prompt = get_prompt(function_list=function_list)

    print("\nGenerated Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)

    print("\nExplanation of params:")
    print("-" * 70)
    print("params is a tuple of fitting parameters that will be optimized.")
    print("\nIn this quadratic example:")
    print("  params[0] = coefficient of x^2 term")
    print("  params[1] = coefficient of x term")
    print("  params[2] = constant term")
    print("\nAfter the LLM suggests a function, the curve_fit algorithm")
    print("optimizes these parameters to best fit the data.")
    print("\nThe LLM only suggests the FORM of the equation (structure),")
    print("not the actual parameter values!")
    print()


def example_8_practical_use_case():
    """
    Example 8: Practical use case with real scenario

    Shows how you might use get_prompt in a real symbolic regression task.
    """
    print("=" * 70)
    print("Example 8: Practical Use Case - Damped Oscillation")
    print("=" * 70)

    # Suppose we're trying to fit data that looks like a damped oscillation
    # We start with some initial guesses

    imports = [
        "import numpy as np",
        "from numpy import sin, cos, exp"  # Allow direct use without np. prefix
    ]

    function_list = [
        # Generation 1: Simple sine wave
        ("params[0] * sin(params[1] * x + params[2])", 1),

        # Generation 2: Added damping
        ("params[0] * exp(-params[1] * x) * sin(params[2] * x + params[3])", 1),
    ]

    prompt = get_prompt(function_list=function_list, imports=imports)

    print("\nScenario: Fitting damped oscillation data")
    print("\nImports provided:")
    for imp in imports:
        print(f"  {imp}")

    print("\nParent functions (evolution):")
    for i, (expr, _) in enumerate(function_list):
        print(f"  Generation {i+1}: {expr}")

    print("\nGenerated Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)

    print("\nWhat happens next:")
    print("1. This prompt is sent to the LLM along with an image of the data")
    print("2. The LLM completes: curve_2 = lambda x, *params: <new expression>")
    print("3. The new expression might improve on the damping model")
    print("4. Parameters are optimized using curve_fit")
    print("5. The best-fitting expression becomes a parent for the next generation")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  get_prompt() Function Demonstration".center(68) + "*")
    print("*" + "  Focus: function_list and imports parameters".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")

    # example_1_default_behavior()
    # input("Press Enter to continue to Example 2...")

    # example_2_custom_function_list()
    # input("Press Enter to continue to Example 3...")

    example_3_multiple_parent_functions()
    input("Press Enter to continue to Example 4...")

    # example_4_custom_imports()
    # input("Press Enter to continue to Example 5...")

    # example_5_complex_expressions()
    # input("Press Enter to continue to Example 6...")

    # example_6_genetic_algorithm_workflow()
    # input("Press Enter to continue to Example 7...")

    # example_7_understanding_params()
    # input("Press Enter to continue to Example 8...")

    # example_8_practical_use_case()

    # print("\n")
    # print("*" * 70)
    # print("*" + " " * 68 + "*")
    # print("*" + "  End of Demonstration".center(68) + "*")
    # print("*" + " " * 68 + "*")
    # print("*" * 70)
    # print("\n")

    # print("Key Takeaways:")
    # print("-" * 70)
    # print("1. function_list: List of (expression_string, int) tuples")
    # print("   - Each tuple represents a 'parent function' for the LLM to build upon")
    # print("   - Used in genetic algorithms to show evolution of expressions")
    # print()
    # print("2. imports: List of import statement strings")
    # print("   - Defines which Python libraries the LLM can use")
    # print("   - Default is ['import numpy as np']")
    # print("   - Can include scipy, math, or other scientific libraries")
    # print()
    # print("3. Prompt structure:")
    # print("   - Import statements come first")
    # print("   - Parent functions defined as curve_0, curve_1, ...")
    # print("   - Final incomplete lambda for LLM to complete")
    # print()
    # print("4. params mechanism:")
    # print("   - params[0], params[1], ... are fitting parameters")
    # print("   - LLM suggests the FORM, curve_fit optimizes VALUES")
    # print("-" * 70)


if __name__ == "__main__":
    main()
