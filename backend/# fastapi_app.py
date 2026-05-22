# fastapi_app.py
import json
import secrets
import os
from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from kafka import KafkaProducer
from datetime import datetime, timezone, timedelta
import model, schema
from database import SessionLocal
from influx_services import delete_telemetry_influx, delete_telemetry_range
from influx_services_new import TelemetryService
# Create tables
model.Base.metadata.create_all(bind=SessionLocal().bind)

app = FastAPI(title="Vehicle Telemetry API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# to store timestamp in json file
def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Kafka producer
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
     value_serializer=lambda v: json.dumps(v, default=json_serializer).encode("utf-8")
)

# Register Vehicle
@app.post("/register_vehicle", response_model=schema.RegisterVehicleResponse, status_code=201)
def register_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    existing = db.query(model.Vehicle).filter_by(vehicle_id=vehicle_id).first()
    if existing:
        return schema.RegisterVehicleResponse(vehicle_id=vehicle_id, api_key=existing.api_key)
    
    api_key = secrets.token_hex(32)
    new_vehicle = model.Vehicle(vehicle_id=vehicle_id, api_key=api_key)
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return schema.RegisterVehicleResponse(vehicle_id=vehicle_id, api_key=api_key)

# Get all vehicles
@app.get("/vehicles")
def get_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(model.Vehicle).all()
    return [{"vehicle_id": v.vehicle_id, "id": v.id} for v in vehicles]

# Push telemetry
@app.post("/telemetry/")
def push_telemetry(
    data: schema.Telemetry_Create,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    vehicle = db.query(model.Vehicle).filter_by(api_key=x_api_key).first()
    if not vehicle or vehicle.vehicle_id != data.vehicle_id:
        raise HTTPException(status_code=403, detail="Invalid API Key or vehicle mismatch")
    
    producer.send("telemetry_data", data.dict())
    return {
        "status": "queued",
        "vehicle_id": data.vehicle_id,
        "timestamp": data.timestamp,
        "speed": data.speed,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "fuel_level": data.fuel_level
    }

# Delete telemetry in range
@app.delete("/telemetry/")
def delete_telemetry(
    vehicle_id: str = Query(...),
    start: str = Query(...),
    stop: str = Query(...),
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    vehicle = db.query(model.Vehicle).filter_by(api_key=x_api_key).first()
    if not vehicle or vehicle.vehicle_id != vehicle_id:
        raise HTTPException(status_code=403, detail="Invalid API Key or vehicle mismatch")

    # Send delete action to Kafka
    producer.send("telemetry_data", {
        "action": "delete",
        "vehicle_id": vehicle_id,
        "start": start,
        "stop": stop
    })

    # Optionally, immediately delete in SQL + Influx (or let Kafka consumer handle)
    delete_telemetry_range(db, vehicle_id, start, stop)
    delete_telemetry_influx(db, vehicle_id, start, stop)

    return {"status": "queued", "vehicle_id": vehicle_id, "start": start, "stop": stop}
