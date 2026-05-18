🏅 OlympicMind — Autonomous AI Navigation Agent for Milan 2026 Winter Olympics

> AI Agent Olympics Hackathon 2026 | Track: Agentic Workflows + Enterprise Utility  
> Deployed on **Vultr** | Powered by **Gemini 2.5 Flash** + **TomTom APIs**

🧠 What is OlympicMind?

OlympicMind is an autonomous AI agent designed to help teams, athletes, and officials navigate Milan during the **2026 Winter Olympics**. It monitors real-time crowd levels at 14 Olympic venues, analyzes live traffic data, and provides intelligent route recommendations — all through a conversational AI interface powered by Google Gemini.

The Problem it Solves:  
During major sporting events like the Olympics, cities face extreme crowd surges, road congestion, and safety risks near venues. Traditional navigation apps don't account for event schedules, real-time crowd density, or multi-venue coordination. OlympicMind bridges that gap.

 ✨ Key Features

- 🤖 **AI Chat Agent** — Conversational interface powered by Gemini 2.5 Flash with full context awareness (crowd data + event schedule + history)
- 🗺️ **Smart Route Planning** — Real-time route recommendations via TomTom Routing API with traffic-aware alternative suggestions
- 👥 **Live Crowd Monitoring** — Tracks crowd levels at 14 Olympic venues using TomTom Traffic Flow API
- ⚠️ **Incident Detection** — Auto-detects road closures, congestion, and crowd surges; flags BLOCKED/CONGESTED routes
- 📅 **Schedule-Aware Risk Scoring** — Combines live crowd data with Olympic event schedule to calculate a 0–100 Risk Score per venue
- 🚨 **WhatsApp Alerts** — Sends automated alerts via N8N webhook for critical incidents
- 🖥️ **React Dashboard** — Live map view, alert panel, route planner, and chat interface in one frontend

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│  Dashboard | MapView | ChatInterface | RoutePlanner  │
│                AlertPanel                            │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Backend (Python)                │
│                                                      │
│  /chat    →  agent.py (Gemini 2.5 Flash)            │
│  /crowd   →  crowd_monitor.py                        │
│  /route   →  routes.py                               │
└────────┬────────────────────────┬───────────────────┘
         │                        │
┌────────▼────────┐    ┌──────────▼────────────┐
│  Google Gemini  │    │    TomTom APIs         │
│  2.5 Flash API  │    │  Traffic Flow +        │
│  (AI Reasoning) │    │  Route Calculation     │
└─────────────────┘    └───────────────────────┘
         │
┌────────▼────────────────────┐
│   schedule_analyzer.py      │
│   Olympic Event Schedule    │
│   Risk Score Calculator     │
└─────────────────────────────┘
         │
┌────────▼────────────────────┐
│   n8n_trigger.py            │
│   WhatsApp Alert Webhooks   │
└─────────────────────────────┘




## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Model | Google Gemini 2.5 Flash |
| Backend | Python, FastAPI |
| Frontend | React (Vite), JSX |
| Traffic Data | TomTom Traffic Flow API |
| Routing | TomTom Routing API |
| Automation | N8N (WhatsApp webhooks) |
| Deployment | Vultr VPS |
| Environment | python-dotenv |

---

## 📁 Project Structure

```
olympicmind/
├── backend/
│   ├── main.py              # FastAPI app, API endpoints
│   ├── agent.py             # Gemini AI agent logic
│   ├── crowd_monitor.py     # Real-time crowd + traffic monitoring
│   ├── routes.py            # Smart route recommendation engine
│   ├── schedule_analyzer.py # Olympic event schedule + risk scoring
│   ├── tomtom_client.py     # TomTom API client (traffic + routing)
│   ├── n8n_trigger.py       # WhatsApp alert via N8N webhook
│   ├── requirements.txt     # Python dependencies
│   └── data/
│       └── crowd_data.json  # Venue data (14 Olympic venues)
└── frontend/
    └── src/
        ├── App.jsx
        ├── components/
        │   ├── Dashboard.jsx
        │   ├── MapView.jsx
        │   ├── ChatInterface.jsx
        │   ├── RoutePlanner.jsx
        │   └── AlertPanel.jsx
        └── main.jsx




## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Gemini API Key (Google AI Studio)
- TomTom API Key

### Backend Setup

```bash
cd olympicmind/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
TOMTOM_API_KEY=your_tomtom_api_key_here
CORS_ORIGINS=http://localhost:5173
N8N_WEBHOOK_URL=your_n8n_webhook_url_here   # optional
```

Run the backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd olympicmind/frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 🌐 Live Deployment

- **Backend API:** `http://95.179.191.1:8000`
- **API Docs (Swagger):** `http://95.179.191.1:8000/docs`
- Deployed on **Vultr VPS** (Ubuntu)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/chat` | Chat with AI agent (message + history) |
| `GET` | `/crowd` | Live crowd levels + incidents at all venues |
| `POST` | `/route` | Get smart route recommendation between venues |

### Example: Chat Request
```json
POST /chat
{
  "message": "How is crowd situation at San Siro?",
  "history": []
}
```

### Example: Route Request
```json
POST /route
{
  "origin": "Milano San Siro Stadium",
  "destination": "Santagiulia Ice Arena"
}
```

---

## 🏟️ Supported Olympic Venues (14 Venues)

| Venue | City | Capacity |
|-------|------|----------|
| Milano San Siro Stadium | Milan | 80,000 |
| Santagiulia Ice Arena | Milan | 15,000 |
| Rho Ice Hockey Arena | Rho | 10,000 |
| Milano Speed Skating Stadium | Milan | 8,000 |
| Milano Ice Skating Arena | Milan | 12,000 |
| Tofane Skiing Centre | Cortina | 5,000 |
| Cortina Sliding Center | Cortina | 3,000 |
| Cortina Curling Stadium | Cortina | 2,000 |
| Stelvio Ski Centre (Bormio) | Bormio | 8,000 |
| Livigno Snow Park | Livigno | 10,000 |
| Predazzo Ski Jumping | Predazzo | 6,000 |
| Tesero Cross-Country | Tesero | 8,000 |
| Antholz Biathlon Arena | Anterselva | 15,000 |
| Verona Olympic Arena | Verona | 15,000 |

---

## 🤖 How the AI Agent Works

1. **User sends a query** (e.g., "Best route from San Siro to Santagiulia right now?")
2. **Backend fetches live crowd data** from TomTom Traffic Flow API for all venues
3. **Risk Score is calculated** — combining live traffic congestion % + event schedule urgency weight
4. **Gemini 2.5 Flash** receives: user query + full crowd context + conversation history
5. **Agent responds** with: current crowd situation, best route, any warnings, estimated travel time
6. **If incidents detected** (road closure / heavy congestion), N8N webhook fires a WhatsApp alert

---

## 📊 Risk Score Formula

```
Risk Score = (crowd_level × 0.6) + event_urgency_weight

Event Urgency Weights:
  CRITICAL (event ending in <30 mins) → +40
  HIGH     (event ending in 30-60 mins) → +25
  MEDIUM   (event starting in <45 mins) → +15
  LOW      (no events) → 0

Risk Levels:
  80-100 → EXTREME 🚨
  60-79  → HIGH ⚠️
  40-59  → MODERATE ⚡
  20-39  → LOW ✅
  0-19   → CLEAR ✅
```

---

## 👥 Team

**NeuroAgents** — AI Agent Olympics Hackathon 2026  
Built during **Milan AI Week 2026** (May 13–20)

---

## 📄 License

MIT License — open source and free to use.
