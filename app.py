from flask import Flask, request, render_template, jsonify, send_file
from transformers import pipeline
from googletrans import Translator
import os

app = Flask(__name__)

# Load AI models
summarizer = pipeline("summarization")
translator = Translator()

# Set up folders
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save uploaded file
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    # Read file content
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Summarize text
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']

    # Translate summary to Kannada
    translated_summary = translator.translate(summary, src="en", dest="kn").text

    # Save outputs
    summary_file = os.path.join(app.config["OUTPUT_FOLDER"], "summary.txt")
    translated_file = os.path.join(app.config["OUTPUT_FOLDER"], "translated.txt")

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)

    with open(translated_file, "w", encoding="utf-8") as f:
        f.write(translated_summary)

    return jsonify({
        "summary": summary,
        "translated": translated_summary,
        "summary_file": "summary.txt",
        "translated_file": "translated.txt"
    })

@app.route("/download/<filename>")
def download_file(filename):
    return send_file(os.path.join(app.config["OUTPUT_FOLDER"], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
