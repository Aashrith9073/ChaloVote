import requests
import math
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


def get_coordinates(city_name: str):
    """Converts a city name to latitude and longitude using MapmyIndia's API."""
    if not settings.MAPMYINDIA_API_KEY:
        return None

    # This is a simplified geocoding endpoint from MapmyIndia
    url = f"https://atlas.mapmyindia.com/api/places/search/json?query={city_name}"
    headers = {
        'Authorization': f'bearer {settings.MAPMYINDIA_API_KEY}',
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if 'suggestedLocations' in data and data['suggestedLocations']:
            # Get the coordinates from the first result
            coords = data['suggestedLocations'][0]
            return f"{coords['longitude']},{coords['latitude']}"
    except Exception as e:
        print(f"Error geocoding '{city_name}': {e}")
    return None


def get_route_info(origin_city: str, dest_city: str, mode: str = "driving"):
    """Gets route info from MapmyIndia Directions API."""
    if not settings.MAPMYINDIA_API_KEY:
        return "Route info not available (MapmyIndia key not set)."

    print(f"AGENT TOOL: Getting {mode} route from {origin_city} to {dest_city} via MapmyIndia...")

    # Step 1: Convert city names to coordinates
    origin_coords = get_coordinates(origin_city)
    dest_coords = get_coordinates(dest_city)

    if not origin_coords or not dest_coords:
        return f"Could not find coordinates for {origin_city} or {dest_city}."

    # Step 2: Use coordinates to get the route
    url = f"https://apis.mapmyindia.com/advancedmaps/v1/{settings.MAPMYINDIA_API_KEY}/route_adv/driving/{origin_coords};{dest_coords}"

    try:
        response = requests.get(url)
        data = response.json()
        if data.get("responseCode") == 200 and data.get("routes"):
            route = data['routes'][0]
            distance_km = round(route['distance'] / 1000)

            # Convert duration from seconds to a readable format
            duration_seconds = route['duration']
            hours = math.floor(duration_seconds / 3600)
            minutes = round((duration_seconds % 3600) / 60)

            return f"Driving distance is {distance_km} km, taking about {hours} hours and {minutes} minutes."
    except Exception as e:
        print(f"Error fetching MapmyIndia route data: {e}")
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