import os
import re
import requests
from flask import Flask, request, jsonify


app = Flask(__name__)

load_dotenv();

@app.route('/validate-and-predict', methods=['POST'])
def validate_and_predict():
    data = request.json
    text = data.get("text")
    # Example regex pattern: only allow alphanumeric and spaces
    pattern = r"^[a-zA-Z0-9 ]+$"
    if not text or not re.match(pattern, text):
        return jsonify({"error": "Invalid format"}), 400

    # Forward to AI model
    headers = {
        "api-key": os.getenv('API_KEY'),
        "Content-Type": "application/json"
    }
    body = {
        "prompt": text,
        # ...other model params as needed
    }
    response = requests.post(os.getenv('OPENAI_API_KEY'), headers=headers, json=body)
    return jsonify(response.json())


if __name__ == "__main__":
    app.run()