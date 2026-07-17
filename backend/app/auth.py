"""Seguridad: hash de contraseñas (bcrypt) y JWT para autorización.

Tras el login el API devuelve un JWT; el frontend lo envía en el header
Authorization: Bearer <token> en cada llamada siguiente (req. 'Other considerations 1').
"""
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models
from .database import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60 * 8   # jornada laboral
RESET_TOKEN_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int, purpose: str = "access", minutes: int = ACCESS_TOKEN_MINUTES) -> str:
    payload = {
        "sub": str(user_id),
        "purpose": purpose,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, purpose: str = "access") -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("purpose") != purpose:
            raise JWTError("Propósito de token inválido")
        return int(payload["sub"])
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido o expirado")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    user_id = decode_token(token)
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no encontrado")
    if user.status != models.UserStatus.active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acceso deshabilitado o pendiente de aprobación")
    return user


def get_current_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != models.UserRole.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Se requieren privilegios de administrador")
    return user
