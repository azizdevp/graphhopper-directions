from dotenv import load_dotenv
import os
import requests
import urllib.parse
import json

# Load environment variables
load_dotenv()
GRAPHHOPPER_API_KEY = os.getenv("GRAPHHOPPER_API_KEY")

# Geocoding function
def geocode_location(location, api_key):
    base_url = "https://graphhopper.com/api/1/geocode"
    params = {
        "q": location,
        "key": api_key,
        "limit": 1
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    print(f"Geocoding API URL: {base_url}?{urllib.parse.urlencode(params)}")
    if response.status_code == 200 and data.get("hits"):
        hit = data["hits"][0]
        lat = hit["point"]["lat"]
        lng = hit["point"]["lng"]
        formatted_location = f"{hit.get('city', '')}, {hit.get('state', '')}, {hit.get('country', '')}".strip(", ")
        return response.status_code, lat, lng, formatted_location
    else:
        print(f"Geocode API status: {response.status_code}")
        if data.get("message"):
            print(f"Error message: {data['message']}")
        return response.status_code, "null", "null", location

# Test
if not GRAPHHOPPER_API_KEY:
    print("Error: GRAPHHOPPER_API_KEY not found in .env file")
else:
    location = "Washington, DC"
    result = geocode_location(location, GRAPHHOPPER_API_KEY)
    print(result)


def save_trip(start, dest, vehicle, data):
    trip = {
        "start": start,
        "dest": dest,
        "vehicle": vehicle,
        "distance": data["paths"][0]["distance"] / 1000,  # meters to km
        "duration": data["paths"][0]["time"] / 3600000  # ms to hours
    }
    try:
        with open("trip_history.json", "r") as f:
            history = json.load(f)
    except:
        history = []
    history.append(trip)
    with open("trip_history.json", "w") as f:
        json.dump(history, f, indent=4)
def display_route_points(data):
    points = data["paths"][0]["points"]["coordinates"]
    print("Route Points (lon, lat):")
    for i, point in enumerate(points[:5], 1):  # First 5 for brevity
        print(f"Point {i}: ({point[0]}, {point[1]})")