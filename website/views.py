import os
import tempfile
from flask import Blueprint, request, jsonify, current_app, render_template, Response

from .process_audio import transcribe, process_with_LLM, speed_up_audio
from .pdf_generator import create_pdf_response

views = Blueprint("views", __name__)


@views.route("/")
def home() -> str:
    """Serve the main page"""
    return render_template("home.html")


@views.route("/api/process-audio", methods=["POST"])
def process_audio() -> Response:
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        
        if audio_file.filename == "":
            return jsonify({"error": "No audio file selected"}), 400
            
        temp_path = speed_up_audio(audio_file) # creates temp file for sped up audio
        
        try:
            transcript = transcribe(temp_path)
            return process_with_LLM(transcript)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        current_app.logger.error(f"Error processing audio: {str(e)}")
        return jsonify({"error": "Failed to process audio", "details": str(e)}), 500
    
@views.route("/api/export-pdf", methods=["POST"])
def export_pdf() -> Response:
    """Export the current summary as a PDF"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        transcript = data.get("transcript", "")
        summary = data.get("summary", "")
        
        if not transcript and not summary:
            return jsonify({"error": "No content to export"}), 400
        
        # Create and return the PDF response
        return create_pdf_response(transcript, summary)
        
    except Exception as e:
        current_app.logger.error(f"Error creating PDF: {str(e)}")
        return jsonify({"error": "Failed to create PDF", "details": str(e)}), 500
