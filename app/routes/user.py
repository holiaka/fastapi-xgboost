from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdateSecure, UserRead
from app.services.user_service import UserService
from app.utils.security import get_current_user
from app.dependencies import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_my_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/update-me", response_model=UserRead)
def update_own_account(
    user_data: UserUpdateSecure,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService(db).update_current_user_fields(current_user, user_data)
