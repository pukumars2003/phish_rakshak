from flask import Flask, request, jsonify
from gradio_client import Client
import time

app = Flask(__name__)

# Function to retry loading Hugging Face Space
def create_gradio_client_with_retry(space_name, retries=5, delay=5):
    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: Connecting to Hugging Face Space...")
            client = Client(space_name)
            print("Loaded as API:", client.space_url, "✔")
            return client
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(delay)
    raise RuntimeError("❌ Failed to connect to Hugging Face Space after multiple attempts.")

# Load your model from Hugging Face Space
client = create_gradio_client_with_retry("Ajay1311/CyberSwaRaksha")

@app.route("/")
def home():
    return "Phish-Rakshak backend is live!"

@app.route("/analyze_phishing", methods=["POST"])
def analyze_phishing():
    try:
        data = request.json
        if not data or "url" not in data:
            return jsonify({"error": "Missing 'url' parameter in JSON"}), 400

        url = data["url"]
        print(f"Received URL for analysis: {url}")

        # Send the URL to the model
        result = client.predict(
            url,     # URL (string)
            api_name="/predict"
        )

        print(f"Model result: {result}")

        return jsonify({
            "url": url,
            "prediction": result
        })

    except Exception as e:
        print("❌ Error analyzing URL:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
