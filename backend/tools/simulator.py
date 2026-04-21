from typing import Dict, List

def simulate_purchase(purchase_amount: float, current_savings: float, upcoming_expenses: float = 0.0) -> Dict:
    """
    Simulates financial scenarios like affordability of a purchase.
    """
    effective_savings = current_savings - upcoming_expenses
    affordable = effective_savings >= purchase_amount
    
    if affordable:
        remaining = effective_savings - purchase_amount
        msg = f"Purchase is affordable! After this purchase (₹{purchase_amount}) and upcoming expenses (₹{upcoming_expenses}), your remaining savings will be ₹{round(remaining, 2)}. "
        
        if remaining < 0.1 * current_savings:
            msg += "Warning: This leaves you with very little safety net."
        else:
            msg += "This seems like a safe purchase financially."
    else:
        shortfall = purchase_amount - effective_savings
        msg = f"Purchase not recommended. You have a shortfall of ₹{round(shortfall, 2)} after accounting for upcoming expenses. Consider saving up more or finding a cheaper alternative."
        
    return {
        "affordable": affordable,
        "message": msg,
        "effective_savings": round(effective_savings, 2),
        "post_purchase_savings": round(effective_savings - purchase_amount, 2) if affordable else round(effective_savings, 2)
    }
