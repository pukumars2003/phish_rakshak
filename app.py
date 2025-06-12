from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx

app = Flask(__name__)
CORS(app)

# ✅ Corrected Hugging Face endpoint (NOT /run/)
SPACE_URL = "https://ajay1311-cyberswaraksha.hf.space/analyze_phishing"

@app.route('/', methods=['GET'])
def index():
    return "Phishing Detection API is live!", 200

def predict_via_space(input_text: str, timeout: float = 30.0):
    """
    Posts to the correct Hugging Face Space HTTP endpoint. Returns
    a tuple (summary, confidence, detail) or None on error.
    """
    try:
        # Use form-style parameters for Spaces with named endpoints
        resp = httpx.post(SPACE_URL, data={"text": input_text}, timeout=timeout)
        resp.raise_for_status()
        js = resp.json()
        
        if isinstance(js, list) and len(js) == 3:
            return tuple(js)
        
        # If Gradio wraps data in {"data": [...]}
        outputs = js.get("data", [])
        if len(outputs) == 3:
            return tuple(outputs)
        
    except Exception as e:
        print("Error calling Space:", e)
    return None

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json() or {}
    input_text = data.get('text', '').strip()
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    result = predict_via_space(input_text)
    if result is None:
        return jsonify({"error": "Prediction failed or timed out."}), 500

    detection_summary, confidence_meter, detailed_analysis = result
    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })

# No app.run(): Use gunicorn app:app on Render
