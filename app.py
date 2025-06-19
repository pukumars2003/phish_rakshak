import logging
from flask import Flask, request, jsonify
from gradio_client import Client
from flask_cors import CORS
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Initialize Gradio client
client = Client("Ajay1311/CyberSwaRaksha")

# --- Safe URL Checker ---
def is_safe_url(url):
    try:
        with open("safe_urls.txt", "r") as f:
            safe_urls = [line.strip() for line in f if line.strip()]
        return any(url.startswith(safe_url) for safe_url in safe_urls)
    except Exception as e:
        logging.error(f"Error reading safe_urls.txt: {e}")
        return False

# --- Prediction with timeout ---
def predict_with_timeout(input_text, timeout=60.0):
    start_time = time.time()
    try:
        logging.debug("Sending prediction request to Gradio Space...")
        result = client.predict(
            text=input_text,
            api_name="/analyze_phishing"
        )
        logging.debug("Received response from Gradio Space.")
        return result
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        if time.time() - start_time > timeout:
            logging.warning("Request timed out")
        return None

# --- API Route ---
@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json()
    input_text = data.get('text')

    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    logging.debug(f"Received URL: {input_text}")

    # Check safe list first
    if is_safe_url(input_text):
        logging.info("URL is in safe list. Skipping prediction.")
        return jsonify({
            "detection_summary": "This website is verified as SAFE (based on safe list).",
            "confidence_meter": "100% Safe",
            "detailed_analysis": "This URL matches a trusted domain in our safe list. No further analysis is needed."
        })

    # Not in safe list — send to model
    result = predict_with_timeout(input_text, timeout=60.0)
    if result is None:
        return jsonify({"error": "Request timed out or failed. Please try again later."}), 500

    detection_summary, confidence_meter, detailed_analysis = result

    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })

# --- Run Server ---
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
