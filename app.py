from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx

app = Flask(__name__)
CORS(app)

# Correct Gradio Space endpoint
SPACE_API_URL = "https://ajay1311-cyberswaraksha.hf.space/api/predict"

# Hugging Face Space function name
API_NAME = "/analyze_phishing"

def predict_via_httpx(input_text, timeout=30.0):
    """
    Call Hugging Face Space using direct HTTP POST to /api/predict.
    """
    payload = {
        "data": [input_text],
        "fn_index": 0  # Can be dynamic, but usually 0 for the first function
    }

    try:
        response = httpx.post(SPACE_API_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json().get("data", [])
        if len(data) == 3:
            return tuple(data)
    except Exception as e:
        print("Error calling HF Space via httpx:", e)
        return None

@app.route('/', methods=['GET'])
def index():
    return "Phishing Detection API is live on Render!", 200

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json()
    input_text = data.get('text', '').strip()
    
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    result = predict_via_httpx(input_text)
    if result is None:
        return jsonify({"error": "Prediction failed. Try again later."}), 500

    detection_summary, confidence_meter, detailed_analysis = result

    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })
