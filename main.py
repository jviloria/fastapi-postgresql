import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from database import get_db, SQLAlchemyError, Session
from models import UserModel
from schemas import UserCreate, UserResponse, UserUpdate, ValidationError,\
    Token, UserInDB, User, TokenData
from typing import List, Optional
from utils import model2Dict, failedMessage, successMessage, encryptPassword,\
    pwd_context, loadConfig
from starlette.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

config = loadConfig()
# Secret key, Must be in environment variable
SECRET_KEY = config['SECRET_KEY']
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = config['ACCESS_TOKEN_EXPIRE_MINUTES']

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(db, username):
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user(db, username: str):
    user = get_user_by_username(db, username)
    if not user: return None
    user_dict = model2Dict(user)
    return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# ROUTES
#============================
@app.get("/")
def root():
    return RedirectResponse(url="/docs/")

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = 
    Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/user/") #, response_model=UserCreate)
async def create_user(User: UserCreate, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    try:
        user = UserModel(**User.dict())
        user.password = encryptPassword(user.password)
        db.add(user)
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as e:
        raise Exception(e)
    return user

@app.get("/user/list/", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    res = db.query(UserModel).all()
    return res

@app.get("/user/{user_id}")
async def get_userdata(user_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    try:
        res = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not res:
            return failedMessage('Registro no existe')
    except SQLAlchemyError as e:
        raise Exception(e)
    try:
        model_dict = model2Dict(res)
        res = UserResponse(**model_dict)
    except ValidationError as e:
        return failedMessage(e)
    return res

@app.put("/user/{user_id}")
async def update_user(user_id: int, User: UserUpdate, 
    db: Session = Depends(get_db), current_user: \
    User = Depends(get_current_active_user)):
    try:
        if not db.query(UserModel).filter(UserModel.id == user_id).first():
            return failedMessage('Registro no existe')
        res = db.query(UserModel).filter(UserModel.id == user_id).\
            update({UserModel.name: User.name, UserModel.email: User.email})
        db.commit()
        model_dict = model2Dict(db.query(UserModel).
            filter(UserModel.id == user_id).first())
        res = UserResponse(**model_dict)
    except SQLAlchemyError as e:
        raise Exception(e)
    return res

@app.delete("/user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    try:
        if not db.query(UserModel).filter(UserModel.id == user_id).first():
            raise Exception('Registro no existe')
        res = db.query(UserModel).filter(UserModel.id == user_id).delete()
        db.commit()
        res = successMessage()
    except Exception as e:
        return failedMessage(e)
    return res


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
