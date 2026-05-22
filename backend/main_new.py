# fastapi_app.py
import json
import secrets
import os
from uuid import uuid4
from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from kafka import KafkaProducer
from datetime import datetime, timezone, timedelta
import model_new, schema_new
from database import SessionLocal
from influx_services_new import create_user_details, write_to_influx, delete_telemetry_influx

model_new.Base.metadata.create_all(bind=SessionLocal().bind)
from sqlalchemy import func

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
producer = None

def get_kafka_producer():
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v, default=json_serializer).encode("utf-8")
        )
    return producer

from fastapi import Header
from jose import jwt, JWTError

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/User_Login")

from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session


def get_current_entity(
    model,
    not_found_message: str,
    required_role: str = None
):
    def dependency(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            user_id = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token payload"
                )

        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        entity = (
            db.query(model)
            .filter_by(user_id=user_id)
            .first()
        )

        if not entity:
            raise HTTPException(
                status_code=401,
                detail=not_found_message
            )

        if required_role and entity.role.lower() != required_role.lower():
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return entity

    return dependency

get_current_user = get_current_entity(
    model_new.Users,
    "User not found"
)

get_current_admin = get_current_entity(
    model_new.Users,
    "Admin not found",
    required_role="admin"
)
# Register User

@app.get("/")
def root():
    return {
        "status": "Vehicle Telemetry API is running",
        "kafka": "connected",
        "time": datetime.utcnow().isoformat()
    }

@app.post("/User_Registration", response_model=schema_new.UserOut, status_code=201)
def register_User(user:schema_new.UserDetails, db: Session = Depends(get_db)):
    existing = db.query(model_new.Users).filter_by(user_name=user.user_name).first() 
    existing_email=db.query(model_new.Users).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = model_new.Users(user_id=str(uuid4()),user_name=user.user_name, password=user.password,email=user.email,timestamp=datetime.utcnow())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return schema_new.UserOut(user_id=new_user.user_id, user_name=new_user.user_name,email=new_user.email,role=new_user.role,timestamp=new_user.timestamp.isoformat(),vehicles_registered=[])


@app.get("/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):

    total_users = db.query(model_new.Users).count()

    total_admins = (
        db.query(model_new.Users)
        .filter_by(role="admin")
        .count()
    )

    total_vehicles = (
        db.query(model_new.Vehicles)
        .count()
    )

    return {
        "users": total_users,
        "admins": total_admins,
        "vehicles": total_vehicles,
    }

# Register Vehicle
@app.post("/register_vehicle", response_model=schema_new.VehicleResponse, status_code=201)
def register_vehicle(
    user_id:str,
    vehicle: schema_new.VehicleCreate,
    db: Session = Depends(get_db),
    current_user: model_new.Users = Depends(get_current_user)   
):
    # check duplicate
    if (current_user.user_id!=user_id and current_user.role!="admin" ):
        raise HTTPException(status_code=403,detail="Access denied")
    
    existing = db.query(model_new.Vehicles).filter_by(
        vehicle_id=vehicle.vehicle_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Vehicle already exists")

    # generate api key
    api_key = secrets.token_hex(32)

    # create vehicle
    new_vehicle = model_new.Vehicles(
        vehicle_id=vehicle.vehicle_id,
        vehicle_type=vehicle.vehicle_type,
        vehicle_class=vehicle.vehicle_class,
        vehicle_model=vehicle.vehicle_model,
        year_bought=vehicle.year_bought,
        timestamp=datetime.utcnow(),
        api_key=api_key,
        owner_id=user_id   
    )

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle
   
# Login User
from jose import jwt

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

class PromoteAdmin(BaseModel):
    user_name: str
    
@app.post("/add_admin")
def add_admin(
    data: PromoteAdmin,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = (
        db.query(model_new.Users)
        .filter_by(user_name=data.user_name)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.role = "admin"

    db.commit()

    return {
        "message": f"{user.user_name} promoted to admin"
    }

@app.post("/demote_admin")
def delete_admin(
    data: PromoteAdmin,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = (
        db.query(model_new.Users)
        .filter_by(user_name=data.user_name)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.role = "user"

    db.commit()

    return {
        "message": f"{user.user_name} promoted to admin"
    }


@app.post("/User_Login")
def Login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = (
        db.query(model_new.Users)
        .filter_by(user_name=form_data.username)
        .first()
    )

    if not user or user.password != form_data.password:
        raise HTTPException(
            status_code=403,
            detail="Invalid credentials"
        )

    token = jwt.encode(
        {"sub": user.user_id},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "user_name": user.user_name,
        "role":user.role
    }



# Get all users
@app.get("/GetAllUser")
def get_users(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    users = db.query(model_new.Users).all()
    return [{"user_id": v.user_id, "user_name": v.user_name,"email": v.email, "role":v.role, "timestamp": v.timestamp.isoformat(),"vehicles": v.vehicles_registered} for v in users]



# Get user_vehicles

@app.get("/my_vehicles")
def get_my_vehicles(
    db: Session = Depends(get_db),
    current_user: model_new.Users = Depends(get_current_user)
):
    return [
    {
        "vehicle_id": v.vehicle_id,
        "vehicle_type": v.vehicle_type,
        "vehicle_class": v.vehicle_class,
        "vehicle_model": v.vehicle_model,
        "year_bought": v.year_bought
    }
    for v in db.query(model_new.Vehicles).filter_by(owner_id=current_user.user_id).all()
]   

@app.get("/user_vehicles/")
def get_user_vehicle(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if (
        current_user.user_id != user_id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Access Denied"
        )

    vehicles = (
        db.query(model_new.Vehicles)
        .filter(
            model_new.Vehicles.owner_id == user_id
        )
        .all()
    )

    return [
        {
            "vehicle_id": v.vehicle_id,
            "vehicle_type": v.vehicle_type,
            "vehicle_class": v.vehicle_class,
            "vehicle_model": v.vehicle_model,
            "year_bought": v.year_bought
        }
        for v in vehicles
    ]
@app.get("/GetAllVehicles/")
def all_vehicle(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    return [
    {
        "vehicle_id": v.vehicle_id,
        "vehicle_type": v.vehicle_type,
        "vehicle_class": v.vehicle_class,
        "vehicle_model": v.vehicle_model,
        "year_bought": v.year_bought
    }
    for v in db.query(model_new.Vehicles).all()
]
    
@app.get("/live_telemetry")
def live_telemetry(

    db:Session=Depends(get_db),
    current_admin=Depends(get_current_admin)

):

    vehicles = (
        db.query(model_new.Vehicles).all())

    data=[]

    for v in vehicles:
        latest = (
            db.query(model_new.Telemetry).filter_by(vehicle_id=v.vehicle_id).order_by( model_new.Telemetry.timestamp.desc()).first()
        )
        if latest:
            data.append(latest)

    return data
# Push telemetry
@app.post("/Telemetry_data/")
def push_telemetry(
    data: schema_new.TelemetryCreate,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    vehicle = db.query(model_new.Vehicles).filter_by(api_key=x_api_key.strip()).first()

    if not vehicle:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    
    payload = data.dict()
    payload["vehicle_id"] = vehicle.vehicle_id

    get_kafka_producer().send("telemetry_data", payload)
    

    return {
        "status": "queued",
        **payload
    }

      
@app.get("/vehicle/{vehicle_id}/telemetry")
def get_vehicle_telemetry(
    vehicle_id:str,
    db:Session=Depends(get_db),
    current_user=Depends(get_current_user)
):
    vehicle = (
        db.query(model_new.Vehicles)
        .filter_by(
            vehicle_id=vehicle_id
        )
        .first()
    )

    if (current_user.role!="admin"  and current_user !=vehicle.owner_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    telemetry = (
        db.query(model_new.Telemetry)
        .filter_by(
            vehicle_id=vehicle_id
        )
        .order_by(
            model_new.Telemetry.timestamp.desc()
        )
        .all()
    )

    return telemetry

@app.get("/risky_vehicles/")
def get_risky_vehicle(
    db: Session=Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    risky_vehicle=(
        db.query(model_new.Alert.vehicle_id,func.count(
            model_new.Alert.id
        ).label(
            "alert_count"
        )).group_by(model_new.Alert.vehicle_id).order_by(
            func.count(
                model_new.Alert.id
            ).desc()
        ).all()
    )
    response = []

    for vehicle in risky_vehicle:

        response.append(
            {
                "vehicle_id": vehicle.vehicle_id,
                "alert_count": vehicle.alert_count
            }
        )

    return response


@app.get("/alerts/")
def get_alerts(
    db: Session=Depends(get_db),
    current_admin=Depends(get_current_admin)
):

    alerts=(db.query(model_new.Alert).order_by(model_new.Alert.created_at.desc()).all())
    return  alerts
    
@app.get("/search/")
def search_user(
    user_name:str,
    db: Session=Depends(get_db),
    current_user=Depends(get_current_admin)
):
    user=(db.query(model_new.Users).filter(model_new.Users.user_name.ilike(f"%{user_name}%")).all())
    return user

@app.put("/alerts/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    alert = (
        db.query(model_new.Alert).filter(model_new.Alert.id == alert_id).first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )
    alert.is_read = True
    db.commit()
    return {
        "message":"Alert marked read"
    }
    
# Delete telemetry in range
@app.delete("/telemetry/")
def delete_telemetry(
    vehicle_id: str = Query(...),
    start: str = Query(...),
    stop: str = Query(...),
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
    current_admin =Depends(get_current_admin)
):
    vehicle = db.query(model_new.Vehicles).filter_by(api_key=x_api_key).first()
    if not vehicle or vehicle.vehicle_id != vehicle_id:
        raise HTTPException(status_code=403, detail="Invalid API Key or vehicle mismatch")

    # Send delete action to Kafka
    get_kafka_producer().send("telemetry_data", {
        "action": "delete",
        "vehicle_id": vehicle_id,
        "start": start,
        "stop": stop
    })

    # Optionally, immediately delete in SQL + Influx (or let Kafka consumer handle)
    delete_telemetry_influx(vehicle_id, start, stop)

    return {"status": "queued", "vehicle_id": vehicle_id, "start": start, "stop": stop}

@app.delete("/Delete_user/{user_id}")
def delete_user(
    user_id:str,
    db:Session =Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    user=db.query(model_new.Users).filter_by(user_id=user_id).first()
    if not user:
        
        raise HTTPException(status_code=404, detail="User not found")
    if (current_user.role!='admin' and current_user.user_name !=user_name):
        raise HTTPException(status_code=404, detail="User not found")
        return 
    vehicles = db.query(model_new.Vehicles).filter_by(owner_id=user.user_id).all()
    
    for v in vehicles:
        db.delete(v)
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted"}

@app.delete("/vehicle/{vehicle_id}")
def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user: model_new.Users = Depends(get_current_user)
):
    
    vehicle = db.query(model_new.Vehicles).filter_by(vehicle_id=vehicle_id).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # ownership check
    if vehicle.owner_id != current_user.user_id and current_user.role!="admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(vehicle)
    db.commit()

    return {"message": "Vehicle deleted"}
@app.get("/my-alerts",
            response_model=list[schema_new.AlertResponse])

def get_my_alerts(
    current_user: model_new.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Get all vehicles owned by current user
    vehicles = (
        db.query(model_new.Vehicles)
        .filter(model_new.Vehicles.owner_id == current_user.id)
        .all()
    )

    vehicle_ids = [v.vehicle_id for v in vehicles]

    # Fetch alerts for only those vehicles
    alerts = (
        db.query(model_new.Alert)
        .filter(model_new.Alert.vehicle_id.in_(vehicle_ids))
        .order_by(model_new.Alert.created_at.desc())
        .all()
    )

    return alerts