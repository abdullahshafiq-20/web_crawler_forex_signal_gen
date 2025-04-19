import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import re
from google import genai

# Load environment variables from .env file
load_dotenv()

api_key=os.getenv("OPENROUTER_API_KEY")

def analyze_with_ai(data_to_analyze):
    """Send data to AI for analysis via OpenRouter API, focusing on trading signals"""
    
    # Get API key from environment variable for security
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OpenRouter API key not found. Set the OPENROUTER_API_KEY environment variable.")
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""
                            Analyze the following economic data from today ({datetime.now().strftime('%Y-%m-%d')}) and generate trading signals:
                            
                            {json.dumps(data_to_analyze, indent=2)}
                            
                            Please provide your analysis in the following JSON format:
                            {{
                                "market_summary": "Brief overall market summary based on economic indicators",
                                "signals": [
                                    {{
                                        "pair": "Currency pair or asset",
                                        "direction": "BUY or SELL",
                                        "strength": "HIGH, MEDIUM, or LOW",
                                        "confidence": "Confidence level in percentage",
                                        "rationale": "Brief explanation of the signal",
                                        "impact": "Potential market impact",
                                    }}
                                ],
                            }}
                            """
                        }
                    ]
                }
            ],
        })
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    

def analyze_signal_gemeni(data_to_analyze):
    gen_api = os.getenv("GENAI_API_KEY")
    if not gen_api:
        print("Error: GENAI_API_KEY environment variable not found")
        return None
        
    prompt = f"""
    Analyze the following economic data from today ({datetime.now().strftime('%Y-%m-%d')}) and generate trading signals:
    {json.dumps(data_to_analyze, indent=2)}
    Please provide your analysis in the following JSON format:

    {{
        "market_summary": "Brief overall market summary based on economic indicators",
        "signals": [
            {{
                "pair": "Currency pair or asset",
                "direction": "BUY or SELL",
                "strength": "HIGH, MEDIUM, or LOW",
                "confidence": "Confidence level in percentage",
                "rationale": "Brief explanation of the signal",
                "impact": "Potential market impact",
            }}
        ],
    }}
    """
    try:
        # Initialize the client
        client = genai.Client(api_key=gen_api)
        # Call the Gemini API with the prompt
        response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt,
        )

        # Check if the response is valid
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

    
def clean_json_response(response_text):
    """Clean the AI response by removing any markdown formatting and extracting just the JSON"""
    # Remove markdown code blocks if present
    json_pattern = r'```(?:json)?(.*?)```'
    match = re.search(json_pattern, response_text, re.DOTALL)
    
    if match:
        # Extract content inside the backticks
        clean_text = match.group(1).strip()
    else:
        clean_text = response_text.strip()
    
    return clean_text
