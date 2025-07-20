from sqlalchemy import Column, Integer, String, DateTime, Interval
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    country = Column(String, default="")
    comment = Column(String, default="")
    token = Column(String, nullable=True)
    token_expiration = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    total_active_time = Column(Interval, default=timedelta())

    def update_last_login(self):
        self.last_login_at = datetime.utcnow()

    def add_active_time(self, duration: timedelta):
        self.total_active_time += duration
