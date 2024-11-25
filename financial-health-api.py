from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime
import numpy as np

app = FastAPI(title="Financial Health Score API")

class Transaction(BaseModel):
    Transaction_Date: str
    Category: str
    Amount: float

class FamilyData(BaseModel):
    Family_ID: str
    Income: float
    Savings: float
    Monthly_Expenses: float
    Loan_Payments: float
    Credit_Card_Spending: float
    Dependents: int
    Transactions: List[Transaction]

class FinancialInsight(BaseModel):
    category: str
    impact: float
    message: str

class FinancialHealthResponse(BaseModel):
    score: float
    insights: List[FinancialInsight]
    recommendations: List[str]

def calculate_savings_ratio(income: float, savings: float) -> float:
    """Calculate savings as a percentage of income"""
    return (savings / income) * 100 if income > 0 else 0

def calculate_debt_to_income(income: float, loan_payments: float, credit_card_spending: float) -> float:
    """Calculate debt-to-income ratio"""
    total_debt = loan_payments + credit_card_spending
    return (total_debt / income) * 100 if income > 0 else 0

def analyze_spending_patterns(transactions: List[Transaction]) -> dict:
    """Analyze transaction patterns by category"""
    df = pd.DataFrame([t.dict() for t in transactions])
    if not df.empty:
        df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
        category_totals = df.groupby('Category')['Amount'].sum()
        return category_totals.to_dict()
    return {}

def calculate_financial_score(data: FamilyData) -> tuple[float, List[FinancialInsight], List[str]]:
    score = 100.0
    insights = []
    recommendations = []
    
    # 1. Savings Analysis (30 points)
    savings_ratio = calculate_savings_ratio(data.Income, data.Savings)
    savings_impact = 0
    if savings_ratio < 20:
        savings_impact = -((20 - savings_ratio) * 1.5)
        insights.append(FinancialInsight(
            category="Savings",
            impact=savings_impact,
            message=f"Savings ratio of {savings_ratio:.1f}% is below the recommended 20%"
        ))
        recommendations.append("Aim to save at least 20% of your monthly income")
    
    # 2. Debt Analysis (25 points)
    debt_ratio = calculate_debt_to_income(data.Income, data.Loan_Payments, data.Credit_Card_Spending)
    debt_impact = 0
    if debt_ratio > 40:
        debt_impact = -((debt_ratio - 40) * 0.625)
        insights.append(FinancialInsight(
            category="Debt",
            impact=debt_impact,
            message=f"Debt-to-income ratio of {debt_ratio:.1f}% exceeds recommended 40%"
        ))
        recommendations.append("Consider debt consolidation or debt reduction strategies")
    
    # 3. Expense Analysis (25 points)
    expense_ratio = (data.Monthly_Expenses / data.Income) * 100 if data.Income > 0 else 0
    expense_impact = 0
    if expense_ratio > 50:
        expense_impact = -((expense_ratio - 50) * 0.5)
        insights.append(FinancialInsight(
            category="Expenses",
            impact=expense_impact,
            message=f"Monthly expenses are {expense_ratio:.1f}% of income, exceeding recommended 50%"
        ))
        recommendations.append("Review and optimize monthly expenses")
    
    # 4. Dependent Factor (20 points)
    dependent_impact = 0
    if data.Dependents > 0:
        dependent_factor = (data.Income / (data.Dependents + 1)) / 12
        if dependent_factor < 1000:
            dependent_impact = -(20 * (1 - (dependent_factor / 1000)))
            insights.append(FinancialInsight(
                category="Dependents",
                impact=dependent_impact,
                message=f"Per-person monthly income of ${dependent_factor:.2f} is below recommended $1,000"
            ))
            recommendations.append("Consider additional income sources or financial assistance programs")
    
    # Calculate final score
    final_score = max(0, min(100, score + savings_impact + debt_impact + expense_impact + dependent_impact))
    
    return final_score, insights, recommendations

@app.post("/calculate-financial-health", response_model=FinancialHealthResponse)
async def calculate_financial_health(data: FamilyData):
    try:
        score, insights, recommendations = calculate_financial_score(data)
        
        return FinancialHealthResponse(
            score=score,
            insights=insights,
            recommendations=recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
