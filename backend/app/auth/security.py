from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _crear_token(data: dict, tipo: str, minutos: int) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=minutos)
    to_encode.update({"exp": expire, "type": tipo})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(data: dict) -> str:
    return _crear_token(data, "access", settings.access_token_expire_minutes)


def create_refresh_token(data: dict) -> str:
    return _crear_token(data, "refresh", settings.refresh_token_expire_minutes)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None