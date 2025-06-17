from flask import Flask, request, jsonify
from gradio_client import Client
import os
import time

app = Flask(__name__)

HF_SPACE_URL = "https://ajay1311-cyberswaraksha.hf.space"

def connect_to_hf_space(url, max_attempts=5, delay=3):
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Attempt {attempt}: Connecting to Hugging Face Space...")
            client = Client(url)
            print(f"Loaded as API: {url} ✔")
            return client
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(delay)
    raise Exception(f "❌ Failed to connect to Hugging Face Space after multiple attempts. {url}")

client = connect_to_hf_space(HF_SPACE_URL)

@app.route("/", methods=["GET"])
def index():
    return "PhishRakshak is live! Use POST /analyze_phishing with JSON {\"url\": \"...\"}"

@app.route("/analyze_phishing", methods=["POST"])
def analyze():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request."}), 400

    url = data["url"]
    print(f"🌐 Sending URL to Hugging Face: {url}")
    try:
        result = client.predict(url, api_name="/predict")
        print(f"✅ Received result: {result}")
        return jsonify({"result": result})
    except Exception as e:
        print(f"❌ Error from HF Space: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
