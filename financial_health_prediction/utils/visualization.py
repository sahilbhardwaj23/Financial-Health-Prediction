import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_gauge_chart(score):
    """
    Create a gauge chart for financial health score
    """
    return go.Indicator(
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
    )

def create_ratio_charts(ratios):
    """
    Create charts for financial ratios
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Savings Rate", "Debt-to-Income", 
                       "Expense Ratio", "Credit Utilization")
    )
    
    # Savings Rate gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=ratios['savings_rate'],
            gauge={'axis': {'range': [0, 50]}},
            title={'text': "Savings Rate (%)"}
        ),
        row=1, col=1
    )
    
    # DTI gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=ratios['dti_ratio'],
            gauge={'axis': {'range': [0, 100]}},
            title={'text': "DTI Ratio (%)"}
        ),
        row=1, col=2
    )
    
    # Expense Ratio gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=ratios['expense_ratio'],
            gauge={'axis': {'range': [0, 100]}},
            title={'text': "Expense Ratio (%)"}
        ),
        row=2, col=1
    )
    
    # Credit Utilization gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=ratios['credit_utilization'],
            gauge={'axis': {'range': [0, 100]}},
            title={'text': "Credit Utilization (%)"}
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    return fig

def create_trend_charts(historical_data):
    """
    Create trend charts from historical data
    """
    if historical_data is None or len(historical_data) == 0:
        return None
        
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Monthly Expenses Trend", "Savings Rate Trend")
    )
    
    # Monthly Expenses trend
    fig.add_trace(
        go.Scatter(
            x=historical_data.index,
            y=historical_data['Monthly Expenses'],
            mode='lines+markers',
            name='Monthly Expenses'
        ),
        row=1, col=1
    )
    
    # Savings Rate trend
    fig.add_trace(
        go.Scatter(
            x=historical_data.index,
            y=historical_data['Savings Rate'],
            mode='lines+markers',
            name='Savings Rate'
        ),
        row=2, col=1
    )
    
    fig.update_layout(height=600, showlegend=True)
    return fig

def create_visualizations(input_data, prediction, ratios):
    """
    Create all visualizations for the dashboard
    """
    return {
        'gauge_chart': create_gauge_chart(prediction),
        'ratio_charts': create_ratio_charts(ratios),
        'recommendations': get_recommendations(ratios, prediction, input_data)[0],
        'total_impact': get_recommendations(ratios, prediction, input_data)[1]
    }