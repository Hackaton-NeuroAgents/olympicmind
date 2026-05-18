from fastapi import FastAPI, HTTPException
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
from weather_client import get_venue_weather, get_all_venue_weather
from news_monitor import get_incident_news, get_simulated_incidents
from athlete_profiles import (
    get_all_athletes, get_athlete, add_athlete,
    get_departure_advice, get_all_departure_alerts
)
from readiness_engine import get_team_readiness

load_dotenv()

app = FastAPI(title="OlympicMind API", version="2.0.0")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Request Models ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    history: list = []

class RouteRequest(BaseModel):
    origin: str
    destination: str

class AthleteRequest(BaseModel):
    id: str
    name: str
    country: str
    sport: str
    phone: str = ""
    events: list = []
    hotel: str = ""
    hotel_coords: dict = {}


# ── Startup ────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_alert_loop(interval_secs=300))
    print("✅ OlympicMind v2.0 started — auto-alert running every 5 mins")


# ── Core Endpoints ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "OlympicMind Agent Running", "version": "2.0.0"}

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


# ── Schedule Endpoints ─────────────────────────────────────────────────────────

@app.get("/schedule")
async def schedule(hours_ahead: int = 3):
    """Upcoming Olympic events in next X hours."""
    events = get_upcoming_events(hours_ahead=hours_ahead)
    return {"upcoming_events": events, "count": len(events)}

@app.get("/departure-warning")
async def departure_warning(venue: str):
    """Should athletes leave NOW to beat post-event crowds?"""
    return get_departure_recommendation(venue_name=venue)

@app.get("/risk")
async def risk(venue: str):
    """Combined risk score 0-100 for a venue."""
    crowd_data = simulate_crowd_change()
    venue_data = next((v for v in crowd_data["venues"] if v["name"].lower() == venue.lower()), None)
    crowd_level = venue_data["crowd_level"] if venue_data else 0
    return get_risk_score(venue_name=venue, crowd_level=crowd_level)

@app.get("/risk/all")
async def risk_all():
    """Risk scores for ALL venues sorted highest to lowest."""
    crowd_data = simulate_crowd_change()
    risks = get_all_venue_risks(crowd_data)
    return {"venue_risks": risks}


# ── Alert Endpoints ────────────────────────────────────────────────────────────

@app.post("/alerts/trigger")
async def trigger_alerts():
    """Manually trigger WhatsApp alert check right now."""
    crowd_data = simulate_crowd_change()
    venue_risks = get_all_venue_risks(crowd_data)
    alerts_sent = check_and_alert(crowd_data, venue_risks)
    return {"alerts_sent": len(alerts_sent), "details": alerts_sent}

@app.get("/alerts/status")
async def alert_status():
    """Current risk status for all venues."""
    crowd_data = simulate_crowd_change()
    venue_risks = get_all_venue_risks(crowd_data)
    high_risk = [v for v in venue_risks if v["risk_level"] in ("EXTREME", "HIGH")]
    return {
        "total_venues": len(venue_risks),
        "high_risk_count": len(high_risk),
        "high_risk_venues": high_risk,
        "all_venues": venue_risks,
    }


# ── Weather Endpoints ──────────────────────────────────────────────────────────

@app.get("/weather")
async def weather(venue: str):
    """Weather conditions and travel risk for a specific venue."""
    return get_venue_weather(venue_name=venue)

@app.get("/weather/all")
async def weather_all():
    """Weather risk for ALL Olympic venues."""
    results = get_all_venue_weather()
    return {"venue_weather": results, "count": len(results)}


# ── News/Incident Endpoints ────────────────────────────────────────────────────

@app.get("/news")
async def news(demo: bool = False):
    """
    Fetch latest Olympic travel incident news.
    Use ?demo=true for simulated incidents when no API available.
    """
    if demo:
        incidents = get_simulated_incidents()
    else:
        incidents = get_incident_news()
        if not incidents:
            incidents = get_simulated_incidents()
    return {"incidents": incidents, "count": len(incidents)}


# ── Athlete Endpoints ──────────────────────────────────────────────────────────

@app.get("/athletes")
async def athletes():
    """Get all registered athletes."""
    return {"athletes": get_all_athletes()}

@app.get("/athletes/{athlete_id}")
async def athlete(athlete_id: str):
    """Get specific athlete by ID."""
    result = get_athlete(athlete_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Athlete {athlete_id} not found")
    return result

@app.post("/athletes")
async def create_athlete(req: AthleteRequest):
    """Register a new athlete."""
    try:
        result = add_athlete(req.dict())
        return {"status": "created", "athlete": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/athletes/{athlete_id}/departure")
async def athlete_departure(athlete_id: str):
    """Personalized departure advice for an athlete."""
    return get_departure_advice(athlete_id=athlete_id)

@app.get("/athletes/alerts/all")
async def athlete_alerts():
    """Departure alerts for ALL athletes with upcoming events."""
    alerts = get_all_departure_alerts()
    return {"alerts": alerts, "count": len(alerts)}


@app.get("/api/v1/teams/{team_id}/readiness")
async def team_readiness(team_id: str):
    """Aggregated readiness score for a team based on member audit logs."""
    readiness = get_team_readiness(team_id)
    if not readiness:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return readiness


# ── Combined Dashboard ─────────────────────────────────────────────────────────

@app.get("/dashboard")
async def dashboard():
    """
    Full situation dashboard — crowd + weather + news + athlete alerts.
    One endpoint to rule them all!
    """
    crowd_data = simulate_crowd_change()
    venue_risks = get_all_venue_risks(crowd_data)
    high_risk = [v for v in venue_risks if v["risk_level"] in ("EXTREME", "HIGH")]
    weather_data = get_all_venue_weather()
    high_weather_risk = [w for w in weather_data if w.get("weather_risk_level") in ("HIGH",)]
    news = get_incident_news() or get_simulated_incidents()
    athlete_alerts = get_all_departure_alerts()

    return {
        "timestamp": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": {
            "high_risk_venues": len(high_risk),
            "weather_warnings": len(high_weather_risk),
            "active_incidents": len(news),
            "athlete_alerts": len(athlete_alerts),
        },
        "high_risk_venues": high_risk,
        "weather_warnings": high_weather_risk,
        "incidents": news[:5],
        "athlete_departure_alerts": athlete_alerts,
    }
