from sqlalchemy import Column, Integer, String, \
    Sequence, DateTime, Boolean
from database import Base, engine

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
    active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)
