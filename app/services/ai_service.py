import json
import litellm
import re
from sqlalchemy.orm import Session
from app.core.config import settings
from app import models
from collections import Counter
from app.services import agent_service

# Updated mock response for the India-focused agent
MOCK_RESPONSE = {
    "recommendations": [
        {"destination": "Araku Valley, Andhra Pradesh",
         "reason": "A beautiful hill station near Visakhapatnam, perfect for a short road trip.",
         "budget_tier": "₹ - Low Budget"},
        {"destination": "Goa",
         "reason": "Famous for its beaches and vibrant nightlife, accessible by flight or a long road trip.",
         "budget_tier": "₹₹ - Moderate"}
    ]
}


def _aggregate_preferences(trip_id: int, db: Session) -> dict:
    """Gathers and combines all survey responses and participant locations for a trip."""
    # First, get the trip to easily access all its participants
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        return {}  # Return empty dict if trip not found

    # NEW: Collect start locations from ALL participants in the trip
    start_locations = [p.start_location for p in trip.participants if p.start_location]

    # Get survey responses as before
    responses = db.query(models.SurveyResponse).join(models.Participant).filter(
        models.Participant.trip_id == trip_id).all()

    if not responses:
        # Fallback to defaults but still include the collected locations
        return {
            "budget": "Moderate",
            "interests": ["hills", "beach"],
            "start_locations": start_locations
        }

    all_interests = []
    for res in responses:
        all_interests.extend(res.preferences.get("interests", []))

    # Return the combined dictionary
    return {
        "interests": [item for item, count in Counter(all_interests).most_common(5)],
        "budget": responses[0].preferences.get("budget", "Moderate"),
        "start_locations": start_locations  # Add the new list here
    }


def create_initial_ideas_prompt(preferences: dict) -> list:
    """Creates a prompt to get initial destination ideas suitable for the group."""
    locations = ", ".join(preferences["start_locations"])
    system_prompt = "You are a travel expert specializing in trips for college students in India."
    user_prompt = f"""
I am planning a trip for a group of {preferences['participants_count']} college students with the following preferences:
- **Starting Locations**: The group is spread out across {locations}.
- **Interests**: {', '.join(preferences['interests'])}
- **Budget**: {preferences['budget']}

Suggest 5 potential destinations in India that are reasonably accessible for this group. For each destination, provide its name and the state.
Return your response as a single valid JSON object with a key "destinations", which is a list of objects.
Each object must have these exact keys: "name", "state". Example: {{"name": "Araku Valley", "state": "Andhra Pradesh"}}
"""
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]


def create_final_summary_prompt(enriched_destinations: list) -> list:
    """Creates a prompt to summarize the enriched data into a final recommendation."""
    system_prompt = "You are a travel expert summarizing trip options for a group of friends in India."
    destination_data_string = "\n\n".join([json.dumps(d, indent=2) for d in enriched_destinations])
    user_prompt = f"""
Based on the following research data, generate a final recommendation for each destination.
For each destination, provide a compelling `reason` and a `budget_tier` (e.g., "₹ - Low Budget", "₹₹ - Moderate", "₹₹₹ - High Budget").
The `reason` should summarize the travel info and why it's a good fit for college students.
Return your response as a single valid JSON object with a key "recommendations", which is a list of objects.
Each object must have these exact keys: "destination", "reason", "budget_tier".

**Research Data:**
{destination_data_string}
"""
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]


def generate_recommendations(trip_id: int, db: Session):
    """Generates enriched travel recommendations using a multi-step agentic workflow."""
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        return None

    aggregated_prefs = _aggregate_preferences(trip_id, db)
    aggregated_prefs["participants_count"] = len(trip.participants)

    recommendations_data = []

    if settings.COHERE_API_KEY:  # Or your chosen provider's key
        try:
            # 1. First LLM call to get initial ideas
            print("AGENT: Getting initial destination ideas...")
            initial_messages = create_initial_ideas_prompt(aggregated_prefs)
            ideas_response = litellm.completion(model="command-r", messages=initial_messages,
                                                api_key=settings.COHERE_API_KEY)
            response_text = ideas_response.choices[0].message.content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("Could not find a valid JSON object in the AI's first response.")
            ideas_content = json.loads(json_match.group(0))
            destination_ideas = ideas_content.get("destinations", [])

            # 2. Use agent tools to enrich the ideas
            print("AGENT: Enriching ideas with real-time data...")
            enriched_destinations = []
            for idea in destination_ideas:
                dest_name = f"{idea['name']}, {idea['state']}"
                enriched_idea_details = {
                    "destination": dest_name,
                    "hotels": agent_service.get_hotel_prices(dest_name)
                }
                #enriched_idea = {"destination": dest_name}

                #enriched_idea["hotel_info"] = agent_service.get_hotel_prices(dest_name)

                #travel_details = []
                travel_details_by_person = {}
                for participant in trip.participants:
                    origin = participant.start_location
                    if origin:
                        # Get an embeddable map URL from Google
                        map_url = f"https://maps.mapmyindia.com/?saddr={origin}&daddr={dest_name}"
                        travel_details_by_person[participant.contact_info] = {
                            "flights": agent_service.get_flight_prices(origin, dest_name, "2025-10"),
                            "route": agent_service.get_route_info(origin, dest_name, "driving"),
                            "map_url": map_url
                        }
                    enriched_idea_details["travel_info"] = travel_details_by_person
                    enriched_destinations.append(enriched_idea_details)

            # 3. Second LLM call to synthesize a final summary
            print("AGENT: Generating final summary...")
            final_messages = create_final_summary_prompt(enriched_destinations)
            final_response = litellm.completion(model="command-r", messages=final_messages,
                                                api_key=settings.COHERE_API_KEY)
            response_text = final_response.choices[0].message.content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("Could not find a valid JSON object in the AI's final response.")
            final_content = json.loads(json_match.group(0))
            recommendations_data = final_content.get("recommendations", [])

        except Exception as e:
            print(f"Error in agent workflow: {e}")
            recommendations_data = MOCK_RESPONSE.get("recommendations", [])
    else:
        print("--- SKIPPING LLM CALL: API_KEY not found. Using mock data. ---")
        recommendations_data = MOCK_RESPONSE.get("recommendations", [])

    # Save the final recommendations to the database
    db_recommendations = []
    for i, item in enumerate(recommendations_data):
        rec = models.Recommendation(
            trip_id=trip_id,
            destination_name=item.get("destination"),
            reason=item.get("reason"),
            estimated_budget=item.get("budget_tier"),
            details=enriched_destinations[i]
        )
        db.add(rec)
        db_recommendations.append(rec)

    db.commit()
    for rec in db_recommendations:
        db.refresh(rec)

    return db_recommendations