import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json

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
    return json.loads(fig.to_json())

def create_ratio_charts(ratios):
    """Create charts for financial ratios"""
    # Create individual figures for each ratio
    figures = {
        'savings_gauge': go.Figure(go.Indicator(
            mode="gauge+number",
            value=ratios['savings_rate'],
            title={'text': "Savings Rate (%)"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 50]},
                'steps': [
                    {'range': [0, 20], 'color': "red"},
                    {'range': [20, 35], 'color': "yellow"},
                    {'range': [35, 50], 'color': "green"}
                ]
            }
        )),
        'dti_gauge': go.Figure(go.Indicator(
            mode="gauge+number",
            value=ratios['dti_ratio'],
            title={'text': "DTI Ratio (%)"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 36], 'color': "green"},
                    {'range': [36, 43], 'color': "yellow"},
                    {'range': [43, 100], 'color': "red"}
                ]
            }
        )),
        'expense_gauge': go.Figure(go.Indicator(
            mode="gauge+number",
            value=ratios['expense_ratio'],
            title={'text': "Expense Ratio (%)"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 50], 'color': "green"},
                    {'range': [50, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ]
            }
        )),
        'credit_gauge': go.Figure(go.Indicator(
            mode="gauge+number",
            value=ratios['credit_utilization'],
            title={'text': "Credit Utilization (%)"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 30], 'color': "green"},
                    {'range': [30, 50], 'color': "yellow"},
                    {'range': [50, 100], 'color': "red"}
                ]
            }
        ))
    }
    
    # Update layouts
    for fig in figures.values():
        fig.update_layout(height=250)
    
    # Convert to JSON
    return {key: json.loads(fig.to_json()) for key, fig in figures.items()}

def create_visualizations(input_data=None, prediction=None, ratios=None):
    """Create all visualizations for the dashboard"""
    try:
        visualizations = {}
        
        # Add gauge chart if prediction is provided
        if prediction is not None:
            visualizations['gauge_chart'] = create_gauge_chart(prediction)
        
        # Add ratio charts if ratios are provided
        if ratios is not None:
            visualizations['ratio_charts'] = create_ratio_charts(ratios)
        
        # Add recommendations if all required data is provided
        if ratios is not None and prediction is not None and input_data is not None:
            recommendations, total_impact = get_recommendations(ratios, prediction, input_data)
            visualizations['recommendations'] = recommendations
            visualizations['total_impact'] = total_impact
        
        return visualizations
        
    except Exception as e:
        raise ValueError(f"Error creating visualizations: {str(e)}")

def get_recommendations(ratios, score, input_data):
    """Generate recommendations based on financial metrics"""
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
    
    # Debt Management
    if ratios['dti_ratio'] > 36:
        impact = min(4, (ratios['dti_ratio'] - 36) / 10)
        recommendations.append({
            'category': '💳 Debt Management',
            'priority': 'High' if ratios['dti_ratio'] > 50 else 'Medium',
            'recommendations': [
                "Consider debt consolidation",
                "Prioritize high-interest debt",
                "Create a debt repayment plan"
            ],
            'impact': impact,
            'current': f"{ratios['dti_ratio']:.1f}%",
            'target': "36%"
        })
        total_impact += impact
    
    return recommendations, total_impact