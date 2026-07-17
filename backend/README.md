# Vacation Planning App — Backend (Fase 1-4)

API REST en FastAPI + SQLAlchemy + SQLite (migrable a PostgreSQL/MSSQL cambiando DATABASE_URL).

## Cómo correrlo
```bash
cd backend
pip install -r requirements.txt
python seed.py                      # una sola vez: catálogos del Excel + admin
uvicorn app.main:app --reload       # API en http://localhost:8000
```
Documentación interactiva (probar endpoints sin frontend): http://localhost:8000/docs

## Credenciales iniciales
- Admin: `admin@dxc.com` / `Admin2026!` (cambiar tras el primer login)
- Los correos (confirmación, reseteo, avisos al admin) se imprimen en la consola del servidor.

## Qué cubre
- **User management**: registro con validación @dxc.com, aprobación por admin antes del primer login, confirmación por email, reseteo self-service, código interno autogenerado, bitácora.
- **Vacation requests**: crear (Draft), Draft→Approved, Approved→Canceled con comentarios obligatorios, cálculo de días hábiles excluyendo fines de semana y feriados del país/ciudad del usuario, acceso solo a solicitudes propias, log por solicitud.
- **Administrator**: filtros por país/ciudad/estado/nombre/apellido, reporte de días por rango, aprobar/rechazar usuarios, editar perfiles, habilitar/deshabilitar acceso, bitácora global.
- **Catálogos del Excel**: 10 países, 8 ciudades, 8 skills, proyectos, 10 tipos de ausencia del tab Legend (con color) y feriados India 2026 por ciudad.

## Pendiente (siguientes fases)
- Frontend React (Fase 5)
- SMTP corporativo real, hosting DXC
