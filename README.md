# CodeAlpha FAQ Chatbot — Production SaaS Application

> **TASK 2: Chatbot for FAQs** | CodeAlpha Internship  
> **Registration ID:** `Akshay Saxena , 25BCE10224`

A production-grade, GPU-accelerated FAQ chatbot with a hybrid NLP search engine, Liquid Glass UI, admin analytics dashboard, and full Docker/Cloud Run deployment infrastructure.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React 18 + Vite)               │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Sidebar  │  │ Chat Console │  │ Telemetry Panel    │    │
│  │ Command  │  │ Conversational│  │ Live Analytics     │    │
│  │ Center   │  │ Nexus        │  │ Confidence Gauge   │    │
│  └──────────┘  └──────────────┘  └────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (Axios)
┌────────────────────────▼────────────────────────────────────┐
│                   Backend (FastAPI + Python)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Hybrid Search Engine                     │   │
│  │  ┌──────────────┐    ┌───────────────────────────┐   │   │
│  │  │ TF-IDF       │    │ Sentence Transformers     │   │   │
│  │  │ Lexical (0.3)│    │ Semantic (0.7) [CUDA GPU] │   │   │
│  │  └──────┬───────┘    └──────────┬────────────────┘   │   │
│  │         └──────────┬────────────┘                    │   │
│  │              Score Fusion                             │   │
│  │     Final = 0.7×Semantic + 0.3×Lexical               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐               │
│  │ SpaCy   │  │ SQLite   │  │ Analytics   │               │
│  │ Pipeline│  │ 3NF DB   │  │ Engine      │               │
│  └─────────┘  └──────────┘  └─────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ & npm
- NVIDIA GPU with CUDA 12.1+ (optional, falls back to CPU)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# Install dependencies (CUDA-enabled PyTorch)
pip install -r requirements.txt

# Download SpaCy model
python -m spacy download en_core_web_sm

# Seed the database (200 FAQs)
python -m backend.seed_db

# Start the API server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Docker (Alternative)

```bash
docker-compose up --build
```

Access:
- **Frontend:** http://localhost:3000 (Docker) or http://localhost:5173 (dev)
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🧠 NLP Engine

| Component | Technology | Purpose |
|---|---|---|
| Preprocessing | SpaCy `en_core_web_sm` | Tokenization, lemmatization, stopword removal |
| Lexical Search | scikit-learn TF-IDF | Keyword overlap via cosine similarity |
| Semantic Search | `all-MiniLM-L6-v2` | Dense embeddings for intent matching |
| GPU Acceleration | PyTorch CUDA | RTX 4050 tensor routing |
| Score Fusion | Custom algorithm | `0.7 × Semantic + 0.3 × Lexical` |
| Fallback | Threshold < 0.45 | Top 3 suggestions + conversational response |

---

## 📊 Database Schema (3NF)

| Table | Purpose |
|---|---|
| `categories` | FAQ topic categories (8 total) |
| `faqs` | 200 FAQ entries with embeddings |
| `chat_history` | Conversation logs with scoring |
| `user_feedback` | Boolean helpfulness tracking |
| `saved_bookmarks` | User-saved FAQ references |
| `system_analytics` | Event logging for dashboard |

---

## 🎨 Frontend Features

- **Liquid Glass UI** — Frosted glass panels with backdrop-blur and mesh gradients
- **Dark/Light Mode** — OS preference detection with manual toggle
- **3-Column Layout** — Sidebar + Chat Console + Telemetry Panel
- **Typing Effect** — Human-cadence character streaming
- **Voice I/O** — Web Speech API dictation + SpeechSynthesis
- **Live Typeahead** — Autocomplete suggestions at ≥3 characters
- **Quick Suggestion Chips** — Context-aware follow-up prompts
- **Admin Dashboard** — Recharts analytics + CRUD data grid
- **Framer Motion** — Spring-physics animations throughout

---

## 📁 Project Structure

```
CodeAlpha_Chatbot for FAQs/
├── backend/
│   ├── config.py               # CUDA config & settings
│   ├── database.py             # SQLite schema & queries
│   ├── main.py                 # FastAPI entry point
│   ├── models.py               # Pydantic validation
│   ├── seed_db.py              # 200 FAQ generator
│   ├── nlp/
│   │   ├── pipeline.py         # SpaCy preprocessing
│   │   ├── embeddings.py       # Sentence Transformer GPU
│   │   └── search_engine.py    # Hybrid fusion engine
│   └── routes/
│       ├── chat.py             # Chat endpoints
│       ├── admin.py            # CRUD endpoints
│       ├── analytics.py        # Dashboard data
│       └── bookmarks.py        # Bookmarks & feedback
├── frontend/
│   └── src/
│       ├── api/client.ts       # Typed API client
│       ├── hooks/index.ts      # Custom React hooks
│       ├── components/layout/  # Sidebar, Chat, Telemetry
│       └── pages/              # ChatPage, AdminPage
├── docker-compose.yml
├── cloudbuild.yaml             # Google Cloud Run deploy
└── README.md
```

---

## ☁️ Cloud Deployment

### Google Cloud Run

```bash
# Submit build
gcloud builds submit --config=cloudbuild.yaml

# Manual deploy
gcloud run deploy faq-chatbot-backend \
  --source=./backend \
  --region=us-central1 \
  --port=8000 \
  --allow-unauthenticated
```

---

## 📜 License & Attribution

**CodeAlpha Internship** — Task 2: Chatbot for FAQs  
**Registration ID:** `Akshay Saxena , 25BCE10224 `  
**Tech Stack:** FastAPI · React 18 · TypeScript · SQLite · SpaCy · Sentence Transformers · PyTorch CUDA · Tailwind CSS · Framer Motion · Recharts

---

<p align="center">
  Built with ❤️ by <strong>Akshay Saxena</strong> for CodeAlpha
</p>
