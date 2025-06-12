from flask import Flask, request, jsonify
from gradio_client import Client
from flask_cors import CORS
import httpx
import json

app = Flask(__name__)
CORS(app)

# Initialize the Gradio Client
client = Client("Ajay1311/CyberSwaRaksha")

@app.route('/', methods=['GET'])
def index():
    return "Phishing Detection API is live!", 200

def predict_with_timeout(input_text, timeout=30.0):
    try:
        # Pass input_text as positional argument
        result = client.predict(input_text, api_name="/analyze_phishing")
        return result
    except httpx.ConnectTimeout as e:
        print(f"Connection timeout error: {e}")
        return None
    except httpx.RequestError as e:
        print(f"HTTP request error: {e}")
        return None

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json()
    input_text = data.get('text')

    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    result = predict_with_timeout(input_text, timeout=30.0)

    if result is None:
        return jsonify({"error": "Request timed out or failed. Please try again later."}), 500

    detection_summary, confidence_meter, detailed_analysis = result

    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })

# Do not include app.run() for Render
