import json
import random
import os

def get_crowd_data():
    file_path = os.path.join(os.path.dirname(__file__), "data", "crowd_data.json")
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def simulate_crowd_change():
    # Simulates real-time crowd changes for demo
    data = get_crowd_data()
    for venue in data["venues"]:
        change = random.randint(-10, 15)
        venue["crowd_level"] = min(100, max(0, venue["crowd_level"] + change))
        if venue["crowd_level"] > 80:
            venue["status"] = "HIGH"
        elif venue["crowd_level"] > 50:
            venue["status"] = "MEDIUM"
        else:
            venue["status"] = "LOW"
    
    # Save the simulated data back
    file_path = os.path.join(os.path.dirname(__file__), "data", "crowd_data.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
        
    return data

def check_for_incidents(crowd_data):
    incidents = []
    for venue in crowd_data["venues"]:
        if venue["crowd_level"] > 80:
            incidents.append({
                "venue": venue["name"],
                "level": venue["crowd_level"],
                "message": f"ALERT: {venue['name']} is overcrowded!"
            })
    return incidents
