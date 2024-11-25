from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
from utils.preprocess import process_user_input
from utils.prediction import predict_financial_health, calculate_financial_ratios
from utils.visualization import create_visualizations
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(
    handlers=[RotatingFileHandler('logs/app.log', maxBytes=100000, backupCount=3)],
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# Load model
try:
    with open('model/dt_model.pkl', 'rb') as file:
        model = pickle.load(file)
except Exception as e:
    logging.error(f"Error loading model: {str(e)}")
    model = None

# Constants
CATEGORY_MAPPING = {
    'Education': 0, 'Entertainment': 1, 'Food': 2, 'Groceries': 3,
    'Healthcare': 4, 'Travel': 5, 'Utilities': 6
}
DAY_MAPPING = {
    'Friday': 0, 'Monday': 1, 'Saturday': 2, 'Sunday': 3,
    'Thursday': 4, 'Tuesday': 5, 'Wednesday': 6
}

@app.route('/')
def home():
    return render_template('index.html',
                         categories=list(CATEGORY_MAPPING.keys()),
                         days=list(DAY_MAPPING.keys()))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data and process it
        input_data = process_user_input(request.form, CATEGORY_MAPPING, DAY_MAPPING)
        
        # Make prediction
        prediction = predict_financial_health(model, input_data)
        
        # Calculate ratios and get recommendations
        ratios = calculate_financial_ratios(input_data)
        
        # Generate visualizations
        visualizations = create_visualizations(input_data, prediction, ratios)
        
        return render_template('result.html',
                             prediction=prediction,
                             ratios=ratios,
                             visualizations=visualizations)
    
    except Exception as e:
        logging.error(f"Error in prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/visualize')
def visualize():
    try:
        df = pd.read_excel("model/family_financial_and_transactions_data.xlsx")
        visualizations = create_visualizations(df)
        return render_template('visualization.html', visualizations=visualizations)
    except Exception as e:
        logging.error(f"Error in visualization: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)