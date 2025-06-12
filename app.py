from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client
import httpx

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Gradio client
client = Client("Ajay1311/CyberSwaRaksha")

# Helper function to call model with timeout
def predict_with_timeout(input_text, timeout=30.0):
    try:
        result = client.predict(text=input_text, api_name="/analyze_phishing")
        return result
    except httpx.RequestError as e:
        print(f"HTTP request error: {e}")
        return None

# Root route for health check
@app.route('/', methods=['GET'])
def index():
    return "Phishing Detection API is live!", 200

# Main phishing analysis endpoint
@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json()
    input_text = data.get('text')
    
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    result = predict_with_timeout(input_text, timeout=30.0)
    
    if result is None:
        return jsonify({"error": "Prediction failed or timed out."}), 500

    detection_summary, confidence_meter, detailed_analysis = result
    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })

