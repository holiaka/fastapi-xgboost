from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService
from app.utils.security import get_current_user
from app.dependencies import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/add", response_model=UserRead)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create_user(user_data)

@router.get("/me", response_model=UserRead)
def get_my_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=list[UserRead])
def get_all_users(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return UserService(db).get_all_users()
