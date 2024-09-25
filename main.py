
from flask import Flask, render_template, request, send_file
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)


def create_function(premium, deductible, subsidy, coinsurance, copay, max_out_of_pocket):
    medical_cost = np.linspace(0, 100000, 100000)  # Medical costs range
    premium = 12 * premium # Convert to yearly premium
    
    # Define conditions for the piecewise function
    if copay != max_out_of_pocket:
        x = [medical_cost < deductible + copay, medical_cost >= deductible + copay]
        actual_cost = [
            lambda medical_cost: premium + medical_cost,  # For medical costs below deductible + copay
            lambda medical_cost: premium + deductible + copay  # For medical costs above deductible + copay
        ]
    else:
        x = [
            medical_cost <= deductible,  # For medical costs less than or equal to deductible
            (medical_cost > deductible) & (medical_cost <= deductible + subsidy), # For when the subsidy kicks in
            (medical_cost > deductible + subsidy) & (deductible + coinsurance * (medical_cost - deductible - subsidy) < max_out_of_pocket),  # Between deductible and max out-of-pocket
            deductible + coinsurance * (medical_cost - deductible - subsidy) >= max_out_of_pocket  # Actual costs above max out-of-pocket
        ]
        actual_cost = [
            lambda medical_cost: premium + medical_cost,  # Up to deductible
            lambda medical_cost: premium + deductible, # Stays Constant if there is a Subsidy
            lambda medical_cost: premium + deductible + coinsurance * (medical_cost - deductible - subsidy),  # Between deductible and out-of-pocket max
            lambda medical_cost: premium + max_out_of_pocket  # Once max out-of-pocket is reached
        ]
    
    # Create the piecewise function
    function = np.piecewise(medical_cost, x, actual_cost)
    
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
    y_intersections = f1[intersections]

    return x_intersections, y_intersections


# Sample data for health insurance plans
data = {
    'Plan': [],
    'Premium': [],
    'Deductible': [],
    'Fixed Subsidy': [],
    'Co-insurance': [],
    'Co-pay': [],
    'Max Out of Pocket': []
}

number_of_plans = int(input('How many healthcare plans would you like to compare? '))

for _ in range(number_of_plans):
    print('If any field does not apply, write N/A')
    print(f'Plan {_+1}:')
    

    plan = input('Name of plan: ')
    premium = input('Cost of Premium ($) (Monthly): ')
    deductible = input('Deductible ($) (Yearly): ')
    subsidy = input('Fixed Subsidy ($): ')
    coinsurance = input('Co-insurance (decimal): ')
    copay = input('Co-pay ($): ')
    max_out_of_pocket = input('Max Out of Pocket ($): ')

    
    data['Plan'].append(plan)
    data['Premium'].append(int(premium) if premium != 'N/A' else 0)
    data['Deductible'].append(int(deductible) if deductible != 'N/A' else 0)
    data['Fixed Subsidy'].append(int(subsidy) if subsidy != 'N/A' else 0)
    data['Co-insurance'].append(float(coinsurance) if coinsurance != 'N/A' else 1)
    data['Co-pay'].append(int(copay) if copay != 'N/A' else int(max_out_of_pocket))
    data['Max Out of Pocket'].append(int(max_out_of_pocket) if max_out_of_pocket != 'N/A' else max_out_of_pocket)
    
    print()


plt.figure()

# Store the medical costs and functions for all plans
medical_costs = []
functions = []

for i in range(len(data['Plan'])):
    medical_cost, function = create_function(
        data['Premium'][i], data['Deductible'][i], data['Fixed Subsidy'][i],
        data['Co-insurance'][i], data['Co-pay'][i], data['Max Out of Pocket'][i])
    
    medical_costs.append(medical_cost)
    functions.append(function)
    
    # Plot each plan
    plt.plot(medical_cost, function, label=data['Plan'][i], linewidth=1)

# Check for intersections between all pairs of plans
for i in range(len(functions)):
    for j in range(i + 1, len(functions)):
        x_intersections, y_intersections = find_intersections(medical_costs[i], functions[i], functions[j])
        
        # Mark the intersection points
        plt.scatter(x_intersections, y_intersections, color='red', label=f'Intersection of {data["Plan"][i]} and {data["Plan"][j]}')

plt.title('Insurance Comparison')
plt.xlabel('Medical Spending ($)')
plt.ylabel('Your Actual Cost ($)')
plt.grid(True)
plt.legend()
plt.show()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    # Get data from form
    premium = float(request.form['premium'])
    deductible = float(request.form['deductible'])
    subsidy = float(request.form['subsidy'])
    coinsurance = float(request.form['coinsurance'])
    copay = float(request.form['copay'])
    max_out_of_pocket = float(request.form['max_out_of_pocket'])
    
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
