# OlympicMind Agent

An autonomous AI agent that helps teams navigate Milan during the 2026 Winter Olympics — detecting crowds, suggesting smart routes, and sending real-time WhatsApp alerts.

## Architecture

- **Frontend**: React + Vite + TailwindCSS + Leaflet + Lucide Icons
- **Backend**: FastAPI + Gemini API + N8N Trigger

## Setup & Running

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
3. Set your `.env` keys for Gemini and N8N:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   N8N_WEBHOOK_URL=your_webhook_url
   ```
4. Run the API:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

Open `http://localhost:5173` to view the OlympicMind dashboard.
