"""
Olympic News & Media Monitor for OlympicMind
Monitors news feeds for incidents that could affect athlete travel.
Uses RSS feeds — no API key needed!
"""

import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)

# Free RSS news sources about Milan/Italy traffic and Olympics
NEWS_FEEDS = [
    {
        "name": "ANSA Italy",
        "url": "https://www.ansa.it/sito/notizie/sport/rss.xml",
        "language": "it",
    },
    {
        "name": "Olympic News",
        "url": "https://olympics.com/en/news/rss.xml",
        "language": "en",
    },
]

# Keywords that indicate travel disruption
INCIDENT_KEYWORDS = [
    "road closed", "strada chiusa", "blocked", "bloccato",
    "accident", "incidente", "crash",
    "protest", "manifestazione", "sciopero", "strike",
    "flood", "alluvione", "snow", "neve", "ice", "ghiaccio",
    "delay", "ritardo", "cancelled", "cancellato",
    "traffic", "traffico", "congestion", "ingorgo",
    "milan", "milano", "cortina", "bormio", "livigno",
    "olympic", "olimpico", "olimpiadi",
    "emergency", "emergenza", "alert", "allerta",
]

VENUE_KEYWORDS = [
    "san siro", "forum assago", "cortina", "bormio",
    "livigno", "predazzo", "anterselva", "antholz",
    "verona", "rho", "milan", "milano",
]


def _fetch_rss(url: str, timeout: int = 8) -> List[Dict[str, Any]]:
    """Fetch and parse RSS feed."""
    try:
        response = requests.get(url, timeout=timeout, headers={
            "User-Agent": "OlympicMind/1.0 (Olympic Safety Monitor)"
        })
        response.raise_for_status()
        root = ET.fromstring(response.content)
        items = []
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            description = item.findtext("description", "").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "").strip()
            items.append({
                "title": title,
                "description": description,
                "link": link,
                "pub_date": pub_date,
            })
        return items
    except Exception as e:
        logger.warning(f"RSS fetch failed for {url}: {e}")
        return []


def _is_relevant(title: str, description: str) -> bool:
    """Check if news item is relevant to Olympic travel."""
    text = (title + " " + description).lower()
    has_incident = any(kw in text for kw in INCIDENT_KEYWORDS)
    has_venue = any(kw in text for kw in VENUE_KEYWORDS)
    return has_incident or has_venue


def _extract_affected_venues(title: str, description: str) -> List[str]:
    """Extract which venues might be affected."""
    text = (title + " " + description).lower()
    affected = []
    venue_map = {
        "san siro": "Milano San Siro Stadium",
        "forum assago": "Rho Ice Hockey Arena",
        "cortina": "Cortina Sliding Center",
        "bormio": "Stelvio Ski Centre (Bormio)",
        "livigno": "Livigno Snow Park",
        "predazzo": "Predazzo Ski Jumping",
        "anterselva": "Antholz Biathlon Arena",
        "antholz": "Antholz Biathlon Arena",
        "verona": "Verona Olympic Arena",
        "rho": "Rho Ice Hockey Arena",
    }
    for keyword, venue in venue_map.items():
        if keyword in text and venue not in affected:
            affected.append(venue)
    return affected


def _severity(title: str, description: str) -> str:
    """Determine incident severity."""
    text = (title + " " + description).lower()
    if any(w in text for w in ["closed", "chiusa", "blocked", "bloccato", "emergency", "emergenza"]):
        return "HIGH"
    elif any(w in text for w in ["accident", "incidente", "protest", "strike", "sciopero"]):
        return "MEDIUM"
    return "LOW"


def get_incident_news() -> List[Dict[str, Any]]:
    """
    Fetch and filter news for Olympic travel incidents.
    Returns list of relevant news items with severity and affected venues.
    """
    all_items = []

    for feed in NEWS_FEEDS:
        items = _fetch_rss(feed["url"])
        for item in items:
            if _is_relevant(item["title"], item["description"]):
                affected = _extract_affected_venues(item["title"], item["description"])
                severity = _severity(item["title"], item["description"])
                all_items.append({
                    "source": feed["name"],
                    "title": item["title"],
                    "description": item["description"][:300],
                    "link": item["link"],
                    "pub_date": item["pub_date"],
                    "severity": severity,
                    "affected_venues": affected,
                    "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

    # Sort by severity
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    all_items.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return all_items


def get_simulated_incidents() -> List[Dict[str, Any]]:
    """
    Returns simulated incidents for demo/testing when news feeds are unavailable.
    """
    return [
        {
            "source": "Demo",
            "title": "Heavy snowfall expected near Cortina — road closures possible",
            "description": "Meteorological service warns of 30cm snowfall overnight near Cortina d'Ampezzo. Athletes competing on Feb 8 should plan early departure.",
            "link": "#",
            "pub_date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"),
            "severity": "HIGH",
            "affected_venues": ["Cortina Sliding Center", "Tofane Skiing Centre"],
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        {
            "source": "Demo",
            "title": "Milan metro line disruption during opening ceremony",
            "description": "ATM Milano warns of reduced service on Line 1 and 5 during opening ceremony at San Siro. Expect 40% longer travel times.",
            "link": "#",
            "pub_date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"),
            "severity": "MEDIUM",
            "affected_venues": ["Milano San Siro Stadium"],
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
    ]