from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey,Text
from sqlalchemy.orm import relationship,declarative_base

from models.user import User, Base


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)

    user_id = Column(Integer, ForeignKey(User.id),nullable=False)

    author = relationship(User, backref="posts")