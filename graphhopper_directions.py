from dotenv import load_dotenv
import os
import requests
import urllib.parse
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from tabulate import tabulate
from colorama import init, Fore, Style
import json

# Initialize color output and load .env
init()
load_dotenv()

GRAPHHOPPER_API_KEY = os.getenv("GRAPHHOPPER_API_KEY")

# Supported vehicles and session
VALID_VEHICLES = ["car", "bike", "foot"]
vehicle_completer = WordCompleter(VALID_VEHICLES)
city_completer = WordCompleter(["Washington, DC", "Baltimore, MD", "Tempe, AZ"])  # Optional
session = PromptSession(completer=city_completer)

def geocode_location(location, api_key):
    if not location.strip():
        return 400, "null", "null", location
    base_url = "https://graphhopper.com/api/1/geocode"
    params = {"q": location, "key": api_key, "limit": 1}
    response = requests.get(base_url, params=params)
    data = response.json()
    if response.status_code == 200 and data.get("hits"):
        hit = data["hits"][0]
        lat = hit["point"]["lat"]
        lng = hit["point"]["lng"]
        formatted_location = f"{hit.get('city', '')}, {hit.get('state', '')}, {hit.get('country', '')}".strip(", ")
        return response.status_code, lat, lng, formatted_location
    return response.status_code, "null", "null", location

def get_directions(orig_lat, orig_lng, dest_lat, dest_lng, vehicle, api_key, preferences=None):
    base_url = "https://graphhopper.com/api/1/route"
    params = {
        "point": [f"{orig_lat},{orig_lng}", f"{dest_lat},{dest_lng}"],
        "vehicle": vehicle,
        "key": api_key
    }
    if preferences:
        params.update(preferences)
    response = requests.get(base_url, params=params)
    return response.status_code, response.json()

def save_trip(start, dest, vehicle, data):
    trip = {
        "start": start,
        "dest": dest,
        "vehicle": vehicle,
        "distance": data["paths"][0]["distance"] / 1000,
        "duration": data["paths"][0]["time"] / 3600000
    }
    try:
        with open("trip_history.json", "r") as f:
            history = json.load(f)
    except:
        history = []
    history.append(trip)
    with open("trip_history.json", "w") as f:
        json.dump(history, f, indent=4)

def display_directions(data, start, dest, vehicle):
    print(Fore.GREEN + f"\nDirections from {start} to {dest} by {vehicle}" + Style.RESET_ALL)
    distance = data["paths"][0]["distance"] / 1000  # meters to km
    duration = data["paths"][0]["time"] / 3600000  # ms to hours
    print(f"Distance: {distance:.1f} km")
    print(f"Duration: {duration:.2f} hours")
    instructions = []
    for i, instr in enumerate(data["paths"][0]["instructions"], 1):
        instructions.append([i, instr["text"], f"{instr['distance']/1000:.1f} km"])
    print(tabulate(instructions, headers=["Step", "Instruction", "Distance"], tablefmt="grid"))

def get_valid_location(prompt_text):
    while True:
        loc = session.prompt(prompt_text)
        status, lat, lng, name = geocode_location(loc, GRAPHHOPPER_API_KEY)
        if status == 200 and lat != "null":
            return lat, lng, name
        else:
            print(Fore.RED + f"Invalid location: {loc}. Try again." + Style.RESET_ALL)

def get_valid_vehicle():
    while True:
        vehicle = session.prompt("Vehicle (car, bike, foot): ", completer=vehicle_completer)
        if vehicle in VALID_VEHICLES:
            return vehicle
        print(Fore.RED + "Invalid vehicle. Choose from: car, bike, foot." + Style.RESET_ALL)

def main_menu():
    print("\n=== Graphhopper Directions App ===")
    print("1. Get Directions\n2. View Trip History\n3. Exit")
    return session.prompt("Select an option: ")

# Main loop
while True:
    choice = main_menu()
    if choice == "1":
        orig_lat, orig_lng, orig_name = get_valid_location("Starting Location: ")
        dest_lat, dest_lng, dest_name = get_valid_location("Destination: ")
        vehicle = get_valid_vehicle()

        status, route_data = get_directions(orig_lat, orig_lng, dest_lat, dest_lng, vehicle, GRAPHHOPPER_API_KEY)
        if status == 200:
            display_directions(route_data, orig_name, dest_name, vehicle)
            save_trip(orig_name, dest_name, vehicle, route_data)
        else:
            print(Fore.RED + "Failed to get directions. Please try again." + Style.RESET_ALL)

    elif choice == "2":
        try:
            with open("trip_history.json", "r") as f:
                history = json.load(f)
            if not history:
                raise Exception("Empty")
            for i, trip in enumerate(history, 1):
                print(f"\nTrip {i}: {trip['start']} to {trip['dest']} by {trip['vehicle']}")
                print(f"Distance: {trip['distance']:.1f} km, Duration: {trip['duration']:.2f} hours")
        except:
            print(Fore.YELLOW + "No trip history found." + Style.RESET_ALL)

    elif choice == "3":
        print("Exiting. Goodbye!")
        break

    else:
        print(Fore.RED + "Invalid choice. Try 1, 2, or 3." + Style.RESET_ALL)
