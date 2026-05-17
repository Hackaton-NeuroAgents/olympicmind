from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from agent import chat_with_agent
from crowd_monitor import get_crowd_data, simulate_crowd_change, check_for_incidents
from routes import get_best_route
from schedule_analyzer import get_upcoming_events, get_departure_recommendation, get_risk_score, get_all_venue_risks

load_dotenv()

app = FastAPI()

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

class RouteRequest(BaseModel):
    origin: str
    destination: str

# Chat with AI Agent
@app.post("/chat")
async def chat(req: ChatRequest):
    crowd_data = get_crowd_data()
    response = chat_with_agent(req.message, crowd_data, req.history)
    return {"response": response}

# Get crowd levels
@app.get("/crowd")
async def crowd():
    data = simulate_crowd_change()
    incidents = check_for_incidents(data)
    return {"crowd_data": data, "incidents": incidents}

# Get route recommendation
@app.post("/route")
async def route(req: RouteRequest):
    crowd_data = get_crowd_data()
    result = get_best_route(req.origin, req.destination, crowd_data)
    return result

# Health check
@app.get("/")
async def root():
    return {"status": "OlympicMind Agent Running"}

# ── NEW: Upcoming Olympic Events ──────────────────────────────────────────────
@app.get("/schedule")
async def schedule(hours_ahead: int = 3):
    """Returns Olympic events happening in the next X hours."""
    events = get_upcoming_events(hours_ahead=hours_ahead)
    return {"upcoming_events": events, "count": len(events)}

# ── NEW: Departure Warning for a Venue ───────────────────────────────────────
@app.get("/departure-warning")
async def departure_warning(venue: str):
    """
    Check if athletes should leave NOW to beat post-event crowds.
    Example: /departure-warning?venue=Forum Assago
    """
    warning = get_departure_recommendation(venue_name=venue)
    return warning

# ── NEW: Risk Score for a Venue ───────────────────────────────────────────────
@app.get("/risk")
async def risk(venue: str):
    """
    Combined risk score (0-100) using live crowd + event schedule.
    Example: /risk?venue=Forum Assago
    """
    crowd_data = simulate_crowd_change()
    venue_data = next(
        (v for v in crowd_data["venues"] if v["name"].lower() == venue.lower()), None
    )
    crowd_level = venue_data["crowd_level"] if venue_data else 0
    result = get_risk_score(venue_name=venue, crowd_level=crowd_level)
    return result

# ── NEW: All Venues Risk Dashboard ───────────────────────────────────────────
@app.get("/risk/all")
async def risk_all():
    """Risk scores for ALL venues sorted highest to lowest risk."""
    crowd_data = simulate_crowd_change()
    risks = get_all_venue_risks(crowd_data)
    return {"venue_risks": risks}