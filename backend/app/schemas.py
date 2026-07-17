"""Esquemas de validación (Pydantic) para el API."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from .models import RequestStatus, UserRole, UserStatus

ALLOWED_DOMAIN = "dxc.com"


# ---------- Catálogos ----------
class CatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class LeaveTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    name: str
    color: str


class HolidayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    name: str
    country_id: int
    city_id: int | None


# ---------- Usuarios / Auth ----------
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    employee_code: str
    country_id: int
    city_id: int
    skill_id: int | None = None
    project_id: int | None = None
    gender: str | None = None

    @field_validator("email")
    @classmethod
    def corporate_email(cls, v: str) -> str:
        if not v.lower().endswith("@" + ALLOWED_DOMAIN):
            raise ValueError(f"Debe usar el correo corporativo @{ALLOWED_DOMAIN}")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    first_name: str
    last_name: str
    employee_code: str
    gender: str | None
    role: UserRole
    status: UserStatus
    country_id: int
    city_id: int
    skill_id: int | None
    project_id: int | None
    lead_id: int | None
    created_at: datetime


class UserUpdate(BaseModel):
    """Edición de perfil por administrador (req. Admin 5)."""
    first_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    country_id: int | None = None
    city_id: int | None = None
    skill_id: int | None = None
    project_id: int | None = None
    lead_id: int | None = None
    role: UserRole | None = None
    status: UserStatus | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


# ---------- Solicitudes ----------
class RequestCreate(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    comments: str | None = None

    @field_validator("end_date")
    @classmethod
    def valid_range(cls, v: date, info) -> date:
        start = info.data.get("start_date")
        if start and v < start:
            raise ValueError("La fecha final no puede ser anterior a la inicial")
        return v


class RequestStatusChange(BaseModel):
    status: RequestStatus
    comments: str | None = None


class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    leave_type: LeaveTypeOut
    start_date: date
    end_date: date
    business_days: int
    status: RequestStatus
    comments: str | None
    cancel_comments: str | None
    created_at: datetime
    updated_at: datetime


class RequestAdminOut(RequestOut):
    user: UserOut


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime
    actor_user_id: int | None
    action: str
    entity: str
    entity_id: int | None
    detail: str | None


class DaysReport(BaseModel):
    """Req. Admin 3: días solicitados en un rango de fechas."""
    start_date: date
    end_date: date
    total_business_days: int
    total_requests: int
