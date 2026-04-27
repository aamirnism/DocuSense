from flask import Flask, request, jsonify, send_from_directory
import PyPDF2
from google import genai
import json
import os

app = Flask(__name__)
client = genai.Client(api_key=os.environ.get("AIzaSyDPYvYmu-sHWbhNBfv783RASImJETbiVc0"))

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["file"]
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    text = text[:2000]

    prompt = f"""Analyze this document. Return ONLY valid JSON with these exact keys:
- action_items: array of tasks someone must do
- deadlines: array of dates or timeframes mentioned
- signatures: array of signature or approval requirements
- important_notes: array of key warnings or critical info

Keep each item under 25 words. Return only a JSON object, no markdown, no explanation.

Document:
{text}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return jsonify(result)

    except Exception as e:
        print("Gemini error:", str(e))
        return jsonify({
            "action_items": [f"Error: {str(e)}"],
            "deadlines": [],
            "signatures": [],
            "important_notes": []
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
