from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client

app = Flask(__name__)
CORS(app)

# Connect to your Hugging Face Space
client = Client("Ajay1311/CyberSwaRaksha")

@app.route('/', methods=['GET'])
def index():
    return "Phishing Detection API is live!", 200

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json() or {}
    input_text = data.get('text', '').strip()
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    try:
        # Use positional argument instead of keyword argument
        detection_summary, confidence_meter, detailed_analysis = client.predict(
            input_text,  # <--- Correct way
            api_name="/analyze_phishing"
        )
    except Exception as e:
        print("Error calling Space via gradio_client:", e)
        return jsonify({"error": "Prediction failed"}), 500

    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })
