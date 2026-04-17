from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_session
from app.models import User
from typing import Optional
from datetime import datetime, timedelta
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/google/login") # Just for reference

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_or_create_google_user(db: Session, google_data: dict) -> User:
    email = google_data.get("email")
    google_id = google_data.get("sub")
    name = google_data.get("name")
    
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        if not user.google_id:
            user.google_id = google_id
            db.commit()
            db.refresh(user)
        return user
    
    # Create new user
    username = email.split("@")[0]
    # Ensure username is unique
    base_username = username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1
        
    new_user = User(
        id=uuid.uuid4(),
        email=email,
        username=username,
        display_name=name,
        google_id=google_id,
        is_email_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
