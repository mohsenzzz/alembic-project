import datetime

from sqlalchemy import  Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50),unique=True,nullable=False)
    hashed_password = Column(String(50),nullable=False)
    email = Column(String(100),unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", backref="user", cascade="all, delete-orphan")