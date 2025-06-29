# 🎙️ Voice-to-Summary Web App

## 🧠 Purpose

Build a minimal web application that allows users to:
1. Record audio in the browser
2. Upload it to a Python backend
3. Transcribe the audio using Whisper
4. Summarize the transcription using Claude or OpenAI
5. Return and display the summary to the user

---

## ✅ Use Cases

### 1. Thought Capture + Summarization
Users record voice memos (e.g. while walking), then get summaries that distill their main ideas or insights.

### 2. Voice Journaling or Self-Reflection
Users speak freely and get a concise summary for later review (e.g. daily mood logs, therapy-like reflection).

### 3. Solo Meeting or Brainstorm Notes
Users talk through plans or problems and get action points or summaries.

### 4. ADHD and Neurodivergent Workflow Support
Users who think better aloud can use the app to make their speech usable as written content or action steps.

### 5. Voice Drafting for Writers or Creators
Users generate early drafts for emails, blogs, or scripts through voice and get a clean summary or outline.

---

## 🛠️ Tech Stack

### Backend
- **Language**: Python
- **Framework**: Flask
- **Audio Transcription**: Whisper (local or API)
- **LLM Integration**: Claude API or OpenAI API
- **Deployment**: Docker + Gunicorn + Nginx (optional)
- **HTTPS**: Certbot (for browser mic support)

### Frontend
- **Tech**: HTML, CSS, JavaScript (vanilla)
- **Audio Recording**: MediaRecorder API
- **Upload Handling**: Fetch API
- **UI/UX**: Simple input, status, and output areas

---

## 🔄 App Flow

```plaintext
[1] User clicks "Record"
  ↓
[2] Browser records audio via MediaRecorder API
  ↓
[3] User clicks "Send" → audio is POSTed to Flask backend
  ↓
[4] Flask saves audio file, transcribes with Whisper
  ↓
[5] Transcript is sent to LLM (Claude/OpenAI) with summarization prompt
  ↓
[6] LLM returns summary → returned to frontend
  ↓
[7] Summary is displayed on the page
