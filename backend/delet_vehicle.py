from database import SessionLocal
from model_new import Vehicles
def delete(vehicle_id):
    db=SessionLocal()

    vehicle=db.query(Vehicles).filter_by(vehicle_id=vehicle_id).first()
    db.delete(vehicle)
    db.commit()
    


def change_type(vehicle_id):
    db=SessionLocal()
    vehicle=db.query(Vehicles).filter_by(vehicle_id=vehicle_id).first()
    vehicle.vehicle_type='EV'
    db.commit()
change_type("nurburing_veh1")
    
    