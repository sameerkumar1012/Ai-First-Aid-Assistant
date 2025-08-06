from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import os
import json

# Load environment variables
print("Loading environment variables...")
load_dotenv()

# Initialize Flask app
print("Initializing Flask app...")
app = Flask(__name__)

# Make the app variable accessible to Flask CLI
application = app

# Print API key status (safely)
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print("API key found")
else:
    print("WARNING: No API key found in environment variables")

# Configure Google AI
try:
    print("Configuring Google AI...")
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    
    print("Initializing Gemini models...")
    # Model for text inputs
    text_model = genai.GenerativeModel('gemini-1.5-flash')
    # Model for image inputs
    vision_model = genai.GenerativeModel('gemini-1.5-flash')
    print("Models initialized successfully")
except Exception as e:
    print(f"Error initializing Gemini AI: {str(e)}")
    raise

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        if request.files.get('image'):
            print("Receiving image...")
            image = request.files['image']
            print(f"Image received: {image.filename}, Content-Type: {image.content_type}")
            
            # Validate image file
            if not image.filename:
                return jsonify({'error': 'No image file selected'}), 400
            
            # Check file size (limit to 10MB)
            image.seek(0, 2)  # Seek to end
            file_size = image.tell()
            image.seek(0)  # Reset to beginning
            
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return jsonify({'error': 'Image file too large. Please use an image smaller than 10MB.'}), 400
            
            # Validate image format
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            file_extension = os.path.splitext(image.filename.lower())[1]
            if file_extension not in allowed_extensions:
                return jsonify({'error': f'Unsupported image format. Please use: {", ".join(allowed_extensions)}'}), 400
            
            image_data = image.read()
            print(f"Image data read, size: {len(image_data)} bytes")
            
            image_prompt = """
            You are a first aid assistant. Analyze this image of an injury and provide ONLY a valid JSON response with these exact fields: 'injury_name', 'first_aid_steps' (as a list of strings), and 'severity' ('minor', 'moderate', or 'severe').

            Respond with ONLY valid JSON in this exact format:
            {
              "injury_name": "Specific injury name",
              "first_aid_steps": [
                "Step 1 description",
                "Step 2 description",
                "Step 3 description"
              ],
              "severity": "minor|moderate|severe"
            }

            If it's a severe injury that requires immediate medical attention, include that as the first step.
            Do not include any text before or after the JSON. Only return the JSON object.
            """
            
            # Create prompt parts with image
            prompt_parts = [
                image_prompt,
                {"mime_type": image.content_type, "data": base64.b64encode(image_data).decode()}
            ]
            
            print("Calling Gemini Vision API...")
            try:
                # Generate response using vision model
                response = vision_model.generate_content(prompt_parts)
                print("Received response from Gemini Vision API")
            except Exception as vision_error:
                print(f"Vision API error: {str(vision_error)}")
                return jsonify({'error': f'Error processing image: {str(vision_error)}'}), 500
            
        else:
            # Handle text input
            data = request.json
            if not data:
                return jsonify({'error': 'No input provided'}), 400
                
            user_text = data.get('message', '')
            if not user_text:
                return jsonify({'error': 'No message provided'}), 400
            
            prompt = f'''
            You are a first aid assistant. Analyze the following injury description and provide ONLY a valid JSON response with these exact fields: 'injury_name', 'first_aid_steps' (as a list of strings), and 'severity' ('minor', 'moderate', or 'severe').

            Injury Description: {user_text}

            Respond with ONLY valid JSON in this exact format:
            {{
              "injury_name": "Specific injury name",
              "first_aid_steps": [
                "Step 1 description",
                "Step 2 description",
                "Step 3 description"
              ],
              "severity": "minor|moderate|severe"
            }}

            Do not include any text before or after the JSON. Only return the JSON object.
            '''
            
            # Generate response using text model
            response = text_model.generate_content(prompt)
        
        # Process the response
        try:
            print("Processing AI response...")
            response_text = response.text
            print(f"Raw response from AI: {response_text}")
            
            # Clean up the response - remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            print(f"Cleaned response: {response_text}")
            
            # Try to parse the response as JSON directly
            parsed_response = json.loads(response_text)
            print("Successfully parsed response as JSON")
            
            # Ensure all required fields are present
            required_fields = ['injury_name', 'first_aid_steps', 'severity']
            missing_fields = [field for field in required_fields if field not in parsed_response]
            
            if missing_fields:
                error_msg = f"Response missing required fields: {', '.join(missing_fields)}"
                print(error_msg)
                return jsonify({'error': error_msg}), 500
            
            print("All required fields present in response")
            return jsonify(parsed_response)
            
        except json.JSONDecodeError as json_error:
            print(f"JSON parsing error: {str(json_error)}")
            print(f"Raw response that failed to parse: {response_text}")
            return jsonify({
                'error': 'Invalid JSON format in AI model response'
            }), 500
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\nStarting Flask server...")
    print("You can access the application at: http://localhost:5001")
    print("Press CTRL+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5001)
