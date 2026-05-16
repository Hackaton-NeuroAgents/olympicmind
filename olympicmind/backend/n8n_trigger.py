import requests
import os
from dotenv import load_dotenv

load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

def send_whatsapp_alert(incident):
    if not N8N_WEBHOOK_URL or N8N_WEBHOOK_URL == "your_n8n_webhook_url_here":
        print(f"Skipping N8N alert (webhook URL not configured): {incident['message']}")
        return {"status": "skipped", "reason": "Webhook URL not set"}

    payload = {
        "venue": incident["venue"],
        "crowd_level": incident["level"],
        "message": incident["message"],
        "recommendation": "Use alternative route via Navigli",
        "timestamp": "2026-05-19 14:30"
    }
    
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        return {"status": "sent", "response": response.status_code}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
