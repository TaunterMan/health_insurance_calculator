from flask import Flask, render_template, request, send_file, session, redirect, url_for, jsonify
from flask_session import Session
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
from io import BytesIO
import healthfunction
import os

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.urandom(24)
Session(app)

# Initialize the session to store graph data
@app.before_request
def setup_session():
    if 'graph_data' not in session:
        session['graph_data'] = []
        
        
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plot', methods=['POST'])
def plot():
    try:
        name = str(request.form['name'])
        premium = float(request.form['premium'])
        deductible = float(request.form['deductible'])
        subsidy = float(request.form['subsidy'])
        coinsurance = float(request.form['coinsurance'])
        copay = float(request.form['copay'])
        max_out_of_pocket = float(request.form['max_out_of_pocket'])
    except (ValueError, KeyError):
        return "Invalid input", 400

    # Generate the function
    medical_cost, function = healthfunction.create_function(premium, deductible, subsidy, coinsurance, copay, max_out_of_pocket)
    # Store the graph data in the session (so it accumulates over multiple submissions)
    session['graph_data'].append((medical_cost, function, name))
        
    points, names = intersections()
        
    return jsonify({
        'points': points,
        'names': names
        })

    
def intersections():
    name_list = []
    intersection_points = []
    for i in range(len(session['graph_data'])):
        for j in range(i + 1, len(session['graph_data'])):
            x_intersection, y_intersection = healthfunction.find_intersections(session['graph_data'][0][0], session['graph_data'][i][1], session['graph_data'][j][1])
            intersection_points.append((x_intersection, y_intersection))
            name_list.append((session['graph_data'][i][2], session['graph_data'][j][2]))
    return intersection_points, name_list

@app.route('/plot_image')
def plot_image():
    # Create the plot
    if session.get('graph_data'):
        # Create or clear the figure (make sure we don't keep plotting on old figures)
        plt.figure()
    
        # Plot all the lines stored in the session
        for medical_cost, function, name in session['graph_data']:
            plt.plot(medical_cost, function, label=name)
        
        plt.title('Comparison of Insurance Costs')
        plt.xlabel('Your Out of Pocket Cost ($)')
        plt.ylabel('Market Price ($)')
        plt.grid(True)
        plt.legend()
    
        # Save the plot to a BytesIO object
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)  # Move the buffer pointer to the beginning
    
        # Close the plot (to prevent memory leakage with multiple plots)
        plt.close()

        # Return the image as a response
        return send_file(buf, mimetype='image/png')

# Reset the graph session
@app.route('/reset', methods=['POST'])
def reset():
    session.pop('graph_data', None)  # Remove the graph data
    return redirect(url_for('index'))  # Redirect back to the index page

if __name__ == '__main__':
    app.run(debug=True)
