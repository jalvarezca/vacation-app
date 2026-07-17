# Vacation Planning App · DXC

Aplicación web de planificación de vacaciones. Backend FastAPI + SQLite (migrable a
PostgreSQL/MSSQL), frontend React. Catálogos y feriados precargados desde el Excel
"Out of Office Planner for UAL2026".

## Cómo correr todo (2 terminales)

### Terminal 1 — Backend
```bash
cd backend
pip install -r requirements.txt
python seed.py                     # solo la primera vez
uvicorn app.main:app --reload      # http://localhost:8000  (docs en /docs)
```

### Terminal 2 — Frontend
```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

## Credenciales iniciales
- Administrador: `admin@dxc.com` / `Admin2026!`
- Los correos (confirmación, reseteo, avisos) se imprimen en la consola del backend.

## Flujo de prueba sugerido
1. Entra como admin → pestaña Administración.
2. En otra ventana (incógnito) regístrate como empleado con un correo @dxc.com.
3. Como admin: Usuarios → Aprobar al nuevo empleado.
4. Como empleado: crea una solicitud (ej. 23 al 28 de enero 2026 → calcula 3 días
   hábiles, descontando fin de semana y Republic Day).
5. Márcala aprobada, cancélala con comentario, y revisa la Bitácora como admin.

## Estructura
```
backend/   API REST (auth JWT, solicitudes, admin, catálogos, bitácora)
frontend/  React (login, registro, mis solicitudes, panel admin)
```
