from pydantic import BaseModel
from typing import List, Optional

class Transaction(BaseModel):
    date: str
    amount: float
    type: str # 'credit' or 'debit'
    merchant: str
    category: Optional[str] = 'Other'

class InsightRequest(BaseModel):
    query: str
    
class InsightResponse(BaseModel):
    insight: str
    reason: str
    recommendation: str

class FinancialSummary(BaseModel):
    income: float
    expenses: float
    savings: float
