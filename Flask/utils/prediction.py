import numpy as np
import pandas as pd

def predict_financial_health(model, input_data):
    """Make prediction using the loaded model"""
    try:
        # Ensure input data has the correct columns
        required_columns = [
            'Category', 'Amount', 'Income', 'Savings', 'Monthly Expenses',
            'Loan Payments', 'Credit Card Spending', 'Dependents',
            'Financial Goals Met (%)', 'Day of Week', 'Total Members'
        ]
        
        for col in required_columns:
            if col not in input_data.columns:
                raise ValueError(f"Missing required column: {col}")
        
        prediction = model.predict(input_data)[0]
        return float(prediction)
    except Exception as e:
        raise ValueError(f"Error making prediction: {str(e)}")

def calculate_financial_ratios(input_data):
    """Calculate key financial ratios from input data"""
    try:
        income = float(input_data['Income'].values[0])
        
        if income <= 0:
            raise ValueError("Income must be greater than 0")
        
        ratios = {
            'savings_rate': (float(input_data['Savings'].values[0]) / income * 100),
            'dti_ratio': ((float(input_data['Loan Payments'].values[0]) + 
                          float(input_data['Credit Card Spending'].values[0])) / income * 100),
            'expense_ratio': (float(input_data['Monthly Expenses'].values[0]) / income * 100),
            'credit_utilization': (float(input_data['Credit Card Spending'].values[0]) / income * 100),
            'debt_payments': (float(input_data['Loan Payments'].values[0]) + 
                            float(input_data['Credit Card Spending'].values[0])),
            'discretionary_income': (income - float(input_data['Monthly Expenses'].values[0]) - 
                                   float(input_data['Loan Payments'].values[0]))
        }
        
        # Round all ratios to 2 decimal places
        ratios = {k: round(v, 2) for k, v in ratios.items()}
        
        return ratios
    except Exception as e:
        raise ValueError(f"Error calculating financial ratios: {str(e)}")