import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment variables")
    exit(1)

print(f"API Key found: {api_key[:10]}...")
genai.configure(api_key=api_key)

# List all available models
print("\n=== Available Models ===")
try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"[OK] {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description[:100]}...")
            print()
except Exception as e:
    print(f"Error listing models: {e}")
    print("\nTrying alternative approach...")
    
    # Try to use a model directly
    test_models = [
        'gemini-1.5-flash',
        'gemini-1.5-pro', 
        'gemini-pro',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-pro'
    ]
    
    print("\n=== Testing Models ===")
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello")
            print(f"[OK] {model_name} - WORKS!")
        except Exception as e:
            print(f"[FAIL] {model_name} - {str(e)[:80]}")
