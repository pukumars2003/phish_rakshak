from flask import Flask, request, jsonify
from gradio_client import Client
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Hugging Face Space client
client = Client("Ajay1311/CyberSwaRaksha")

def predict_with_timeout(input_text, timeout=30.0):
    try:
        # Call the model using positional argument
        result = client.predict(input_text, api_name="/analyze_phishing")
        return result
    except Exception as e:
        print(f"Error calling Gradio model: {e}")
        return None

@app.route('/', methods=['GET'])
def index():
    return "Phishing Detection API is live!", 200

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json()
    input_text = data.get('text', '').strip()
    
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    result = predict_with_timeout(input_text)
    if result is None:
        return jsonify({"error": "Prediction failed. Try again later."}), 500

    detection_summary, confidence_meter, detailed_analysis = result

    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })
