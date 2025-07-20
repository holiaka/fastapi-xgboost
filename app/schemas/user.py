from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    country: str
    comment: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    surname: str
    country: str
    comment: str
    created_at: datetime
    last_login_at: Optional[datetime]
    total_active_time: Optional[timedelta]

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    surname: str

    class Config:
        orm_mode = True  # або from_attributes = True для Pydantic v2


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdateSecure(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    password: Optional[str] = None  # новий пароль (якщо змінюється)
    country: Optional[str] = None
    comment: Optional[str] = None
    old_password: str  # 🛡️ обов’язково для перевірки
