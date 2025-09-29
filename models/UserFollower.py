from sqlalchemy import Column, Integer, String, ForeignKey

from sqlalchemy.orm import relationship,declarative_base
from models.user import User, Base

class UserFollower(Base):
    __tablename__ = "user_followers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    follower_id = Column(Integer, ForeignKey("users.id"))

