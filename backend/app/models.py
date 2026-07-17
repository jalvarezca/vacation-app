"""Modelo de datos normalizado desde el Excel 'Out of Office Planner'."""
import enum
from datetime import datetime, date

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserRole(str, enum.Enum):
    employee = "employee"
    admin = "admin"


class UserStatus(str, enum.Enum):
    pending = "pending"      # Registrado, esperando aprobación del administrador
    active = "active"
    disabled = "disabled"
    rejected = "rejected"


class RequestStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    canceled = "canceled"


class Country(Base):
    __tablename__ = "countries"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)


class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    country: Mapped["Country"] = relationship()
    __table_args__ = (UniqueConstraint("name", "country_id"),)


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)


class LeaveType(Base):
    """Acrónimos del tab Legend, con color para identificar el estado en la UI."""
    __tablename__ = "leave_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(5), unique=True)   # P, HP, SL, ML...
    name: Mapped[str] = mapped_column(String(120))
    color: Mapped[str] = mapped_column(String(9))               # hex para la UI


class Holiday(Base):
    """Feriados por país (req. 'considerar Holidays por país'). city_id NULL = nacional."""
    __tablename__ = "holidays"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    name: Mapped[str] = mapped_column(String(150))
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    city_id: Mapped[int | None] = mapped_column(ForeignKey("cities.id"), nullable=True)
    country: Mapped["Country"] = relationship()
    city: Mapped["City | None"] = relationship()


class User(Base):
    __tablename__ = "users"
    # 'internal code' del requerimiento 6: este id autogenerado
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    employee_code: Mapped[str] = mapped_column(String(40), unique=True)  # DXC Employee id
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.employee)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.pending)
    email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    country: Mapped["Country"] = relationship()
    city: Mapped["City"] = relationship()
    skill: Mapped["Skill | None"] = relationship()
    project: Mapped["Project | None"] = relationship()
    lead: Mapped["User | None"] = relationship(remote_side=[id])
    requests: Mapped[list["VacationRequest"]] = relationship(back_populates="user")


class VacationRequest(Base):
    __tablename__ = "vacation_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    leave_type_id: Mapped[int] = mapped_column(ForeignKey("leave_types.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    business_days: Mapped[int] = mapped_column(Integer)  # excluye fines de semana y feriados
    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.draft)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancel_comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="requests")
    leave_type: Mapped["LeaveType"] = relationship()


class AuditLog(Base):
    """Bitácora transversal: cubre el requerimiento de log en los 3 módulos."""
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(60), index=True)   # login, request_created, status_changed...
    entity: Mapped[str] = mapped_column(String(40))               # user | vacation_request
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
