from database import SessionLocal
from model_new import Vehicles

db = SessionLocal()

vehicles = db.query(Vehicles).all()

for v in vehicles:
    print(vars(v))