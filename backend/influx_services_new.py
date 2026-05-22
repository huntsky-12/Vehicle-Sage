import os
from datetime import datetime
from typing import Generator, Dict
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from model_new import Users
from database import SessionLocal
from util import hash_password

load_dotenv()
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

if not all([INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET]):
    raise RuntimeError("InfluxDB environment variables not properly set!")

influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1, flush_interval=1000))


# session :Bridges ORM and DB:

# ------------------------------
# DB session helper
# ------------------------------
def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------
# SQLAlchemy helpers
# ------------------------------
def create_user_details(db,user:Users):
    db_user = Users(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        password_hashed=hash_password(user.password_hashed)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ------------------------------
# InfluxDB helpers
# ------------------------------
def write_to_influx(data: Dict):
    try:
        timestamp = datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.utcnow()

        point = (
            Point("telemetry")  # measurement name
            .tag("vehicle_id", data["vehicle_id"])
            .field("speed", data.get("speed", 0))
            .field("odometer", data.get("odometer", 0))
            .field("trip_distance", data.get("trip_distance", 0))
            .field("idle_time", data.get("idle_time", 0))
            .field("altitude", data.get("altitude"))
            .field("latitude", data.get("latitude", 0))
            .field("longitude", data.get("longitude", 0))
            .field("fuel_level", data.get("fuel_level"))
            .field("fuel_consumption_rate", data.get("fuel_consumption_rate"))
            .field("engine_temp", data.get("engine_temp"))
            .field("battery_voltage", data.get("battery_voltage"))
            .field("battery_temp", data.get("battery_temp"))
            .field("motor_temp", data.get("motor_temp"))
            .field("charging_status", data.get("charging_status", ""))
            .field("range_remaining", data.get("range_remaining"))
            .field("tire_pressure_fl", data.get("tire_pressure_fl"))
            .field("tire_pressure_fr", data.get("tire_pressure_fr"))
            .field("tire_pressure_rl", data.get("tire_pressure_rl"))
            .field("tire_pressure_rr", data.get("tire_pressure_rr"))
            .field("tire_temp_fl", data.get("tire_temp_fl"))
            .field("tire_temp_fr", data.get("tire_temp_fr"))
            .field("tire_temp_rl", data.get("tire_temp_rl"))
            .field("tire_temp_rr", data.get("tire_temp_rr"))
            .field("door_status", int(data.get("door_status", 0)))
            .field("harsh_acceleration", int(data.get("harsh_acceleration", 0)))
            .field("overspeeding", int(data.get("overspeeding", 0)))
            .time(timestamp)
        )

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"InfluxDB insert success for vehicle {data['vehicle_id']}")

    except Exception as e:
        print(f"InfluxDB write error: {e}")


def delete_telemetry_influx(vehicle_id: str, start: str, stop: str):
    try:
        delete_api = influx_client.delete_api()
        delete_api.delete(
            start=start,
            stop=stop,
            predicate=f'vehicle_id="{vehicle_id}"',
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG
        )
        print(f"Deleted InfluxDB telemetry for vehicle {vehicle_id} from {start} to {stop}")
        return {"success": True}

    except Exception as e:
        print(f"InfluxDB delete error: {e}")
        return {"success": False, "error": str(e)}


