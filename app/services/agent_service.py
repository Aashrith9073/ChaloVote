import requests
from app.core.config import settings


# app/services/agent_service.py

def get_flight_prices(origin_city: str, dest_city: str, date: str):
    """Tool to get flight prices from Skyscanner."""
    if not settings.RAPIDAPI_KEY:
        return [{"airline": "Flight info not available.", "price": "N/A"}]

    origin_iata = get_iata_code(origin_city)
    dest_iata = get_iata_code(dest_city)

    url = f"https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/IN/INR/en-US/{origin_iata}-sky/{dest_iata}-sky/{date}"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        flights = []
        for quote in data.get("Quotes", [])[:3]: # Get top 3 quotes
            carrier_name = "Unknown Airline"
            # Find the carrier name from the carrier ID
            for carrier in data.get("Carriers", []):
                if carrier["CarrierId"] == quote["OutboundLeg"]["CarrierIds"][0]:
                    carrier_name = carrier["Name"]
                    break
            flights.append({"airline": carrier_name, "price": f"₹{quote['MinPrice']}"})
        return flights if flights else [{"airline": "No direct flights found.", "price": ""}]
    except Exception as e:
        print(f"Error fetching flight data: {e}")
        return [{"airline": "Could not retrieve flight prices.", "price": ""}]

def get_route_info(origin_city: str, dest_city: str, mode: str = "driving"):
    """Gets route info from Google Maps Directions API."""
    if not settings.GOOGLE_MAPS_API_KEY:
        return "Route info not available (Google Maps API key not set)."

    print(f"AGENT TOOL: Getting {mode} route from {origin_city} to {dest_city}...")
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin_city,
        "destination": dest_city,
        "mode": "driving",  # or "two_wheeler" for bikes
        "key": settings.GOOGLE_MAPS_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        data = response.json()
        if data["status"] == "OK":
            route = data["routes"][0]["legs"][0]
            distance = route["distance"]["text"]
            duration = route["duration"]["text"]
            return f"{mode.capitalize()} distance is {distance}, taking about {duration}."
    except Exception as e:
        print(f"Error fetching route data: {e}")
    return "Could not retrieve route information."




def get_hotel_prices(dest_city: str):
    """Gets a list of hotel prices from a RapidAPI endpoint."""
    if not settings.RAPIDAPI_KEY:
        return [{"name": "Hotel info not available.", "price": "N/A"}]

    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"  # Example URL
    querystring = {"dest_id": "-2092174", "order_by": "popularity", "filter_by_currency": "INR", "units": "metric",
                   "room_number": "1", "checkin_date": "2025-10-15", "checkout_date": "2025-10-18",
                   "adults_number": "2", "locale": "en-gb", "dest_type": "city"}
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com"  # Example Host
    }

    try:
        # NOTE: A real app would first need to get the dest_id for the dest_city
        # For now, we'll use a hardcoded search and just return the first few results.
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        hotels = []
        for hotel in data.get('result', [])[:3]:  # Get top 3 hotels
            hotels.append({"name": hotel.get('hotel_name'), "price": f"₹{hotel.get('min_total_price')}"})
        return hotels if hotels else [{"name": "No hotels found.", "price": ""}]
    except Exception as e:
        print(f"Error fetching hotel data: {e}")
        return [{"name": "Could not retrieve hotel prices.", "price": ""}]


def get_iata_code(city_name: str):
    """Gets the IATA code for a city."""
    # This is a mock. A real implementation would use another API to look this up.
    # Example: Visakhapatnam -> VTZ, Delhi -> DEL, Mumbai -> BOM
    iata_map = {"vizag": "VTZ", "visakhapatnam": "VTZ", "hyderabad": "HYD"}
    return iata_map.get(city_name.lower(), "DEL") # Default to Delhi