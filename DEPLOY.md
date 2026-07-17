# Publicar en Render.com (gratis) — pasos

## 1. Sube el proyecto a GitHub (una sola vez, desde tu laptop)
```bash
cd vacation-app
git init
git add .
git commit -m "Vacation Planning App - prototipo"
```
Crea un repositorio vacío en github.com (puede ser privado) y luego:
```bash
git remote add origin https://github.com/TU_USUARIO/vacation-app.git
git branch -M main
git push -u origin main
```

## 2. Despliega en Render
1. Entra a https://render.com y crea la cuenta gratis con tu GitHub.
2. Botón **New +** → **Blueprint** → selecciona el repo `vacation-app`.
3. Render lee `render.yaml` y crea los dos servicios. Clic en **Apply**.
4. En 3-5 minutos tendrás dos URLs:
   - Frontend: `https://vacation-planner-web-dxc.onrender.com`  ← esta compartes con tu equipo
   - API: `https://vacation-planner-api-dxc.onrender.com/docs`
   (Si un nombre estaba ocupado, Render te pedirá cambiarlo en render.yaml.)

## 3. Prueba
Entra al frontend con `admin@dxc.com` / `Admin2026!` y sigue el flujo del README.

## Limitaciones del plan gratuito (bien para pruebas, no para producción)
- El backend **se duerme tras 15 min sin uso**: la primera petición tarda ~1 minuto
  en despertar. Avísale al equipo para que no piensen que está caído.
- El disco es **efímero**: usuarios y solicitudes de prueba se borran cuando el
  servicio se reinicia o se vuelve a desplegar. El seed recrea catálogos, feriados
  y el admin automáticamente en cada arranque, así que la app siempre queda usable.
- Para datos persistentes: agregar el PostgreSQL de Render (gratis 30 días) y
  apuntar DATABASE_URL a él — un cambio de variable de entorno, sin tocar código.

## Nota de datos
Es un ambiente público de pruebas: usen contraseñas de prueba y eviten cargar
datos personales reales del equipo.
