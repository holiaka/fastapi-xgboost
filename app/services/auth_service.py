from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.utils.password import verify_password
from app.utils.jwt import create_access_token
from app.schemas.user import UserLogin, TokenResponse
from app.models.user import User
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, user_data: UserLogin) -> TokenResponse:
        user = self.db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, user.password):
            raise ValueError("Invalid credentials")

        user.update_last_login()
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires)
        user.token = token
        user.token_expiration = datetime.utcnow() + access_token_expires

        self.db.commit()
        return TokenResponse(access_token=token)
