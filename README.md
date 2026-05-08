# 🧠 MindOS AI — Multimodal Mental Health Companion

> An empathetic AI companion that **listens**, **understands**, **remembers**, and **responds** with voice, text, and emotion awareness.

![Version](https://img.shields.io/badge/version-0.1.0_MVP-purple)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Next.js](https://img.shields.io/badge/Next.js-15-black)

## ✨ Features

- **🎤 Voice-First Interaction** — Speak naturally; AI responds with synthesized voice
- **🧠 Long-Term Memory** — Remembers past conversations via vector embeddings (Pinecone)
- **💚 Emotion Detection** — Analyzes text sentiment and adapts tone accordingly
- **🛡️ Crisis Detection** — Detects self-harm signals and provides hotline resources
- **📊 Mood Tracking** — Log moods with emoji scale, visualize trends
- **🌙 Premium Dark UI** — Glassmorphic design with smooth animations

## 🏗️ Architecture

```
User → [Voice/Text] → FastAPI Backend
                          ├── Whisper (STT)
                          ├── Emotion Detector
                          ├── Crisis Detector
                          ├── Pinecone Memory (RAG)
                          ├── GPT-4o (LLM)
                          └── ElevenLabs (TTS) → Audio Response
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- API keys (see below)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your API keys

# Start server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

### 3. API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| **OpenAI** | GPT-4o, Whisper STT, Embeddings | [platform.openai.com](https://platform.openai.com) |
| **ElevenLabs** *(optional)* | Text-to-Speech voice | [elevenlabs.io](https://elevenlabs.io) |
| **Pinecone** *(optional)* | Vector memory DB | [pinecone.io](https://pinecone.io) |

> 💡 The app works without optional keys — ElevenLabs falls back to text-only, Pinecone falls back to in-memory storage.

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/api/chat` | Send text message |
| `POST` | `/api/mood` | Log mood entry |
| `GET` | `/api/mood/{user_id}` | Get mood history |
| `GET` | `/api/mood/{user_id}/summary` | AI mood summary |
| `WS` | `/ws/voice/{user_id}` | Real-time voice chat |

## 🛡️ Safety & Privacy

- **Crisis Detection**: Automatic detection of self-harm language with hotline resources
- **No Diagnosis**: The AI never diagnoses conditions or prescribes medication
- **Data Deletion**: Users can delete all their data (GDPR-compliant)
- **Encryption**: All communication over HTTPS/WSS
- **Disclaimer**: Clearly labeled as a wellness tool, not a therapist replacement

## 📁 Project Structure

```
MINDOS/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings
│   │   ├── models/              # Database & schemas
│   │   ├── services/            # STT, LLM, TTS, Memory, Emotion, Crisis
│   │   ├── routers/             # API endpoints
│   │   └── prompts/             # System prompts
│   └── requirements.txt
├── frontend/
│   └── src/app/
│       ├── page.tsx             # Main page
│       ├── globals.css          # Design system
│       └── components/          # React components
└── README.md
```

## ⚠️ Disclaimer

MindOS AI is a **wellness companion tool** and is **NOT** a substitute for professional mental health care. If you or someone you know is in crisis, please contact:

- 🇮🇳 **AASRA**: 9820466726
- 🇺🇸 **988 Lifeline**: Call or text 988
- 🇬🇧 **Samaritans**: 116 123
- 🌍 **Emergency**: Your local emergency number
