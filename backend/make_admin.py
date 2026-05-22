from database import SessionLocal
import model_new

db = SessionLocal()

user = (
    db.query(model_new.Users)
    .filter_by(user_name="madmax")
    .first()
)

print(user.role)   # check current value

user.role = "admin"

db.commit()

print(user.role)

db.close()