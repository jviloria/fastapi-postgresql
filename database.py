from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import os

try:
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
except Exception as e:
    POSTGRES_PASSWORD = 1234567


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:%s@localhost/daten" % POSTGRES_PASSWORD
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234567@localhost/daten"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
