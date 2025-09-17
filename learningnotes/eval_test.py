#!/usr/bin/env python3
"""
Test script to demonstrate how eval() works in the context of the llmlex codebase.
This shows how mathematical expressions are converted from strings to callable functions.
"""

import numpy as np

def demonstrate_eval_basics():
    """Basic demonstration of eval() function"""
    print("=" * 60)
    print("1. BASIC EVAL DEMONSTRATION")
    print("=" * 60)
    
    # Simple expression evaluation
    expression = "2 + 3 * 4"
    result = eval(expression)
    print(f"String: '{expression}'")
    print(f"eval('{expression}') = {result}")
    print()
    
    # Variable in expression
    x = 5
    expression = "x ** 2 + 2 * x + 1"
    result = eval(expression)
    print(f"With x = {x}")
    print(f"String: '{expression}'")
    print(f"eval('{expression}') = {result}")
    print()

def demonstrate_lambda_eval():
    """Demonstrate eval with lambda functions (like in the codebase)"""
    print("=" * 60)
    print("2. LAMBDA FUNCTION EVAL (LIKE IN LLMLEX)")
    print("=" * 60)
    
    # Example 1: Simple quadratic function
    ansatz_str = "params[0] * x**2 + params[1] * x + params[2]"
    lambda_str = "lambda x, *params: " + ansatz_str
    
    print(f"ansatz_str = '{ansatz_str}'")
    print(f"lambda_str = '{lambda_str}'")
    
    # Convert string to actual function using eval
    curve = eval(lambda_str)
    print(f"curve = eval(lambda_str)")
    print(f"Type of curve: {type(curve)}")
    
    # Test the function
    x_val = 2.0
    params = [1, -3, 2]  # coefficients: 1*x^2 + (-3)*x + 2
    result = curve(x_val, *params)
    expected = params[0] * x_val**2 + params[1] * x_val + params[2]
    
    print(f"\nTesting curve({x_val}, {params}):")
    print(f"Result: {result}")
    print(f"Expected: {expected}")
    print(f"Match: {result == expected}")
    print()

def demonstrate_complex_expressions():
    """Demonstrate with more complex mathematical expressions"""
    print("=" * 60)
    print("3. COMPLEX MATHEMATICAL EXPRESSIONS")
    print("=" * 60)
    
    examples = [
        "params[0] * np.sin(params[1] * x) + params[2]",
        "params[0] * np.exp(-params[1] * x**2)",
        "params[0] / (1 + np.exp(-params[1] * (x - params[2])))",  # Sigmoid
        "params[0] * x**params[1] + params[2]"
    ]
    
    for i, ansatz_str in enumerate(examples, 1):
        print(f"Example {i}: {ansatz_str}")
        lambda_str = "lambda x, *params: " + ansatz_str
        
        try:
            curve = eval(lambda_str)
            
            # Test with some values
            x_val = 1.0
            params = [2.0, 0.5, 1.0]
            result = curve(x_val, *params)
            
            print(f"  Function created successfully")
            print(f"  curve({x_val}, {params}) = {result}")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        print()

def demonstrate_error_cases():
    """Show what happens when eval fails"""
    print("=" * 60)
    print("4. ERROR CASES")
    print("=" * 60)
    
    bad_expressions = [
        "params[0] * unknown_function(x)",
        "params[0] * x +",  # Incomplete expression
        "import os; os.system('ls')",  # Dangerous code
    ]
    
    for expr in bad_expressions:
        lambda_str = "lambda x, *params: " + expr
        print(f"Trying: '{lambda_str}'")
        
        try:
            curve = eval(lambda_str)
            print("  Success (unexpected!)")
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")
        print()

def simulate_llmlex_workflow():
    """Simulate the actual workflow from the llmlex codebase"""
    print("=" * 60)
    print("5. SIMULATING LLMLEX WORKFLOW")
    print("=" * 60)
    
    # Simulate what might come from an AI model
    ai_responses = [
        "2.5 * x**2 - 1.3 * x + 0.8",
        "1.2 * np.exp(-0.5 * x**2)",
        "3.0 * np.sin(1.5 * x) + 2.0 * np.cos(0.8 * x)"
    ]
    
    for i, ansatz_str in enumerate(ai_responses, 1):
        print(f"AI Response {i}: '{ansatz_str}'")
        
        # This mimics the code in response.py around line 166-172
        lambda_str = "lambda x,*params: " + ansatz_str
        print(f"Lambda string: '{lambda_str}'")
        
        try:
            # The actual eval call from the codebase
            curve = eval(lambda_str)
            print("✓ Successfully converted to function")
            
            # Test it with some data points
            x_values = np.array([0, 1, 2, 3, 4])
            results = [curve(x) for x in x_values]
            
            print(f"Test values: x = {x_values}")
            print(f"Results: y = {np.array(results)}")
            
        except Exception as e:
            print(f"✗ Failed to evaluate: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    print("EVAL() DEMONSTRATION FOR LLMLEX CODEBASE")
    print("This script shows how eval() converts string expressions to callable functions")
    print()
    
    demonstrate_eval_basics()
    demonstrate_lambda_eval()
    demonstrate_complex_expressions()
    demonstrate_error_cases()
    simulate_llmlex_workflow()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("eval() in the llmlex codebase:")
    print("1. Takes a string containing a lambda function definition")
    print("2. Converts it to an actual callable Python function")
    print("3. Allows dynamic creation of mathematical functions from AI responses")
    print("4. Enables the system to work with arbitrary mathematical expressions")
    print()
    print("Security note: eval() can be dangerous with untrusted input!")
