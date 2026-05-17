from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
from dotenv import load_dotenv
from agent import chat_with_agent
from crowd_monitor import get_crowd_data, simulate_crowd_change, check_for_incidents
from routes import get_best_route
from schedule_analyzer import get_upcoming_events, get_departure_recommendation, get_risk_score, get_all_venue_risks
from auto_alert import check_and_alert, auto_alert_loop

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


# ── Startup: Launch background alert loop ─────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_alert_loop(interval_secs=300))
    print("✅ Auto-alert background task started (every 5 mins)")


# ── Existing Endpoints ─────────────────────────────────────────────────────────

@app.post("/chat")
async def chat(req: ChatRequest):
    crowd_data = get_crowd_data()
    response = chat_with_agent(req.message, crowd_data, req.history)
    return {"response": response}

@app.get("/crowd")
async def crowd():
    data = simulate_crowd_change()
    incidents = check_for_incidents(data)
    return {"crowd_data": data, "incidents": incidents}

@app.post("/route")
async def route(req: RouteRequest):
    crowd_data = get_crowd_data()
    result = get_best_route(req.origin, req.destination, crowd_data)
    return result

@app.get("/")
async def root():
    return {"status": "OlympicMind Agent Running"}


# ── Schedule Endpoints ────────────────────────────────────────────────────────

@app.get("/schedule")
async def schedule(hours_ahead: int = 3):
    events = get_upcoming_events(hours_ahead=hours_ahead)
    return {"upcoming_events": events, "count": len(events)}

@app.get("/departure-warning")
async def departure_warning(venue: str):
    warning = get_departure_recommendation(venue_name=venue)
    return warning

@app.get("/risk")
async def risk(venue: str):
    crowd_data = simulate_crowd_change()
    venue_data = next(
        (v for v in crowd_data["venues"] if v["name"].lower() == venue.lower()), None
    )
    crowd_level = venue_data["crowd_level"] if venue_data else 0
    result = get_risk_score(venue_name=venue, crowd_level=crowd_level)
    return result

@app.get("/risk/all")
async def risk_all():
    crowd_data = simulate_crowd_change()
    risks = get_all_venue_risks(crowd_data)
    return {"venue_risks": risks}


# ── Alert Endpoints ───────────────────────────────────────────────────────────

@app.post("/alerts/trigger")
async def trigger_alerts():
    """Manually trigger alert check right now."""
    crowd_data = simulate_crowd_change()
    venue_risks = get_all_venue_risks(crowd_data)
    alerts_sent = check_and_alert(crowd_data, venue_risks)
    return {
        "alerts_sent": len(alerts_sent),
        "details": alerts_sent,
    }

@app.get("/alerts/status")
async def alert_status():
    """Show current risk status for all venues."""
    crowd_data = simulate_crowd_change()
    venue_risks = get_all_venue_risks(crowd_data)
    high_risk = [v for v in venue_risks if v["risk_level"] in ("EXTREME", "HIGH")]
    return {
        "total_venues": len(venue_risks),
        "high_risk_count": len(high_risk),
        "high_risk_venues": high_risk,
        "all_venues": venue_risks,
    }