import os
import json
from google import genai

FALLBACK_RESPONSE = {"error": "Internal Server Error", "code": 500}

client = None

def init_gemini():
    global client
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        client = genai.Client(api_key=api_key)
    return client is not None

def clean_response(text):
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def generate_honeypot_response(method, endpoint, payload):
    global client
    
    if client is None:
        if not init_gemini():
            return json.dumps(FALLBACK_RESPONSE)
    
    system_instruction = """You are a backend server for a legacy financial corporation. You must generate a realistic JSON response for the following request. If the user sends a POST, generate a 'success' or 'validation error' response. If GET, return realistic dummy data. OUTPUT ONLY RAW JSON. NO MARKDOWN. NO CODE BLOCKS."""
    
    user_prompt = f"""Request Details:
- Method: {method}
- Endpoint: {endpoint}
- Payload: {payload if payload else 'None'}

Generate an appropriate JSON response for this API request."""
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_prompt,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.7,
                "max_output_tokens": 1024
            }
        )
        
        if response and response.text:
            cleaned = clean_response(response.text)
            json.loads(cleaned)
            return cleaned
        else:
            return json.dumps(FALLBACK_RESPONSE)
            
    except json.JSONDecodeError:
        return clean_response(response.text) if response and response.text else json.dumps(FALLBACK_RESPONSE)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return json.dumps(FALLBACK_RESPONSE)
