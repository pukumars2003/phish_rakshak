import logging
from flask import Flask, request, jsonify
from gradio_client import Client
from flask_cors import CORS
import time
import os
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Flask app setup
app = Flask(__name__)
CORS(app)

# Gradio Client
client = Client("Ajay1311/CyberSwaRaksha")


# ------------------ SAFE URL CHECK ------------------ #
def normalize_url(url):
    """Normalize by lowercasing, removing www., and stripping trailing slashes."""
    try:
        parsed = urlparse(url.lower().rstrip("/"))
        hostname = parsed.hostname or ""
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return f"{parsed.scheme}://{hostname}"
    except Exception as e:
        logging.error(f"URL normalization error: {e}")
        return url.lower().rstrip("/")

def is_safe_url(url):
    normalized_input = normalize_url(url)
    filepath = os.path.join(os.path.dirname(__file__), "safe_urls.txt")

    try:
        if not os.path.exists(filepath):
            logging.warning("safe_urls.txt not found.")
            return False

        with open(filepath, "r") as f:
            safe_urls = [normalize_url(line.strip()) for line in f if line.strip()]

        if not safe_urls:
            logging.warning("safe_urls.txt is empty.")
            return False

        for safe_url in safe_urls:
            if normalized_input.startswith(safe_url):
                logging.info(f"✅ URL matched safe list entry: {safe_url}")
                return True

        logging.info(f"❌ No safe list match for URL: {url}")
        return False

    except Exception as e:
        logging.error(f"Error reading safe_urls.txt: {e}")
        return False


# ------------------ GRADIO CALL ------------------ #
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


# ------------------ API ROUTE ------------------ #
@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json()
    input_text = data.get('text')

    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    logging.debug(f"📥 Received URL: {input_text}")
    logging.debug("🔍 Checking if URL is in safe list...")

    if is_safe_url(input_text):
        logging.info("✅ URL is in safe list. Skipping model prediction.")
        return jsonify({
            "detection_summary": "This website is verified as SAFE (based on safe list).",
            "confidence_meter": "100% Safe",
            "detailed_analysis": "This URL matches a trusted domain in our safe list. No further analysis is needed."
        })

    # Not in safe list — analyze
    result = predict_with_timeout(input_text, timeout=60.0)
    if result is None:
        return jsonify({"error": "Request timed out or failed. Please try again later."}), 500

    detection_summary, confidence_meter, detailed_analysis = result

    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })


# ------------------ START SERVER ------------------ #
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
