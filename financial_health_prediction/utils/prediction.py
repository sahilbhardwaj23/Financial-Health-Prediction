import numpy as np
import pandas as pd

def predict_financial_health(model, input_data):
    """
    Make prediction using the loaded model
    """
    try:
        prediction = model.predict(input_data)[0]
        return float(prediction)
    except Exception as e:
        raise ValueError(f"Error making prediction: {str(e)}")

def calculate_financial_ratios(input_data):
    """
    Calculate key financial ratios from input data
    """
    income = input_data['Income'].values[0]
    
    try:
        ratios = {
            'savings_rate': (input_data['Savings'].values[0] / income * 100) if income > 0 else 0,
            'dti_ratio': ((input_data['Loan Payments'].values[0] + 
                          input_data['Credit Card Spending'].values[0]) / income * 100) if income > 0 else 0,
            'expense_ratio': (input_data['Monthly Expenses'].values[0] / income * 100) if income > 0 else 0,
            'credit_utilization': (input_data['Credit Card Spending'].values[0] / income * 100) if income > 0 else 0,
            'debt_payments': (input_data['Loan Payments'].values[0] + 
                            input_data['Credit Card Spending'].values[0]),
            'discretionary_income': (income - input_data['Monthly Expenses'].values[0] - 
                                   input_data['Loan Payments'].values[0])
        }
        
        return ratios
    except Exception as e:
        raise ValueError(f"Error calculating financial ratios: {str(e)}")

def get_recommendations(ratios, score, input_data):
    """
    Generate detailed financial recommendations based on ratios and score
    """
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
                "Look for additional income opportunities"
            ],
            'impact': impact,
            'current': f"{ratios['savings_rate']:.1f}%",
            'target': "20%"
        })
        total_impact += impact
    
    # Add more recommendation categories here...
    
    return recommendations, total_impact

def calculate_score_components(input_data, ratios):
    """
    Calculate individual components that make up the financial health score
    """
    components = {
        'savings': min(100, ratios['savings_rate'] * 5),
        'debt_management': max(0, 100 - ratios['dti_ratio'] * 2),
        'expense_management': max(0, 100 - ratios['expense_ratio']),
        'goals': input_data['Financial Goals Met (%)'].values[0]
    }
    
    weights = {
        'savings': 0.3,
        'debt_management': 0.3,
        'expense_management': 0.25,
        'goals': 0.15
    }
    
    weighted_score = sum(components[k] * weights[k] for k in components)
    
    return components, weighted_score