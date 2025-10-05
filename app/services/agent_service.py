# app/services/agent_service.py
import litellm
import time
import json
from app.core.config import settings

def _ask_gemini(question: str) -> str | None:
    """A generic internal tool to ask Gemini a question."""
    if not settings.GEMINI_API_KEY:
        print("ERROR: Gemini API key not found for agent tool.")
        return None
    try:
        print(f"AGENT TOOL: Asking Gemini -> '{question}'")
        time.sleep(2)
        response = litellm.completion(
            model="vertex_ai/gemini-2.5-flash",
            messages=[{"role": "user", "content": question}],
            api_key=settings.GEMINI_API_KEY
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling Gemini tool: {e}")
        return None

def get_route_info(origin_city: str, dest_city: str):
    """Gets route distance and duration from Gemini."""
    question = f"""What is the driving distance in kilometers and estimated duration by car from {origin_city}, India to {dest_city}, India? 
Respond ONLY with a valid JSON object with keys "distance_km" (int) and "duration_text" (str)."""
    response_text = _ask_gemini(question)
    try:
        data = json.loads(response_text)
        return {
            "text": f"Driving is {data.get('distance_km')} km, about {data.get('duration_text')}.",
            "distance_km": data.get('distance_km', 0)
        }
    except Exception:
        return {"text": response_text or "Could not retrieve route info.", "distance_km": 0}

def get_flight_prices(origin_city: str, dest_city: str):
    """Gets estimated flight prices from Gemini."""
    question = f"""What are the estimated budget-friendly flight prices for one person from {origin_city} to {dest_city}, India? 
Respond ONLY with a valid JSON object with one key 'price_estimate' (str). Example: {{"price_estimate": "Around ₹4,500 - ₹6,000"}}"""
    response_text = _ask_gemini(question)
    try:
        return json.loads(response_text).get("price_estimate", "Estimate not available.")
    except Exception:
        return response_text or "Estimate not available."

def get_hotel_recommendations(dest_city: str):
    """Gets top 4 budget hotel/hostel recommendations from Gemini."""
    question = f"""List the top 4 budget-friendly hostels or guesthouses in {dest_city}, India, suitable for college students. Order them by rating. 
Respond ONLY with a valid JSON list of objects. Each object must have keys 'name', 'rating' (float or string), and 'estimated_price' (str)."""
    response_text = _ask_gemini(question)
    try:
        # Use regex to find the JSON list, as Gemini might add text
        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return [{"name": "Could not parse hotel data.", "rating": "N/A", "price": "N/A"}]
    except Exception:
        return [{"name": "Could not retrieve hotel data.", "rating": "N/A", "price": "N/A"}]

def get_petrol_price(city: str) -> float:
    """Gets petrol price for a city from Gemini."""
    question = f"What is the current price of 1 litre of petrol in {city}, India? Respond with only the number."
    response_text = _ask_gemini(question)
    try:
        return float(response_text)
    except (ValueError, TypeError):
        return 100.0 # Fallback price