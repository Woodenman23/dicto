import os
import tempfile
import time
from typing import Dict, Any
from flask import Blueprint, request, jsonify, current_app, render_template, Response
from openai import OpenAI

from .process_audio import transcribe, process_with_LLM, speed_up_audio
from .pdf_generator import create_pdf_response

views = Blueprint("views", __name__)


@views.route("/")
def home() -> str:
    """Serve the main page"""
    return render_template("home.html")


@views.route("/health")
def health() -> Response:
    """Health check endpoint for monitoring"""
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time.time(),
        "dependencies": {}
    }
    
    # Check OpenAI API connectivity
    try:
        client = OpenAI()
        client.models.list()
        health_status["dependencies"]["openai"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["openai"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return jsonify(health_status)


@views.route("/metrics-dashboard")
def metrics_dashboard() -> str:
    """Simple HTML view of key metrics"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dicto Metrics</title>
        <style>
            body { font-family: monospace; margin: 20px; }
            pre { background: #f5f5f5; padding: 10px; border-radius: 5px; }
            .status-healthy { color: green; }
            .status-degraded { color: orange; }
            .status-unhealthy { color: red; }
        </style>
    </head>
    <body>
        <h1>Dicto Monitoring Dashboard</h1>
        <p><a href="/health">Health Check JSON</a> | <a href="/metrics">Raw Metrics</a></p>
        <h2>Health Status</h2>
        <pre id="status">Loading...</pre>
        <script>
            function updateStatus() {
                fetch('/health')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').textContent = JSON.stringify(data, null, 2);
                        document.getElementById('status').className = 'status-' + data.status;
                    })
                    .catch(e => {
                        document.getElementById('status').textContent = 'Error: ' + e.message;
                        document.getElementById('status').className = 'status-unhealthy';
                    });
            }
            updateStatus();
            setInterval(updateStatus, 5000);
        </script>
    </body>
    </html>
    """


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
