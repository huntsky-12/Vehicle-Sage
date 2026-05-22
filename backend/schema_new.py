from pydantic import BaseModel
from datetime import datetime
from pydantic import EmailStr
from typing import List, Optional,Literal

# class VehicleDetails(BaseModel):
    
#     vehicle_id: str
#     vehicle_type: Literal["ICE", "EV"]       # Only allows "ICE" or "EV"
#     vehicle_class: Literal["LIGHT", "HEAVY"]     
#     vehicle_model: str
#     year_bought: int
#     timestamp: Optional[datetime] = None 

#     class Config:
#         orm_mode = True

class VehicleCreate(BaseModel):
    vehicle_id: str
    vehicle_type: Literal["ICE", "EV"]
    vehicle_class: Literal["LIGHT", "HEAVY"]
    vehicle_model: str
    year_bought: int


class VehicleResponse(BaseModel):
    vehicle_id: str
    vehicle_type: Literal["ICE", "EV"]
    vehicle_class: Literal["LIGHT", "HEAVY"]
    vehicle_model: str
    year_bought: int


    class Config:
        orm_mode = True   

class UserDetails(BaseModel):
    user_name: str
    email: EmailStr
    password: str
    timestamp: Optional[datetime] = None
    vehicles_registered: Optional[List[str]] = None
    
class UserOut(BaseModel):
    user_id: str
    user_name: str
    email: EmailStr
    role: str
    timestamp:Optional[datetime] = None
    vehicles_registered: Optional[List[str]] = None

    class Config:
        orm_mode = True
        
class TelemetryCreate(BaseModel):
    
    timestamp: datetime
    speed: float
    odometer: float
    trip_distance: float
    idle_time: float
    altitude: Optional[float] = None
    latitude: float
    longitude: float
    fuel_level: Optional[float] = None
    fuel_consumption_rate: Optional[float] = None
    engine_temp: Optional[float] = None
    battery_voltage: Optional[float] = None
    battery_temp: Optional[float] = None
    motor_temp: Optional[float] = None
    charging_status: Optional[str] = None
    range_remaining: Optional[float] = None
    tire_pressure_fl: Optional[float] = None
    tire_pressure_fr: Optional[float] = None
    tire_pressure_rl: Optional[float] = None
    tire_pressure_rr: Optional[float] = None
    tire_temp_fl: Optional[float] = None
    tire_temp_fr: Optional[float] = None
    tire_temp_rl: Optional[float] = None
    tire_temp_rr: Optional[float] = None
    door_status: Optional[bool] = None
    harsh_acceleration: Optional[bool] = None
    overspeeding: Optional[bool] = None
    
    

class TelemetryOut(BaseModel):
    vehicle_id: str
    timestamp: datetime
    speed: float
    odometer: float
    trip_distance: float
    idle_time: float
    altitude: Optional[float] = None
    latitude: float
    longitude: float
    fuel_level: Optional[float] = None
    fuel_consumption_rate: Optional[float] = None
    engine_temp: Optional[float] = None
    battery_voltage: Optional[float] = None
    battery_temp: Optional[float] = None
    motor_temp: Optional[float] = None
    charging_status: Optional[str] = None
    range_remaining: Optional[float] = None
    tire_pressure_fl: Optional[float] = None
    tire_pressure_fr: Optional[float] = None
    tire_pressure_rl: Optional[float] = None
    tire_pressure_rr: Optional[float] = None
    tire_temp_fl: Optional[float] = None
    tire_temp_fr: Optional[float] = None
    tire_temp_rl: Optional[float] = None
    tire_temp_rr: Optional[float] = None
    door_status: Optional[bool] = None
    harsh_acceleration: Optional[bool] = None
    overspeeding: Optional[bool] = None

    
    class Config:
        orm_mode=True
class AlertResponse(BaseModel):
    type: str
    severity: str
    vehicle_id: str
    message: str
    created_at: datetime
    is_read:bool
    class Config:
        orm_mode=True
        
