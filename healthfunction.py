import numpy as np

def create_function(premium, deductible, subsidy, coinsurance, copay, max_out_of_pocket):
    medical_cost = np.linspace(0, 100000, 100000)  # Medical costs range
    premium = 12 * premium  # Convert to yearly premium
    
    if coinsurance == 0:
        coinsurance = 1
    if copay == 0:
        copay = max_out_of_pocket

    # Phase 1: Medical costs below the deductible
    price = [medical_cost <= deductible]
    actual_cost = [lambda medical_cost: premium + medical_cost]  # You pay the premium + actual medical costs up to the deductible

    # Phase 2: Subsidy covers costs between deductible and deductible + subsidy
    if subsidy > 0:
        price.append((medical_cost > deductible) & (medical_cost <= deductible + subsidy))
        actual_cost.append(lambda medical_cost: premium + deductible)  # You pay the premium and deductible, costs are covered by the subsidy

    # Phase 3: Coinsurance applies after deductible and subsidy, up to copay or max out-of-pocket
    price.append((medical_cost > deductible + subsidy) & (deductible + coinsurance * (medical_cost - deductible - subsidy) <= min(copay, max_out_of_pocket)))
    actual_cost.append(lambda medical_cost: premium + deductible + coinsurance * (medical_cost - deductible - subsidy))  # Pay premium, deductible, and a fraction of costs

    # Phase 4: Once max out-of-pocket is reached, costs are capped
    price.append((deductible + coinsurance * (medical_cost - deductible - subsidy)) > min(copay, max_out_of_pocket))
    actual_cost.append(lambda medical_cost: premium + min(copay, max_out_of_pocket))  # Cap total costs at the out-of-pocket maximum
    
    
    # Create the piecewise function
    function = np.piecewise(medical_cost, price, actual_cost)
    return medical_cost, function

def find_intersections(medical_cost, f1, f2):
    """
    Find intersections between two cost functions.
    """
    diff = f1 - f2
    signs = np.sign(diff)
    intersections = np.where(np.diff(signs) != 0)[0]  # Points where the sign changes

    # Get the x and y values of the intersections
    x_intersections = medical_cost[intersections]
    x = [point.tolist() if isinstance(point, np.ndarray) else point for point in x_intersections]
    
    y_intersections = f1[intersections]
    y = [point.tolist() if isinstance(point, np.ndarray) else point for point in y_intersections]

    return x, y

'''
import matplotlib.pyplot as plt

lst = []
# Generate the function
medical_cost, function = create_function(1000, 5000, 6000, 0.5, 40000, 40000)
lst.append((medical_cost, function))
medical_cost, function = create_function(2000, 3000, 6000, 0.7, 40000, 40000)
lst.append((medical_cost, function))
medical_cost, function = create_function(4000, 1000, 4000, 0.2, 40000, 40000)
lst.append((medical_cost, function))

plt.figure()

# Plot all the lines stored in the session
for medical_cost, function in lst:
    plt.plot(medical_cost, function, label='lal')

plt.title('Insurance Plan Cost vs Medical Spending')
plt.xlabel('Medical Spending ($)')
plt.ylabel('Actual Cost ($)')
plt.grid(True)
plt.legend()

plt.show()
'''
