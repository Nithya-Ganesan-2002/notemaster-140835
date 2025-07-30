# Authentication logic, utils and password hashing

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.api.db import User
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "CHANGEME_SECRET"  # Should be set via env var for production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*3  # 3 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# PUBLIC_INTERFACE
def verify_password(plain_password, hashed_password):
    """Verifies a plain password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

# PUBLIC_INTERFACE
def get_password_hash(password):
    """Returns hashed version of password."""
    return pwd_context.hash(password)

# PUBLIC_INTERFACE
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Validates user email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
