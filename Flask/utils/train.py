import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import os

# Get the absolute path of the project directory (one level up from utils)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_and_preprocess_data(file_path):
    """
    Load and preprocess the training data from models directory
    """
    # Construct absolute path to the data file in models directory
    data_path = os.path.join(PROJECT_DIR, 'model', file_path)
    
    # Check if file exists
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}. Please ensure 'training.csv' exists in the models directory.")
    
    # Load the data
    df = pd.read_csv(data_path)
    
    # Extract total members from Member ID
    df['Total Members'] = df['Member ID'].str.extract(r'Member(\d+)', expand=False).astype(int)
    
    # Select required features
    selected_columns = [
        'Category', 'Amount', 'Income', 'Savings', 'Monthly Expenses',
        'Loan Payments', 'Credit Card Spending', 'Dependents',
        'Financial Goals Met (%)', 'Day of Week', 'Total Members',
        'Financial Health Score'
    ]
    
    df = df[selected_columns]
    
    return df

def encode_categorical_features(X_train, X_test):
    """
    Encode categorical features using LabelEncoder
    """
    # Initialize encoders
    category_encoder = LabelEncoder()
    day_encoder = LabelEncoder()
    
    # Fit and transform training data
    X_train['Category'] = category_encoder.fit_transform(X_train['Category'])
    X_train['Day of Week'] = day_encoder.fit_transform(X_train['Day of Week'])
    
    # Transform test data
    X_test['Category'] = category_encoder.transform(X_test['Category'])
    X_test['Day of Week'] = day_encoder.transform(X_test['Day of Week'])
    
    # Save the encoders
    encoders_path = os.path.join(PROJECT_DIR, 'model', 'encoders.pkl')
    with open(encoders_path, 'wb') as f:
        pickle.dump({'category': category_encoder, 'day': day_encoder}, f)
    print(f"Encoders saved to {encoders_path}")
    
    return X_train, X_test

def train_model(X_train, y_train, X_test, y_test):
    """
    Train and evaluate the Decision Tree model
    """
    # Initialize and train the model
    model = DecisionTreeRegressor(random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return model, mse, r2

def save_model(model, file_name):
    """
    Save the trained model to the models directory
    """
    # Save model
    model_path = os.path.join(PROJECT_DIR, 'model', file_name)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

def main():
    # Configuration
    DATA_FILE = 'training.csv'
    MODEL_FILE = 'dt_model.pkl'
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    
    print("Loading and preprocessing data...")
    try:
        df = load_and_preprocess_data(DATA_FILE)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease ensure your project structure is as follows:")
        print(f"{PROJECT_DIR}/")
        print("├── models/")
        print("│   ├── training.csv")
        print("│   ├── dt_model.pkl (will be created)")
        print("│   └── encoders.pkl (will be created)")
        print("└── utils/")
        print("    └── train.py")
        return
    
    # Split features and target
    X = df.drop(columns=['Financial Health Score'])
    y = df['Financial Health Score']
    
    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    
    print("Encoding categorical features...")
    X_train, X_test = encode_categorical_features(X_train, X_test)
    
    print("Training model...")
    model, mse, r2 = train_model(X_train, y_train, X_test, y_test)
    
    print("\nModel Performance:")
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"R² Score: {r2:.4f}")
    
    print(f"\nSaving model...")
    save_model(model, MODEL_FILE)
    
    print("Training completed successfully!")

if __name__ == "__main__":
    main()