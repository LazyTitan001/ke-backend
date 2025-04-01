import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Create a clean .env file with correct format (no comments or special characters)
try:
    env_path = Path('.') / '.env'
    with open(env_path, 'w') as f:
        f.write("GOOGLE_API_KEY=AIzaSyCbIXGRB_1RHgrlLXZ4-ZtFrnVuyPf1Ta8\n")
        f.write("FLASK_ENV=development\n")
    print(f"Created clean .env file at {env_path.absolute()}")
except Exception as e:
    print(f"Error creating .env file: {str(e)}")

# Manually set the API key for this test
API_KEY = "AIzaSyCbIXGRB_1RHgrlLXZ4-ZtFrnVuyPf1Ta8"
os.environ["GOOGLE_API_KEY"] = API_KEY

print(f"\nAPI key length: {len(API_KEY)}")
print(f"First 4 chars: {API_KEY[:4]}...")
print(f"Last 4 chars: ...{API_KEY[-4:]}")

# Configure Gemini
genai.configure(api_key=API_KEY)

# Test available models
try:
    print("\nListing available models...")
    for m in genai.list_models():
        if "gemini" in m.name.lower():
            print(f"• {m.name}")
except Exception as e:
    print(f"Error listing models: {str(e)}")

# Try multiple model versions
models_to_try = [
    "gemini-pro", 
    "gemini-1.0-pro",
    "gemini-1.5-pro", 
    "gemini-2.0-flash",
    "gemini-2.0-pro"
]

for model_name in models_to_try:
    try:
        print(f"\nTesting with model: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, world!")
        print(f"✅ Success with {model_name}! Response: {response.text}")
        # If successful, break out of the loop
        successful_model = model_name
        break
    except Exception as e:
        print(f"❌ Error with {model_name}: {str(e)}")

print("\nAPI Test Summary:")
if 'successful_model' in locals():
    print(f"✅ Successfully connected to Gemini API using model: {successful_model}")
    print("Your API key is valid and working correctly!")
else:
    print("❌ Could not connect to Gemini API with any model.")
    print("\nTROUBLESHOOTING:")
    print("1. Verify your API key on Google AI Studio: https://aistudio.google.com/")
    print("2. Make sure you've enabled the Gemini API in your Google AI Studio project")
    print("3. Check if you need to set up billing for your project")
    print("4. Try the curl command from Google AI Studio to test the API directly")
