# Kissan Expert Backend

This is the backend service for the Kissan Expert application, which provides crop recommendations and agricultural advice using machine learning and Gemini AI.

## Setup

1. Create a virtual environment:

   ```
   python -m venv venv
   ```

2. Activate the virtual environment:

   ```
   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Make sure you have a `.env` file with your API keys:

   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   FLASK_ENV=development
   GEMINI_MODEL=gemini-1.5-pro
   ```

5. Run the application:
   ```
   python app.py
   ```

## API Endpoints

### Crop Prediction

**Endpoint:** `/api/predict`
**Method:** POST
**Description:** Predicts the most suitable crop based on soil and climate parameters.

**Request Body:**

```json
{
  "nitrogen": 90,
  "phosphorous": 42,
  "potassium": 43,
  "temperature": 20.87,
  "humidity": 82.0,
  "pH": 6.5,
  "rainfall": 202.93
}
```

### AI Assistant for Crop Questions

**Endpoint:** `/api/ask`
**Method:** POST
**Description:** Provides answers to crop-specific questions using Gemini AI.

**Request Body:**

```json
{
  "crop": "rice",
  "question": "What is the best time to plant rice in Punjab region?",
  "language": "Hindi" //  defaults to English if not provided
}
```

**Supported Languages:**
The API supports multiple languages including but not limited to:

- English (default)
- Hindi
- Tamil
- Telugu
- Marathi
- Bengali
- Gujarati
- Kannada
- Malayalam
- Punjabi
- Urdu

**Response:**

```json
{
  "status": "success",
  "crop": "rice",
  "language": "Hindi",
  "response": "पंजाब क्षेत्र में धान की रोपाई के लिए सबसे अच्छा समय जून के पहले पखवाड़े से जुलाई के मध्य तक है। मानसून की शुरुआत के साथ रोपाई करने से पानी की उपलब्धता सुनिश्चित होती है और अच्छी पैदावार मिलती है।"
}
```

### Multilingual Examples

#### Example: Hindi Query

**Request:**

```json
{
  "crop": "wheat",
  "question": "What is the best fertilizer for wheat farming?",
  "language": "Hindi"
}
```

**Response:**

```json
{
  "status": "success",
  "crop": "wheat",
  "language": "Hindi",
  "response": "गेहूं के लिए नाइट्रोजन, फॉस्फोरस और पोटाश (NPK) के संतुलित मिश्रण वाला उर्वरक सबसे अच्छा होता है। बुवाई के समय DAP (100-150 किग्रा/हेक्टेयर) का प्रयोग करें और बाद में यूरिया (100-150 किग्रा/हेक्टेयर) की दो खुराक दें - पहली सिंचाई और दूसरी फूल आने के समय। मिट्टी परीक्षण के आधार पर उर्वरक की मात्रा समायोजित करें।"
}
```

#### Testing with cURL

```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "rice",
    "question": "How to prevent rice blast disease?",
    "language": "Hindi"
  }'
```

#### Testing with Postman

1. Set the request method to **POST**
2. Enter the URL: `http://localhost:5000/api/ask`
3. Go to the **Headers** tab and add:
   - Key: `Content-Type`
   - Value: `application/json`
4. Go to the **Body** tab, select **raw** and then **JSON** format
5. Enter the JSON request:
   ```json
   {
     "crop": "rice",
     "question": "How to prevent rice blast disease?",
     "language": "Hindi"
   }
   ```
6. Click **Send**

## Troubleshooting

If you encounter issues with the Gemini API, run the test script:

```
python test_gemini.py
```

This will help diagnose any API connection or authentication issues.
