import os
import tempfile
from flask import Blueprint, request, jsonify, current_app, render_template
from openai import OpenAI

views = Blueprint("views", __name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@views.route("/")
def home():
    """Serve the main page"""
    return render_template("home.html")

@views.route("/api/process-audio", methods=["POST"])
def process_audio():
    """Process uploaded audio: transcribe with Whisper, summarize with GPT"""
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Step 1: Transcribe audio with Whisper
            current_app.logger.info("Starting transcription...")
            with open(temp_path, 'rb') as audio:
                transcript_response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )
            
            transcript = transcript_response.strip()
            current_app.logger.info(f"Transcription complete: {len(transcript)} characters")
            
            if not transcript:
                return jsonify({'error': 'No speech detected in audio'}), 400
            
            # Step 2: Summarize with GPT
            current_app.logger.info("Starting summarization...")
            summary_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a helpful assistant that creates concise, actionable
                        summaries of voice recordings. 
                        
                        Focus on:
                        - Key points and main ideas
                        - Action items or next steps
                        - Important insights or decisions
                        - Keep it brief but comprehensive
                        - Use bullet points when appropriate"""
                    },
                    {
                        "role": "user", 
                        "content": f"Please summarize this transcript: {transcript}"
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            summary = summary_response.choices[0].message.content
            current_app.logger.info("Summarization complete")
            
            return jsonify({
                'transcript': transcript,
                'summary': summary,
                'status': 'success'
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        current_app.logger.error(f"Error processing audio: {str(e)}")
        return jsonify({
            'error': 'Failed to process audio',
            'details': str(e)
        }), 500