# AS_tooli_ia

Proyecto: API Gateway (Flask) + Frontend (Flutter) + workflows n8n para integración con GLPI.

## Estructura principal
- backend/: Flask API, entrada en `backend/run.py` y creación de app en `backend/app/__init__.py`.
- frontend/: Aplicación Flutter, entrada en `frontend/lib/main.dart`.
- Chatbot n8n: `Chatbot GLPI.json`
- Docker / Orquestación: `docker-compose.yml`, `backend/Dockerfile`, `Dockerfile` (si aplica).

## Componentes claves (backend)
- Rutas de autenticación y proxy: `backend/app/routes/*` (ej. `proxy.py`, `auth.py`).
- Servicio de comunicación con n8n: `backend/app/services/n8n_proxy.py`.
- Configuración por entorno: `backend/app/config.py` y `backend/.env.example`.

## Quickstart (desarrollo)

### Backend (Windows)
```sh
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env    # o `cp .env.example .env` en Unix
python run.py
```

### Frontend (Flutter)
```sh
cd frontend
flutter pub get
flutter run
```

### Levantar todo con Docker
```sh
docker-compose up --build
```

## Endpoints principales (resumen)
- POST /api/auth/login
- GET  /api/auth/profile
- POST /api/chat/message  -> proxy a n8n (chat)
- GET/POST /api/tickets   -> proxy a GLPI via n8n
- GET /api/inventory      -> proxy a GLPI via n8n

(Ver rutas exactas en `backend/app/routes/proxy.py` y `auth.py`)

## Configuración
- Ajusta URLs y timeouts de n8n en `backend/app/config.py` o mediante variables en `.env`.
- El frontend por defecto apunta a `http://localhost:5000`; modificar si es necesario.

## Despliegue
- Cada componente tiene su Dockerfile: usar los Dockerfiles en `backend/` y la raíz.
- Para despliegue en producción, revisar variables de entorno, secretos y políticas de CORS.

## Contribuir
- Abrir issues y pull requests.
- No subir credenciales: `.env` está en `.gitignore`. Añadir tests y documentación para cambios importantes.

## Licencia
- Añadir un archivo `LICENSE` según la licencia que prefieras.
