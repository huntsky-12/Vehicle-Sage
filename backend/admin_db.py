from database import SessionLocal
from model_new import Users

db = SessionLocal()

admin= db.query(Users).all()

for v in admin:
    print(vars(v))