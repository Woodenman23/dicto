import os
import tempfile
import re

from flask import jsonify, current_app
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def transcribe(audio_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
        audio_file.save(temp_file.name)
        temp_path = temp_file.name
    
    try:
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
        
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        return transcript

def markdown_to_plain_text(markdown_text):
    """Convert markdown to plain text suitable for email/notepad"""
    text = markdown_text
    
    # Convert headers to plain text with extra spacing
    text = re.sub(r'^### (.+)$', r'\1\n', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'\1\n', text, flags=re.MULTILINE) 
    text = re.sub(r'^# (.+)$', r'\1\n', text, flags=re.MULTILINE)
    
    # Remove bold/italic formatting but keep the text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Convert bullet points to proper bullets
    text = re.sub(r'^[-*+] (.+)$', r'• \1', text, flags=re.MULTILINE)
    
    # Convert numbered lists to bullets
    text = re.sub(r'^\d+\. (.+)$', r'• \1', text, flags=re.MULTILINE)
    
    # Handle links - keep the text, remove the URL
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remove inline code formatting
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Handle blockquotes
    text = re.sub(r'^> (.+)$', r'> \1', text, flags=re.MULTILINE)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text

def process_with_LLM(transcript: str):
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
    
    # Convert markdown to plain text for copying
    plain_text = markdown_to_plain_text(summary)
    
    return jsonify({
        'transcript': transcript,
        'summary': summary,
        'plain_text': plain_text,
        'status': 'success'
    })