from gradio_client import Client
import os

# Initialize the client without a token (only works if the Space is public)
client = Client("Ajay1311/CyberSwaRaksha")

# Input text (simulate phishing or safe message)
input_text = "Please verify your account by clicking this link: http://bit.ly/fake-login"

# Run prediction using the default function (only one function in your Space)
try:
    result_summary, result_plot, result_analysis = client.predict(
        input_text,  # input
        api_name="/predict"  # use the default function route
    )

    print("=== Detection Summary ===")
    print(result_summary)

    print("\n=== Detailed Analysis ===")
    print(result_analysis)

    print("\n=== Plot Info ===")
    print("Plot object returned:", type(result_plot))

except Exception as e:
    print("Error occurred while calling the Space:", e)
