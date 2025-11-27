# 🤖 Agente Inteligente para GLPI (Tooli)

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/Flutter-3.0+-cyan.svg)](https://flutter.dev/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-orange.svg)](https://groq.com/)
[![GLPI](https://img.shields.io/badge/GLPI-10.x-red.svg)](https://glpi-project.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Asistente inteligente de lenguaje natural para GLPI IT Service Management**
>
> Consulta tickets, inventario y estadísticas usando IA conversacional con LLaMA 3.3.

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso)

</div>

---

## 📋 Descripción

Sistema de asistente virtual que utiliza **Groq AI** (LLaMA 3.3) para procesar consultas en lenguaje natural y extraer información del sistema **GLPI IT Service Management**. Desarrollado con **FastAPI** (backend) y **Flutter** (frontend multiplataforma).

**Agente de IA que facilita el acceso a datos de inventario, tickets y reportes en GLPI (Tooli), brindando respuestas rápidas y precisas a solicitudes internas.**

---

## ✨ Características

### 🎫 Gestión de Tickets

- Consulta tickets por estado (abiertos, cerrados, pendientes)
- Búsqueda por fechas, usuarios, categorías
- Análisis estadístico avanzado con visualización de distribuciones
- Identificación de tendencias y patrones

### 💻 Inventario de TI

- Consulta de equipos y activos tecnológicos
- Búsqueda por ubicación, tipo, modelo, fabricante
- Detalle técnico de componentes (CPU, RAM, disco, red)
- Información de software instalado

### 🤖 IA Conversacional

- Procesamiento de lenguaje natural con **Groq LLaMA 3.3-70B**
- Comprensión contextual de consultas complejas
- Respuestas en español e inglés
- Análisis de grandes volúmenes de datos (1000+ tickets)

### 🔐 Seguridad

- Autenticación JWT para API REST
- Soporte para SSO con OAuth 2.0 (Microsoft Entra ID)
- Cifrado de credenciales y tokens
- Integración segura con API de GLPI

### 📊 Reporting

- Estadísticas en tiempo real
- Distribución por estado, urgencia, impacto, prioridad
- Top categorías y ubicaciones más afectadas
- Resúmenes ejecutivos automáticos

---

## 🛠️ Stack Tecnológico

### Backend

- **FastAPI** 0.100+ – Framework web moderno de Python
- **Groq AI** – LLaMA 3.3-70B Versatile (≈280 tokens/s)
- **SQLAlchemy** – ORM para persistencia de datos
- **MariaDB/MySQL** – Base de datos relacional
- **JWT** – Autenticación y autorización
- **Pydantic** – Validación de datos
- **Loguru** – Sistema de logs profesional

### Frontend

- **Flutter** 3.0+ – Framework UI multiplataforma
- **Provider** – State management
- **HTTP** – Cliente REST
- **Flutter Secure Storage** – Almacenamiento de tokens
- **Markdown** – Renderizado de respuestas formateadas

### Integraciones

- **GLPI REST API** – Gestión de tickets e inventario
- **Groq Cloud API** – Modelos de lenguaje avanzados

---

## 📋 Requisitos

### Software Necesario

- **Python** 3.10 o superior
- **Flutter SDK** 3.0 o superior
- **MariaDB** o **MySQL** 8.0+
- **GLPI** 10.x con REST API habilitada
- **Cuenta Groq** (gratuita) con API key

### API Keys Requeridas

- **Groq API Key**: Obtener en [console.groq.com](https://console.groq.com/)
- **GLPI Credentials**: App Token y User Token de GLPI

---

## 🚀 Instalación

### 1. Clonar Repositorio

```bash
git clone https://github.com/TU_USUARIO/glpi-ai-assistant.git
cd glpi-ai-assistant
```

### 2. Configurar Backend

#### 2.1 Crear Entorno Virtual

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 2.2 Instalar Dependencias

```bash
pip install -r requirements.txt
```

#### 2.3 Configurar Variables de Entorno

Crear archivo `.env` en la carpeta `backend/`:

```env
# ===== GROQ CONFIGURATION =====
GROQ_API_KEY=gsk_tu_api_key_aqui
GROQ_MODEL=llama-3.3-70b-versatile

# ===== GLPI CONFIGURATION =====
GLPI_URL=http://tu-servidor-glpi/apirest.php
GLPI_APP_TOKEN=tu_app_token_aqui
GLPI_USER_TOKEN=tu_user_token_aqui

# ===== DATABASE CONFIGURATION =====
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=glpi_sso

# ===== SECURITY =====
SECRET_KEY=tu_clave_secreta_super_segura_minimo_32_caracteres
```

#### 2.4 Iniciar Base de Datos

```bash
mysql -u root -p
CREATE DATABASE glpi_sso CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit
```

#### 2.5 Iniciar Backend

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend disponible en: **http://localhost:8000**  
Documentación API: **http://localhost:8000/docs**

### 3. Configurar Frontend

#### 3.1 Instalar Dependencias Flutter

```bash
cd ../frontend
flutter pub get
```

#### 3.2 Verificar Configuración

```bash
flutter doctor
```

#### 3.3 Iniciar Frontend

```bash
# Web
flutter run -d chrome --web-port 8080

# Desktop (Windows)
flutter run -d windows

# Desktop (macOS)
flutter run -d macos

# Desktop (Linux)
flutter run -d linux
```

Frontend disponible en: **http://localhost:8080** (web)

---

## 🎯 Uso

### Ejemplos de Consultas

#### Tickets

- ¿Cuántos tickets hay abiertos?
- Muéstrame los tickets cerrados de esta semana
- Tickets pendientes en el área de soporte
- Análisis de tickets por prioridad
- ¿Cuál es la distribución de tickets por estado?

#### Inventario

- ¿Cuántas computadoras hay en total?
- Laptops en la oficina de Santiago
- Equipos con Windows 11
- Computadoras con más de 16GB de RAM
- Servidores Dell

#### Estadísticas

- Dame un resumen de tickets
- Estadísticas de soporte técnico
- Top 5 categorías con más tickets
- Distribución de tickets por urgencia

### Capturas de Pantalla (idea)

1. **Login**: Autenticación con credenciales GLPI  
2. **Chat**: Interface conversacional con IA  
3. **Resultados**: Respuestas formateadas con Markdown  
4. **Estadísticas**: Visualización de distribuciones  

---

<!-- Secciones técnicas detalladas (arquitectura y estructura de carpetas) se han simplificado para mantener el README ligero y fácil de leer. -->

## 🔒 Seguridad

### Buenas Prácticas Implementadas

- **`.env` ignorado por Git** – Secrets fuera del repositorio.  
- **JWT tokens** con expiración configurable.  
- **Hashing de contraseñas** con bcrypt.  
- **Validación de inputs** con Pydantic.  
- **CORS configurado** para permitir solo origins autorizados.  
- **Logs seguros** sin exposición de credenciales.  
- **API Keys en variables de entorno** – Nunca hardcodeadas.  

### Checklist de Seguridad

- [ ] Cambiar `SECRET_KEY` en `.env` a un valor único y seguro (32+ caracteres).  
- [ ] Rotar API keys regularmente.  
- [ ] Usar HTTPS en producción (no HTTP).  
- [ ] Configurar firewall para limitar acceso a puertos (8000, 3306).  
- [ ] Mantener dependencias actualizadas (`pip list --outdated`).  
- [ ] Habilitar logs de auditoría en GLPI.  
- [ ] Implementar rate limiting en endpoints críticos.  

---

## 🚢 Despliegue (ideas)

### Backend

- Railway / Render / DigitalOcean / AWS (FastAPI + DB).  
- Opcional: Dockerizar el backend con un `Dockerfile`.  

### Frontend

- Vercel / Netlify / Firebase Hosting para Flutter Web.  

### Base de Datos

- MariaDB/MySQL en servidor propio o cloud (Railway, PlanetScale, AWS RDS, etc.).  

---

## 🤝 Contribuir

1. Haz fork de este repositorio.  
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`.  
3. Commit de tus cambios: `git commit -m "Agregar nueva funcionalidad"`.  
4. Push a tu rama: `git push origin feature/nueva-funcionalidad`.  
5. Abre un Pull Request.  

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

**Desarrollado con ❤️ usando Groq AI, FastAPI y Flutter**  

Si este proyecto te fue útil, considera darle una ⭐ en GitHub.

</div>


## 📐 Arquitectura



```# ===== GLPI CONFIGURATION =====- **MariaDB/MySQL** - Base de datos relacional

┌─────────────────────┐

│   Flutter Frontend  │  ← Interface de usuario (Web/Desktop/Mobile)GLPI_URL=http://tu-servidor-glpi/apirest.php

│  (localhost:8080)   │

└──────────┬──────────┘GLPI_APP_TOKEN=tu_app_token_aqui- **JWT** - Autenticación y autorización- **JWT** - Autenticación segura### Intelligent Query Processing

           │ HTTP/REST

           ▼GLPI_USER_TOKEN=tu_user_token_aqui

┌─────────────────────┐

│   FastAPI Backend   │  ← API REST + Lógica de negocio- **Pydantic** - Validación de datos

│  (localhost:8000)   │

└─────┬───────┬───────┘# ===== DATABASE CONFIGURATION =====

      │       │

      │       └─────────────┐DB_HOST=localhost- **Loguru** - Sistema de logs profesional- **Loguru** - Sistema de logging

      ▼                     ▼

┌──────────┐        ┌──────────────┐DB_PORT=3306

│  Groq AI │        │  GLPI API    │

│  LLaMA   │        │  REST API    │DB_USER=root

└──────────┘        └──────────────┘

      │                     │DB_PASSWORD=tu_password

      │                     ▼

      │             ┌──────────────┐DB_NAME=glpi_sso### Frontend- Natural language understanding with Groq AI (llama-3.3-70b-versatile)```

      │             │  GLPI DB     │

      │             │  (Tickets)   │

      │             └──────────────┘

      ▼# ===== SECURITY =====- **Flutter** 3.0+ - Framework UI multiplataforma

┌──────────┐

│ MariaDB  │  ← Persistencia de sesiones y usuariosSECRET_KEY=tu_clave_secreta_super_segura_minimo_32_caracteres

└──────────┘

``````- **Provider** - State management### Frontend



### Flujo de Procesamiento



1. **Usuario** ingresa consulta en lenguaje natural#### 2.4 Iniciar Base de Datos- **HTTP** - Cliente REST

2. **Frontend** envía request HTTP a `/api/v1/query`

3. **Backend** recibe consulta y la envía a **Groq AI**```bash

4. **Groq** analiza intención y extrae parámetros

5. **Backend** consulta datos en **GLPI API**# Crear base de datos- **Flutter Secure Storage** - Almacenamiento de tokens- **Flutter** - Framework multiplataforma- Automatic intent classification and parameter extraction💬 "¿Cuántos tickets tengo abiertos?"

6. **Backend** envía datos a **Groq** para generar respuesta

7. **Groq** genera respuesta en lenguaje naturalmysql -u root -p

8. **Frontend** muestra respuesta formateada en Markdown

CREATE DATABASE glpi_sso CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;- **Markdown** - Renderizado de respuestas formateadas

---

exit

## 📁 Estructura del Proyecto

```- **Provider** - Gestión de estado

```

glpi-ai-assistant/

├── backend/                     # Backend FastAPI

│   ├── ai/                      # Módulo de IA#### 2.5 Iniciar Backend### Integraciones

│   │   ├── __init__.py

│   │   └── agent.py             # Agente Groq AI```bash

│   ├── api/                     # Endpoints REST

│   │   ├── __init__.pycd backend- **GLPI REST API** - Gestión de tickets e inventario- **Material Design** - Diseño responsive- Confidence scoring for transparency🤖 "Tienes 5 tickets abiertos actualmente..."

│   │   ├── routes.py            # Rutas principales

│   │   ├── schemas.py           # Modelos Pydanticpython -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

│   │   ├── chat_schemas.py      # Schemas de chat

│   │   ├── conversation_routes.py```- **Groq Cloud API** - Modelos de lenguaje avanzados

│   │   ├── inventory_routes.py

│   │   ├── settings_routes.py

│   │   ├── statistics_routes.py

│   │   └── tickets_routes.pyBackend disponible en: **http://localhost:8000**  

│   ├── auth/                    # Autenticación

│   │   ├── __init__.pyDocumentación API: **http://localhost:8000/docs**

│   │   ├── jwt_auth.py          # JWT tokens

│   │   ├── models.py            # Modelos de usuarios## 📋 Requisitos

│   │   ├── auth_routes.py       # Login/Logout

│   │   ├── sso_models.py        # Modelos SSO### 3. Configurar Frontend

│   │   └── sso_routes.py        # OAuth 2.0 routes

│   ├── integrations/            # Integraciones externas### Infraestructura- Multi-language support (Spanish/English)

│   │   ├── __init__.py

│   │   └── glpi_client.py       # Cliente GLPI API#### 3.1 Instalar Dependencias Flutter

│   ├── services/                # Lógica de negocio

│   │   ├── __init__.py```bash### Software Necesario

│   │   ├── agent_service.py     # Servicio principal

│   │   ├── conversation_service.pycd ../frontend

│   │   └── ticket_service.py

│   ├── config.py                # Configuración globalflutter pub get- **Python** 3.10 o superior- **MariaDB/MySQL** - Base de datos

│   ├── main.py                  # Punto de entrada FastAPI

│   ├── requirements.txt         # Dependencias Python```

│   └── .env.example             # Template de configuración

│- **Flutter SDK** 3.0 o superior

├── frontend/                    # Frontend Flutter

│   ├── lib/#### 3.2 Verificar Configuración

│   │   ├── main.dart            # Punto de entrada

│   │   ├── models/              # Modelos de datos```bash- **MariaDB** o **MySQL** 8.0+- **GLPI REST API** - Integración con GLPI 10.0+💬 "Busca la computadora de Juan"

│   │   ├── providers/           # State management

│   │   ├── screens/             # Pantallasflutter doctor

│   │   │   ├── login_screen.dart

│   │   │   ├── chat_screen.dart```- **GLPI** 10.x con REST API habilitada

│   │   │   └── settings_screen.dart

│   │   ├── services/            # API clients

│   │   │   └── api_service.dart

│   │   └── widgets/             # Componentes reutilizables#### 3.3 Iniciar Frontend- **Cuenta Groq** (gratuita) con API key- **Microsoft Entra ID** - SSO OAuth2

│   ├── assets/                  # Recursos estáticos

│   │   └── logo.png```bash

│   └── pubspec.yaml             # Dependencias Flutter

│# Web

├── .gitignore                   # Archivos ignorados por Git

├── LICENSE                      # Licencia MITflutter run -d chrome --web-port 8080

└── README.md                    # Este archivo

```### API Keys Requeridas### Comprehensive Analytics🤖 "💻 PC-LAB-05 (Dell OptiPlex), Piso 2, Oficina 204"



---# Desktop (Windows)



## 🔒 Seguridadflutter run -d windows- **Groq API Key**: Obtener en [console.groq.com](https://console.groq.com/)



### Buenas Prácticas Implementadas



✅ **Nunca commitear `.env`** - Archivo con secrets excluido de Git  # Desktop (macOS)- **GLPI Credentials**: App Token y User Token de GLPI---

✅ **JWT tokens** con expiración configurable  

✅ **Hashing de contraseñas** con bcrypt  flutter run -d macos

✅ **Validación de inputs** con Pydantic  

✅ **CORS configurado** para permitir solo origins autorizados  

✅ **Logs seguros** sin exposición de credenciales  

✅ **API Keys en variables de entorno** - No hardcodeadas  # Desktop (Linux)



### Checklist de Seguridadflutter run -d linux## 🚀 Instalación- Real-time ticket statistics (status, priority, type, urgency, impact)



- [ ] Cambiar `SECRET_KEY` en `.env` a un valor único y seguro (32+ caracteres)```

- [ ] Rotar API keys regularmente

- [ ] Usar HTTPS en producción (no HTTP)

- [ ] Configurar firewall para limitar acceso a puertos (8000, 3306)

- [ ] Mantener dependencias actualizadas (`pip list --outdated`)Frontend disponible en: **http://localhost:8080** (web)

- [ ] Habilitar logs de auditoría en GLPI

- [ ] Implementar rate limiting en endpoints críticos### 1. Clonar Repositorio## 📋 Requisitos



---## 🎯 Uso



## 🚢 Despliegue```bash



### Backend (Sugerencias)### Ejemplos de Consultas



- **Railway**: [railway.app](https://railway.app/) - Deploy automático desde GitHubgit clone https://github.com/TU_USUARIO/glpi-ai-assistant.git- Historical trend analysis💬 "Muéstrame el ticket 123"

- **Render**: [render.com](https://render.com/) - Free tier disponible

- **DigitalOcean**: App Platform con Python + MySQL#### Tickets

- **AWS**: EC2 + RDS MySQL

- **Docker**: Containerizar con `Dockerfile` (pendiente agregar)```cd glpi-ai-assistant



### Frontend (Sugerencias)- ¿Cuántos tickets hay abiertos?



- **Vercel**: Para Flutter Web- Muéstrame los tickets cerrados de esta semana```- **Python** 3.10+

- **Netlify**: Para aplicaciones estáticas

- **GitHub Pages**: Hosting gratuito- Tickets pendientes en el área de soporte

- **Firebase Hosting**: CDN global

- Análisis de tickets por prioridad

### Base de Datos

- ¿Cuál es la distribución de tickets por estado?

- **MariaDB/MySQL** local o cloud

- **PlanetScale**: MySQL serverless gratuito```### 2. Configurar Backend- **Flutter** 3.0+- Custom report generation🤖 "🎫 Ticket #123: Problema con impresora..."

- **Railway**: MySQL managed database

- **AWS RDS**: MySQL en Amazon



---#### Inventario



## 🤝 Contribuir```



Las contribuciones son bienvenidas! Por favor:- ¿Cuántas computadoras hay en total?#### 2.1 Crear Entorno Virtual- **MariaDB/MySQL** 8.0+



1. Fork este repositorio- Laptops en la oficina de Santiago

2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)

3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)- Equipos con Windows 11```bash

4. Push a la rama (`git push origin feature/nueva-funcionalidad`)

5. Abre un Pull Request- Computadoras con más de 16GB de RAM



---- Servidores Dellcd backend- **GLPI** 10.0+ con API REST habilitada- Inventory management insights```



## 📄 Licencia```



Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.python -m venv venv



---#### Estadísticas



<div align="center">```- **Groq API Key** (gratis en [console.groq.com](https://console.groq.com))



**Desarrollado con ❤️ usando Groq AI y FastAPI**- Dame un resumen de tickets



Si este proyecto te fue útil, considera darle una ⭐ en GitHub!- Estadísticas de soporte técnico# Windows



</div>- Top 5 categorías con más tickets


- Distribución de tickets por urgenciavenv\Scripts\activate

```



### Capturas de Pantalla

# Linux/Mac---

1. **Login**: Autenticación con credenciales GLPI

2. **Chat**: Interface conversacional con IAsource venv/bin/activate

3. **Resultados**: Respuestas formateadas con Markdown

4. **Estadísticas**: Visualización de distribuciones```### Professional User Interface---



## 📐 Arquitectura



```#### 2.2 Instalar Dependencias## 🚀 Instalación

┌─────────────────────┐

│   Flutter Frontend  │  ← Interface de usuario (Web/Desktop/Mobile)```bash

│  (localhost:8080)   │

└──────────┬──────────┘pip install -r requirements.txt- Microsoft Fluent Design principles

           │ HTTP/REST

           ▼```

┌─────────────────────┐

│   FastAPI Backend   │  ← API REST + Lógica de negocio### 1️⃣ Clonar Repositorio

│  (localhost:8000)   │

└─────┬───────┬───────┘#### 2.3 Configurar Variables de Entorno

      │       │

      │       └─────────────┐Crear archivo `.env` en la carpeta `backend/`:- Light/Dark theme with persistence## ✨ Características

      ▼                     ▼

┌──────────┐        ┌──────────────┐```env

│  Groq AI │        │  GLPI API    │

│  LLaMA   │        │  REST API    │# ===== GROQ CONFIGURATION =====```bash

└──────────┘        └──────────────┘

      │                     │GROQ_API_KEY=gsk_tu_api_key_aqui

      │                     ▼

      │             ┌──────────────┐GROQ_MODEL=llama-3.3-70b-versatilegit clone https://github.com/tu-usuario/glpi-ai-assistant.git- Responsive layout for desktop and web

      │             │  GLPI DB     │

      │             │  (Tickets)   │

      │             └──────────────┘

      ▼# ===== GLPI CONFIGURATION =====cd glpi-ai-assistant

┌──────────┐

│ MariaDB  │  ← Persistencia de sesiones y usuariosGLPI_URL=http://tu-servidor-glpi/apirest.php

└──────────┘

```GLPI_APP_TOKEN=tu_app_token_aqui```- Accessibility-compliant (WCAG 2.1)### Funcionalidades Actuales



### Flujo de ProcesamientoGLPI_USER_TOKEN=tu_user_token_aqui



1. **Usuario** ingresa consulta en lenguaje natural

2. **Frontend** envía request HTTP a `/api/v1/query`

3. **Backend** recibe consulta y la envía a **Groq AI**# ===== DATABASE CONFIGURATION =====

4. **Groq** analiza intención y extrae parámetros

5. **Backend** consulta datos en **GLPI API**DB_HOST=localhost### 2️⃣ Backend- ✅ **Consulta de Tickets**: Abiertos, cerrados, por usuario

6. **Backend** envía datos a **Groq** para generar respuesta

7. **Groq** genera respuesta en lenguaje naturalDB_PORT=3306

8. **Frontend** muestra respuesta formateada en Markdown

DB_USER=root

## 📁 Estructura del Proyecto

DB_PASSWORD=tu_password

```

glpi-ai-assistant/DB_NAME=glpi_sso```bash## 🏗️ Technical Architecture- ✅ **Inventario Inteligente**: Búsqueda de equipos y activos

├── backend/                     # Backend FastAPI

│   ├── ai/                      # Módulo de IA

│   │   ├── __init__.py

│   │   └── agent.py             # Agente Groq AI# ===== SECURITY =====cd backend

│   ├── api/                     # Endpoints REST

│   │   ├── __init__.pySECRET_KEY=tu_clave_secreta_super_segura_minimo_32_caracteres

│   │   ├── routes.py            # Rutas principales

│   │   ├── schemas.py           # Modelos Pydantic```- ✅ **Reportes Automáticos**: Estadísticas y análisis

│   │   ├── chat_schemas.py      # Schemas de chat

│   │   ├── conversation_routes.py

│   │   ├── inventory_routes.py

│   │   ├── settings_routes.py#### 2.4 Iniciar Base de Datos# Crear entorno virtual

│   │   ├── statistics_routes.py

│   │   └── tickets_routes.py```bash

│   ├── auth/                    # Autenticación

│   │   ├── __init__.py# Crear base de datospython -m venv venv### Clean Architecture Implementation- ✅ **Lenguaje Natural**: Entiende español conversacional

│   │   ├── jwt_auth.py          # JWT tokens

│   │   ├── models.py            # Modelos de usuariosmysql -u root -p

│   │   ├── auth_routes.py       # Login/Logout

│   │   ├── sso_models.py        # Modelos SSOCREATE DATABASE glpi_sso CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

│   │   └── sso_routes.py        # OAuth 2.0 routes

│   ├── integrations/            # Integraciones externasexit

│   │   ├── __init__.py

│   │   └── glpi_client.py       # Cliente GLPI API```# Activar (Windows)- ✅ **API REST Completa**: Documentación interactiva con Swagger

│   ├── services/                # Lógica de negocio

│   │   ├── __init__.py

│   │   ├── agent_service.py     # Servicio principal

│   │   ├── conversation_service.py#### 2.5 Iniciar Backendvenv\Scripts\activate

│   │   └── ticket_service.py

│   ├── config.py                # Configuración global```bash

│   ├── main.py                  # Punto de entrada FastAPI

│   ├── requirements.txt         # Dependencias Pythoncd backend```- ✅ **Integración Azure OpenAI**: GPT-4 para procesamiento inteligente

│   └── .env.example             # Template de configuración

│python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

├── frontend/                    # Frontend Flutter

│   ├── lib/```# Activar (Linux/Mac)

│   │   ├── main.dart            # Punto de entrada

│   │   ├── models/              # Modelos de datos

│   │   ├── providers/           # State management

│   │   ├── screens/             # PantallasBackend disponible en: **http://localhost:8000**  source venv/bin/activate┌─────────────────────────────────────┐

│   │   │   ├── login_screen.dart

│   │   │   ├── chat_screen.dartDocumentación API: **http://localhost:8000/docs**

│   │   │   └── settings_screen.dart

│   │   ├── services/            # API clients

│   │   │   └── api_service.dart

│   │   └── widgets/             # Componentes reutilizables### 3. Configurar Frontend

│   ├── assets/                  # Recursos estáticos

│   │   └── logo.png# Instalar dependencias│         Presentation Layer          │### En Desarrollo

│   └── pubspec.yaml             # Dependencias Flutter

│#### 3.1 Instalar Dependencias Flutter

├── .gitignore                   # Archivos ignorados por Git

├── LICENSE                      # Licencia MIT```bashpip install -r requirements.txt

└── README.md                    # Este archivo

```cd ../frontend



## 🔒 Seguridadflutter pub get│   (Flutter UI + FastAPI Routes)     │- ⏳ Frontend con Flutter (iOS, Android, Web)



### Buenas Prácticas Implementadas```



✅ **Nunca commitear `.env`** - Archivo con secrets excluido de Git  # Configurar variables de entorno

✅ **JWT tokens** con expiración configurable  

✅ **Hashing de contraseñas** con bcrypt  #### 3.2 Verificar Configuración

✅ **Validación de inputs** con Pydantic  

✅ **CORS configurado** para permitir solo origins autorizados  ```bashcopy .env.example .env└───────────────┬─────────────────────┘- ⏳ Crear y actualizar tickets

✅ **Logs seguros** sin exposición de credenciales  

✅ **API Keys en variables de entorno** - No hardcodeadas  flutter doctor



### Checklist de Seguridad```# Edita .env con tus credenciales



- [ ] Cambiar `SECRET_KEY` en `.env` a un valor único y seguro (32+ caracteres)

- [ ] Rotar API keys regularmente

- [ ] Usar HTTPS en producción (no HTTP)#### 3.3 Iniciar Frontend                │- ⏳ Notificaciones en tiempo real

- [ ] Configurar firewall para limitar acceso a puertos (8000, 3306)

- [ ] Mantener dependencias actualizadas (`pip list --outdated`)```bash

- [ ] Habilitar logs de auditoría en GLPI

- [ ] Implementar rate limiting en endpoints críticos# Web# Iniciar servidor



## 🚢 Despliegueflutter run -d chrome --web-port 8080



### Backend (Sugerencias)uvicorn main:app --host 0.0.0.0 --port 8000 --reload┌───────────────▼─────────────────────┐- ⏳ Reportes personalizados avanzados



- **Railway**: [railway.app](https://railway.app/) - Deploy automático desde GitHub# Desktop (Windows)

- **Render**: [render.com](https://render.com/) - Free tier disponible

- **DigitalOcean**: App Platform con Python + MySQLflutter run -d windows```

- **AWS**: EC2 + RDS MySQL

- **Docker**: Containerizar con `Dockerfile` (pendiente agregar)



### Frontend (Sugerencias)# Desktop (macOS)│       Application Layer              │



- **Vercel**: Para Flutter Webflutter run -d macos

- **Netlify**: Para aplicaciones estáticas

- **GitHub Pages**: Hosting gratuito**Configurar `.env`:**

- **Firebase Hosting**: CDN global

# Desktop (Linux)

### Base de Datos

flutter run -d linux│    (Use Cases + Services)            │---

- **MariaDB/MySQL** local o cloud

- **PlanetScale**: MySQL serverless gratuito```

- **Railway**: MySQL managed database

- **AWS RDS**: MySQL en Amazon```properties



## 🤝 ContribuirFrontend disponible en: **http://localhost:8080** (web)



Las contribuciones son bienvenidas! Por favor:GROQ_API_KEY=tu_groq_api_key_aqui└───────────────┬─────────────────────┘



1. Fork este repositorio## 🎯 Uso

2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)

3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)GLPI_URL=http://tu-glpi.com/apirest.php

4. Push a la rama (`git push origin feature/nueva-funcionalidad`)

5. Abre un Pull Request### Ejemplos de Consultas



## 📄 LicenciaGLPI_APP_TOKEN=tu_app_token                │## 🏗️ Arquitectura



Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.#### Tickets



---```GLPI_USER_TOKEN=tu_user_token



<div align="center">- ¿Cuántos tickets hay abiertos?



**Desarrollado con ❤️ usando Groq AI y FastAPI**- Muéstrame los tickets cerrados de esta semanaSECRET_KEY=cambia-esta-clave-en-produccion┌───────────────▼─────────────────────┐



Si este proyecto te fue útil, considera darle una ⭐ en GitHub!- Tickets pendientes en el área de soporte



</div>- Análisis de tickets por prioridad```


- ¿Cuál es la distribución de tickets por estado?

```│          Domain Layer                │```



#### Inventario### 3️⃣ Frontend

```

- ¿Cuántas computadoras hay en total?│   (Entities + Business Rules)        │┌─────────────┐

- Laptops en la oficina de Santiago

- Equipos con Windows 11```bash

- Computadoras con más de 16GB de RAM

- Servidores Dellcd frontend└───────────────┬─────────────────────┘│   Usuario   │ "¿Cuántos tickets tengo?"

```



#### Estadísticas

```# Instalar dependencias                │└──────┬──────┘

- Dame un resumen de tickets

- Estadísticas de soporte técnicoflutter pub get

- Top 5 categorías con más tickets

- Distribución de tickets por urgencia┌───────────────▼─────────────────────┐       │

```

# Ejecutar web

### Capturas de Pantalla

flutter run -d chrome --web-port 8080│      Infrastructure Layer            │       ▼

1. **Login**: Autenticación con credenciales GLPI

2. **Chat**: Interface conversacional con IA

3. **Resultados**: Respuestas formateadas con Markdown

4. **Estadísticas**: Visualización de distribuciones# O para Windows desktop│   (GLPI Client + AI Provider)        │┌──────────────┐



## 📐 Arquitecturaflutter run -d windows



``````└─────────────────────────────────────┘│   Frontend   │ (Flutter - Próxima fase)

┌─────────────────────┐

│   Flutter Frontend  │  ← Interface de usuario (Web/Desktop/Mobile)

│  (localhost:8080)   │

└──────────┬──────────┘---```│  Chat UI     │

           │ HTTP/REST

           ▼

┌─────────────────────┐

│   FastAPI Backend   │  ← API REST + Lógica de negocio## 📖 Uso└──────┬───────┘

│  (localhost:8000)   │

└─────┬───────┬───────┘

      │       │

      │       └─────────────┐Ejemplos de consultas en lenguaje natural:### Technology Stack       │ HTTP/REST

      ▼                     ▼

┌──────────┐        ┌──────────────┐

│  Groq AI │        │  GLPI API    │

│  LLaMA   │        │  REST API    │```       ▼

└──────────┘        └──────────────┘

      │                     │"¿Cuántos tickets hay abiertos?"

      │                     ▼

      │             ┌──────────────┐"Muéstrame los tickets de alta prioridad"**Backend:**┌─────────────────────────────────┐

      │             │  GLPI DB     │

      │             │  (Tickets)   │"Busca el ticket 123"

      │             └──────────────┘

      ▼"¿Cuántas computadoras hay en el inventario?"- Python 3.14.0│  Backend (FastAPI + Python)     │

┌──────────┐

│ MariaDB  │  ← Persistencia de sesiones y usuarios"Busca la PC de Juan"

└──────────┘

```"Genera estadísticas de este mes"- FastAPI 0.121.1 (Async web framework)│  ┌──────────────────────────┐   │



### Flujo de Procesamiento```



1. **Usuario** ingresa consulta en lenguaje natural- Groq AI (Free tier: 30 req/min)│  │  API REST                │   │

2. **Frontend** envía request HTTP a `/api/v1/query`

3. **Backend** recibe consulta y la envía a **Groq AI**---

4. **Groq** analiza intención y extrae parámetros

5. **Backend** consulta datos en **GLPI API**- Pydantic 2.12.4 (Data validation)│  │  /query  /chat  /health  │   │

6. **Backend** envía datos a **Groq** para generar respuesta

7. **Groq** genera respuesta en lenguaje natural## 🔧 Obtener API Keys

8. **Frontend** muestra respuesta formateada en Markdown

│  └────────┬─────────────────┘   │

## 📁 Estructura del Proyecto

### Groq API Key

```

glpi-ai-assistant/1. Crear cuenta en [console.groq.com](https://console.groq.com)**Frontend:**│           │                      │

├── backend/                     # Backend FastAPI

│   ├── ai/                      # Módulo de IA2. Ir a **API Keys** → **Create API Key**

│   │   ├── __init__.py

│   │   └── agent.py             # Agente Groq AI3. Copiar y pegar en `.env`- Flutter 3.32.0 / Dart 3.8.0│  ┌────────▼──────────┐          │

│   ├── api/                     # Endpoints REST

│   │   ├── __init__.py

│   │   ├── routes.py            # Rutas principales

│   │   ├── schemas.py           # Modelos Pydantic### GLPI Tokens- Provider (State management)│  │  Agent Service    │          │

│   │   ├── chat_schemas.py      # Schemas de chat

│   │   ├── conversation_routes.py1. GLPI → **Configuración** → **API** → Habilitar API REST

│   │   ├── inventory_routes.py

│   │   ├── settings_routes.py2. Crear **App Token** y **User Token**- Google Fonts (Segoe UI)│  │  (Orquestador)    │          │

│   │   ├── statistics_routes.py

│   │   └── tickets_routes.py3. Agregar a `.env`

│   ├── auth/                    # Autenticación

│   │   ├── __init__.py- Material Design 3│  └────┬──────────┬───┘          │

│   │   ├── jwt_auth.py          # JWT tokens

│   │   ├── models.py            # Modelos de usuarios---

│   │   ├── auth_routes.py       # Login/Logout

│   │   ├── sso_models.py        # Modelos SSO│       │          │               │

│   │   └── sso_routes.py        # OAuth 2.0 routes

│   ├── integrations/            # Integraciones externas## 🏗️ Arquitectura

│   │   ├── __init__.py

│   │   └── glpi_client.py       # Cliente GLPI API## 🚀 Quick Start│  ┌────▼───┐  ┌──▼────┐         │

│   ├── services/                # Lógica de negocio

│   │   ├── __init__.py```

│   │   ├── agent_service.py     # Servicio principal

│   │   ├── conversation_service.pyFrontend (Flutter)│  │ AI     │  │ GLPI  │         │

│   │   └── ticket_service.py

│   ├── config.py                # Configuración global      ↓

│   ├── main.py                  # Punto de entrada FastAPI

│   ├── requirements.txt         # Dependencias Python  REST API### Backend Deployment│  │ Agent  │  │Client │         │

│   └── .env.example             # Template de configuración

│      ↓

├── frontend/                    # Frontend Flutter

│   ├── lib/Backend (FastAPI)│  └────┬───┘  └──┬────┘         │

│   │   ├── main.dart            # Punto de entrada

│   │   ├── models/              # Modelos de datos   ↙    ↘

│   │   ├── providers/           # State management

│   │   ├── screens/             # PantallasGroq AI   GLPI API```powershell└───────│─────────│───────────────┘

│   │   │   ├── login_screen.dart

│   │   │   ├── chat_screen.dart   ↘    ↙

│   │   │   └── settings_screen.dart

│   │   ├── services/            # API clients  MariaDBcd backend        │         │

│   │   │   └── api_service.dart

│   │   └── widgets/             # Componentes reutilizables```

│   ├── assets/                  # Recursos estáticos

│   │   └── logo.png        ▼         ▼

│   └── pubspec.yaml             # Dependencias Flutter

│**Flujo:**

├── .gitignore                   # Archivos ignorados por Git

├── LICENSE                      # Licencia MIT1. Usuario escribe pregunta# Setup environment   ┌────────┐  ┌──────┐

└── README.md                    # Este archivo

```2. Backend analiza con Groq AI



## 🔒 Seguridad3. Consulta datos en GLPIpython -m venv venv   │ Azure  │  │ GLPI │



### Buenas Prácticas Implementadas4. IA genera respuesta natural



✅ **Nunca commitear `.env`** - Archivo con secrets excluido de Git  5. Frontend muestra resultado.\venv\Scripts\Activate.ps1   │OpenAI  │  │Server│

✅ **JWT tokens** con expiración configurable  

✅ **Hashing de contraseñas** con bcrypt  

✅ **Validación de inputs** con Pydantic  

✅ **CORS configurado** para permitir solo origins autorizados  ---pip install -r requirements.txt   └────────┘  └──────┘

✅ **Logs seguros** sin exposición de credenciales  

✅ **API Keys en variables de entorno** - No hardcodeadas  



### Checklist de Seguridad## 📁 Estructura```



- [ ] Cambiar `SECRET_KEY` en `.env` a un valor único y seguro (32+ caracteres)

- [ ] Rotar API keys regularmente

- [ ] Usar HTTPS en producción (no HTTP)```# Configure

- [ ] Configurar firewall para limitar acceso a puertos (8000, 3306)

- [ ] Mantener dependencias actualizadas (`pip list --outdated`)glpi-ai-assistant/

- [ ] Habilitar logs de auditoría en GLPI

- [ ] Implementar rate limiting en endpoints críticos├── backend/copy .env.example .env## 🚀 Inicio Rápido



## 🚢 Despliegue│   ├── ai/                # Agente IA



### Backend (Sugerencias)│   ├── api/               # Endpoints RESTnotepad .env  # Add your credentials



- **Railway**: [railway.app](https://railway.app/) - Deploy automático desde GitHub│   ├── auth/              # Autenticación

- **Render**: [render.com](https://render.com/) - Free tier disponible

- **DigitalOcean**: App Platform con Python + MySQL│   ├── services/          # Lógica de negocio### Prerrequisitos

- **AWS**: EC2 + RDS MySQL

- **Docker**: Containerizar con `Dockerfile` (pendiente agregar)│   ├── integrations/      # GLPI client



### Frontend (Sugerencias)│   ├── main.py# Launch



- **Vercel**: Para Flutter Web│   └── requirements.txt

- **Netlify**: Para aplicaciones estáticas

- **GitHub Pages**: Hosting gratuito│python start_server.py- ✅ Python 3.9 o superior

- **Firebase Hosting**: CDN global

├── frontend/

### Base de Datos

│   ├── lib/```- ✅ GLPI con API REST habilitada

- **MariaDB/MySQL** local o cloud

- **PlanetScale**: MySQL serverless gratuito│   │   ├── screens/

- **Railway**: MySQL managed database

- **AWS RDS**: MySQL en Amazon│   │   ├── widgets/- ✅ Azure OpenAI configurado (o cuenta OpenAI)



## 🤝 Contribuir│   │   └── services/



Las contribuciones son bienvenidas! Por favor:│   └── pubspec.yaml**Server Endpoints:**- ✅ 10 minutos de tu tiempo



1. Fork este repositorio│

2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)

3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)├── .gitignore- API: `http://localhost:8000/api/v1/`

4. Push a la rama (`git push origin feature/nueva-funcionalidad`)

5. Abre un Pull Request├── LICENSE



## 📄 Licencia└── README.md- Docs: `http://localhost:8000/docs`### Instalación Rápida (Windows)



Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.```



---- Health: `http://localhost:8000/api/v1/health`



<div align="center">---



**Desarrollado con ❤️ usando Groq AI y FastAPI**```powershell



Si este proyecto te fue útil, considera darle una ⭐ en GitHub!## 🔒 Seguridad



</div>### Frontend Deployment# 1. Navegar al proyecto


⚠️ **IMPORTANTE:**

- ✅ **NUNCA** subas `.env` a Gitcd "c:\Users\SANTIAGO\Documents\proyectos\lets see\backend"

- ✅ Cambia `SECRET_KEY` en producción

- ✅ Usa HTTPS en producción```powershell

- ✅ Limita CORS a dominios específicos

cd frontend# 2. Crear entorno virtual

---

python -m venv venv

## 🚢 Despliegue

# Setup.\venv\Scripts\Activate.ps1

### Backend

```bashflutter pub get

# Producción con Gunicorn

pip install gunicorn# 3. Instalar dependencias

gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

```# Run (Chrome recommended)pip install -r requirements.txt



### Frontendflutter run -d chrome

```bash

# Build para web# 4. Configurar

flutter build web --release

# Archivos en build/web/# Or build for productioncopy .env.example .env

```

flutter build webnotepad .env  # Edita con tus tokens

---

```

## 🤝 Contribuir

# 5. Ejecutar

1. Fork el proyecto

2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)## 📋 Configuration Guidepython main.py

3. Commit (`git commit -m 'Agregar funcionalidad'`)

4. Push (`git push origin feature/nueva-funcionalidad`)```

5. Abre un Pull Request

### Required Environment Variables

---

### Verificar Instalación

## 📝 Licencia

```env

MIT License - Ver [LICENSE](LICENSE)

# AI ConfigurationAbre en tu navegador:

---

AI_PROVIDER=groq```

## 🙏 Créditos

GROQ_API_KEY=gsk_xxxxx  # Get free at console.groq.comhttp://localhost:8000/docs

- [Groq](https://groq.com) - IA ultrarrápida

- [GLPI](https://glpi-project.org) - ITSM open sourceGROQ_MODEL=llama-3.3-70b-versatile```

- [FastAPI](https://fastapi.tiangolo.com) - Web framework

- [Flutter](https://flutter.dev) - UI toolkit



---# GLPI ConfigurationDeberías ver la documentación interactiva de Swagger UI.



## 📧 SoporteGLPI_URL=https://your-glpi.com/apirest.php



- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/glpi-ai-assistant/issues)GLPI_APP_TOKEN=xxxxx  # Setup → General → API### Primera Consulta

- 💬 Discussions: [GitHub Discussions](https://github.com/tu-usuario/glpi-ai-assistant/discussions)

GLPI_USER_TOKEN=xxxxx  # My Settings → Remote access keys

---

En Swagger UI, prueba:

<div align="center">

# Optional```json

**⭐ Si te gusta este proyecto, dale una estrella! ⭐**

HOST=0.0.0.0{

Hecho con ❤️ y ☕

PORT=8000  "query": "¿Cuántos tickets tengo abiertos?"

</div>

DEBUG=false}

MAX_TOKENS=1500```

TEMPERATURE=0.7

```---



### GLPI API Setup## 📖 Documentación Completa



1. Enable REST API in GLPI: **Setup → General → API**- **🚀 [QUICKSTART.md](QUICKSTART.md)**: Comandos rápidos de instalación

2. Create Application Token- **📋 [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)**: Plan completo del proyecto

3. Generate User Token: **My Settings → Remote access keys**- **📘 [GETTING_STARTED.md](docs/GETTING_STARTED.md)**: Guía paso a paso detallada

4. Ensure user has appropriate permissions- **🔧 [GLPI_API_GUIDE.md](docs/GLPI_API_GUIDE.md)**: Configurar GLPI API

- **🧠 [AZURE_OPENAI_SETUP.md](docs/AZURE_OPENAI_SETUP.md)**: Configurar Azure OpenAI

## 📊 API Reference- **💬 [EXAMPLES.md](docs/EXAMPLES.md)**: Ejemplos de consultas

- **❓ [FAQ.md](docs/FAQ.md)**: Preguntas frecuentes

### POST /api/v1/query- **📊 [EXECUTIVE_SUMMARY.md](docs/EXECUTIVE_SUMMARY.md)**: Resumen ejecutivo



Process natural language queries against GLPI data.---



**Request:**## � Estructura del Proyecto

```json

{```

  "query": "How many high priority tickets are open?",lets see/

  "user_id": 1├── 📄 README.md                    ← Estás aquí

}├── 🚀 QUICKSTART.md                ← Inicio rápido

```│

├── backend/                        ← Aplicación backend

**Response:**│   ├── main.py                     ← Punto de entrada

```json│   ├── config.py                   ← Configuración

{│   ├── requirements.txt            ← Dependencias

  "success": true,│   ├── .env                        ← Variables (crear desde .env.example)

  "message": "## System Overview\n\nTotal tickets: 1012...",│   │

  "data": {│   ├── api/                        ← API REST

    "total": 1012,│   │   ├── routes.py               ← Endpoints

    "showing": 1012,│   │   └── schemas.py              ← Modelos de datos

    "stats": {│   │

      "por_estado": {"Nuevo": 1009, "En Proceso (Asignado)": 2},│   ├── services/                   ← Lógica de negocio

      "por_prioridad": {"Alta": 207, "Media": 209, "Baja": 209}│   │   └── agent_service.py        ← Orquestador principal

    }│   │

  },│   ├── integrations/               ← Integraciones externas

  "intention": "consultar_tickets",│   │   └── glpi_client.py          ← Cliente API GLPI

  "confidence": 0.98│   │

}│   └── ai/                         ← Inteligencia Artificial

```│       └── agent.py                ← Agente IA (Azure OpenAI)

│

### GET /api/v1/health└── docs/                           ← Documentación

    ├── GETTING_STARTED.md          ← Guía completa

Check system health and connectivity.    ├── IMPLEMENTATION_PLAN.md      ← Plan del proyecto

    ├── GLPI_API_GUIDE.md           ← Setup GLPI

**Response:**    ├── AZURE_OPENAI_SETUP.md       ← Setup Azure OpenAI

```json    ├── EXAMPLES.md                 ← Ejemplos de uso

{    ├── FAQ.md                      ← Preguntas frecuentes

  "status": "healthy",    └── EXECUTIVE_SUMMARY.md        ← Resumen ejecutivo

  "glpi_connected": true,```

  "azure_openai_available": true

}---

```

## 🔑 Tecnologías Utilizadas

## 🎨 Design System

### Backend

### Response Format Standards- **[Python 3.9+](https://www.python.org/)**: Lenguaje principal

- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web moderno

✅ **Professional:**- **[Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)**: GPT-4 para IA

```- **[Requests](https://requests.readthedocs.io/)**: Cliente HTTP para GLPI

## Ticket Analysis- **[Pydantic](https://pydantic-docs.helpmanual.io/)**: Validación de datos

- **[Uvicorn](https://www.uvicorn.org/)**: Servidor ASGI

Total open tickets: 247

### Frontend (Próxima fase)

### Breakdown by Priority- **[Flutter](https://flutter.dev/)**: Framework multiplataforma

• High: 45 tickets (18.2%)- **[Dart](https://dart.dev/)**: Lenguaje de programación

• Medium: 156 tickets (63.2%)

• Low: 46 tickets (18.6%)### Integraciones

- **[GLPI API REST](https://glpi-project.org/)**: Sistema de gestión de TI

### Recommendation- **[Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)**: Procesamiento de lenguaje natural

Consider addressing high-priority tickets first to improve SLA compliance.

```---



❌ **Avoid Excessive Emojis:**## 💡 Ejemplos de Uso

```

🎉🎉 WOW! 🚀 You have 247 tickets! 😱### Consultar Tickets

📊 Let's see: ```json

🔥 High: 45 ticketsPOST /api/v1/query

⭐ Medium: 156 tickets{

✅ Low: 46 tickets  "query": "¿Cuántos tickets tengo abiertos?",

```  "user_id": 2

}

### UI/UX Principles```



- **Color Palette**: Microsoft-inspired blues (#0078D4)**Respuesta:**

- **Typography**: Segoe UI font family```json

- **Spacing**: 4px/8px/12px/16px grid system{

- **Borders**: 1px subtle dividers  "success": true,

- **Shadows**: Minimal, elevation-based  "message": "📊 Tienes 5 tickets abiertos actualmente:\n1. 🎫 #123 - Problema con impresora\n2. 🎫 #124 - Solicitud de software...",

  "intention": "consultar_tickets",

## 📈 Performance Characteristics  "confidence": 0.98

}

| Metric | Target | Actual |```

|--------|--------|--------|

| Ticket Processing (1K) | <10s | ~7s |### Buscar Ticket Específico

| Query Response Time | <3s | <2s |```json

| Intent Classification | >90% | 95%+ |POST /api/v1/query

| Concurrent Users | 50+ | 100+ |{

| UI Frame Rate | 60fps | 60fps |  "query": "Muéstrame el ticket 123"

}

## 🔒 Security & Compliance```



- **Authentication**: Token-based (GLPI app/user tokens)### Inventario

- **Data Validation**: Pydantic models on all inputs```json

- **Rate Limiting**: Configurable per endpointPOST /api/v1/query

- **CORS**: Configurable origins{

- **Secrets Management**: Environment variables only  "query": "Busca la computadora de Juan"

- **Audit Logging**: All queries logged with timestamps}

```

## 🛠️ Development

Ver más ejemplos en **[docs/EXAMPLES.md](docs/EXAMPLES.md)**

### Project Structure

---

```

glpi-assistant/## 🎯 Roadmap

├── backend/

│   ├── domain/         # Business entities### ✅ Fase 1: Backend MVP (Completado)

│   ├── application/    # Use cases & services- [x] Estructura del proyecto

│   ├── infrastructure/ # External integrations- [x] Integración con GLPI API

│   └── api/            # REST endpoints- [x] Integración con Azure OpenAI

├── frontend/- [x] API REST funcional

│   ├── lib/- [x] Documentación completa

│   │   ├── theme/      # Design system

│   │   ├── providers/  # State management### ⏳ Fase 2: Configuración (En progreso)

│   │   ├── screens/    # Main views- [ ] Instalar dependencias

│   │   └── widgets/    # UI components- [ ] Configurar GLPI tokens

│   └── assets/- [ ] Configurar Azure OpenAI

└── docs/               # Technical documentation- [ ] Primera consulta exitosa

```

### 📱 Fase 3: Frontend Flutter

### Code Quality Standards- [ ] Setup de Flutter

- [ ] Diseño de interfaz

- **Type Safety**: Full type hints in Python, strong typing in Dart- [ ] Integración con API

- **Linting**: Enforced via flake8 (Python) and dart analyze- [ ] Testing en dispositivos

- **Documentation**: Docstrings on all public methods

- **Testing**: Unit tests for business logic### 🚀 Fase 4: Producción

- **Version Control**: Semantic versioning (MAJOR.MINOR.PATCH)- [ ] Deploy backend (Azure/Railway)

- [ ] Deploy frontend (Firebase)

## 📝 License- [ ] Monitoreo y logs

- [ ] Usuarios en producción

MIT License - See LICENSE file for complete terms

---

## 🤝 Contributing

## 🤝 Contribuciones

Contributions welcome! Please:

1. Fork the repositoryEste proyecto está en desarrollo activo. Las contribuciones son bienvenidas:

2. Create a feature branch (`git checkout -b feature/amazing-feature`)

3. Commit changes (`git commit -m 'Add amazing feature'`)1. Fork el proyecto

4. Push to branch (`git push origin feature/amazing-feature`)2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)

5. Open a Pull Request3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)

4. Push a la rama (`git push origin feature/nueva-funcionalidad`)

## 🗺️ Roadmap5. Abre un Pull Request



### Phase 2 (Q1 2026)---

- [ ] Advanced filtering (date ranges, custom fields)

- [ ] Export functionality (PDF, Excel, CSV)## 📝 Notas Importantes

- [ ] Custom dashboard builder

- [ ] Email notifications### Seguridad

- ⚠️ **Nunca** subas el archivo `.env` a Git

### Phase 3 (Q2 2026)- ⚠️ Los tokens de GLPI y Azure OpenAI son confidenciales

- [ ] Mobile apps (iOS/Android)- ✅ El archivo `.gitignore` ya está configurado correctamente

- [ ] Multi-language UI

- [ ] Voice commands### Costos

- [ ] Predictive analytics- **Desarrollo**: $5-15 USD/mes (Azure OpenAI)

- **Producción**: $30-100 USD/mes (depende del uso)

### Phase 4 (Q3 2026)- **Alternativa gratis**: Usar modelos locales (Ollama)

- [ ] Integration with MS Teams/Slack

- [ ] Automated ticket routing### Soporte

- [ ] SLA tracking and alerts- 📖 Consulta la documentación en `docs/`

- [ ] Custom AI model training- 🐛 Revisa logs en `logs/app.log`

- ❓ Lee el [FAQ](docs/FAQ.md)

## 📞 Support

---

- **Documentation**: See `/docs` folder

- **API Docs**: `http://localhost:8000/docs`## 📄 Licencia

- **Issues**: GitHub Issues

- **Email**: support@example.comEste proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.



------



**Version**: 1.0.0  ## 🙏 Agradecimientos

**Status**: ✅ Production Ready  

**Last Updated**: November 13, 2025  - [GLPI Project](https://glpi-project.org/) - Sistema de gestión de TI

**Maintainer**: Enterprise IT Team- [FastAPI](https://fastapi.tiangolo.com/) - Framework web

- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - Servicio de IA
- [OpenAI](https://openai.com/) - Modelos GPT

---

## 📞 Contacto y Soporte

Para preguntas y soporte:
- 📖 Lee la [documentación completa](docs/)
- ❓ Consulta las [preguntas frecuentes](docs/FAQ.md)
- 🚀 Sigue la [guía de inicio rápido](QUICKSTART.md)

---

<div align="center">

**🤖 Agente Inteligente para GLPI (Tooli)**

*Facilitando el acceso a información de TI mediante IA*

[Documentación](docs/) • [Inicio Rápido](QUICKSTART.md) • [Ejemplos](docs/EXAMPLES.md)

</div>
