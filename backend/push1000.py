import os
import random
import json
import time
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Simulation settings
NUM_VEHICLES = 10       # Number of vehicles
TELEMETRY_INTERVAL = 0.001  # Delay between pushes in seconds

def register_vehicle(vehicle_id: str) -> str:
    url = f"{BASE_URL}/register_vehicle"
    for _ in range(5):
        try:
            resp = requests.post(url, params={"vehicle_id": vehicle_id})
            if resp.status_code == 409:
                return resp.json().get("api_key")
            resp.raise_for_status()
            return resp.json()["api_key"]
        except requests.exceptions.RequestException:
            print(f"Backend not ready, retrying for {vehicle_id}...")
            time.sleep(1)
    raise Exception(f"Failed to register vehicle {vehicle_id}")




def push_telemetry(vehicle_id: str, api_key: str, timestamp: datetime):
    """Push telemetry data to the backend."""
    url = f"{BASE_URL}/telemetry/"
    payload = {
        "vehicle_id": vehicle_id,
        "timestamp": timestamp.isoformat() if timestamp else None,  # Safe conversion
        "speed": round(random.uniform(120, 400), 2),
        "latitude": round(random.uniform(-90.0, 90.0), 6),
        "longitude": round(random.uniform(-180.0, 180.0), 6),
        "fuel_level": round(random.uniform(2, 9), 2)
    }
    headers = {"x-api-key": api_key}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code not in (200, 201):
            print(f"[ERROR] Telemetry push failed for {vehicle_id}: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception while pushing telemetry for {vehicle_id}: {e}")

def main():
    # Register vehicles once
    vehicle_keys = {}
    for i in range(NUM_VEHICLES):
        vid = f"veh_{i}"
        vehicle_keys[vid] = register_vehicle(vid)

    # Save API keys
    with open("vehicle_keys.json", "w") as f:
        json.dump(vehicle_keys, f, indent=4)

    print("Telemetry simulation started. Press Ctrl+C to stop.")

    try:
        # Continuous telemetry loop
        while True:
            start = time.time()

            for vid, api_key in vehicle_keys.items():
                timestamp = datetime.now(timezone.utc)
                push_telemetry(vid, api_key, timestamp)

            # Maintain fixed interval
            elapsed = time.time() - start
            time.sleep(max(0, TELEMETRY_INTERVAL - elapsed))

    except KeyboardInterrupt:
        print("\n Telemetry simulation stopped by user.")
    

if __name__ == "__main__":
    main()
