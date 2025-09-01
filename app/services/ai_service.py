# app/services/ai_service.py
import json
import litellm
from sqlalchemy.orm import Session
from app.core.config import settings
from app import models, schemas

# This is a "mock" response for testing without a real API key
MOCK_RESPONSE = [
    {"destination": "Kyoto, Japan", "reason": "Rich cultural history and beautiful temples.", "budget_tier": "$$$ - Expensive"},
    {"destination": "Medellín, Colombia", "reason": "Vibrant city with a perfect climate and friendly locals.", "budget_tier": "$ - Budget-Friendly"}
]

def generate_recommendations(trip_id: int, db: Session):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        return None # Or raise an error

    # In the future, we'll collect participant preferences from the survey
    # For now, we'll use placeholder preferences
    prompt = create_travel_prompt({
        "budget": "Moderate",
        "interests": ["history", "food", "nature"],
        "participants_count": len(trip.participants)
    })

    if settings.OPENAI_API_KEY:
        try:
            response = litellm.completion(
                model="huggingface/mistralai/Mistral-7B-Instruct-v0.2",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"} # Ask for JSON output
            )
            recommendations_data = json.loads(response.choices[0].message.content).get("recommendations", [])
        except Exception as e:
            print(f"Error calling LLM: {e}")
            recommendations_data = MOCK_RESPONSE # Fallback to mock data on error
    else:
        print("--- SKIPPING LLM CALL: HUGGINGFACE_API_TOKEN not found. Using mock data. ---")
        recommendations_data = MOCK_RESPONSE

    # Save the recommendations to the database
    db_recommendations = []
    for item in recommendations_data:
        rec = models.Recommendation(
            trip_id=trip.id,
            destination_name=item.get("destination"),
            reason=item.get("reason"),
            estimated_budget=item.get("budget_tier")
        )
        db.add(rec)
        db_recommendations.append(rec)

    db.commit()
    for rec in db_recommendations:
        db.refresh(rec)

    return db_recommendations

def create_travel_prompt(preferences: dict) -> str:
    return f"""
    You are an expert travel planner. Generate 5 personalized travel destination recommendations
    for a group of {preferences['participants_count']} people.

    **Group Preferences:**
    - **Budget:** {preferences['budget']}
    - **Interests:** {', '.join(preferences['interests'])}

    Return your response as a single JSON object with a key "recommendations", which is a list of objects.
    Each object in the list must have these exact keys: "destination", "reason", "budget_tier".
    Example format:
    {{
      "recommendations": [
        {{
          "destination": "Lisbon, Portugal",
          "reason": "Offers a vibrant culture with great food that fits a moderate budget.",
          "budget_tier": "$$ - Moderate"
        }}
      ]
    }}
    """