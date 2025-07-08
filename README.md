# 🎙️ Dicto - Your Voice Summarised.

A minimal web application that records audio in the browser, transcribes it using OpenAI's Whisper API, and generates summaries using GPT.

## 🧠 Purpose

Record your thoughts and get instant written summaries. Perfect for:
- **Thought Capture**: Voice memos while walking → distilled insights
- **Voice Journaling**: Daily reflections → concise summaries  
- **Meeting Notes**: Solo brainstorms → action points
- **ADHD Support**: Think-aloud workflow → usable written content
- **Voice Drafting**: Rough ideas → clean outlines

## 🛠️ Tech Stack

**Backend**:
- Python 3.10+ with Poetry
- Flask web framework
- OpenAI API (Whisper + GPT-4o-mini)
- Flask-CORS for frontend communication

**Frontend**:
- Vanilla HTML/CSS/JavaScript
- MediaRecorder API for browser audio recording
- Fetch API for server communication

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install Python dependencies
poetry install

# Copy environment template
cp .env.example .env
```

### 2. Configure API Keys
Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
SECRET_KEY=your-secret-key-here
```

### 3. Run the Application
```bash
# Start the Flask server
poetry run python app.py
```

### 4. Use the App
1. Open http://127.0.0.1:5005 in your browser
2. Click "Start Recording" and speak your thoughts
3. Click "Stop Recording" - it will auto-process
4. View your transcription and AI-generated summary

## 🔄 How It Works

```
[1] User clicks "Record" → Browser captures audio via MediaRecorder API
[2] User clicks "Stop" → Audio auto-uploads to Flask backend  
[3] Flask saves audio temporarily, sends to OpenAI Whisper API
[4] Transcript gets sent to GPT-4o-mini with summarization prompt
[5] Summary returns to frontend and displays on page
```

## 📁 Project Structure

```
dicto/
├── app.py                          # Flask entry point
├── pyproject.toml                  # Poetry dependencies
├── .env                           # Environment variables (not in git)
├── .env.example                   # Environment template
├── website/                       # Flask application package
│   ├── __init__.py               # App factory with CORS setup
│   ├── views.py                  # Routes: home page + API endpoint
│   ├── templates/
│   │   ├── home.html            # Main page template
|   |   └── layout.html          # Template for common elements across all pages
│   └── static/
│       ├── css/
│       │   └── style.css        # Application styling
│       └── js/
│           └── script.js        # Audio recording logic
└── CLAUDE.md                     # Project specification
```

## ⚙️ Key Features

- **Browser Audio Recording**: Uses MediaRecorder API with optimized settings
- **Validation**: Rejects silent/empty recordings (< 1KB)
- **Auto-Processing**: No playback step - straight to transcription
- **Error Handling**: Graceful failures with user feedback
- **Responsive Design**: Works on desktop and mobile
- **Clean Architecture**: Flask blueprints + proper static file serving

## 💰 API Costs

- **Whisper API**: ~$0.006 per minute of audio
- **GPT-4o-mini**: ~$0.0001 per summary (very cheap)

## 🔒 Security Notes

- API keys stored in `.env` (gitignored)
- 16MB max upload limit
- Temporary files cleaned up after processing
- CORS enabled for browser communication

## 🚧 Future Enhancements

- Local Whisper option (free but slower)
- Claude API integration option
- Audio format optimization
- User accounts and history
- Batch processing
- Export options (PDF, markdown)

## 🚀 Kubernetes Deployment (In Development)

> **⚠️ Development Feature**: The Kubernetes deployment is currently in development and intended for local testing with minikube.

### Prerequisites
- Docker
- minikube
- kubectl

### Quick Deploy to Local Kubernetes
```bash
# Start minikube
minikube start

# Deploy using the provided script
./deploy_k8s.sh
```

The deployment script will:
1. Build the Docker image locally
2. Apply Kubernetes secrets (API keys)
3. Deploy the application to your local cluster
4. Expose the service and start port-forwarding to `http://localhost:9000`

### Manual Kubernetes Deployment
```bash
# Build and load image into minikube
eval $(minikube docker-env)
docker build -t dicto:latest .

# Apply Kubernetes manifests
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment-local.yaml
kubectl apply -f k8s/service.yaml

# Port forward to access the app
kubectl port-forward service/dicto-service 9000:80
```

### Configuration Files
- `k8s/deployment-local.yaml` - Local development deployment
- `k8s/deployment-prod.yaml` - Production deployment template
- `k8s/service.yaml` - Service definition
- `k8s/secret.yaml` - Secrets for API keys (create from `secret.example.yaml`)

### Setting Up Secrets
```bash
# Copy the example secret file
cp k8s/secret.example.yaml k8s/secret.yaml

# Edit the secret file and add your base64-encoded OpenAI API key
# To encode: echo -n "your-api-key" | base64
```

## 📝 Development

Built following Flask best practices:
- App factory pattern
- Blueprint organization  
- Environment-based configuration
- Proper static file handling
- Poetry for dependency management