import google.generativeai as genai

"""
Simple script to test the Gemini API directly with hardcoded values.
This bypasses any .env or environment variable issues.
"""

# Direct API key - no environment variables or .env files
API_KEY = "AIzaSyCbIXGRB_1RHgrlLXZ4-ZtFrnVuyPf1Ta8"
MODEL = "gemini-1.5-pro"

print(f"Testing Gemini API with key: {API_KEY[:4]}...{API_KEY[-4:]}")
print(f"Using model: {MODEL}")

try:
    # Configure the API
    genai.configure(api_key=API_KEY)
    
    # Create the model
    model = genai.GenerativeModel(MODEL)
    
    # Generate content
    response = model.generate_content("Say hello")
    
    # Print result
    print("\nSUCCESS! Response received:")
    print(response.text)
    
    print("\nYour Gemini API is working correctly with direct configuration.")
    print("If your main app is still not working, the issue is with how it loads the API key.")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    print("\nThe API key or model name might be invalid. Please check:")
    print("1. That you've enabled the Gemini API in your Google AI Studio project")
    print("2. Your API key is correct")
    print("3. You're using a valid model name")
    print("4. Your network can connect to Google's APIs")
