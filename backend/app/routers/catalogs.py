"""Catálogos precargados desde el Excel (req. User mgmt 4: listas preloaded)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/catalogs", tags=["catalogs"])


@router.get("/countries", response_model=list[schemas.CatalogItem])
def countries(db: Session = Depends(get_db)):
    return db.scalars(select(models.Country).order_by(models.Country.name)).all()


@router.get("/cities", response_model=list[schemas.CatalogItem])
def cities(db: Session = Depends(get_db), country_id: int | None = None):
    stmt = select(models.City).order_by(models.City.name)
    if country_id:
        stmt = stmt.where(models.City.country_id == country_id)
    return db.scalars(stmt).all()


@router.get("/skills", response_model=list[schemas.CatalogItem])
def skills(db: Session = Depends(get_db)):
    return db.scalars(select(models.Skill).order_by(models.Skill.name)).all()


@router.get("/projects", response_model=list[schemas.CatalogItem])
def projects(db: Session = Depends(get_db)):
    return db.scalars(select(models.Project).order_by(models.Project.name)).all()


@router.get("/leave-types", response_model=list[schemas.LeaveTypeOut])
def leave_types(db: Session = Depends(get_db)):
    return db.scalars(select(models.LeaveType).order_by(models.LeaveType.code)).all()


@router.get("/holidays", response_model=list[schemas.HolidayOut])
def holidays(db: Session = Depends(get_db), country_id: int | None = None):
    stmt = select(models.Holiday).order_by(models.Holiday.date)
    if country_id:
        stmt = stmt.where(models.Holiday.country_id == country_id)
    return db.scalars(stmt).all()
