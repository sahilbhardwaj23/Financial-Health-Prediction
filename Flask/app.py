from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages and session

# Constants
CATEGORY_MAPPING = {'Education': 0, 'Entertainment': 1, 'Food': 2, 'Groceries': 3, 
                   'Healthcare': 4, 'Travel': 5, 'Utilities': 6}
DAY_MAPPING = {'Friday': 0, 'Monday': 1, 'Saturday': 2, 'Sunday': 3, 
               'Thursday': 4, 'Tuesday': 5, 'Wednesday': 6}

# Load dataset
def load_data():
    try:
        return pd.read_excel("data/family_financial_and_transactions_data.xlsx")
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None

# Load prediction model
def load_model():
    try:
        with open('models/dt_model.pkl', 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

def calculate_financial_ratios(data):
    """Calculate key financial ratios from input data"""
    income = data['Income'].values[0]
    ratios = {
        'savings_rate': (data['Savings'].values[0] / income * 100) if income > 0 else 0,
        'dti_ratio': ((data['Loan Payments'].values[0] + data['Credit Card Spending'].values[0]) / income * 100) if income > 0 else 0,
        'expense_ratio': (data['Monthly Expenses'].values[0] / income * 100) if income > 0 else 0,
        'credit_utilization': (data['Credit Card Spending'].values[0] / income * 100) if income > 0 else 0,
        'debt_payments': data['Loan Payments'].values[0] + data['Credit Card Spending'].values[0],
        'discretionary_income': income - data['Monthly Expenses'].values[0] - data['Loan Payments'].values[0]
    }
    return ratios

def get_detailed_recommendations(ratios, score, input_data):
    """Generate detailed financial recommendations based on ratios and score"""
    recommendations = []
    total_impact = 0
    
    # Savings Recommendations
    if ratios['savings_rate'] < 20:
        impact = min(5, (20 - ratios['savings_rate']) / 4)
        monthly_savings_target = (input_data['Income'].values[0] * 0.2) - input_data['Savings'].values[0]
        recommendations.append({
            'category': '💰 Savings',
            'priority': 'High',
            'recommendations': [
                f"Increase monthly savings by ${monthly_savings_target:.2f}",
                "Set up automatic transfers to savings account",
                "Look for additional income opportunities",
                "Review and eliminate unnecessary subscriptions"
            ],
            'impact': impact,
            'current': f"{ratios['savings_rate']:.1f}%",
            'target': "20%",
            'tips': [
                "Use the 50/30/20 budgeting rule",
                "Save windfalls and tax refunds",
                "Consider a high-yield savings account"
            ]
        })
        total_impact += impact

    # Debt Management
    if ratios['dti_ratio'] > 36:
        impact = min(4, (ratios['dti_ratio'] - 36) / 10)
        debt_reduction_target = ratios['debt_payments'] - (input_data['Income'].values[0] * 0.36)
        recommendations.append({
            'category': '💳 Debt Management',
            'priority': 'High' if ratios['dti_ratio'] > 50 else 'Medium',
            'recommendations': [
                f"Reduce monthly debt payments by ${debt_reduction_target:.2f}",
                "Consider debt consolidation",
                "Prioritize high-interest debt",
                "Negotiate lower interest rates"
            ],
            'impact': impact,
            'current': f"{ratios['dti_ratio']:.1f}%",
            'target': "36%",
            'tips': [
                "Use debt avalanche or snowball method",
                "Avoid taking on new debt",
                "Consider balance transfer options"
            ]
        })
        total_impact += impact

    # Add other recommendations (Expense Management, Credit Card Usage, etc.)
    # ... (Similar structure as above)
    
    return recommendations, total_impact

def create_figure_to_base64(fig):
    """Convert matplotlib figure to base64 string"""
    img = io.BytesIO()
    FigureCanvas(fig).print_png(img)
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

# Routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get form data and convert appropriately
            input_data = pd.DataFrame({
                'Category': [CATEGORY_MAPPING[request.form.get('category')]],
                'Amount': [float(request.form.get('amount'))],
                'Income': [float(request.form.get('income'))],
                'Savings': [float(request.form.get('savings'))],
                'Monthly Expenses': [float(request.form.get('monthly_expenses'))],
                'Loan Payments': [float(request.form.get('loan_payments'))],
                'Credit Card Spending': [float(request.form.get('credit_card_spending'))],
                'Dependents': [int(float(request.form.get('dependents')))],  # Convert to float first, then int
                'Financial Goals Met (%)': [int(float(request.form.get('financial_goals_met')))],  # Convert to float first, then int
                'Day of Week': [DAY_MAPPING[request.form.get('day_of_week')]],
                'Total Members': [int(float(request.form.get('total_members')))]  # Convert to float first, then int
            })

            # Load model and make prediction
            model = load_model()
            if model is None:
                return jsonify({'error': 'Model loading failed'}), 500

            prediction = model.predict(input_data)[0]
            ratios = calculate_financial_ratios(input_data)
            recommendations, total_impact = get_detailed_recommendations(ratios, prediction, input_data)

            # Create gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prediction,
                title={'text': "Financial Health Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "red"},
                        {'range': [50, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': prediction
                    }
                }
            ))

            return jsonify({
                'prediction': prediction,
                'ratios': ratios,
                'recommendations': recommendations,
                'total_impact': total_impact,
                'gauge_chart': fig.to_json()
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # GET request - render the prediction form
    return render_template('prediction.html', 
                         categories=CATEGORY_MAPPING.keys(),
                         days=DAY_MAPPING.keys())
    
# Update the visualize route in app.py

@app.route('/visualize')
def visualize():
    df = load_data()
    if df is None:
        return render_template('visualization.html', error="Data loading failed")

    # Create visualizations dictionary
    visualizations = {}

    # 1. Category Distribution
    plt.figure(figsize=(10, 8))
    category_counts = df['Category'].value_counts()
    plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', 
            startangle=90, colors=plt.cm.Blues(np.linspace(0.3, 0.7, len(category_counts))))
    plt.title('Distribution of Categories')
    visualizations['category_dist'] = create_figure_to_base64(plt.gcf())
    plt.close()

    # 2. Family Member Distribution
    plt.figure(figsize=(12, 6))
    member_counts = df['Member ID'].str.extract(r'Member(\d+)', expand=False).astype(int).value_counts()
    sns.barplot(x=member_counts.index, y=member_counts.values, palette="viridis")
    plt.title("Family Member Distribution")
    plt.xlabel("Member Number")
    plt.ylabel("Frequency")
    visualizations['member_dist'] = create_figure_to_base64(plt.gcf())
    plt.close()

    # 3. Transaction Trends
    plt.figure(figsize=(14, 7))
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
    date_amount = df.groupby('Transaction Date')['Monthly Expenses'].mean().reset_index()
    plt.plot(date_amount['Transaction Date'], date_amount['Monthly Expenses'], 
            marker='o', color='blue', linewidth=2)
    plt.title("Transaction Date vs Monthly Expenses")
    plt.xlabel("Transaction Date")
    plt.ylabel("Monthly Expenses")
    plt.xticks(rotation=45)
    plt.tight_layout()
    visualizations['transaction_trends'] = create_figure_to_base64(plt.gcf())
    plt.close()

    # 4. Expenses by Day
    plt.figure(figsize=(10, 8))
    df['Day of Week'] = df['Transaction Date'].dt.day_name()
    day_expenses = df.groupby('Day of Week')['Monthly Expenses'].mean()
    plt.pie(day_expenses, labels=day_expenses.index, autopct='%1.1f%%', 
            startangle=90, colors=sns.color_palette("pastel"))
    plt.title("Average Monthly Expenses by Day of the Week")
    visualizations['expenses_by_day'] = create_figure_to_base64(plt.gcf())
    plt.close()

    # 5. Category-wise Analysis
    plt.figure(figsize=(10, 8))
    category_analysis = df.groupby('Category')['Monthly Expenses'].mean()
    plt.pie(category_analysis, labels=category_analysis.index, autopct='%1.1f%%', 
            startangle=140, colors=sns.color_palette("tab10"))
    plt.title("Average Monthly Expenses by Category")
    visualizations['category_analysis'] = create_figure_to_base64(plt.gcf())
    plt.close()

    return render_template('visualization.html', visualizations=visualizations)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)