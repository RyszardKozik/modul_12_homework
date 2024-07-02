# Import necessary modules
from datetime import datetime, timedelta
from typing import Union

# Import FastAPI modules
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Import JWT-related modules
from jose import JWTError, jwt

# Import password hashing module
from passlib.context import CryptContext

# Import Pydantic module for defining models
from pydantic import BaseModel

# Import SQLAlchemy session and User model from db.py
from sqlalchemy.orm import Session
from db import SessionLocal, get_db
from models import User
from config import settings

# Define authentication class
class Auth:
    # Initialize password hashing context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Set JWT secret key and algorithm
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    
    # Set expiration time for access token
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    # Initialize OAuth2PasswordBearer for token authentication
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    # Define method to verify password
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return Auth.pwd_context.hash(plain_password, hashed_password)

    # Define method to hash password
    @staticmethod
    def get_password_hash(password: str):
        return Auth.pwd_context.hash(password)

# Define Pydantic model for token
class Token(BaseModel):
    access_token: str
    token_type: str

# Define Pydantic model for token data
class TokenData(BaseModel):
    email: Union[str, None] = None

# Define function to create a new access token
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Auth.SECRET_KEY, algorithm=Auth.ALGORITHM)
    return encoded_jwt

# Define function to create a new refresh token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
    encoded_jwt = jwt.encode(to_encode, Auth.SECRET_KEY, algorithm=Auth.ALGORITHM)
    return encoded_jwt

# Define function to extract email from refresh token
def get_email_from_refresh_token(token: str):
    try:
        payload = jwt.decode(token, Auth.SECRET_KEY, algorithms=[Auth.ALGORITHM])
        if payload['scope'] == 'refresh_token':
            email: str = payload.get("sub")
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, Auth.SECRET_KEY, algorithms=[Auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    return token_data

# Define function to create a new user in the database
def create_user(db: Session, user: User):
    hashed_password = Auth.get_password_hash(user.hashed_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Define function to retrieve a user from the database by email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Define function to authenticate user based on email and password
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not Auth.verify_password(password, user.hashed_password):
        return False
    return user

# Define function to get current authenticated user based on JWT token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(Auth.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, Auth.SECRET_KEY, algorithms=[Auth.ALGORITHM])
        if payload['scope'] == 'access_token':
            email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return user

# Dependency to get current user based on JWT token
def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

# Instantiate Auth class for use in the application
auth_service = Auth()
