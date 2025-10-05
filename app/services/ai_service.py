import json
import re
from sqlalchemy.orm import Session
from app.core.config import settings
from app import models
from collections import Counter
from app.services import agent_service
import litellm

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
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        return {}

    start_locations = [p.start_location for p in trip.participants if p.start_location]
    responses = db.query(models.SurveyResponse).join(models.Participant).filter(
        models.Participant.trip_id == trip_id).all()

    if not responses:
        return {
            "budget": "Moderate",
            "interests": ["hills", "beach"],
            "start_locations": start_locations
        }

    all_interests = []
    for res in responses:
        all_interests.extend(res.preferences.get("interests", []))

    return {
        "interests": [item for item, count in Counter(all_interests).most_common(5)],
        "budget": responses[0].preferences.get("budget", "Moderate"),
        "start_locations": start_locations
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
    system_prompt = "You are a travel expert summarizing trip options for a group of Indian college students on a budget."
    destination_data_string = "\n\n".join([json.dumps(d, indent=2) for d in enriched_destinations])
    user_prompt = f"""
Based on my research below, generate a final, compelling recommendation for each destination.
For each destination, provide:
1. A `reason` summarizing why it's a great fit.
2. An `estimated_total_cost` which should be a simple string like "Approx. ₹12,000 per person".
3. A `top_stays` list containing the top 4 budget accommodation options with their price and rating.
4. A `budget_tier` string (e.g., "₹ - Low Budget", "₹₹ - Moderate", "₹₹₹ - High Budget").

Return your response as a single valid JSON object with a key "recommendations". 
Each object must have keys: "destination", "reason", "estimated_total_cost", "top_stays", and "budget_tier".

**My Research Data:**
{destination_data_string}
"""
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]


def generate_recommendations(trip_id: int, db: Session):
    """Generates enriched travel recommendations using Gemini for all AI tasks."""
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip: return None

    aggregated_prefs = _aggregate_preferences(trip_id, db)
    aggregated_prefs["participants_count"] = len(trip.participants)

    recommendations_data = []
    enriched_destinations = []

    if settings.GEMINI_API_KEY:
        try:
            # 1. First LLM call to get initial ideas
            print("AGENT: Getting initial destination ideas using Gemini...")
            initial_messages = create_initial_ideas_prompt(aggregated_prefs)
            ideas_response = litellm.completion(model="vertex_ai/gemini-2.5-flash", messages=initial_messages,
                                                api_key=settings.GEMINI_API_KEY)
            response_text = ideas_response.choices[0].message.content

            # --- NEW DEBUGGING STATEMENT ---
            print("\n--- RAW AI RESPONSE (Initial Ideas) ---")
            print(response_text)
            print("---------------------------------------\n")
            # --- END DEBUGGING STATEMENT ---

            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("Could not find a valid JSON object in Gemini's first response.")
            ideas_content = json.loads(json_match.group(0))
            destination_ideas = ideas_content.get("destinations", [])

            # 2. Use agent tools to enrich the ideas
            print("AGENT: Enriching ideas with real-time data...")
            for idea in destination_ideas:
                dest_name = f"{idea['name']}, {idea['state']}"

                # These now call our new Gemini-powered tools
                hotel_recs = agent_service.get_hotel_recommendations(dest_name)

                enriched_idea_details = {"destination": dest_name, "top_4_hotels": hotel_recs}

                travel_details_by_person = {}
                for participant in trip.participants:
                    origin = participant.start_location
                    if origin:
                        route_info = agent_service.get_route_info(origin, dest_name)
                        petrol_price = agent_service.get_petrol_price(origin)
                        flight_info = agent_service.get_flight_prices(origin, dest_name)

                        # Create the Google Maps Embed URL
                        map_url = f"https://www.google.com/maps/embed/v1/directions?key={settings.GOOGLE_MAPS_API_KEY}&origin={origin}&destination={dest_name}"

                        fuel_cost = round((route_info.get('distance_km', 0) / 15) * petrol_price) * 2  # Return trip

                        travel_details_by_person[participant.contact_info] = {
                            "route_text": route_info.get('text'),
                            "estimated_fuel_cost": f"~₹{fuel_cost}",
                            "flight_estimate": flight_info,
                            "map_url": map_url
                        }
                enriched_idea_details["travel_info"] = travel_details_by_person
                enriched_destinations.append(enriched_idea_details)

            # 3. Second LLM call to synthesize a final summary
            print("AGENT: Generating final summary using Gemini...")
            final_messages = create_final_summary_prompt(enriched_destinations)
            final_response = litellm.completion(model="vertex_ai/gemini-2.5-flash", messages=final_messages,
                                                api_key=settings.GEMINI_API_KEY)
            response_text_final = final_response.choices[0].message.content

            # --- NEW DEBUGGING STATEMENT ---
            print("\n--- RAW AI RESPONSE (Final Summary) ---")
            print(response_text_final)
            print("---------------------------------------\n")
            # --- END DEBUGGING STATEMENT ---

            json_match_final = re.search(r'\{.*\}', response_text_final, re.DOTALL)
            if not json_match_final:
                raise ValueError("Could not find a valid JSON object in Gemini's final response.")
            final_content = json.loads(json_match_final.group(0))
            recommendations_data = final_content.get("recommendations", [])

        except Exception as e:
            print(f"Error in agent workflow: {e}")
            recommendations_data = MOCK_RESPONSE.get("recommendations", [])
    else:
        print("--- SKIPPING LLM CALL: GEMINI_API_KEY not found. Using mock data. ---")
        recommendations_data = MOCK_RESPONSE.get("recommendations", [])

    # Save the final recommendations to the database
    db_recommendations = []
    for i, item in enumerate(recommendations_data):
        details_data = enriched_destinations[i] if i < len(enriched_destinations) else {}

        details_data['reason'] = item.get("reason")
        details_data['estimated_total_cost'] = item.get("estimated_total_cost")
        details_data['top_stays'] = item.get("top_stays")

        rec = models.Recommendation(
            trip_id=trip_id,
            destination_name=item.get("destination"),
            reason=item.get("reason"),
            estimated_budget=item.get("budget_tier"),
            details=details_data
        )
        db.add(rec)
        db_recommendations.append(rec)

    db.commit()
    for rec in db_recommendations:
        db.refresh(rec)

    return db_recommendations