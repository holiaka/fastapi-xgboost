from app.utils.rate_limit import rate_limit_dependency
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserLogin, TokenResponse
from app.services.auth_service import AuthService
from app.dependencies import get_db
from app.utils.security import get_current_user
from app.models.user import User
from datetime import datetime
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency),
):
    service = AuthService(db)
    try:
        return service.authenticate_user(user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )


@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency),
):
    service = UserService(db)
    return service.create_user(user)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"Before logout: token={current_user.token}")

    if current_user.token is None or current_user.token_expiration is None:
        return {"message": "Already logged out"}

    current_user.token = None
    current_user.token_expiration = None
    current_user.last_logout_at = datetime.utcnow()

    db.commit()
    db.refresh(current_user)

    print(f"After logout: token={current_user.token}")

    return {"message": "Logged out successfully"}
