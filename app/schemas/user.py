from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    role: str
    created_at: datetime
    last_login_at: Optional[datetime]
    total_active_time: Optional[timedelta]

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    class Config:
        orm_mode = True  # або from_attributes = True для Pydantic v2


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
