from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from app.utils.jwt import decode_token
from app.models.user import User
from app.dependencies import get_db

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user or user.token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if user.token_expiration and datetime.utcnow() > user.token_expiration:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    now = datetime.utcnow()
    if user.last_login_at:
        session_duration = now - user.last_login_at
        user.add_active_time(session_duration)
    user.last_login_at = now

    db.commit()
    return user
