from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from models import load_model
from data import crop_info
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # More specific CORS setting

# Load the trained model
model = load_model()

# Configure Gemini AI
logger.info("Initializing Gemini AI...")
gemini_model = None

# APPROACH 1: Direct hardcoded API key as fallback
API_KEY = "AIzaSyCbIXGRB_1RHgrlLXZ4-ZtFrnVuyPf1Ta8"  # Fallback for testing
MODEL_NAME = "gemini-1.5-pro"  # This model worked in testing

try:
    # APPROACH 2: Try environment variables first
    env_key = os.getenv("GOOGLE_API_KEY", "")
    if env_key and len(env_key) > 30:
        API_KEY = env_key.strip('"\'')
        logger.info(f"Using API key from environment: {API_KEY[:4]}...{API_KEY[-4:]}")
    else:
        logger.warning("Environment API key not found or invalid, using fallback key")
    
    # Configure Gemini
    logger.info(f"Configuring Gemini with model {MODEL_NAME}")
    genai.configure(api_key=API_KEY)
    gemini_model = genai.GenerativeModel(MODEL_NAME)
    
    # Quick test
    logger.info("Testing Gemini connection...")
    test_response = gemini_model.generate_content("Test")
    logger.info(f"Gemini test successful: {test_response.text}")
except Exception as e:
    logger.error(f"ERROR initializing Gemini: {str(e)}")
    gemini_model = None

# Add a health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint that also verifies Gemini API status
    """
    health_status = {
        'status': 'online',
        'gemini_ai': 'not_configured'
    }
    
    if gemini_model:
        try:
            # Quick test of the Gemini connection
            test = gemini_model.generate_content("test")
            health_status['gemini_ai'] = 'connected'
        except Exception as e:
            health_status['gemini_ai'] = f'error: {str(e)}'
    
    return jsonify(health_status)

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Required fields
        required_fields = ['nitrogen', 'phosphorous', 'potassium', 
                          'temperature', 'humidity', 'pH', 'rainfall']
        
        # Check if all required fields are present
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract features from request
        try:
            N = float(data['nitrogen'])
            P = float(data['phosphorous'])
            K = float(data['potassium'])
            temperature = float(data['temperature'])
            humidity = float(data['humidity'])
            ph = float(data['pH'])
            rainfall = float(data['rainfall'])
        except ValueError:
            return jsonify({"error": "All values must be numeric"}), 400
        
        # Input validation
        if not all(v >= 0 for v in [N, P, K, temperature, humidity, ph, rainfall]):
            return jsonify({"error": "All values must be non-negative"}), 400
            
        # Make prediction
        import numpy as np
        input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        prediction = model.predict(input_data)[0]
        
        logger.info(f"Prediction made: {prediction}")
        
        # Get crop information
        crop_data = crop_info.get(prediction, {
            'description': 'Information not available',
            'types': 'Information not available',
            'disease': 'Information not available',
            'companion': 'Information not available',
            'pests': 'Information not available',
            'fertilizer': 'Information not available',
            'tips': 'Information not available',
            'spacing': 'Information not available',
            'watering': 'Information not available',
            'storage': 'Information not available'
        })
        
        # Return prediction and crop information
        return jsonify({
            'status': 'success',
            'crop': prediction,
            'info': crop_data
        })
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route('/api/ask', methods=['POST'])
def ask_gemini():
    """
    Endpoint to receive a crop-specific question and return Gemini's response.
    
    Expected JSON payload:
    {
        "crop": "crop_name",
        "question": "user's question about the crop",
        "language": "language_code"  # Optional, defaults to English
    }
    """
    try:
        # Check if Gemini model is configured
        if not gemini_model:
            return jsonify({"error": "Gemini AI is not configured. Please set GOOGLE_API_KEY in environment variables."}), 503
        
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Get crop name and question from request
        crop = data.get('crop')
        question = data.get('question')
        language = data.get('language', 'English')  # Default to English if not specified
        
        if not crop:
            return jsonify({"error": "Missing crop parameter"}), 400
        if not question:
            return jsonify({"error": "Missing question parameter"}), 400
        
        # Log the incoming question with crop info
        logger.info(f"Processing question about {crop} in {language}: {question[:50]}...")
        
        # Get crop information from our database if available
        crop_data = crop_info.get(crop.lower(), {})
        
        # Construct a well-structured prompt for Gemini that includes crop context and language preference
        prompt = f"""You are a concise agricultural expert for Indian farmers.

CROP: {crop} ({crop_data.get('TYPE', 'crop')})

QUESTION: {question}

INSTRUCTIONS:
- Provide a direct, practical answer in 3-5 sentences maximum
- Focus only on Indian farming conditions and practices
- Use simple, clear language that farmers would understand
- Include precise measurements and specific timeframes when relevant
- If you're unsure about specifics for this crop, be honest but brief
- RESPOND IN {language.upper()} LANGUAGE

FORMAT YOUR ANSWER LIKE THIS:
[Brief, direct answer with the most important information first in {language}]
"""
        
        # Generate response from Gemini with the enhanced prompt
        try:
            logger.info(f"Sending request to Gemini API (language: {language})")
            response = gemini_model.generate_content(prompt)
            logger.info("Successfully received response from Gemini API")
            
            return jsonify({
                'status': 'success',
                'crop': crop,
                'language': language,
                'response': response.text
            })
            
        except genai.types.generation_types.BlockedPromptException:
            logger.error("The prompt was blocked by Gemini's safety filters")
            return jsonify({
                'status': 'error',
                'error': "Your question contains content that cannot be processed due to safety filters. Please rephrase your question."
            }), 400
            
        except genai.types.generation_types.StopCandidateException:
            logger.error("The response was blocked by Gemini's safety filters")
            return jsonify({
                'status': 'error',
                'error': "The response contained content that was flagged by safety filters. Please try a different question."
            }), 400
            
        except Exception as api_error:
            logger.error(f"Gemini API specific error: {str(api_error)}")
            # In development, return the actual error for debugging
            if os.getenv("FLASK_ENV") == "development":
                return jsonify({
                    'status': 'error',
                    'error': f"Gemini API error: {str(api_error)}"
                }), 500
            else:
                return jsonify({
                    'status': 'error',
                    'error': "There was an issue generating a response. Please try again later."
                }), 500
        
    except Exception as e:
        logger.error(f"Error in Gemini AI processing: {str(e)}")
        # In development, return the actual error for debugging
        if os.getenv("FLASK_ENV") == "development":
            import traceback
            return jsonify({
                'status': 'error',
                'error': f"An error occurred: {str(e)}",
                'traceback': traceback.format_exc()
            }), 500
        else:
            return jsonify({
                'status': 'error',
                'error': "An error occurred while processing your request"
            }), 500

if __name__ == '__main__':
    # Use environment variable to determine debug mode
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(debug=debug_mode)

