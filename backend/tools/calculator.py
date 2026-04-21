from typing import List, Dict

def calculate_summary(transactions: List[Dict]) -> Dict:
    """
    Computes financial summaries, savings, and category breakdowns.
    """
    income = 0.0
    expenses = 0.0
    category_breakdown = {}
    
    for t in transactions:
        amount = t.get("amount", 0.0)
        
        if t.get("type", "debit").lower() == "credit":
            income += amount
        else:
            expenses += amount
            
            # Group by category, assuming 'category' field is present by the time this is called
            cat = t.get("category", "Other")
            if cat not in category_breakdown:
                category_breakdown[cat] = 0.0
            category_breakdown[cat] += amount
            
    savings = income - expenses
    
    # Savings recommendations based on 50/30/20 rule if income > 0
    suggestions = []
    if income > 0:
        needs_target = income * 0.50
        wants_target = income * 0.30
        savings_target = income * 0.20
        
        if savings < savings_target:
            suggestions.append(f"Ideally you should save ₹{round(savings_target, 2)} (20% of income). You are currently saving ₹{round(savings, 2)}.")
            
        # Analyze highest expense category
        if category_breakdown:
            top_category = max(category_breakdown, key=category_breakdown.get)
            top_amount = category_breakdown[top_category]
            suggestions.append(f"Your highest expense is in {top_category} (₹{round(top_amount, 2)}). Look for areas to reduce spending here.")

    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "savings": round(savings, 2),
        "category_breakdown": {k: round(v, 2) for k, v in category_breakdown.items()},
        "suggestions": suggestions
    }
