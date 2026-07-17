# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Vacation Planning App for DXC: FastAPI + SQLAlchemy + SQLite backend, React (Vite, no router library) frontend. Catalogs (countries, cities, skills, projects, leave types) and 2026 India holidays are preloaded from an Excel export ("Out of Office Planner for UAL2026") via `backend/seed_data.json`.

Code comments, docstrings, and user-facing strings are in Spanish; this is intentional — match that convention when editing existing files.

## Commands

### Backend (from `backend/`)
```bash
pip install -r requirements.txt
python seed.py                       # one-time: loads catalogs/holidays + admin user (no-ops if DB already has data)
uvicorn app.main:app --reload        # http://localhost:8000, interactive docs at /docs
```
There is no test suite and no lint/format tooling configured for the backend.

### Frontend (from `frontend/`)
```bash
npm install
npm run dev                          # http://localhost:5173
npm run build
npm run preview
```
There is no test suite and no lint/format tooling configured for the frontend.

### Seed / reset data
`seed.py` is a no-op once any `Country` row exists. To re-seed from scratch, delete `backend/vacation_app.db` (SQLite file, gitignored) and rerun `python seed.py`.

### Initial credentials (created by seed.py)
`admin@dxc.com` / `Admin2026!`. Emails (confirmation, password reset, admin notifications) are not actually sent — `utils.send_email` just prints them to the backend console.

## Architecture

### Backend (`backend/app/`)
- `database.py` — SQLAlchemy engine/session. `DATABASE_URL` env var defaults to local SQLite; swapping to Postgres/MSSQL is meant to be a connection-string change only, no code changes.
- `models.py` — all ORM models in one file: `Country`/`City`/`Skill`/`Project`/`LeaveType`/`Holiday` (catalogs), `User`, `VacationRequest`, `AuditLog`.
- `schemas.py` — Pydantic request/response models. Registration enforces `@dxc.com` email domain (`ALLOWED_DOMAIN` in this file) and an 8-char minimum password.
- `auth.py` — bcrypt password hashing + JWT (`python-jose`). `get_current_user` / `get_current_admin` are the FastAPI dependencies routers use for auth; a user's `status` must be `active` to pass `get_current_user`.
- `utils.py` — three cross-cutting helpers used by every router: `audit()` (writes to `AuditLog`, called on nearly every mutation), `send_email()` (console-only stub), `business_days()` (computes working days between two dates, excluding weekends and holidays scoped to the user's country/city).
- `routers/auth.py` — registration, email confirmation, login, password reset, `/me`. New users start in `pending` status and cannot log in until an admin approves them.
- `routers/requests.py` — vacation request CRUD, scoped to `request.user.id == current_user.id` (users cannot see or modify others' requests). Status transitions are governed by the `ALLOWED` state machine at the top of the file: `draft → approved|canceled`, `approved → canceled`, `canceled` is terminal. Canceling requires a `comments` value.
- `routers/admin.py` — all routes require `get_current_admin`. Covers cross-user request listing/filtering, a days-report aggregate, user approve/reject/edit, and the global audit log.
- `routers/catalogs.py` — read-only lookups for countries/cities/skills/projects/leave-types/holidays, used by the frontend to populate dropdowns.
- `main.py` — wires routers, runs `Base.metadata.create_all` on startup (no migration framework — schema changes require a fresh DB or manual ALTERs), and configures CORS from the `CORS_ORIGINS` env var (comma-separated; defaults to the local Vite ports).

Business-rule notes worth knowing before changing request logic:
- `business_days()` in `utils.py` is the single source of truth for day counting; it's called both when creating a request and would need to be called again if editing were ever added (currently requests aren't editable, only status-transitioned).
- Holidays apply if `city_id IS NULL` (national) or matches the user's `city_id`, and only within the user's `country_id`.

### Frontend (`frontend/src/`)
- No React Router — `App.jsx` holds a `view` string in state (`login | register | requests | admin`) and conditionally renders pages; navigation is just `setView(...)` calls.
- `api.js` — the only HTTP client. Wraps `fetch`, injects the `Authorization: Bearer` header from an in-memory token mirrored to `localStorage`, and throws on non-OK responses using the FastAPI error `detail` shape. `VITE_API_URL` env var points at the backend (defaults to `http://localhost:8000`).
- `pages/` — one file per view (`Login`, `Register`, `Requests`, `Admin`); `components/shared.jsx` holds small cross-page UI pieces.
- Auth/session state (`user`, JWT) lives in `App.jsx` and is passed down via props — there is no global store.

## Deployment

`render.yaml` defines a Render.com Blueprint with two free-tier services: `vacation-planner-api-dxc` (backend, runs `python seed.py` on every boot since the free-tier disk is ephemeral) and `vacation-planner-web-dxc` (static frontend build, gets `VITE_API_URL` wired to the API service's URL automatically). See `DEPLOY.md` for the full walkthrough.
