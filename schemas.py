from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional


class User(BaseModel):
    username: str
    name: str = None

class UserCreate(User):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True

class UserResponse(User):
    id: int
    email: EmailStr
    active: int

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(BaseModel):
    username: Optional[str] = None
    password: str = None
    active: int = True

class TokenData(BaseModel):
    username: Optional[str] = None
    name: str = None