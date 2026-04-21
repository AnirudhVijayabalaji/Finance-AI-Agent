from typing import Dict
from google import genai
import os

def analyze_transaction_graph(image_path: str) -> Dict:
    """
    Analyzes Google Pay / UPI transaction graphs and screenshots using Gemini Vision.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY environment variable not set."}
        
    client = genai.Client(api_key=api_key)
    
    try:
        # We would typically upload the file, but here we pass the local read bytes
        # to the model. Note: For Google GenAI, we use generate_content
        import PIL.Image
        img = PIL.Image.open(image_path)
        
        prompt = '''
        Analyze this financial graph/screenshot. 
        Return ONLY a JSON object with:
        {
          "insights": {
            "top_category": "Name of top spending category",
            "monthly_spending": Total number,
            "trends": "Short sentence about the trend seen"
          }
        }
        Do not guess unclear values. If it's completely ambiguous, return {"error": "unclear data"}.
        '''
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img]
        )
        
        # In a robust app we'd parse this string to JSON safely
        # For simplicity, we just return the raw text block, assuming JSON
        import json
        import re
        
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return {"raw_text": response.text}
        
    except Exception as e:
        return {"error": str(e)}
