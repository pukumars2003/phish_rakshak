import logging
from flask import Flask, request, jsonify
from gradio_client import Client
from flask_cors import CORS
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app and enable CORS for cross-origin requests
app = Flask(__name__)
CORS(app)

# Initialize Gradio Client for CyberSwaRaksha model
client = Client("Ajay1311/CyberSwaRaksha")

# Custom function to handle timeouts manually with logging
def predict_with_timeout(input_text, timeout=60.0):  # Increased timeout to 60 seconds
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

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    data = request.get_json()
    input_text = data.get('text')

    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    # Attempt to get the result from the Gradio model
    logging.debug("Processing request for phishing analysis...")
    result = predict_with_timeout(input_text, timeout=60.0)

    if result is None:
        return jsonify({"error": "Request timed out or failed. Please try again later."}), 500

    detection_summary, confidence_meter, detailed_analysis = result

    return jsonify({
        "detection_summary": detection_summary,
        "confidence_meter": confidence_meter,
        "detailed_analysis": detailed_analysis
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
