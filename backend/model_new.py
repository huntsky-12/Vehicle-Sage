from sqlalchemy import String, Float, Integer, Column, DateTime, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from database import Base

from database import engine

from datetime import datetime

# | Field                | Type                          | Notes                                            |
# | -------------------- | ----------------------------- | ------------------------------------------------ |
# | user\_id             | string / UUID                 | Primary key                                      |
# | username             | string                        | Login / display name                             |
# | email                | string                        | Optional, for alerts                             |
# | password\_hash       | string                        | Hashed password                                  |
# | vehicles\_registered | array / JSON / relation table | List of vehicle\_ids this user owns / can access |

# | user_id | user_name | email                                   | vehicles_registered         |
# | ------- | --------- | --------------------------------------- | --------------------------- |
# | u1      | Alice     | [alice@mail.com](mailto:alice@mail.com) | ["veh_1", "veh_2", "veh_3"] |

#Internal Combustion Engine
class Users(Base):
    __tablename__= "UserDetails"
    user_id = Column(String, primary_key=True, index=True)
    user_name = Column(String,unique=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, default="user")

    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow) 
    vehicles_registered= relationship("Vehicles", back_populates="owner", cascade="all, delete-orphan")
class Vehicles(Base):
    __tablename__ = "VehicleDetails"

    vehicle_id=Column(String, primary_key=True,index=True) 
    vehicle_type = Column(String, nullable=False)
    vehicle_class = Column(String, nullable=False)
    vehicle_model = Column(String, nullable=True)
    year_bought = Column(Integer, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    api_key = Column(String, unique=True, nullable=False)    
    # Foreign key to map to User
    owner_id = Column(String, ForeignKey("UserDetails.user_id"), nullable=False)

    # Relationship back to user
    owner = relationship("Users", back_populates="vehicles_registered")
    telemetry = relationship("Telemetry", back_populates="vehicle", cascade="all, delete-orphan")

     


    
# vehicle_id: str
#     timestamp: datetime
#     speed: float
#     odometer: float
#     trip_distance: float
#     idle_time: float
#     altitude: Optional[float] = None
#     latitude: float
#     longitude: float
#     fuel_level: Optional[float] = None
#     fuel_consumption_rate: Optional[float] = None
#     engine_temp: Optional[float] = None
#     battery_voltage: Optional[float] = None
#     battery_temp: Optional[float] = None
#     motor_temp: Optional[float] = None
#     charging_status: Optional[str] = None
#     range_remaining: Optional[float] = None
#     tire_pressure_fl: Optional[float] = None
#     tire_pressure_fr: Optional[float] = None
#     tire_pressure_rl: Optional[float] = None
#     tire_pressure_rr: Optional[float] = None
#     tire_temp_fl: Optional[float] = None
#     tire_temp_fr: Optional[float] = None
#     tire_temp_rl: Optional[float] = None
#     tire_temp_rr: Optional[float] = None
#     door_status: Optional[bool] = None
#     harsh_acceleration: Optional[bool] = None
#     overspeeding: Optional[bool] = None

class Telemetry(Base):
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("VehicleDetails.vehicle_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    speed = Column(Float, nullable=False)
    odometer = Column(Float, nullable=False)
    trip_distance = Column(Float, nullable=False)
    idle_time = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    fuel_level = Column(Float, nullable=True)
    fuel_consumption_rate = Column(Float, nullable=True)
    engine_temp = Column(Float, nullable=True)
    battery_voltage = Column(Float, nullable=True)
    battery_temp = Column(Float, nullable=True)
    motor_temp = Column(Float, nullable=True)
    charging_status = Column(String, nullable=True)
    range_remaining = Column(Float, nullable=True)
    tire_pressure_fl = Column(Float, nullable=True)
    tire_pressure_fr = Column(Float, nullable=True)
    tire_pressure_rl = Column(Float, nullable=True)
    tire_pressure_rr = Column(Float, nullable=True)
    tire_temp_fl = Column(Float, nullable=True)
    tire_temp_fr = Column(Float, nullable=True)
    tire_temp_rl = Column(Float, nullable=True)
    tire_temp_rr = Column(Float, nullable=True)
    door_status = Column(Boolean, nullable=True)
    harsh_acceleration = Column(Boolean, nullable=True)
    overspeeding = Column(Boolean, nullable=True)

    # Relationship back to vehicle
    vehicle = relationship("Vehicles", back_populates="telemetry")

    # Indexes for faster queries
    __table_args__ = (
        Index("idx_vehicle_timestamp", "vehicle_id", "timestamp"),
    )
    


# class Admin(Base):
#     __tablename__="admin"
    
#     id=Column(Integer,primary_key=True, index=True)
#     user_name = Column(String,unique=True, nullable=False)
#     email = Column(String, nullable=False, unique=True)
#     role = Column(String, default="admin")
#     password = Column(String, nullable=False)
    
class Alert(Base):
    __tablename__ ="alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("VehicleDetails.vehicle_id"), nullable=False, index=True)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean,default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)