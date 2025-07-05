# 🎙️ Dicto - Voice-to-Summary Web App

## 🧠 Purpose

Build a minimal web application that allows users to:
1. Record audio in the browser
2. Upload it to a Python backend
3. Transcribe the audio using Whisper
4. Summarize the transcription using OpenAI
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

## 🛠️ Tech Stack (IMPLEMENTED)

### Backend
- **Language**: Python 3.10+ with Poetry
- **Framework**: Flask with blueprints
- **Audio Transcription**: OpenAI Whisper API
- **LLM Integration**: OpenAI GPT-4o-mini
- **CORS**: Flask-CORS for browser communication

### Frontend
- **Tech**: Vanilla HTML/CSS/JavaScript served by Flask
- **Audio Recording**: MediaRecorder API (WebM format)
- **Upload Handling**: Fetch API with FormData
- **UI/UX**: Single page with auto-processing (no playback)

---

## 🔄 Current App Flow (WORKING)

```plaintext
[1] User visits http://127.0.0.1:5005
  ↓
[2] User clicks "Start Recording" → MediaRecorder captures audio
  ↓
[3] User clicks "Stop Recording" → Auto-uploads to /api/process-audio
  ↓
[4] Flask saves temp file → OpenAI Whisper transcribes
  ↓
[5] Transcript → GPT-4o-mini summarizes with structured prompt
  ↓
[6] Summary displayed on page, ready for new recording
```

---

## ✅ COMPLETED FEATURES

### Core Functionality
- ✅ Browser audio recording with MediaRecorder API
- ✅ Audio validation (rejects < 1KB silence)
- ✅ OpenAI Whisper transcription via API
- ✅ GPT-4o-mini summarization with optimized prompts
- ✅ Auto-processing (no playback step)
- ✅ Clean Flask architecture with blueprints

### Technical Implementation  
- ✅ Poetry dependency management
- ✅ Environment variables with .env/.env.example
- ✅ Flask templates and static files properly organized
- ✅ CORS configuration for API communication
- ✅ Error handling and user feedback
- ✅ Temporary file cleanup
- ✅ Responsive design for mobile/desktop

---

## 🚧 NEXT PRIORITIES

### 1. UI/UX Polish
- Improve visual design and output presentation
- Better status indicators and loading states
- Enhanced responsive design

### 2. Note Storage & Export
**Storage Options:**
- Local browser storage for session history
- Optional user accounts for persistence

**Export Integrations:**
- **Note Apps**: Notion, Apple Notes, Obsidian, Google Keep
- **Productivity**: Todoist, Google Calendar, Slack
- **Documents**: Google Docs, Dropbox Paper, Email
- **Developer**: GitHub Issues, Linear/Jira
- **Webhook approach**: Users configure custom endpoints

### 3. Advanced Features
- Batch processing multiple recordings
- Different summary styles (bullet points, action items, etc.)
- Audio format optimization
- Local Whisper option (free but slower)

---

## 📁 Current Project Structure

```
dicto/
├── app.py                          # Flask entry point
├── pyproject.toml                  # Poetry dependencies  
├── .env/.env.example              # Environment configuration
├── website/                       # Flask application package
│   ├── __init__.py               # App factory with CORS
│   ├── views.py                  # Routes: home + /api/process-audio
│   ├── templates/home.html       # Main page template
│   └── static/css/style.css      # Styling
│   └── static/js/script.js       # Audio recording logic
├── README.md                      # Documentation
└── CLAUDE.md                     # This specification file
```

---

## 💰 Current API Costs
- **Whisper API**: ~$0.006 per minute of audio
- **GPT-4o-mini**: ~$0.0001 per summary (very cheap)

---

## 💭 Design Considerations

### Frontend Framework Thoughts
- Considering moving away from Bootstrap for more flexibility
- Interested in using pure JavaScript and CSS for custom design
- Want to avoid framework complexities that overwrite custom JavaScript
- Exploring the viability of using Flask without Bootstrap for more control