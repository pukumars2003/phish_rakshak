from flask import Flask, request, jsonify
from flask_cors import CORS
import time

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Custom function to call Hugging Face model with timeout and retries
def predict_with_timeout(input_text, timeout=30.0, retries=3, delay=2):
    from gradio_client import Client

    start_time = time.time()
    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: Connecting to Hugging Face Space...")
            client = Client("Ajay1311/CyberSwaRaksha")

            result = client.predict(
                text=input_text,
                api_name="/analyze_phishing"
            )
            return result
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if time.time() - start_time > timeout:
                print("Request timed out.")
                break
            time.sleep(delay)
    return None

@app.route('/analyze_phishing', methods=['POST'])
def analyze_phishing():
    try:
        data = request.get_json()
        input_text = data.get('text')

        if not input_text:
            return jsonify({"error": "No input text provided"}), 400

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
        print(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
