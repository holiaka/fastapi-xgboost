from app.utils.rate_limit import rate_limit_dependency
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserLogin, TokenResponse
from app.services.auth_service import AuthService
from app.dependencies import get_db

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


from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.schemas.user import UserResponse


@router.post("/register", response_model=UserResponse)
def register(
    user: UserLogin,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency),
):
    service = UserService(db)
    return service.create_user(user)
