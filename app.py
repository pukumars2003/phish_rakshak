from flask import Flask, request, jsonify
from gradio_client import Client
from flask_cors import CORS
import httpx
import os

# Initialize Flask app and enable CORS for cross-origin requests from Chrome Extension
app = Flask(__name__)
CORS(app)

# Initialize the Gradio Client for CyberSwaRaksha model
client = Client("Ajay1311/CyberSwaRaksha")

# Custom function to handle timeouts manually
def predict_with_timeout(input_text, timeout=30.0):
    try:
        # Make the prediction call to the model API with a timeout
        result = client.predict(text=input_text, api_name="/analyze_phishing")
        return result
    except httpx.ConnectTimeout as e:
        # Handle connection timeout errors
        print(f"Connection timeout error: {e}")
        return None
    except httpx.RequestError as e:
        # Handle general request errors
        print(f"HTTP request error: {e}")
        return None

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json()
    input_text = data.get('text')
    
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400
    
    # Attempt to get the result from the Gradio model
    result = predict_with_timeout(input_text, timeout=30.0)
    
    if result is None:
        return jsonify({"error": "Request timed out or failed. Please try again later."}), 500
    
    # Unpack the result tuple
    detection_summary, confidence_meter, detailed_analysis = result
    
    # Return the results as JSON
    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })

if __name__ == '__main__':
    # Get port from environment variable or default to 5000 for local development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
