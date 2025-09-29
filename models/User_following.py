from sqlalchemy import Column, Integer, String, ForeignKey

from sqlalchemy.orm import relationship,declarative_base
from models.user import User, Base

class UserFollowing(Base):
    __tablename__ = "user_followings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))

