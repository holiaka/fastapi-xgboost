from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdateSecure
from app.utils.password import verify_password, hash_password
from datetime import datetime


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        # 🔍 Перевірка: чи існує вже користувач з таким email
        existing_user = self.db.query(User).filter_by(email=user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Користувач з таким email вже існує"
            )

        # 🛠 Створення користувача
        user = User(
            name=user_data.name,
            surname=user_data.surname,
            email=user_data.email,
            password=hash_password(user_data.password),
            country=user_data.country,
            comment=user_data.comment,
            created_at=datetime.utcnow(),
        )
        self.db.add(user)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Помилка при створенні користувача"
            )

        self.db.refresh(user)
        return user

    def get_all_users(self):
        return self.db.query(User).all()

    def update_current_user_fields(
        self, user: User, user_data: UserUpdateSecure
    ) -> User:
        # 🛡️ Перевірка старого паролю
        if not verify_password(user_data.old_password, user.password):
            raise HTTPException(status_code=403, detail="Невірний поточний пароль")

        update_fields = user_data.dict(exclude_unset=True, exclude={"old_password"})

        for field, value in update_fields.items():
            if field == "password" and value:
                setattr(user, "password", hash_password(value))
            elif value is not None:
                setattr(user, field, value)

        user.last_login_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
