import os
import tempfile


from flask import jsonify, current_app, Response
from openai import OpenAI
from pydub import AudioSegment
from pydub.effects import speedup
from werkzeug.datastructures import FileStorage


from website.utils import markdown_to_plain_text


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")
client = OpenAI(api_key=api_key)


def speed_up_audio(audio_file: FileStorage) -> str:
    audio = AudioSegment.from_file(audio_file, format="webm")
    sped_up_audio = speedup(audio, playback_speed=1.5)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
        sped_up_audio.export(temp_file.name, format="webm")
        temp_path = temp_file.name
    return temp_path


def transcribe(audio_file_path: str) -> str:
    try:
        current_app.logger.info("Starting transcription...")
        with open(audio_file_path, "rb") as audio:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1", file=audio, response_format="text"
            )

        transcript = transcript_response.strip()
        current_app.logger.info(f"Transcription complete: {len(transcript)} characters")

        if not transcript:
            raise ValueError("No speech detected in audio")

        return transcript

    except Exception as e:
        current_app.logger.error(f"Error during transcription: {str(e)}")
        raise


def process_with_LLM(transcript: str) -> Response:
    current_app.logger.info("Starting summarization...")
    summary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant that creates concise, actionable
                summaries of voice recordings. 
                
                Start with a ## Title that summarizes the entire transcript in one line ##
                
                Focus on:
                - Key points and main ideas
                - Action items or next steps
                - Important insights or decisions
                - Keep it brief but comprehensive
                - Use bullet points when appropriate""",
            },
            {
                "role": "user",
                "content": f"Please summarize this transcript: {transcript}",
            },
        ],
        max_tokens=300,
        temperature=0.3,
    )

    summary = summary_response.choices[0].message.content
    current_app.logger.info("Summarization complete")

    # Convert markdown to plain text for copying
    plain_text = markdown_to_plain_text(summary)

    return jsonify(
        {
            "transcript": transcript,
            "summary": summary,
            "plain_text": plain_text,
            "status": "success",
        }
    )
