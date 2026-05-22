import requests
import random
import time
from datetime import datetime

API_URL = "http://localhost:8000/Telemetry_data/"

API_KEY = "93b550adcafd5843b124b69c95fcaf03f29ed1c813cf69d6957c931bc4e166ea"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}


while True:

    telemetry_data = {

        "timestamp":
        datetime.utcnow().isoformat(),

        "speed":
        round(random.uniform(20,120),2),

        "odometer":
        round(random.uniform(5000,10000),2),

        "trip_distance":
        round(random.uniform(0,50),2),

        "idle_time":
        round(random.uniform(0,15),2),

        "altitude":
        round(random.uniform(100,500),2),

        "latitude":
        round(random.uniform(28.55,28.75),6),

        "longitude":
        round(random.uniform(77.05,77.30),6),

        "fuel_level":
        round(random.uniform(10,100),2),

        "fuel_consumption_rate":
        round(random.uniform(5,15),2),

        "engine_temp":
        round(random.uniform(70,110),2),

        "battery_voltage":
        round(random.uniform(11,15),2),

        "battery_temp":
        round(random.uniform(25,50),2),

        "motor_temp":
        round(random.uniform(40,80),2),

        "charging_status":
        random.choice(
            [
                "Charging",
                "Not Charging"
            ]
        ),

        "range_remaining":
        round(random.uniform(50,400),2),

        "tire_pressure_fl":
        round(random.uniform(30,35),2),

        "tire_pressure_fr":
        round(random.uniform(30,35),2),

        "tire_pressure_rl":
        round(random.uniform(30,35),2),

        "tire_pressure_rr":
        round(random.uniform(30,35),2),

        "tire_temp_fl":
        round(random.uniform(25,45),2),

        "tire_temp_fr":
        round(random.uniform(25,45),2),

        "tire_temp_rl":
        round(random.uniform(25,45),2),

        "tire_temp_rr":
        round(random.uniform(25,45),2),

        "door_status":
        random.choice([True,False]),

        "harsh_acceleration":
        random.choice([True,False]),

        "overspeeding":
        random.choice([True,False])

    }

    try:

        response = requests.post(
            API_URL,
            headers=headers,
            json=telemetry_data
        )

        print(
            f"[{datetime.now()}]"
        )

        print(
            response.status_code
        )

        print(
            response.json()
        )

        print("-"*50)

    except Exception as e:

        print(
            "Error:",
            e
        )

    time.sleep(3)