import secrets
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from requests import Session
from . import schemas , models
from .database import get_db
from .config import settings  # Make sure settings is imported from your config module

# OAuth2 scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# JWT configuration constants 
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    
    to_encode = data.copy()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expiry})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception, db):
  
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = str(payload.get("user_id"))
        
        if user_id is None:
            raise credentials_exception
               # 🔍 CRITICAL FIX: Get actual user from database
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    return user  # Return User object, not TokenData!


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db) ):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_access_token(token, credentials_exception, db)


def create_refresh_token(user_id: int, db: Session):
    """Create a new refresh token and save to database"""
    
    # Generate a random string (like a serial number)
    token_value = secrets.token_urlsafe(32)
    
    # Set expiry (7 days from now)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Create database record
    db_token = models.RefreshToken(
        token=token_value,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.add(db_token)
    db.commit()
    
    return token_value

def validate_refresh_token(token: str, db: Session):
    """Check if refresh token is valid and not expired"""
    
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token,
        models.RefreshToken.is_active == True,
        models.RefreshToken.expires_at > datetime.now(timezone.utc)
    ).first()
    
    return db_token

def revoke_refresh_token(token: str, db: Session):
    """Make a refresh token unusable"""
    
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token
    ).first()
    
    if db_token:
        db_token.is_active = False
        db.commit()