"""Bitácora, notificaciones (simuladas) y cálculo de días hábiles."""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


def audit(db: Session, action: str, entity: str, entity_id: int | None = None,
          actor_id: int | None = None, detail: str | None = None) -> None:
    """Registra una transacción en la bitácora (requisito en los 3 módulos)."""
    db.add(models.AuditLog(action=action, entity=entity, entity_id=entity_id,
                           actor_user_id=actor_id, detail=detail))


def send_email(to: str, subject: str, body: str) -> None:
    """Simulación de correo. En producción se conecta al SMTP corporativo de DXC.

    En el prototipo el 'correo' se imprime en la consola del servidor para
    poder probar los flujos de confirmación, reseteo y avisos a administradores.
    """
    print(f"\n=== EMAIL (simulado) ===\nPara: {to}\nAsunto: {subject}\n{body}\n========================\n")


def business_days(db: Session, user: models.User, start: date, end: date) -> int:
    """Días hábiles del rango: excluye sábados, domingos y feriados del país
    del usuario (nacionales o de su ciudad)."""
    stmt = select(models.Holiday.date).where(
        models.Holiday.country_id == user.country_id,
        models.Holiday.date >= start,
        models.Holiday.date <= end,
        (models.Holiday.city_id.is_(None)) | (models.Holiday.city_id == user.city_id),
    )
    holidays = {d for (d,) in db.execute(stmt)}
    count, day = 0, start
    while day <= end:
        if day.weekday() < 5 and day not in holidays:
            count += 1
        day += timedelta(days=1)
    return count
