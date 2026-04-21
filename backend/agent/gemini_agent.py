import os
from google import genai
from pydantic import BaseModel
import json

class AgentResponse(BaseModel):
    insight: str
    reason: str
    recommendation: str

def get_gemini_client():
    # Using the API key you provided
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyAg9QkQAxIsQbQm0nwLCobUcWXvU2bmMSs")
    if not api_key or api_key == "dummy_key":
        print("Warning: GEMINI_API_KEY environment variable is not set. Responses will be dummies.")
        return None
    return genai.Client(api_key=api_key)

def process_query_with_agent(query: str, context_data: dict) -> AgentResponse:
    """
    Uses Gemini API to process natural language queries over uploaded financial data.
    """
    client = get_gemini_client()
    
    if not client:
        return AgentResponse(
            insight=f"Analyzed query: {query}",
            reason="Based on the context data provided.",
            recommendation="Consider reviewing your recent spending in the highest category. (Note: Set GEMINI_API_KEY to see real AI responses)"
        )

    system_prompt = """
    You are a Personal Finance AI Assistant. Analyze the user's financial data and their query.
    Your response MUST be a valid JSON object matching this schema EXACTLY:
    {
      "insight": "What is happening - a clear observation based on data",
      "reason": "Why it is happening - explanation of the observation",
      "recommendation": "What to do next - actionable, practical advice"
    }
    
    Rules:
    - Base responses ONLY on available data.
    - Tailor insights; avoid generic financial advice.
    - Be clear, concise, professional, but friendly.
    - Do NOT fabricate financial values.
    """
    
    user_prompt = f"User Query: {query}\n\nFinancial Context: {json.dumps(context_data, indent=2)}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[system_prompt, user_prompt],
        )
        
        # Parse the JSON from the markdown block or direct text
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return AgentResponse(
                insight=data.get("insight", "Could not extract insight."),
                reason=data.get("reason", "Could not extract reason."),
                recommendation=data.get("recommendation", "Could not extract recommendation.")
            )
            
        return AgentResponse(
            insight="AI provided a non-JSON response.",
            reason=response.text[:200] + "...",
            recommendation="Please try asking again."
        )
        
    except Exception as e:
        return AgentResponse(
            insight="Error connecting to AI Assistant.",
            reason=str(e),
            recommendation="Please verify your API key and network connection."
        )

def _precalculate_totals(transactions: list) -> dict:
    """
    Calculate savings using the most accurate method:
      Savings = Closing Balance - Opening Balance

    Every bank statement has a running balance column.
    First transaction line's last number = opening balance after first tx.
    Last transaction line's last number = closing balance.
    Falls back to DR/CR sum method if balance extraction fails.
    """
    import re
    # Match amounts with decimals (e.g. 1,23,456.78 or 562.00)
    amount_pattern = re.compile(r'[\d,]+\.\d{2}')

    # ── Method 1: Opening / Closing Balance ────────────────────────────────────
    # The last decimal number on each line is the running balance.
    # Savings = last line's balance - first line's balance.
    balances = []
    for t in transactions:
        raw = t.get("raw_line", "")
        amounts = amount_pattern.findall(raw)
        if amounts and len(amounts) >= 2:
            # Last number = running balance (always present in bank statements)
            try:
                bal = float(amounts[-1].replace(",", ""))
                if bal > 0:
                    balances.append(bal)
            except ValueError:
                continue

    if len(balances) >= 2:
        opening_balance = balances[0]
        closing_balance = balances[-1]
        net_savings = round(closing_balance - opening_balance, 2)
        print(f"Balance method → Opening: {opening_balance}, Closing: {closing_balance}, Net: {net_savings}")

        # Also estimate income/expenses via DR/CR for categorization widths
        total_expenses = 0.0
        total_income = 0.0
        for t in transactions:
            raw = t.get("raw_line", "")
            line = raw.upper()
            amounts_list = [float(a.replace(",","")) for a in amount_pattern.findall(raw)]
            if len(amounts_list) < 2:
                continue
            amount = amounts_list[-2]  # second-to-last = transaction amount
            if amount <= 0:
                continue
            if any(k in line for k in ["UPI-DR", "NEFT-DR", "IMPS-DR", "RTGS-DR", " DR", "WITHDRAWAL", "DEBIT"]):
                total_expenses += amount
            elif any(k in line for k in ["UPI-CR", "NEFT-CR", "IMPS-CR", "RTGS-CR", " CR", "DEPOSIT", "CREDIT", "SALARY"]):
                total_income += amount

        return {
            "total_income":   round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "total_savings":  net_savings   # ← accurate balance-based savings
        }

    # ── Method 2: Fallback — sum DR/CR (less accurate) ─────────────────────────
    print("⚠️  Could not find balance column, falling back to DR/CR sum method.")
    total_income = 0.0
    total_expenses = 0.0
    for t in transactions:
        raw = t.get("raw_line", "")
        line = raw.upper()
        debit  = float(t.get("debit", 0) or 0)
        credit = float(t.get("credit", 0) or 0)
        if debit > 0 or credit > 0:
            total_expenses += debit
            total_income += credit
            continue
        amounts_list = [float(a.replace(",","")) for a in amount_pattern.findall(raw)]
        if not amounts_list:
            continue
        amount = amounts_list[-2] if len(amounts_list) >= 2 else amounts_list[-1]
        if amount <= 0:
            continue
        if any(k in line for k in ["UPI-DR", "NEFT-DR", " DR", "WITHDRAWAL", "DEBIT"]):
            total_expenses += amount
        elif any(k in line for k in ["UPI-CR", "NEFT-CR", " CR", "DEPOSIT", "CREDIT", "SALARY"]):
            total_income += amount

    return {
        "total_income":   round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "total_savings":  round(total_income - total_expenses, 2)
    }


def get_dashboard_summary(context_data: dict) -> dict:
    client = get_gemini_client()
    if not client:
        return {"error": "No API key"}

    transactions = context_data.get("recent_transactions", [])

    # ── Step 1: Python calculates savings (reliable) ──────────────────────────
    totals = _precalculate_totals(transactions)
    print(f"Pre-calculated → Income: {totals['total_income']}, "
          f"Expenses: {totals['total_expenses']}, "
          f"Savings: {totals['total_savings']}")

    # ── Step 2: Gemini only categorizes spending ──────────────────────────────
    system_prompt = f"""
    You are a financial dashboard generator. The savings have already been calculated for you:
    - Total Income  : ₹{totals['total_income']}
    - Total Expenses: ₹{totals['total_expenses']}
    - Total Savings : ₹{totals['total_savings']}

    Your ONLY job is to categorize the expenses into spending categories.
    Return a STRICT JSON object — no extra text, no markdown fences:
    {{
      "total_savings": {totals['total_savings']},
      "stats": [
        {{ "label": "Food & Dining", "amount": 500, "width": "20%" }},
        {{ "label": "Shopping", "amount": 2000, "width": "60%" }}
      ],
      "insight": "One-line observation about spending",
      "reason": "Brief explanation",
      "recommendation": "One actionable tip"
    }}

    CATEGORY MAPPING — use these to classify merchants correctly:
    - Food & Dining   : Zomato, Swiggy, EatClub, Domino's, McDonald's, KFC, restaurant, cafe, hotel dining
    - Groceries       : BigBasket, Blinkit, Swiggy Instamart, DMart, Zepto, Grofers, supermarket, kirana
    - Shopping        : Amazon, Flipkart, Myntra, Ajio, Meesho, Nykaa, Tata Cliq, retail, store
    - Transport       : Uber, Ola, Rapido, BMTC, metro, fuel, petrol, auto, cab, parking, toll
    - Travel          : MakeMyTrip, Yatra, GoIbibo, IRCTC, airline, flight, hotel, OYO, Airbnb
    - Entertainment   : INOX, PVR, BookMyShow, Netflix, Hotstar, Spotify, gaming, amusement
    - Subscriptions   : Netflix, Spotify, Amazon Prime, Hotstar, JioCinema, Apple, Google Play, Adobe
    - Bills           : Airtel, Jio, Vi, BSNL, electricity, EB, gas, water, insurance, DTH, broadband
    - Utilities       : electricity board, water bill, gas cylinder, internet provider, utility
    - Housing         : rent, society charges, maintenance, home loan, EMI, landlord
    - Health          : Apollo, Medplus, 1mg, PharmEasy, hospital, clinic, doctor, pharmacy, medicine
    - Other           : ONLY use this if you truly cannot match any category above

    RULES:
    1. Use total_savings exactly as given above: {totals['total_savings']}. DO NOT recalculate it.
    2. Read the UPI description carefully — e.g. "UPI-DR-xxx-ZOMATO" → Food & Dining, "UPI-DR-xxx-UBER" → Transport.
    3. Include every category that has non-zero spend. MINIMIZE use of "Other".
    4. Set width as % proportional to each category's share of ₹{totals['total_expenses']} total expenses.
    5. Do NOT add a "color" field.
    """

    user_prompt = f"Transactions to categorize:\n" + "\n".join(
        t.get("raw_line", "") for t in transactions[:200]   # cap at 200 lines for token limit
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[system_prompt, user_prompt]
        )
        import re
        raw = response.text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            # Always enforce our pre-calculated savings — never trust Gemini's math
            result["total_savings"]   = totals["total_savings"]
            result["total_spent"]     = totals["total_expenses"]
            result["total_received"]  = totals["total_income"]
            result["closing_balance"] = totals.get("closing_balance", 0)
            result["opening_balance"] = totals.get("opening_balance", 0)
            # Daily avg spend: total spent / 30 (assume monthly statement)
            result["avg_daily_spend"] = round(totals["total_expenses"] / 30, 2)
            return result
        print("Gemini summary raw output:", raw[:500])
    except Exception as e:
        print("Error in summary generation:", e)

    return {"error": "Could not parse."}
