import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WriteOptions
import model
from database import SessionLocal

# Load environment variables
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
write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))


# DB session helper
def get_db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# SQLAlchemy helpers
def create_telemetry(db: Session, data: dict):
    db_data = model.Telemetry(
        vehicle_id=data["vehicle_id"],
        timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.utcnow(),
        speed=data.get("speed", 0),
        latitude=data.get("latitude", 0),
        longitude=data.get("longitude", 0),
        fuel_level=data.get("fuel_level", 0)
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    print(f"SQLAlchemy insert success for vehicle {data['vehicle_id']}")
    return db_data


def delete_telemetry_range(db: Session, vehicle_id: str, start: str, stop: str):
    try:
        start_dt = datetime.fromisoformat(start)
        stop_dt = datetime.fromisoformat(stop)

        rows = (
            db.query(model.Telemetry)
            .filter(
                model.Telemetry.vehicle_id == vehicle_id,
                model.Telemetry.timestamp >= start_dt,
                model.Telemetry.timestamp <= stop_dt
            )
            .all()
        )

        if not rows:
            print(f"No telemetry found for {vehicle_id} between {start} and {stop}")
            return {"success": False, "deleted": 0}

        deleted_count = len(rows)
        for row in rows:
            db.delete(row)
        db.commit()

        print(f"Deleted {deleted_count} telemetry rows for {vehicle_id} in SQLAlchemy")
        return {"success": True, "deleted": deleted_count}

    except Exception as e:
        db.rollback()
        print(f"SQLAlchemy delete error: {e}")
        return {"success": False, "error": str(e)}


# InfluxDB helpers
def write_to_influx(data: dict):
    try:
        timestamp = data.get("timestamp")
        if timestamp:
            timestamp = datetime.fromisoformat(timestamp)

        point = (
            Point("telemetry")
            .tag("vehicle_id", data["vehicle_id"])
            .field("speed", data.get("speed", 0))
            .field("latitude", data.get("latitude", 0))
            .field("longitude", data.get("longitude", 0))
            .field("fuel_level", data.get("fuel_level", 0))
        )

        if timestamp:
            point = point.time(timestamp)

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"InfluxDB insert success for vehicle {data['vehicle_id']}")

    except Exception as e:
        print(f"InfluxDB write error: {e}")


def delete_telemetry_influx(db: Session, vehicle_id: str, start: str, stop: str):
    try:
        vehicle = db.query(model.Vehicle).filter(model.Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            return {"success": False, "error": f"Vehicle {vehicle_id} not found."}

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



