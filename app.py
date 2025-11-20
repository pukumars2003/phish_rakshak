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


# ------------------ API ROUTES ------------------ #

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    """Endpoint for URL analysis (includes safe list check)"""
    data = request.get_json()
    input_text = data.get('text')

    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    logging.debug(f"📥 Received URL: {input_text}")
    logging.debug("🔍 Checking if URL is in safe list...")

    # ✅ SAFE LIST RESPONSE
    if is_safe_url(input_text):
        logging.info("✅ URL is in safe list. Skipping model prediction.")
        return jsonify({
            "detection_summary": "Content Safe (Confidence: 100.0%)",
            "confidence_meter": "100.0%",
            "detailed_analysis": (
                "✅ No Threat Detected. This URL is listed in the trusted safe list.\n\n"
                "**Confidence:** 100.0%\n\n"
                "**General Safety Tips:**\n"
                "- Avoid clicking unknown links\n"
                "- Be cautious with personal data\n"
                "- Always confirm requests from unknown senders\n\n"
                "**Recommendation:**\n"
                "Proceed with standard caution."
            )
        })

    # 🔍 GRADIO PREDICTION RESPONSE
    result = predict_with_timeout(input_text, timeout=60.0)
    if result is None:
        return jsonify({"error": "Request timed out or failed. Please try again later."}), 500

    detection_summary, confidence_meter, detailed_analysis = result

    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })


@app.route('/analyze_message', methods=['POST'])
def analyze_message():
    """Endpoint for Message/Text analysis (SKIPS safe list check)"""
    data = request.get_json()
    input_text = data.get('text')

    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    logging.debug(f"📥 Received Message: {input_text}")
    logging.debug("⏩ Skipping safe list check for message content.")

    # 🔍 GRADIO PREDICTION RESPONSE
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
