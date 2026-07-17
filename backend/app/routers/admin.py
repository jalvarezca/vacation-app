"""Módulo Administrator: revisión de solicitudes, reportes y gestión de usuarios."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_admin
from ..database import get_db
from ..utils import audit, send_email

router = APIRouter(prefix="/api/admin", tags=["admin"],
                   dependencies=[Depends(get_current_admin)])


@router.get("/requests", response_model=list[schemas.RequestAdminOut])
def all_requests(
    db: Session = Depends(get_db),
    country_id: int | None = None,
    city_id: int | None = None,
    req_status: models.RequestStatus | None = Query(None, alias="status"),
    first_name: str | None = None,
    last_name: str | None = None,
):
    """Req. Admin 1-2: cualquier solicitud, filtrada por país, ciudad, estado,
    nombre o apellido del empleado."""
    stmt = select(models.VacationRequest).join(models.User)
    if country_id:
        stmt = stmt.where(models.User.country_id == country_id)
    if city_id:
        stmt = stmt.where(models.User.city_id == city_id)
    if req_status:
        stmt = stmt.where(models.VacationRequest.status == req_status)
    if first_name:
        stmt = stmt.where(models.User.first_name.ilike(f"%{first_name}%"))
    if last_name:
        stmt = stmt.where(models.User.last_name.ilike(f"%{last_name}%"))
    return db.scalars(stmt.order_by(models.VacationRequest.start_date.desc())).all()


@router.get("/reports/days", response_model=schemas.DaysReport)
def days_report(start_date: date, end_date: date, db: Session = Depends(get_db)):
    """Req. Admin 3: número de días solicitados en un rango de fechas."""
    stmt = select(
        func.coalesce(func.sum(models.VacationRequest.business_days), 0),
        func.count(models.VacationRequest.id),
    ).where(
        models.VacationRequest.start_date <= end_date,
        models.VacationRequest.end_date >= start_date,
        models.VacationRequest.status != models.RequestStatus.canceled,
    )
    total_days, total_reqs = db.execute(stmt).one()
    return schemas.DaysReport(start_date=start_date, end_date=end_date,
                              total_business_days=total_days, total_requests=total_reqs)


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db),
               user_status: models.UserStatus | None = Query(None, alias="status")):
    stmt = select(models.User).order_by(models.User.created_at.desc())
    if user_status:
        stmt = stmt.where(models.User.status == user_status)
    return db.scalars(stmt).all()


@router.post("/users/{user_id}/approve", response_model=schemas.UserOut)
def approve_user(user_id: int, admin: models.User = Depends(get_current_admin),
                 db: Session = Depends(get_db)):
    """Req. Admin 4: aprobar el acceso de un usuario nuevo."""
    user = _get_user(user_id, db)
    user.status = models.UserStatus.active
    send_email(user.email, "Acceso aprobado", "Tu acceso a la app de vacaciones fue aprobado.")
    audit(db, "user_approved", "user", user.id, actor_id=admin.id)
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/reject", response_model=schemas.UserOut)
def reject_user(user_id: int, admin: models.User = Depends(get_current_admin),
                db: Session = Depends(get_db)):
    """Req. Admin 4: rechazar el acceso de un usuario nuevo."""
    user = _get_user(user_id, db)
    user.status = models.UserStatus.rejected
    send_email(user.email, "Acceso rechazado", "Tu solicitud de acceso fue rechazada.")
    audit(db, "user_rejected", "user", user.id, actor_id=admin.id)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, data: schemas.UserUpdate,
                admin: models.User = Depends(get_current_admin),
                db: Session = Depends(get_db)):
    """Req. Admin 5: editar cualquier perfil y habilitar/deshabilitar el acceso
    (enviando status active/disabled)."""
    user = _get_user(user_id, db)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(user, field, value)
    audit(db, "user_updated", "user", user.id, actor_id=admin.id, detail=str(changes))
    db.commit()
    db.refresh(user)
    return user


@router.get("/audit", response_model=list[schemas.AuditOut])
def audit_log(db: Session = Depends(get_db), limit: int = 200):
    """Req. Admin 6: bitácora de todas las transacciones."""
    stmt = select(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(limit)
    return db.scalars(stmt).all()


def _get_user(user_id: int, db: Session) -> models.User:
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return user
