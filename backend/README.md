# API Gateway Minimalista para Tooli

Este proyecto es un API Gateway minimalista construido con Flask que actúa como intermediario entre el frontend Flutter/Dart y los workflows de n8n. Se enfoca en autenticación básica con usuario/contraseña y proxy de peticiones a n8n.

## Instalación

1. Clona el repositorio.
2. Crea un entorno virtual: `python -m venv venv`
3. Activa el entorno: `venv\Scripts\activate` (Windows)
4. Instala dependencias: `pip install -r requirements.txt`
5. Copia `.env.example` a `.env` y configura las variables.

## Configuración

Edita el archivo `.env` con tus configuraciones:
- `N8N_WEBHOOK_URL_CHAT`: URL del webhook de n8n para chat.
- `N8N_WEBHOOK_URL_GLPI`: URL del webhook de n8n para GLPI.
- Otras variables como `SECRET_KEY`, etc.

## Ejecución

### Desarrollo
`python run.py`

### Producción
Usa Docker: `docker build -t tooli-gateway . && docker run -p 5000:5000 tooli-gateway`

O con gunicorn: `gunicorn --bind 0.0.0.0:5000 run:app`

## Endpoints

Todos los endpoints requieren enviar `username` y `password` en el body JSON (excepto login que los usa para validar).

- `POST /api/auth/login`: Login (username: admin, password: password)
- `GET /api/auth/profile`: Perfil (envía username/password en body)
- `POST /api/chat/message`: Enviar mensaje al bot (envía username/password + message en body)
- `GET /api/tickets`: Listar tickets (envía username/password en body)
- `POST /api/tickets`: Crear ticket (envía username/password + datos en body)
- `GET /api/inventory`: Listar inventario (envía username/password en body)

Las credenciales dummy son username: "admin", password: "password".