"""
curve_fit.py - Comprehensive Guide to scipy.optimize.curve_fit

This file explains the curve_fit function from scipy.optimize, which is used for
non-linear least squares fitting of functions to data.

Author: Learning Notes
Date: September 17, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, OptimizeWarning
import warnings


def introduction():
    """
    curve_fit is a powerful function for fitting arbitrary functions to data.
    
    Syntax:
    popt, pcov = curve_fit(f, xdata, ydata, p0=None, sigma=None, absolute_sigma=False,
                          check_finite=True, bounds=(-inf, inf), method=None,
                          jac=None, **kwargs)
    
    Parameters:
    - f: callable function to fit (takes x as first argument, then parameters)
    - xdata: array_like, independent variable data
    - ydata: array_like, dependent variable data  
    - p0: array_like, initial guess for parameters (optional)
    - sigma: array_like, uncertainties in ydata (optional)
    - bounds: 2-tuple of array_like, bounds for parameters (optional)
    
    Returns:
    - popt: array, optimal parameters
    - pcov: 2d array, covariance matrix of parameters
    """
    print("curve_fit: Non-linear least squares fitting")
    print("=" * 50)


def linear_example():
    """Example 1: Fitting a linear function y = ax + b"""
    print("\n1. Linear Function Example")
    print("-" * 30)
    
    # Define the linear function
    def linear_func(x, a, b):
        return a * x + b
    
    # Generate synthetic data with noise
    x_data = np.linspace(0, 10, 50)
    y_true = 2.5 * x_data + 1.3  # True parameters: a=2.5, b=1.3
    noise = np.random.normal(0, 0.5, len(x_data))
    y_data = y_true + noise
    
    # Fit the curve
    popt, pcov = curve_fit(linear_func, x_data, y_data)
    
    print(f"True parameters: a=2.5, b=1.3")
    print(f"Fitted parameters: a={popt[0]:.3f}, b={popt[1]:.3f}")
    print(f"Parameter uncertainties: ±{np.sqrt(np.diag(pcov))}")
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.scatter(x_data, y_data, alpha=0.6, label='Data with noise')
    plt.plot(x_data, linear_func(x_data, *popt), 'r-', label='Fitted curve')
    plt.plot(x_data, y_true, 'g--', label='True curve')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.title('Linear Function Fitting')
    plt.grid(True, alpha=0.3)
    plt.show()
    plt.savefig('linear_function_fitting.png')


def exponential_example():
    """Example 2: Fitting an exponential function y = a * exp(b * x) + c"""
    print("\n2. Exponential Function Example")
    print("-" * 35)
    
    # Define the exponential function
    def exp_func(x, a, b, c):
        return a * np.exp(b * x) + c
    
    # Generate synthetic data
    x_data = np.linspace(0, 2, 30)
    y_true = 2.0 * np.exp(-1.5 * x_data) + 0.5  # True: a=2.0, b=-1.5, c=0.5
    noise = np.random.normal(0, 0.1, len(x_data))
    y_data = y_true + noise
    
    # Initial guess is important for non-linear functions
    initial_guess = [1.0, -1.0, 0.0]
    
    try:
        popt, pcov = curve_fit(exp_func, x_data, y_data, p0=initial_guess)
        
        print(f"True parameters: a=2.0, b=-1.5, c=0.5")
        print(f"Fitted parameters: a={popt[0]:.3f}, b={popt[1]:.3f}, c={popt[2]:.3f}")
        print(f"Parameter uncertainties: ±{np.sqrt(np.diag(pcov))}")
        
        # Calculate R-squared
        y_pred = exp_func(x_data, *popt)
        ss_res = np.sum((y_data - y_pred) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        print(f"R-squared: {r_squared:.4f}")
        
    except RuntimeError as e:
        print(f"Fitting failed: {e}")


def polynomial_example():
    """Example 3: Fitting a polynomial function"""
    print("\n3. Polynomial Function Example")
    print("-" * 33)
    
    # Define polynomial function
    def poly_func(x, a, b, c, d):
        return a * x**3 + b * x**2 + c * x + d
    
    # Generate data
    x_data = np.linspace(-2, 2, 40)
    y_true = 0.5 * x_data**3 - 1.2 * x_data**2 + 0.8 * x_data + 2.1
    noise = np.random.normal(0, 0.2, len(x_data))
    y_data = y_true + noise
    
    # Fit with bounds
    bounds = ([-np.inf, -np.inf, -np.inf, -np.inf], 
              [np.inf, np.inf, np.inf, np.inf])
    
    popt, pcov = curve_fit(poly_func, x_data, y_data, bounds=bounds)
    
    print(f"True coefficients: [0.5, -1.2, 0.8, 2.1]")
    print(f"Fitted coefficients: {popt}")


def with_uncertainties_example():
    """Example 4: Using measurement uncertainties (sigma parameter)"""
    print("\n4. Fitting with Measurement Uncertainties")
    print("-" * 42)
    
    def gaussian(x, amp, mean, std):
        return amp * np.exp(-((x - mean) ** 2) / (2 * std ** 2))
    
    # Generate data with varying uncertainties
    x_data = np.linspace(-5, 5, 50)
    y_true = gaussian(x_data, 10, 0, 1.5)
    
    # Simulate measurement uncertainties (higher at edges)
    uncertainties = 0.2 + 0.3 * np.abs(x_data) / 5
    noise = np.random.normal(0, uncertainties)
    y_data = y_true + noise
    
    # Fit without uncertainties
    popt1, pcov1 = curve_fit(gaussian, x_data, y_data)
    
    # Fit with uncertainties
    popt2, pcov2 = curve_fit(gaussian, x_data, y_data, sigma=uncertainties)
    
    print("Without uncertainties:", popt1)
    print("With uncertainties:", popt2)
    print("Uncertainty-weighted fit gives different results!")


def bounded_fitting_example():
    """Example 5: Using parameter bounds"""
    print("\n5. Bounded Parameter Fitting")
    print("-" * 31)
    
    def sigmoid(x, a, b, c, d):
        return a / (1 + np.exp(-b * (x - c))) + d
    
    x_data = np.linspace(-10, 10, 50)
    y_true = 5 / (1 + np.exp(-0.5 * (x_data - 2))) + 1
    noise = np.random.normal(0, 0.2, len(x_data))
    y_data = y_true + noise
    
    # Set bounds: a > 0, b > 0, c can be anything, d >= 0
    bounds = ([0, 0, -np.inf, 0], [np.inf, np.inf, np.inf, np.inf])
    
    try:
        popt, pcov = curve_fit(sigmoid, x_data, y_data, bounds=bounds)
        print(f"Fitted parameters with bounds: {popt}")
        print("Bounds ensure physically meaningful parameters!")
        
    except ValueError as e:
        print(f"Bounds error: {e}")


def error_handling_examples():
    """Example 6: Common errors and how to handle them"""
    print("\n6. Error Handling and Troubleshooting")
    print("-" * 38)
    
    def difficult_func(x, a, b, c):
        return a * np.sin(b * x + c)
    
    x_data = np.linspace(0, 10, 30)
    y_data = 2 * np.sin(3 * x_data + 1) + np.random.normal(0, 0.1, 30)
    
    print("Common issues and solutions:")
    print("1. OptimizeWarning - covariance matrix issues")
    print("2. RuntimeError - maximum iterations exceeded")
    print("3. ValueError - invalid bounds or initial guess")
    
    # Suppress warnings for demonstration
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", OptimizeWarning)
        
        try:
            # This might fail without good initial guess
            popt, pcov = curve_fit(difficult_func, x_data, y_data, 
                                 p0=[1, 1, 0], maxfev=5000)
            print(f"Success with good initial guess: {popt}")
            
        except RuntimeError:
            print("Failed: Try better initial guess or increase maxfev")
        except ValueError as e:
            print(f"Parameter error: {e}")


def advanced_features():
    """Example 7: Advanced features"""
    print("\n7. Advanced Features")
    print("-" * 20)
    
    print("Advanced curve_fit features:")
    print("• method parameter: 'lm', 'trf', 'dogbox'")
    print("• jac parameter: provide analytical Jacobian")
    print("• absolute_sigma: treat sigma as absolute vs relative")
    print("• check_finite: check for NaN/inf in input data")
    print("• **kwargs: additional arguments passed to underlying optimizer")
    
    def custom_func(x, a, b):
        return a * x**b
    
    # Example with different methods
    x_data = np.linspace(1, 10, 20)
    y_data = 2.5 * x_data**1.3 + np.random.normal(0, 0.1, 20)
    
    methods = ['lm', 'trf', 'dogbox']
    for method in methods:
        try:
            popt, _ = curve_fit(custom_func, x_data, y_data, method=method)
            print(f"Method '{method}': a={popt[0]:.3f}, b={popt[1]:.3f}")
        except Exception as e:
            print(f"Method '{method}' failed: {e}")


def best_practices():
    """Best practices for using curve_fit"""
    print("\n8. Best Practices")
    print("-" * 17)
    
    practices = [
        "1. Always provide good initial guesses (p0) for non-linear functions",
        "2. Use bounds to constrain parameters to physically meaningful ranges",
        "3. Include measurement uncertainties (sigma) when available",
        "4. Check the covariance matrix for parameter correlation",
        "5. Validate results by plotting fitted curve vs data",
        "6. Use try-except blocks to handle fitting failures gracefully",
        "7. Consider data preprocessing (scaling, outlier removal)",
        "8. For complex functions, try different optimization methods",
        "9. Check residuals to assess goodness of fit",
        "10. Be aware of local minima in non-linear optimization"
    ]
    
    for practice in practices:
        print(practice)


def main():
    """Run all examples and explanations"""
    introduction()
    linear_example()
    exponential_example()
    polynomial_example()
    with_uncertainties_example()
    bounded_fitting_example()
    error_handling_examples()
    advanced_features()
    best_practices()
    
    print("\n" + "=" * 60)
    print("curve_fit is a versatile tool for fitting functions to data!")
    print("Remember: good initial guesses and bounds are key to success.")
    print("=" * 60)


if __name__ == "__main__":
    # Set random seed for reproducible examples
    np.random.seed(42)
    main()
