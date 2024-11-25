import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="💰",
    layout="wide"
)

# Load dataset locally
@st.cache_data
def load_data():
    try:
        return pd.read_excel("family_financial_and_transactions_data.xlsx")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Load prediction model
def load_model():
    try:
        with open('dt_model.pkl', 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
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

def create_gauge_chart(score):
    """Create a gauge chart for financial health score"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
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
                'value': score
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

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

    # Expense Management
    if ratios['expense_ratio'] > 50:
        impact = min(3, (ratios['expense_ratio'] - 50) / 10)
        expense_reduction_target = ratios['expense_ratio'] - 50
        recommendations.append({
            'category': '📊 Expense Management',
            'priority': 'Medium',
            'recommendations': [
                f"Reduce monthly expenses by {expense_reduction_target:.1f}%",
                "Create a detailed budget",
                "Track all expenses",
                "Find areas for cost-cutting"
            ],
            'impact': impact,
            'current': f"{ratios['expense_ratio']:.1f}%",
            'target': "50%",
            'tips': [
                "Use budgeting apps",
                "Meal plan to reduce food costs",
                "Review and negotiate bills"
            ]
        })
        total_impact += impact

    # Credit Card Usage
    if ratios['credit_utilization'] > 30:
        impact = min(3, (ratios['credit_utilization'] - 30) / 10)
        credit_reduction_target = input_data['Credit Card Spending'].values[0] * 0.2
        recommendations.append({
            'category': '💳 Credit Card Usage',
            'priority': 'Medium',
            'recommendations': [
                f"Reduce credit card spending by ${credit_reduction_target:.2f}",
                "Pay more than minimum payment",
                "Keep utilization below 30%",
                "Consider a balance transfer"
            ],
            'impact': impact,
            'current': f"{ratios['credit_utilization']:.1f}%",
            'target': "30%",
            'tips': [
                "Use cash for discretionary spending",
                "Create a debt payoff plan",
                "Set up payment alerts"
            ]
        })
        total_impact += impact

    return recommendations, total_impact

# Sidebar navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio("Go to", ["Home", "Prediction", "Visualization"])

# Home Tab
if options == "Home":
    st.title("Welcome to the Financial Dashboard 💰")
    st.markdown("""
        ### About this Project  
        This project is developed as part of the **Data Science Internship Assignment** for **Sustain Farmers**. The primary objective is to create a comprehensive and interactive dashboard that helps families analyze their financial health and spending patterns.  

        ### Key Features  
        - **Predict Financial Health Score**: Enter key financial metrics and predict a personalized financial health score.  
        - **Interactive Visualizations**: Explore detailed insights into financial transactions with customizable visualizations.  
        - **Data-driven Insights**: Gain a better understanding of income, savings, and expenses to make informed financial decisions.  

        ### Tools & Techniques  
        This dashboard is built using:  
        - **Python** for data manipulation and model integration.  
        - **Streamlit** for creating a dynamic and interactive web interface.  
        - **Machine Learning Models** for predicting financial health scores.  

        ### About Sustain Farmers  
        Sustain Farmers is dedicated to promoting sustainable farming practices and empowering communities through innovative data-driven solutions. This project demonstrates the application of data science to improve financial planning and decision-making, which is a crucial aspect of sustainable development.  

        ### Instructions  
        Use the sidebar to navigate through the dashboard:  
        - **Prediction**: Predict your financial health score.  
        - **Visualization**: Explore insights through dynamic charts and graphs.  

        Thank you for reviewing this project!
    """)

# Prediction Tab
elif options == "Prediction":
    st.title("Financial Health Score Predictor & Advisor 💰")
    st.write("Enter your financial information below to get your score and personalized recommendations.")
    
    # User input
    col1, col2 = st.columns(2)
    CATEGORY_MAPPING = {'Education': 0, 'Entertainment': 1, 'Food': 2, 'Groceries': 3, 'Healthcare': 4, 'Travel': 5, 'Utilities': 6}
    DAY_MAPPING = {'Friday': 0, 'Monday': 1, 'Saturday': 2, 'Sunday': 3, 'Thursday': 4, 'Tuesday': 5, 'Wednesday': 6}

    with col1:
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        income = st.number_input("Monthly Income", min_value=0.0, format="%.2f")
        savings = st.number_input("Monthly Savings", min_value=0.0, format="%.2f")
        monthly_expenses = st.number_input("Monthly Expenses", min_value=0.0, format="%.2f")
        loan_payments = st.number_input("Monthly Loan Payments", min_value=0.0, format="%.2f")
    with col2:
        credit_card_spending = st.number_input("Monthly Credit Card Spending", min_value=0.0, format="%.2f")
        dependents = st.number_input("Number of Dependents", min_value=0, max_value=10, step=1)
        financial_goals_met = st.slider("Financial Goals Met (%)", 0, 100, 50)
        total_members = st.number_input("Total Household Members", min_value=1, step=1)
        category = st.selectbox("Primary Expense Category", list(CATEGORY_MAPPING.keys()))
        day_of_week = st.selectbox("Day of Week", list(DAY_MAPPING.keys()))
    
    # Predict button
    if st.button("Analyze Financial Health"):
        model = load_model()
        if model:
            input_data = pd.DataFrame({
                'Category': [CATEGORY_MAPPING[category]],
                'Amount': [amount],
                'Income': [income],
                'Savings': [savings],
                'Monthly Expenses': [monthly_expenses],
                'Loan Payments': [loan_payments],
                'Credit Card Spending': [credit_card_spending],
                'Dependents': [dependents],
                'Financial Goals Met (%)': [financial_goals_met],
                'Day of Week': [DAY_MAPPING[day_of_week]],
                'Total Members': [total_members]
            })
            
            # Get prediction
            prediction = model.predict(input_data)[0]
            
            # Calculate financial ratios
            ratios = calculate_financial_ratios(input_data)
            
            # Get recommendations
            recommendations, total_impact = get_detailed_recommendations(ratios, prediction, input_data)
            
            # Display Results
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.plotly_chart(create_gauge_chart(prediction))
            
            with col2:
                st.metric(
                    "Potential Score Improvement",
                    f"+{total_impact:.1f} points",
                    "by following all recommendations"
                )
            
            # Display Financial Health Summary
            st.subheader("💹 Financial Health Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Savings Rate",
                    f"{ratios['savings_rate']:.1f}%",
                    f"{ratios['savings_rate'] - 20:.1f}%" if ratios['savings_rate'] > 20 else f"{20 - ratios['savings_rate']:.1f}% below target",
                    delta_color="normal" if ratios['savings_rate'] > 20 else "inverse"
                )
            
            with col2:
                st.metric(
                    "Debt-to-Income",
                    f"{ratios['dti_ratio']:.1f}%",
                    f"{36 - ratios['dti_ratio']:.1f}%" if ratios['dti_ratio'] < 36 else f"{ratios['dti_ratio'] - 36:.1f}% above target",
                    delta_color="normal" if ratios['dti_ratio'] < 36 else "inverse"
                )
            
            with col3:
                st.metric(
                    "Expense Ratio",
                    f"{ratios['expense_ratio']:.1f}%",
                    f"{50 - ratios['expense_ratio']:.1f}%" if ratios['expense_ratio'] < 50 else f"{ratios['expense_ratio'] - 50:.1f}% above target",
                    delta_color="normal" if ratios['expense_ratio'] < 50 else "inverse"
                )
            
            with col4:
                st.metric(
                    "Discretionary Income",
                    f"${ratios['discretionary_income']:.2f}",
                    "monthly"
                )
            
            # Display Recommendations
            st.subheader("🎯 Personalized Recommendations")
            
            for rec in recommendations:
                with st.expander(f"{rec['category']} (Impact: +{rec['impact']:.1f} points) - {rec['priority']} Priority"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("#### Key Actions:")
                        for r in rec['recommendations']:
                            st.markdown(f"• {r}")
                            
                        st.markdown("#### Helpful Tips:")
                        for tip in rec['tips']:
                            st.markdown(f"• {tip}")
                    
                    with col2:
                        st.markdown("#### Current vs Target:")
                        st.markdown(f"**Current:** {rec['current']}")
                        st.markdown(f"**Target:** {rec['target']}")
                        
                        # Progress bar
                        current_val = float(rec['current'].strip('%'))
                        target_val = float(rec['target'].strip('%'))
                        progress = min(1.0, current_val / target_val if target_val > current_val else target_val / current_val)
                        st.progress(progress)

# Visualization Tab
elif options == "Visualization":
    st.title("Visualize Your Financial Data 📊")
    df = load_data()
    
    if df is not None:
        # Sidebar options for visualization
        st.sidebar.subheader("Visualization Options")
        vis_type = st.sidebar.selectbox(
            "Select a Visualization",
            ["Category Distribution", "Family Member Distribution", "Transaction Trends", "Expenses by Day", "Category-wise Analysis"]
        )
        
        if vis_type == "Category Distribution":
            st.subheader("Category Distribution")
            category_counts = df['Category'].value_counts()
            plt.figure(figsize=(8, 8))
            category_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, cmap='Blues')
            plt.title('Distribution of Categories')
            plt.ylabel('')  # Aesthetic improvement
            st.pyplot(plt)
        
        elif vis_type == "Family Member Distribution":
            st.subheader("Family Member Distribution")
            member_counts = df['Member ID'].str.extract(r'Member(\d+)', expand=False).astype(int).value_counts()
            plt.figure(figsize=(12, 6))
            sns.barplot(x=member_counts.index, y=member_counts.values, palette="viridis")
            plt.title("Family Member Distribution")
            plt.xlabel("Member Number")
            plt.ylabel("Frequency")
            st.pyplot(plt)
        
        elif vis_type == "Transaction Trends":
            st.subheader("Transaction Trends")
            df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
            date_amount = df.groupby('Transaction Date')['Monthly Expenses'].mean().reset_index()
            plt.figure(figsize=(14, 7))
            plt.plot(date_amount['Transaction Date'], date_amount['Monthly Expenses'], marker='o', color='blue')
            plt.title("Transaction Date vs Monthly Expenses")
            plt.xlabel("Transaction Date")
            plt.ylabel("Monthly Expenses")
            st.pyplot(plt)
        
        elif vis_type == "Expenses by Day":
            st.subheader("Expenses by Day")
            df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
            df['Day of Week'] = df['Transaction Date'].dt.day_name()
            day_expenses = df.groupby('Day of Week')['Monthly Expenses'].mean()
            plt.figure(figsize=(8, 8))
            plt.pie(
                day_expenses,
                labels=day_expenses.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=sns.color_palette("pastel")
            )
            plt.title("Average Monthly Expenses by Day of the Week")
            st.pyplot(plt)
        
        elif vis_type == "Category-wise Analysis":
            st.subheader("Category-wise Analysis")
            category_analysis = df.groupby('Category')['Monthly Expenses'].mean()
            plt.figure(figsize=(10, 8))
            plt.pie(
                category_analysis,
                labels=category_analysis.index,
                autopct='%1.1f%%',
                startangle=140,
                colors=sns.color_palette("tab10")
            )
            plt.title("Average Monthly Expenses by Category")
            st.pyplot(plt)
