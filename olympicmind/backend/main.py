from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import chat_with_agent
from crowd_monitor import get_crowd_data, simulate_crowd_change, check_for_incidents
from routes import get_best_route
from n8n_trigger import send_whatsapp_alert

app = FastAPI()

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
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
    
    # Auto send WhatsApp if incidents found
    for incident in incidents:
        send_whatsapp_alert(incident)
    
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
