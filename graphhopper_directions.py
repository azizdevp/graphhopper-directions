from dotenv import load_dotenv
import os
import requests
import urllib.parse

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