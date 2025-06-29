from flask import Blueprint, request, jsonify, current_app, render_template

from .process_audio import transcribe, process_with_LLM

views = Blueprint("views", __name__)


@views.route("/")
def home():
    """Serve the main page"""
    return render_template("home.html")


@views.route("/api/process-audio", methods=["POST"])
def process_audio():
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        if audio_file.filename == "":
            return jsonify({"error": "No audio file selected"}), 400

        transcript = transcribe(audio_file)
        return process_with_LLM(transcript)

    except Exception as e:
        current_app.logger.error(f"Error processing audio: {str(e)}")
        return jsonify({"error": "Failed to process audio", "details": str(e)}), 500
