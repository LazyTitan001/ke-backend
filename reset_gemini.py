import os
import sys
from pathlib import Path

"""
Utility script to reset the Gemini configuration.
This will recreate the .env file with the correct format and test the configuration.
"""

def main():
    print("===== Gemini Configuration Reset Utility =====")
    
    # Get the API key from the user if not provided
    api_key = input("Enter your Gemini API key (press Enter to use existing key): ").strip()
    
    # If no key provided, try to get it from existing .env
    if not api_key:
        try:
            env_path = Path('.env')
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('GOOGLE_API_KEY='):
                            api_key = line.split('=', 1)[1].strip()
                            print(f"Using existing API key: {api_key[:4]}...{api_key[-4:]}")
        except Exception as e:
            print(f"Error reading existing .env file: {e}")
    
    if not api_key:
        print("ERROR: No API key provided. Please get a key from https://aistudio.google.com/")
        return
    
    # Create a clean .env file
    try:
        with open('.env', 'w') as f:
            f.write(f"GOOGLE_API_KEY={api_key}\n")
            f.write("FLASK_ENV=development\n")
            f.write("GEMINI_MODEL=gemini-1.5-pro\n")
        print("Successfully created .env file with clean format")
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return
    
    # Test the configuration
    print("\nTesting Gemini configuration...")
    try:
        import google.generativeai as genai
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # List available models
        print("Available Gemini models:")
        models = [m.name for m in genai.list_models() if "gemini" in m.name.lower()]
        for i, model_name in enumerate(models[:10]):  # Show first 10 models
            print(f"  {i+1}. {model_name}")
        
        if len(models) > 10:
            print(f"  ... and {len(models)-10} more")
        
        # Test the model
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content("Hello, please respond with a short greeting.")
        
        print(f"\n✅ Connection successful! Response: {response.text}")
        print("\nYour Gemini configuration is working correctly!")
        print("You can now run the application with: python app.py")
        
    except Exception as e:
        print(f"\n❌ Error testing Gemini configuration: {e}")
        print("\nTROUBLESHOOTING STEPS:")
        print("1. Verify your API key is correct")
        print("2. Make sure you've enabled the Gemini API in your Google AI Studio project")
        print("3. Try getting a new API key from https://aistudio.google.com/")
        print("4. Check if your network allows connections to Google APIs")

if __name__ == "__main__":
    main()
