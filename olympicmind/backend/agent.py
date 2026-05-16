import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# genai.configure(api_key="AIzaSyAB0K2QhiDDdnjZmM74zv0HN8N7e2Szx7c")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    You are OlympicMind, an autonomous AI agent helping 
    teams navigate Milan during the 2026 Winter Olympics.
    
    
    You have access to:
    - Real-time crowd levels at venues
    - Olympic event schedules  
    - Alternative route suggestions
    - Incident reports
    
    Always respond with:
    1. Current crowd situation
    2. Best route recommendation
    3. Any warnings or incidents
    4. Estimated travel time
    
    Be concise, helpful and alert-focused.
    """
)

def chat_with_agent(user_message, crowd_data, history=[]):
    # Convert history to Gemini format
    gemini_history = []
    for msg in history:
        # Assuming history format is [{"role": "user"/"model", "content": "..."}]
        # Map user/assistant to user/model
        role = "user" if msg.get("role") == "user" else "model"
        content = msg.get("content", "")
        gemini_history.append({
            "role": role,
            "parts": [content]
        })
    
    # Start chat with history
    chat = model.start_chat(history=gemini_history)
    
    # Send message with crowd context
    full_message = f"""
    User request: {user_message}
    
    Current crowd data: {crowd_data}
    
    Provide route advice and any alerts needed.
    """
    
    response = chat.send_message(full_message)
    return response.text
