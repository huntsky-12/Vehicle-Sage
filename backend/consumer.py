import os
import json
import time
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point
from datetime import datetime
from model_new import Alert
from database import SessionLocal
from model_new import Telemetry
from database import SessionLocal



# Environment variables
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "telemetry_data")
INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "Vehicle-telemetry")

# Connect to InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()

# Connect to Kafka with retry loop
while True:
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="telemetry-consumer-group"
        )
        print("Connected to Kafka!")
        break
    except Exception as e:
        print(f"Kafka not ready yet: {e}")
        time.sleep(5)

print("Kafka → InfluxDB consumer running...")


def process_alerts(data):
    alerts = []
    vid = data["vehicle_id"]
    ts = datetime.utcnow()

    def add(alert_type, severity, message):
        alerts.append({"alert_type": alert_type, "severity": severity,
                        "vehicle_id": vid, "message": message, "created_at": ts})

    if float(data["speed"]) > 80:
        add("overspeed", "high", "Overspeed detected")

    if float(data.get("engine_temp") or 0) > 110:
        add("engine_overheat", "critical", "Engine overheating detected")

    if (fuel := float(data.get("fuel_level") or 999)) < 10:
        add("low_fuel", "severe" if fuel < 5 else "medium",
            "Critical fuel level detected" if fuel < 5 else "Low fuel level detected")

    return alerts
def save_alert(db, alert_data):
    
    try:
        print("Incoming alert:", alert_data)

        alert = Alert(
            vehicle_id=alert_data["vehicle_id"],
            alert_type=alert_data["alert_type"],
            severity=alert_data["severity"],
            message=alert_data["message"],
            created_at=alert_data["created_at"],
            is_read=False
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        print(f"Saved alert id: {alert.id}")

        return alert

    except Exception as e:
        print("SAVE ALERT ERROR:", e)
        db.rollback()
            
for msg in consumer:
    data = msg.value

    # Handle delete actions
    if data.get("action") == "delete":
        print(f"Delete request received for {data['vehicle_id']}")
        try:
            delete_api = client.delete_api()
            start = datetime.fromisoformat(data["start"])
            stop = datetime.fromisoformat(data["stop"])
            delete_api.delete(
                start=start,
                stop=stop,
                predicate=f'vehicle_id="{data["vehicle_id"]}"',
                bucket=INFLUX_BUCKET,
                org=INFLUX_ORG
            )
            print(f"Deleted InfluxDB telemetry for {data['vehicle_id']} from {data['start']} to {data['stop']}")
        except Exception as e:
            print(f"Failed to delete InfluxDB data: {e}")
        continue  # Skip writing

    # Normal write logic
    try:
        timestamp = datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        from influxdb_client import Point

        point = (
            Point("telemetry")
            .tag("vehicle_id", data["vehicle_id"])
            .field("timestamp", data["timestamp"])
            .field("speed", float(data["speed"]))
            .field("odometer", float(data["odometer"]))
            .field("trip_distance", float(data["trip_distance"]))
            .field("idle_time", float(data["idle_time"]))
            .field("latitude", float(data["latitude"]))
            .field("longitude", float(data["longitude"]))
            
        )

        # Optional fields
        optional_fields = [
            "altitude",
            "fuel_level",
            "fuel_consumption_rate",
            "engine_temp",
            "battery_voltage",
            "battery_temp",
            "motor_temp",
            "charging_status",
            "range_remaining",
            "tire_pressure_fl",
            "tire_pressure_fr",
            "tire_pressure_rl",
            "tire_pressure_rr",
            "tire_temp_fl",
            "tire_temp_fr",
            "tire_temp_rl",
            "tire_temp_rr",
            "door_status",
            "harsh_acceleration",
            "overspeeding"
        ]

        for field in optional_fields:
            if field in data and data[field] is not None:
                point = point.field(field, data[field])

        if timestamp:
            point = point.time(timestamp)
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG,record=point)
        print(f"Written to InfluxDB: {data['vehicle_id']} at {data.get('timestamp')}")
        
        # --------------------
        # Save to SQL
        # --------------------

        db = SessionLocal()

        try:

            telemetry = Telemetry(

                vehicle_id=data["vehicle_id"],
                timestamp=datetime.fromisoformat(
                    data["timestamp"]
                ),

                speed=float(data["speed"]),
                odometer=float(data["odometer"]),
                trip_distance=float(data["trip_distance"]),
                idle_time=float(data["idle_time"]),

                altitude=data.get("altitude"),

                latitude=float( data["latitude"]),

                longitude=float(data["longitude"]),

                fuel_level=data.get("fuel_level"),

                fuel_consumption_rate=data.get("fuel_consumption_rate"),

                engine_temp=data.get("engine_temp" ),

                battery_voltage=data.get("battery_voltage"),

                battery_temp=data.get("battery_temp"),

                motor_temp=data.get("motor_temp"),

                charging_status=data.get( "charging_status"),

                range_remaining=data.get( "range_remaining" ),

                tire_pressure_fl=data.get("tire_pressure_fl"),

                tire_pressure_fr=data.get("tire_pressure_fr"),

                tire_pressure_rl=data.get("tire_pressure_rl"),

                tire_pressure_rr=data.get( "tire_pressure_rr"),

                tire_temp_fl=data.get("tire_temp_fl"),

                tire_temp_fr=data.get("tire_temp_fr"),

                tire_temp_rl=data.get("tire_temp_rl" ),

                tire_temp_rr=data.get( "tire_temp_rr"),

                door_status=data.get("door_status"),

                harsh_acceleration=data.get("harsh_acceleration"),
                overspeeding=data.get("overspeeding")

            )

            db.add(telemetry)
            db.commit()
            print("Saved to SQL DB")
            alerts = process_alerts(data)
            print("Generated alerts:")
            print(alerts)

            alerts = process_alerts(data)

            print("Generated:")
            print(alerts)

            for alert in alerts:

                save_alert(
                    db,
                    alert
                )

        except Exception as e:
            print(f"Failed to write: {e}")
        finally:
            db.close()
    except Exception as e:
        print(f"Failed to write: {e}")


