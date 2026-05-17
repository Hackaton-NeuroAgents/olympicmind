"""
Auto Alert System for OlympicMind
Runs a background task every 5 minutes checking risk scores
and sends WhatsApp alerts via n8n when risk is HIGH or EXTREME.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

import requests
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

# Track already-alerted venues to avoid spam
_alerted_venues = {}
ALERT_COOLDOWN_MINS = 15  # Don't re-alert same venue within 15 mins


def _should_alert(venue_name: str, risk_level: str) -> bool:
    """Check if we should send alert or cooldown still active."""
    if risk_level not in ("EXTREME", "HIGH"):
        return False

    now = datetime.now()
    last_alert = _alerted_venues.get(venue_name)

    if last_alert is None:
        return True

    mins_since = (now - last_alert).total_seconds() / 60
    return mins_since >= ALERT_COOLDOWN_MINS


def _mark_alerted(venue_name: str):
    """Mark venue as alerted with current timestamp."""
    _alerted_venues[venue_name] = datetime.now()


def send_whatsapp_alert(incident: Dict[str, Any]) -> Dict[str, Any]:
    """Send WhatsApp alert via n8n webhook."""
    if not N8N_WEBHOOK_URL or N8N_WEBHOOK_URL == "your_n8n_webhook_url_here":
        print(f"[AUTO-ALERT] Skipping (webhook not set): {incident['message']}")
        return {"status": "skipped", "reason": "Webhook URL not set"}

    payload = {
        "venue": incident["venue"],
        "crowd_level": incident.get("level", incident.get("risk_score", 0)),
        "message": incident["message"],
        "risk_level": incident.get("risk_level", "HIGH"),
        "recommendation": incident.get("recommendation", "Use alternative route"),
        "departure_warning": incident.get("departure_warning", ""),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        logger.info(f"Alert sent for {incident['venue']}: {response.status_code}")
        return {"status": "sent", "response": response.status_code}
    except Exception as e:
        logger.error(f"Alert failed for {incident['venue']}: {e}")
        return {"status": "failed", "error": str(e)}


def check_and_alert(crowd_data: Dict[str, Any], venue_risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Check all venue risks and send alerts for HIGH/EXTREME ones.
    Returns list of alerts that were sent.
    
    Args:
        crowd_data: Live crowd data from crowd_monitor
        venue_risks: Risk scores from schedule_analyzer.get_all_venue_risks()
    
    Returns:
        List of sent alert results
    """
    sent_alerts = []

    for risk in venue_risks:
        venue_name = risk["venue"]
        risk_level = risk["risk_level"]
        risk_score = risk["risk_score"]

        if not _should_alert(venue_name, risk_level):
            continue

        # Build incident payload
        incident = {
            "venue": venue_name,
            "level": risk_score,
            "risk_level": risk_level,
            "message": f"🚨 {risk_level} RISK at {venue_name} — Score: {risk_score}/100. {risk['recommendation']}",
            "recommendation": risk["recommendation"],
            "departure_warning": risk.get("departure_warning", ""),
        }

        result = send_whatsapp_alert(incident)
        _mark_alerted(venue_name)

        sent_alerts.append({
            "venue": venue_name,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "alert_result": result,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

        logger.info(f"Auto-alert: {venue_name} ({risk_level}, {risk_score}) → {result['status']}")

    return sent_alerts


async def auto_alert_loop(interval_secs: int = 300):
    """
    Background loop that runs every 5 minutes.
    Checks risk scores and sends WhatsApp alerts automatically.
    
    Args:
        interval_secs: How often to check (default 300 = 5 mins)
    """
    from crowd_monitor import simulate_crowd_change
    from schedule_analyzer import get_all_venue_risks

    logger.info(f"Auto-alert system started — checking every {interval_secs//60} mins")

    while True:
        try:
            logger.info("Auto-alert: Running risk check...")
            crowd_data = simulate_crowd_change()
            venue_risks = get_all_venue_risks(crowd_data)

            alerts_sent = check_and_alert(crowd_data, venue_risks)

            if alerts_sent:
                logger.info(f"Auto-alert: Sent {len(alerts_sent)} alerts")
            else:
                logger.info("Auto-alert: No high-risk venues — no alerts sent")

        except Exception as e:
            logger.error(f"Auto-alert loop error: {e}")

        await asyncio.sleep(interval_secs)