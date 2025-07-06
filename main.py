from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext
import xgboost as xgb
import numpy as np

from app.config import DATABASE_URL, SECRET_KEY

app = FastAPI()

model = xgb.XGBRegressor()
model.load_model("model.json")

security = HTTPBearer()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserLog(Base):
    __tablename__ = "user-log"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


Base.metadata.create_all(bind=engine)


class Features(BaseModel):
    sp: str
    origin: str
    h: float
    dbh: float
    ba: float


class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return credentials.credentials


@app.post("/login")
def login(user: UserLogin):
    db = SessionLocal()
    db_user = db.query(UserLog).filter(UserLog.email == user.email).first()
    db.close()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return {"access_token": SECRET_KEY}


@app.post("/predict")
def predict(data: Features, token: str = Depends(get_current_token)):
    features_array = np.array(
        [[float(data.sp), float(data.origin), data.h, data.dbh, data.ba]]
    )
    prediction = model.predict(features_array)
    return {"prediction": prediction.tolist()}


@app.post("/users/add")
def add_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db = SessionLocal()
    db_user = UserLog(
        name=user.name, surname=user.surname, email=user.email, password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return {
        "id": db_user.id,
        "name": db_user.name,
        "surname": db_user.surname,
        "email": db_user.email,
    }


@app.get("/users")
def get_users(token: str = Depends(get_current_token)):
    db = SessionLocal()
    users = db.query(UserLog).all()
    result = [
        {"id": u.id, "name": u.name, "surname": u.surname, "email": u.email}
        for u in users
    ]
    db.close()
    return result
