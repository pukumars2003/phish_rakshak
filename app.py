from flask import Flask, request, jsonify
from gradio_client import Client
from flask_cors import CORS
import httpx
import os
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

app = Flask(__name__)
CORS(app)

# Initialize Gradio Client
try:
    client = Client("Ajay1311/CyberSwaRaksha")
except Exception as e:
    print(f"Failed to initialize Gradio Client: {e}")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((httpx.ConnectTimeout, httpx.RequestError)),
    before_sleep=lambda retry_state: print(f"Retrying due to error: {retry_state.outcome.exception()}")
)
def predict_with_timeout(input_text, timeout=60.0):
    try:
        result = client.predict(text=input_text, api_name="/analyze_phishing")
        return result
    except httpx.ConnectTimeout as e:
        print(f"Connection timeout error: {e}")
        raise
    except httpx.RequestError as e:
        print(f"HTTP request error: {e}")
        raise

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json()
    input_text = data.get('text')
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400
    
    try:
        result = predict_with_timeout(input_text)
        if result is None:
            return jsonify({"error": "Request timed out or failed. Please try again later."}), 500
        detection_summary, confidence_meter, detailed_analysis = result
        return jsonify({
            "detection_summary": detection_summary,
            "confidence_meter": confidence_meter,
            "detailed_analysis": detailed_analysis
        })
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": "Failed to process request. Please try again."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
