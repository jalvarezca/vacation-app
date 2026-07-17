"""Módulo User management: registro, confirmación, login y reseteo de contraseña."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import (
    RESET_TOKEN_MINUTES, create_token, decode_token, get_current_user,
    hash_password, verify_password,
)
from ..database import get_db
from ..utils import audit, send_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(data: schemas.UserRegister, db: Session = Depends(get_db)):
    """Registro con correo @dxc.com. El usuario queda 'pending' hasta que un
    administrador apruebe su acceso (req. User mgmt 3 y Admin 4)."""
    if db.scalar(select(models.User).where(models.User.email == data.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya está registrado")
    if db.scalar(select(models.User).where(models.User.employee_code == data.employee_code)):
        raise HTTPException(status.HTTP_409_CONFLICT, "El código de empleado ya está registrado")
    city = db.get(models.City, data.city_id)
    if not city or city.country_id != data.country_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "La ciudad no pertenece al país seleccionado")

    user = models.User(
        email=data.email,
        hashed_password=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        employee_code=data.employee_code,
        gender=data.gender,
        country_id=data.country_id,
        city_id=data.city_id,
        skill_id=data.skill_id,
        project_id=data.project_id,
    )
    db.add(user)
    db.flush()  # asigna el id (el 'internal code' del req. 6)

    # Correo de confirmación al usuario (req. User mgmt 5)
    confirm_token = create_token(user.id, purpose="confirm", minutes=60 * 24)
    send_email(user.email, "Confirma tu registro",
               f"Confirma tu correo con este token: {confirm_token}")

    # Aviso a todos los administradores (req. Admin 4)
    admins = db.scalars(select(models.User).where(models.User.role == models.UserRole.admin)).all()
    for a in admins:
        send_email(a.email, "Nuevo usuario pendiente de aprobación",
                   f"{user.first_name} {user.last_name} ({user.email}) espera aprobación.")

    audit(db, "user_registered", "user", user.id, actor_id=user.id)
    db.commit()
    db.refresh(user)
    return user


@router.post("/confirm-email")
def confirm_email(token: str, db: Session = Depends(get_db)):
    user_id = decode_token(token, purpose="confirm")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    user.email_confirmed = True
    audit(db, "email_confirmed", "user", user.id, actor_id=user.id)
    db.commit()
    return {"message": "Correo confirmado. Tu acceso será habilitado cuando un administrador lo apruebe."}


@router.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")
    if user.status == models.UserStatus.pending:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tu acceso aún no ha sido aprobado por un administrador")
    if user.status in (models.UserStatus.disabled, models.UserStatus.rejected):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tu acceso está deshabilitado")

    audit(db, "login", "user", user.id, actor_id=user.id)
    db.commit()
    return schemas.TokenOut(access_token=create_token(user.id), user=user)


@router.post("/password-reset/request")
def password_reset_request(data: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    """Self-service password reset (req. User mgmt 2)."""
    user = db.scalar(select(models.User).where(models.User.email == data.email.lower()))
    if user:
        token = create_token(user.id, purpose="reset", minutes=RESET_TOKEN_MINUTES)
        send_email(user.email, "Reseteo de contraseña",
                   f"Usa este token para restablecer tu contraseña (30 min): {token}")
        audit(db, "password_reset_requested", "user", user.id)
        db.commit()
    # Respuesta idéntica exista o no el correo, para no revelar cuentas
    return {"message": "Si el correo existe, se envió un enlace de reseteo"}


@router.post("/password-reset/confirm")
def password_reset_confirm(data: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    user_id = decode_token(data.token, purpose="reset")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if len(data.new_password) < 8:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "La contraseña debe tener al menos 8 caracteres")
    user.hashed_password = hash_password(data.new_password)
    audit(db, "password_reset", "user", user.id, actor_id=user.id)
    db.commit()
    return {"message": "Contraseña actualizada"}


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user
