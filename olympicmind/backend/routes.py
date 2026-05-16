MILAN_ROUTES = {
    "fiera_to_duomo": {
        "fast": {
            "name": "Metro Line 1",
            "time": "25 mins",
            "avoid": [],
            "steps": ["Walk to Rho Fiera Metro", 
                     "Take M1 Red Line", 
                     "Exit at Duomo"]
        },
        "safe": {
            "name": "Bus Route 78",
            "time": "40 mins", 
            "avoid": ["Cadorna"],
            "steps": ["Take Bus 78 from Fiera",
                     "Transfer at Garibaldi",
                     "Walk 5 mins to Duomo"]
        },
        "scenic": {
            "name": "Walking + Tram",
            "time": "55 mins",
            "avoid": ["Central Station"],
            "steps": ["Walk to Tram 19",
                     "Ride through Navigli",
                     "Walk to Duomo"]
        }
    }
}

def get_best_route(origin, destination, crowd_data):
    # Filter routes based on crowd levels
    high_crowd_venues = [v["name"] for v in crowd_data["venues"] 
                        if v["status"] == "HIGH"]
    
    route_key = f"{origin.lower()}_to_{destination.lower()}"
    routes = MILAN_ROUTES.get(route_key)
    
    if not routes:
        # Generate generic dynamic routes for any combo of venues
        routes = {
            "fast": {
                "name": "Olympic Express Shuttle",
                "time": "35 mins",
                "avoid": [],
                "steps": [f"Board Express Shuttle at {origin}", 
                         "Direct transit via Olympic lane", 
                         f"Arrive at {destination}"]
            },
            "safe": {
                "name": "Metro + Walking",
                "time": "50 mins", 
                "avoid": high_crowd_venues[:2] if high_crowd_venues else [],
                "steps": [f"Walk to nearest Metro from {origin}",
                         "Take Green Line",
                         f"Walk 10 mins to {destination}"]
            },
            "scenic": {
                "name": "Regional Train",
                "time": "1 hr 15 mins",
                "avoid": [],
                "steps": [f"Take local transit from {origin}",
                         "Transfer to Regional Rail",
                         f"Arrive at {destination} Station"]
            }
        }
    
    # Return route avoiding high crowd areas
    return {
        "recommended": "safe" if high_crowd_venues else "fast",
        "reason": f"Avoiding {', '.join(high_crowd_venues)}" 
                  if high_crowd_venues else "Clear path available",
        "routes": routes
    }
