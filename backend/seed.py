"""Precarga la base de datos con los catálogos extraídos del Excel
'Out of Office Planner for UAL2026.xlsx' (seed_data.json) y crea el
usuario administrador inicial.

Correr una sola vez:  python seed.py
"""
import json
from datetime import date

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app import models

ADMIN_EMAIL = "admin@dxc.com"
ADMIN_PASSWORD = "Admin2026!"  # cambiar tras el primer login

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(models.Country).count() > 0:
    print("La base ya tiene datos. Nada que hacer.")
    raise SystemExit

with open("seed_data.json", encoding="utf-8") as f:
    data = json.load(f)

# Países
countries = {}
for name in data["countries"]:
    c = models.Country(name=name)
    db.add(c)
    countries[name] = c
db.flush()

# Ciudades (todas las del planner pertenecen a India)
cities = {}
for name in data["cities"]:
    country = countries[data["city_country"].get(name, "India")]
    city = models.City(name=name, country_id=country.id)
    db.add(city)
    cities[name] = city
db.flush()

# Skills y proyectos
for name in data["skills"]:
    db.add(models.Skill(name=name))
seen = set()
for name in data["projects"]:
    key = name.lower()
    if key not in seen:  # evita duplicados tipo 'Moved Out' / 'Moved out'
        seen.add(key)
        db.add(models.Project(name=name))

# Tipos de ausencia (Legend) con color para la UI
for lt in data["leave_types"]:
    db.add(models.LeaveType(code=lt["code"], name=lt["name"], color=lt["color"]))

# Feriados India 2026 (nacionales y por ciudad)
for h in data["holidays"]:
    d = date.fromisoformat(h["date"])
    country_id = countries[h["country"]].id
    if h["cities"]:
        for city_name in h["cities"]:
            if city_name in cities:
                db.add(models.Holiday(date=d, name=h["name"], country_id=country_id,
                                      city_id=cities[city_name].id))
    else:
        db.add(models.Holiday(date=d, name=h["name"], country_id=country_id))
db.flush()

# Administrador inicial
india = countries["India"]
admin = models.User(
    email=ADMIN_EMAIL,
    hashed_password=hash_password(ADMIN_PASSWORD),
    first_name="Admin",
    last_name="DXC",
    employee_code="ADMIN-001",
    role=models.UserRole.admin,
    status=models.UserStatus.active,
    email_confirmed=True,
    country_id=india.id,
    city_id=cities["Bangalore"].id,
)
db.add(admin)
db.commit()

print(f"Seed completo: {len(countries)} países, {len(cities)} ciudades, "
      f"{len(data['skills'])} skills, {len(data['leave_types'])} tipos de ausencia, "
      f"feriados 2026 cargados.")
print(f"Admin inicial: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
