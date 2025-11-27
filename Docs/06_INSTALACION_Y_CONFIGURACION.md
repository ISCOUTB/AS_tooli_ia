# Guía de Instalación y Configuración

## 📋 Requisitos Previos

### Software Requerido

#### Para Backend
- **Python**: 3.10 o superior
- **pip**: Gestor de paquetes de Python
- **virtualenv**: Para entorno virtual (opcional pero recomendado)

#### Para Frontend
- **Flutter**: 3.0 o superior
- **Dart**: Incluido con Flutter

#### Para Base de Datos
- **MariaDB**: 10.11 o superior (o MySQL 8.0+)

#### Servicios Externos
- **Cuenta Groq**: Para API de LLaMA 3.3
  - Registro gratuito en: https://console.groq.com
  - Obtener API Key

- **Servidor GLPI**: Debe estar accesible
  - GLPI 10.x o superior
  - API REST habilitada
  - App-Token y User-Token generados

---

## 🚀 Instalación del Backend

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/AS_tooli_ia.git
cd AS_tooli_ia/backend
```

### Paso 2: Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Contenido de requirements.txt**:
```
fastapi==0.115.5
uvicorn[standard]==0.34.0
pydantic==2.10.3
pydantic-settings==2.6.1
openai==1.55.3
azure-identity==1.19.0
requests==2.32.3
httpx==0.28.1
python-dotenv==1.0.0
python-multipart==0.0.6
fastapi-cors==0.0.6
loguru==0.7.2
python-dateutil==2.8.2
groq==0.11.0
pymysql==1.1.0
sqlalchemy==2.0.23
passlib==1.7.4
bcrypt==4.1.1
python-jose[cryptography]==3.3.0
```

### Paso 4: Configurar Variables de Entorno

Crear archivo `.env` en `backend/`:

```bash
# backend/.env

# ========================================
# CONFIGURACIÓN DEL SERVIDOR
# ========================================
HOST=0.0.0.0
PORT=8000
DEBUG=True

# ========================================
# GLPI CONFIGURATION
# ========================================
GLPI_URL=http://20.151.72.161:8200/apirest.php
GLPI_APP_TOKEN=tu_app_token_aqui
GLPI_USER_TOKEN=tu_user_token_aqui

# ========================================
# GROQ AI CONFIGURATION
# ========================================
GROQ_API_KEY=gsk_tu_api_key_de_groq_aqui
GROQ_MODEL=llama-3.3-70b-versatile

# ========================================
# SECURITY (JWT)
# ========================================
SECRET_KEY=cambia_esto_por_una_clave_super_segura_aleatoria_de_minimo_32_caracteres

# ========================================
# DATABASE (para SSO y Autenticación)
# ========================================
DB_HOST=20.151.72.161
DB_PORT=3306
DB_USER=sso_user
DB_PASSWORD=Sso123Secure!
DB_NAME=glpi_sso

# ========================================
# AGENT CONFIGURATION
# ========================================
MAX_TOKENS=1500
TEMPERATURE=0.7
```

### Paso 5: Configurar Base de Datos

```bash
# Conectar a MariaDB
mysql -h 20.151.72.161 -u root -p

# Crear base de datos y usuario
CREATE DATABASE glpi_sso CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sso_user'@'%' IDENTIFIED BY 'Sso123Secure!';
GRANT ALL PRIVILEGES ON glpi_sso.* TO 'sso_user'@'%';
FLUSH PRIVILEGES;

# Salir de MySQL
EXIT;

# Aplicar schema
mysql -h 20.151.72.161 -u sso_user -p glpi_sso < backend/database/complete_schema.sql
```

### Paso 6: Crear Directorio de Logs

```bash
mkdir -p backend/logs
```

### Paso 7: Ejecutar el Backend

```bash
# Método 1: Con uvicorn directamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Método 2: Con Python
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Método 3: Script personalizado (si existe)
python run.py
```

**Verificar que está funcionando**:
- Abrir navegador: http://localhost:8000
- Documentación API: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

---

## Instalación del Frontend

### Paso 1: Instalar Flutter

Si no tienes Flutter instalado:

```bash
# Linux/Mac
# Descargar Flutter
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:`pwd`/flutter/bin"

# Windows
# Descargar desde: https://flutter.dev/docs/get-started/install
# Agregar a PATH

# Verificar instalación
flutter doctor
```

### Paso 2: Navegar al Directorio del Frontend

```bash
cd frontend
```

### Paso 3: Instalar Dependencias

```bash
flutter pub get
```

### Paso 4: Configurar URL del Backend

Editar `frontend/lib/config/api_config.dart`:

```dart
class ApiConfig {
  // Cambiar según tu configuración
  static const String baseUrl = 'http://localhost:8000';
  
  // Endpoints (no cambiar)
  static const String queryEndpoint = '/api/v1/query';
  static const String chatEndpoint = '/api/v1/chat';
  static const String healthEndpoint = '/api/v1/health';
  static const String loginEndpoint = '/api/v1/auth/login';
  static const String registerEndpoint = '/api/v1/auth/register';
  static const String ticketsEndpoint = '/api/v1/tickets';
  static const String inventoryEndpoint = '/api/v1/inventory';
}
```

**Para despliegue en producción**, cambiar `baseUrl` a:
```dart
static const String baseUrl = 'https://tu-dominio.com';
```

### Paso 5: Ejecutar el Frontend

```bash
# Para Web
flutter run -d chrome

# Para compilar para producción (web)
flutter build web

# Para Android (con dispositivo conectado)
flutter run -d android

# Para iOS (solo en Mac)
flutter run -d ios
```

**Verificar que está funcionando**:
- La aplicación debe abrir en el navegador
- Debe mostrar pantalla de login
- Verificar conexión con backend (indicador en la barra superior)

---

## Despliegue con Docker 

### Backend con Docker

**Crear `Dockerfile` en `backend/`**:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Construir y ejecutar**:

```bash
# Construir imagen
docker build -t glpi-assistant-backend .

# Ejecutar contenedor
docker run -d \
  --name glpi-backend \
  -p 8000:8000 \
  --env-file .env \
  glpi-assistant-backend
```

### Frontend con Docker (Web)

**Crear `Dockerfile` en `frontend/`**:

```dockerfile
FROM nginx:alpine

# Copiar build de Flutter
COPY build/web /usr/share/nginx/html

# Configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Compilar y ejecutar**:

```bash
# Compilar Flutter para web
flutter build web

# Construir imagen
docker build -t glpi-assistant-frontend .

# Ejecutar contenedor
docker run -d \
  --name glpi-frontend \
  -p 80:80 \
  glpi-assistant-frontend
```

### Docker Compose Completo

**Crear `docker-compose.yml` en raíz**:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - GLPI_URL=${GLPI_URL}
      - GLPI_APP_TOKEN=${GLPI_APP_TOKEN}
      - GLPI_USER_TOKEN=${GLPI_USER_TOKEN}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - DB_HOST=${DB_HOST}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
    volumes:
      - ./backend/logs:/app/logs
    restart: unless-stopped
    networks:
      - glpi-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - glpi-network

networks:
  glpi-network:
    driver: bridge
```

**Ejecutar todo con Docker Compose**:

```bash
docker-compose up -d
```

---

## 🔧 Configuración de GLPI

### Habilitar API REST en GLPI

1. Acceder a GLPI como administrador
2. Ir a **Configuración → General → API**
3. Activar **Habilitar API REST**
4. Configurar:
   - Rango de IPs permitidas (o `0.0.0.0/0` para desarrollo)
   - Tamaño máximo de respuesta

### Crear App Token

1. Ir a **Configuración → General → API**
2. En sección **Clientes API**:
   - Nombre: `GLPI Assistant`
   - IPv4 activa: Marcar
   - Dirección IPv4: `0.0.0.0/0` (o IP específica)
   - Copiar el **App Token** generado

### Crear User Token

1. Ir a **Administración → Usuarios**
2. Seleccionar usuario (o crear uno específico para la API)
3. En pestaña **Autenticación remota**:
   - Habilitar **API token**
   - Copiar el **User Token** generado

**Alternativa con SQL**:

```sql
-- Generar token manualmente
INSERT INTO glpi_apiclients (name, is_active, ipv4_range_start, ipv4_range_end, app_token)
VALUES ('GLPI Assistant', 1, 0, 4294967295, 'tu_app_token_generado');

-- Para user token: usar la interfaz web
```

---

## Configuración de Groq API

### Obtener API Key

1. Registrarse en: https://console.groq.com
2. Ir a **API Keys**
3. Click en **Create API Key**
4. Copiar la clave (solo se muestra una vez)
5. Pegar en `.env` como `GROQ_API_KEY`

**Límites gratuitos** (verificar actualizaciones):
- ~14,000 tokens por minuto
- Ideal para desarrollo y pruebas

---

## Generar Secret Key Seguro

Para JWT en producción, generar clave aleatoria:

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

Copiar el resultado en `.env` como `SECRET_KEY`.

---

## Verificación de Instalación

### 1. Verificar Backend

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Respuesta esperada:
{
  "status": "healthy",
  "glpi_connected": true,
  "groq_ai_available": true
}
```

### 2. Verificar Base de Datos

```bash
python backend/database/test_connection.py
```

### 3. Verificar GLPI

```bash
# Consulta manual a GLPI
curl -X GET "http://ip-glpi:8200/apirest.php/initSession" \
  -H "Content-Type: application/json" \
  -H "App-Token: tu_app_token" \
  -H "Authorization: user_token tu_user_token"
```

### 4. Verificar Groq API

```bash
# Test desde Python
python -c "
from groq import Groq
client = Groq(api_key='tu_groq_api_key')
response = client.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{'role': 'user', 'content': 'Test'}]
)
print(response.choices[0].message.content)
"
```

---

## Solución de Problemas Comunes

### Error: "No se pudo conectar a GLPI"

**Causas**:
- URL incorrecta
- Tokens inválidos
- API REST no habilitada en GLPI
- Firewall bloqueando conexión

**Solución**:
```bash
# Verificar URL y tokens
echo $GLPI_URL
echo $GLPI_APP_TOKEN
echo $GLPI_USER_TOKEN

# Test manual
curl -X GET "$GLPI_URL/initSession" \
  -H "App-Token: $GLPI_APP_TOKEN" \
  -H "Authorization: user_token $GLPI_USER_TOKEN"
```

### Error: "Groq API key inválida"

**Solución**:
1. Verificar que la key esté correcta en `.env`
2. Verificar que no haya espacios extra
3. Generar una nueva key en Groq Console

### Error: "Cannot connect to database"

**Solución**:
```bash
# Verificar conexión
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME

# Verificar credenciales en .env
# Verificar que el usuario tenga permisos
GRANT ALL PRIVILEGES ON glpi_sso.* TO 'sso_user'@'%';
```

### Error: "CORS policy"

**Solución**: En `backend/main.py`, verificar:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Monitoreo

### Logs del Backend

```bash
# Ver logs en tiempo real
tail -f backend/logs/app.log

# Buscar errores
grep -i error backend/logs/app.log
```

### Logs de Docker

```bash
# Backend
docker logs -f glpi-backend

# Frontend
docker logs -f glpi-frontend
```

---

## Despliegue en Producción

### Checklist de Producción

- [ ] Cambiar `DEBUG=False` en `.env`
- [ ] Generar `SECRET_KEY` aleatorio y seguro
- [ ] Usar HTTPS (certificado SSL)
- [ ] Configurar CORS con dominios específicos
- [ ] Usar base de datos en servidor dedicado
- [ ] Configurar backups automáticos de DB
- [ ] Implementar rate limiting
- [ ] Configurar logs externos (Sentry, Logstash)
- [ ] Usar reverse proxy (Nginx, Apache)
- [ ] Configurar firewall
- [ ] Deshabilitar documentación API (`docs_url=None`)

### Nginx como Reverse Proxy

```nginx
# /etc/nginx/sites-available/glpi-assistant

server {
    listen 80;
    server_name tu-dominio.com;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name tu-dominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Frontend
    location / {
        root /var/www/glpi-assistant/frontend/build/web;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## Recursos Adicionales

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación Flutter](https://flutter.dev/docs)
- [Documentación GLPI API](https://github.com/glpi-project/glpi/blob/master/apirest.md)
- [Documentación Groq](https://console.groq.com/docs)
- [Documentación Docker](https://docs.docker.com/)

---

## Resumen

### Pasos Esenciales

1. Instalar Python 3.10+ y Flutter 3.0+
2. Clonar repositorio
3. Configurar `.env` con tokens y credenciales
4. Crear y configurar base de datos
5. Instalar dependencias (backend y frontend)
6. Ejecutar backend: `uvicorn main:app --reload`
7. Ejecutar frontend: `flutter run -d chrome`
8. Verificar conexiones (GLPI, Groq, DB)
9. Acceder a http://localhost
10. Probar funcionalidad

**Tiempo estimado de instalación**: 30-45 minutos

**¡Listo para usar el GLPI AI Assistant!** 🎉
