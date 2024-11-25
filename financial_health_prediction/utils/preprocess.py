import pandas as pd
import numpy as np

def process_user_input(form_data, category_mapping, day_mapping):
    """
    Process form data into a format suitable for model prediction
    """
    try:
        input_dict = {
            'Category': [category_mapping[form_data.get('category')]],
            'Amount': [float(form_data.get('amount'))],
            'Income': [float(form_data.get('income'))],
            'Savings': [float(form_data.get('savings'))],
            'Monthly Expenses': [float(form_data.get('monthly_expenses'))],
            'Loan Payments': [float(form_data.get('loan_payments'))],
            'Credit Card Spending': [float(form_data.get('credit_card_spending'))],
            'Dependents': [int(form_data.get('dependents'))],
            'Financial Goals Met (%)': [float(form_data.get('financial_goals_met'))],
            'Day of Week': [day_mapping[form_data.get('day_of_week')]],
            'Total Members': [int(form_data.get('total_members'))]
        }
        
        return pd.DataFrame(input_dict)
    
    except Exception as e:
        raise ValueError(f"Error processing input data: {str(e)}")

def validate_input_data(data):
    """
    Validate input data for basic sanity checks
    """
    validations = {
        'positive_values': all(data[col].iloc[0] >= 0 for col in [
            'Amount', 'Income', 'Savings', 'Monthly Expenses',
            'Loan Payments', 'Credit Card Spending'
        ]),
        'expenses_within_income': (data['Monthly Expenses'].iloc[0] +
                                 data['Loan Payments'].iloc[0]) <= data['Income'].iloc[0],
        'valid_dependents': 0 <= data['Dependents'].iloc[0] <= data['Total Members'].iloc[0],
        'valid_goals': 0 <= data['Financial Goals Met (%)'].iloc[0] <= 100
    }
    
    validation_messages = {
        'positive_values': 'All monetary values must be positive',
        'expenses_within_income': 'Total expenses cannot exceed income',
        'valid_dependents': 'Number of dependents cannot exceed total members',
        'valid_goals': 'Financial goals must be between 0 and 100%'
    }
    
    failed_validations = [msg for check, msg in validation_messages.items()
                         if not validations[check]]
    
    if failed_validations:
        raise ValueError(' | '.join(failed_validations))
    
    return True

def normalize_features(data, feature_ranges=None):
    """
    Normalize numerical features to a standard range
    """
    if feature_ranges is None:
        feature_ranges = {
            'Amount': (0, 10000),
            'Income': (0, 20000),
            'Savings': (0, 5000),
            'Monthly Expenses': (0, 10000),
            'Loan Payments': (0, 5000),
            'Credit Card Spending': (0, 5000)
        }
    
    normalized_data = data.copy()
    
    for feature, (min_val, max_val) in feature_ranges.items():
        if feature in normalized_data.columns:
            normalized_data[feature] = (normalized_data[feature] - min_val) / (max_val - min_val)
    
    return normalized_data