"""Módulo Vacation requests: CRUD con estados Draft → Approved → Canceled.

El usuario solo ve y modifica sus propias solicitudes (req. Vacation 5).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..utils import audit, business_days

router = APIRouter(prefix="/api/requests", tags=["requests"])

# Transiciones permitidas de la máquina de estados
ALLOWED = {
    models.RequestStatus.draft: {models.RequestStatus.approved, models.RequestStatus.canceled},
    models.RequestStatus.approved: {models.RequestStatus.canceled},
    models.RequestStatus.canceled: set(),
}


def _own_request(req_id: int, user: models.User, db: Session) -> models.VacationRequest:
    req = db.get(models.VacationRequest, req_id)
    if not req or req.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Solicitud no encontrada")
    return req


@router.get("", response_model=list[schemas.RequestOut])
def my_requests(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = (select(models.VacationRequest)
            .where(models.VacationRequest.user_id == user.id)
            .order_by(models.VacationRequest.start_date.desc()))
    return db.scalars(stmt).all()


@router.post("", response_model=schemas.RequestOut, status_code=201)
def create_request(data: schemas.RequestCreate,
                   user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    if not db.get(models.LeaveType, data.leave_type_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de ausencia inválido")
    days = business_days(db, user, data.start_date, data.end_date)
    req = models.VacationRequest(
        user_id=user.id,
        leave_type_id=data.leave_type_id,
        start_date=data.start_date,
        end_date=data.end_date,
        business_days=days,
        comments=data.comments,
    )
    db.add(req)
    db.flush()
    audit(db, "request_created", "vacation_request", req.id, actor_id=user.id,
          detail=f"{data.start_date} a {data.end_date} ({days} días hábiles)")
    db.commit()
    db.refresh(req)
    return req


@router.patch("/{req_id}/status", response_model=schemas.RequestOut)
def change_status(req_id: int, data: schemas.RequestStatusChange,
                  user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """El usuario marca Approved cuando el proceso externo lo revisa (req. Vacation 2),
    o Canceled con comentarios una vez aprobada (req. Vacation 3)."""
    req = _own_request(req_id, user, db)
    if data.status not in ALLOWED[req.status]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"No se puede pasar de {req.status.value} a {data.status.value}")
    if data.status == models.RequestStatus.canceled:
        if not data.comments:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "Cancelar requiere comentarios (req. Vacation 3)")
        req.cancel_comments = data.comments
    old = req.status
    req.status = data.status
    audit(db, "request_status_changed", "vacation_request", req.id, actor_id=user.id,
          detail=f"{old.value} → {data.status.value}")
    db.commit()
    db.refresh(req)
    return req


@router.get("/{req_id}/log", response_model=list[schemas.AuditOut])
def request_log(req_id: int, user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    """Bitácora de la solicitud: creación, cambios de estado (req. Vacation 4)."""
    _own_request(req_id, user, db)
    stmt = (select(models.AuditLog)
            .where(models.AuditLog.entity == "vacation_request",
                   models.AuditLog.entity_id == req_id)
            .order_by(models.AuditLog.timestamp))
    return db.scalars(stmt).all()
