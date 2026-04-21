from typing import Dict
from google import genai
import os

def categorize_expense(merchant: str, amount: float) -> str:
    """
    Classifies transactions into predefined categories using rules and Gemini LLM as fallback.
    """
    merchant_lower = merchant.lower()
    
    # 1. Rule-based categorization (fast path)
    categories = {
        "Food": ["zomato", "swiggy", "restaurant", "cafe", "starbucks", "mcdonalds", "kfc", "dominos", "food"],
        "Transport": ["uber", "ola", "metro", "fuel", "petrol", "indian oil", "bharat petroleum", "irctc", "flight"],
        "Shopping": ["amazon", "flipkart", "myntra", "retail", "mart", "supermarket", "ajio", "zara", "h&m"],
        "Bills": ["electricity", "rent", "water", "airtel", "jio", "vi", "bsnl", "broadband", "gas"],
        "Subscriptions": ["netflix", "spotify", "prime", "hotstar", "youtube", "apple", "google one"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in merchant_lower for keyword in keywords):
            return category
            
    # 2. LLM-based categorization (fallback)
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f'''
            Categorize the following transaction into exactly ONE of these categories:
            [Food, Transport, Shopping, Bills, Subscriptions, Other].
            Merchant/Description: {merchant}
            Amount: {amount}
            
            Return ONLY the category name. Do not output anything else.
            '''
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            cat = response.text.strip()
            if cat in ["Food", "Transport", "Shopping", "Bills", "Subscriptions", "Other"]:
                return cat
        except Exception:
            pass # fallback to Other on error

    return "Other"
