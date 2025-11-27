# Arquitectura General del Sistema

## 🎯 Resumen Ejecutivo

**GLPI AI Assistant (Tooli)** es un chatbot inteligente diseñado para administradores de TI de la Universidad Tecnológica de Pereira. El sistema permite consultar información de GLPI (inventario, tickets, estadísticas) mediante preguntas en lenguaje natural, utilizando inteligencia artificial para interpretar las consultas y generar respuestas precisas.

---

## 📊 Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO FINAL                            │
│                    (Administradores de TI)                      │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND - Flutter Web                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  • Interfaz de Chat                                      │   │
│  │  • Gestión de Tickets                                    │   │
│  │  • Inventario de TI                                      │   │
│  │  • Estadísticas y Reportes                               │   │
│  │  • Autenticación (Login / SSO)                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP/REST API
                  ▼
┌────────────────────────────────────────────────────────────────┐
│                   BACKEND - FastAPI (Python)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API REST Endpoints                                      │  │
│  │  • /api/v1/query  (consultas en lenguaje natural)        │  │
│  │  • /api/v1/tickets (CRUD tickets)                        │  │
│  │  • /api/v1/inventory (consulta inventario)               │  │
│  │  • /api/v1/auth (autenticación JWT)                      │  │
│  │  • /api/v1/sso (Single Sign-On)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AI Agent Service (Orquestador)                          │  │
│  │  • Procesa consultas del usuario                         │  │
│  │  • Coordina IA + GLPI                                    │  │
│  │  • Genera respuestas naturales                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌────────────────────┐    ┌──────────────────────────────┐    │
│  │  AI Agent (Groq)   │    │   GLPI Client                │    │
│  │  • LLaMA 3.3 70B   │    │   • Integración API REST     │    │
│  │  • NLP             │    │   • Sesiones                 │    │
│  │  • Intenciones     │    │   • Consultas estructuradas  │    │
│  └────────────────────┘    └──────────────────────────────┘    │
└─────────────────┬──────────────────┬───────────────────────────┘
                  │                  │
                  │ Groq API         │ GLPI API REST
                  ▼                  ▼
┌─────────────────────────┐  ┌──────────────────────────────────┐
│    Groq Cloud           │  │   VM - Contenedores Docker       │
│  (LLaMA 3.3 70B API)    │  │  ┌────────────────────────────┐  │
└─────────────────────────┘  │  │  GLPI 11.0.2               │  │
                             │  │  (IT Service Management)   │  │
┌─────────────────────────┐  │  └────────────────────────────┘  │
│   Base de Datos SSO     │  │                                  │
│   MariaDB               │  │  ┌────────────────────────────┐  │
│   • glpi_sso            │  │  │  MariaDB 10.11             │  │
│   • Usuarios            │  │  │  (Base de datos GLPI)      │  │
│   • Sesiones JWT        │  │  │  • Tickets                 │  │
│   • Refresh Tokens      │  │  │  • Inventario              │  │
└─────────────────────────┘  │  │  • Usuarios                │  │
                             │  │  • Configuración           │  │
                             │  └────────────────────────────┘  │
                             └──────────────────────────────────┘
```

---

##  Stack Tecnológico

### Backend
- **Lenguaje**: Python 3.10+
- **Framework Web**: FastAPI 0.115.5
- **Servidor ASGI**: Uvicorn
- **IA**: Groq API (LLaMA 3.3-70B-Versatile)
- **Autenticación**: JWT (JSON Web Tokens)
- **ORM**: SQLAlchemy
- **Base de Datos**: MariaDB (para SSO)
- **Logging**: Loguru
- **HTTP Client**: Requests, HTTPX

### Frontend
- **Framework**: Flutter 3.0+
- **Lenguaje**: Dart
- **Plataforma**: Web (compatible con móvil/desktop)
- **Estado**: Provider pattern
- **HTTP**: http package

### Infraestructura Externa (VM)
- **GLPI**: 11.0.2 (Containerizado - Docker)
- **Base de Datos GLPI**: MariaDB 10.11
- **Orquestación**: Docker Compose
- **Automatización**: N8N (opcional)

---

##  Flujo General de Funcionamiento

### 1. Autenticación del Usuario

```
Usuario → Login (Username/Password o SSO) → Backend valida credenciales
                                         ↓
                      Se genera JWT token (Access + Refresh)
                                         ↓
                      Token se almacena en frontend (memoria/localStorage)
                                         ↓
                      Todas las peticiones incluyen: Authorization: Bearer <token>
```

### 2. Consulta en Lenguaje Natural (Chatbot)

**Ejemplo**: Usuario pregunta "¿Cuántos tickets hay abiertos?"

```
┌──────────────────────────────────────────────────────────────────┐
│  PASO 1: Usuario escribe en el chat                              │
│  "¿Cuántos tickets hay abiertos?"                                │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 2: Frontend envía POST a /api/v1/query                     │
│  Body: { "query": "¿Cuántos tickets hay abiertos?" }             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 3: Backend - Agent Service recibe la consulta              │
│  → Llama a AIAgent.understand_query()                            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 4: AI Agent (Groq LLaMA 3.3) analiza el texto              │
│  • Identifica INTENCIÓN: "consultar_tickets"                     │
│  • Extrae PARÁMETROS: { "status": "open" }                       │
│  • Devuelve JSON estructurado                                    │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 5: Agent Service ejecuta acción en GLPI                    │
│  → Llama a GLPIClient.get_tickets({"status": "open"})            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 6: GLPI Client consulta API REST de GLPI                   │
│  GET https://glpi-vm/apirest.php/Ticket?criteria[0][field]=12    │
│  • Autenticación: App-Token + Session-Token                      │
│  • Parámetros: expand_dropdowns=true, filtros de búsqueda        │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 7: GLPI devuelve JSON con tickets                          │
│  [                                                               │
│    {"id": 1, "name": "Problema red", "status": 2, ...},          │
│    {"id": 2, "name": "PC no enciende", "status": 2, ...},        │
│    ...                                                           │
│  ]                                                               │
│  + Header: Content-Range: 0-99/1523 (indica total)               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 8: GLPI Client procesa respuesta                           │
│  • Pagina resultados si hay más de 100 tickets                   │
│  • Genera estadísticas (por estado, prioridad, tipo)             │
│  • Devuelve: {                                                   │
│      "tickets": [...],                                           │
│      "total": 1523,                                              │
│      "showing": 1000,                                            │
│      "stats": {...}                                              │
│    }                                                             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 9: Agent Service recibe datos de GLPI                      │
│  → Llama a AIAgent.generate_response()                           │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 10: AI Agent genera respuesta en lenguaje natural          │
│  • Recibe: query original + datos GLPI + estadísticas            │
│  • Groq LLaMA procesa y genera texto profesional                 │
│  • Ejemplo de respuesta:                                         │
│    " Análisis de Tickets Abiertos                                │
│     Total en sistema: 1,523 tickets                              │
│     Analizados: 1,000 tickets                                    │
│                                                                  │
│     Por Estado:                                                  │
│     • En Proceso: 456 (45.6%)                                    │
│     • Nuevo: 312 (31.2%)                                         │
│     • En Espera: 232 (23.2%)                                     │
│     ..."                                                         │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 11: Backend devuelve respuesta al frontend                 │
│  {                                                               │
│    "success": true,                                              │
│    "message": " Análisis de Tickets...",                         │
│    "data": {...},                                                │
│    "intention": "consultar_tickets",                             │
│    "confidence": 0.98                                            │
│  }                                                               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PASO 12: Frontend muestra respuesta en el chat                  │
│  • Renderiza mensaje formateado (Markdown)                       │
│  • Muestra gráficas si es necesario                              │
│  • Usuario ve la respuesta                                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Características Clave

### 1. Procesamiento de Lenguaje Natural (NLP)
- **Modelo**: LLaMA 3.3-70B (via Groq API)
- **Capacidades**:
  - Comprensión de consultas en español e inglés
  - Extracción de intenciones y parámetros
  - Generación de respuestas contextuales
  - Análisis de grandes volúmenes de datos (1000+ tickets)

### 2. Integración con GLPI
- **Método**: API REST de GLPI (no acceso directo a base de datos)
- **Endpoints utilizados**:
  - `/initSession` - Autenticación
  - `/Ticket` - Consulta de tickets
  - `/Computer` - Consulta de inventario
  - `/search/{itemType}` - Búsquedas avanzadas
  - `/killSession` - Cierre de sesión

### 3. Seguridad
- **Autenticación**: JWT (Access + Refresh tokens)
- **SSO**: OAuth 2.0 con Microsoft Entra ID
- **Validación de dominios**: Solo @unitecnologica.edu.co
- **Cifrado**: Passwords con bcrypt
- **Auditoría**: Logs de intentos de login y accesos SSO

### 4. Arquitectura Modular
- **Backend**: Separación de responsabilidades (API, Servicios, Integraciones)
- **Frontend**: Patrón Provider para gestión de estado
- **Escalabilidad**: Diseñado para soportar múltiples usuarios concurrentes

---

## 📈 Capacidades del Sistema

### Consultas Soportadas

1. **Tickets**
   - Consultar tickets por estado (abiertos, cerrados, pendientes)
   - Buscar ticket específico por ID
   - Estadísticas de tickets (por prioridad, categoría, tipo)
   - Tickets asignados a un usuario

2. **Inventario**
   - Listar computadoras y activos de TI
   - Buscar equipos por nombre, ubicación, modelo
   - Detalles técnicos de hardware (CPU, RAM, disco)
   - Software instalado

3. **Estadísticas y Reportes**
   - Distribución de tickets por estado/prioridad
   - Análisis de tendencias
   - Reportes personalizados

4. **Gestión**
   - Visualización de tickets en tablas
   - Filtrado avanzado
   - Detalles completos de tickets e inventario

---

## 🚀 Ventajas del Sistema

1. **Acceso Rápido**: Consultas en lenguaje natural vs. navegación manual en GLPI
2. **Análisis Inteligente**: IA procesa grandes volúmenes de datos y genera insights
3. **Multiplataforma**: Acceso desde web, móvil o desktop (Flutter)
4. **Seguro**: Autenticación robusta con JWT y SSO institucional
5. **Escalable**: Arquitectura preparada para crecer

---

## 📝 Notas Técnicas

- **Límite de extracción**: Máximo 10,000 tickets por consulta (por rendimiento)
- **Paginación**: GLPI devuelve 100 items por página, el cliente pagina automáticamente
- **Timeouts**: 30 segundos por petición HTTP
- **Cache**: No implementado (cada consulta es en tiempo real)
- **Logs**: Rotación automática cada 10 MB, retención 7 días

---

## 🔗 Referencias

- [Documentación GLPI API REST](https://github.com/glpi-project/glpi/blob/master/apirest.md)
- [Groq API Documentation](https://console.groq.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Flutter Documentation](https://flutter.dev/docs)
