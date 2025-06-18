import os
from gradio_client import Client

def main():
    # Your token should be stored in environment variables for safety
    HF_TOKEN = os.getenv("HF_TOKEN", "cb1c9f744ed6d9e4eea6465dfddc1bdb")  # fallback for demo

    try:
        # Initialize the client with your token
        client = Client("Ajay1311/CyberSwaRaksha", hf_token=HF_TOKEN)

        # Example input to your Space
        input_data = "Hello from app.py!"

        # Call the predict method, adjust function name & inputs as needed
        output = client.predict(input_data)

        print("Output from the Space:", output)
    except Exception as e:
        print("Error during call to the Space:", e)

if __name__ == "__main__":
    main()
