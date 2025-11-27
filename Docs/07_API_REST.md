# Referencia Completa de API REST

## Información General

**Base URL**: `http://localhost:8000` (desarrollo) o `https://tu-dominio.com` (producción)

**Documentación Interactiva**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Autenticación**: JWT Bearer Token (donde se requiera)

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Agent Endpoints

### POST /api/v1/query

Procesa una consulta en lenguaje natural usando IA.

**Request**:
```json
{
  "query": "¿Cuántos tickets hay abiertos?",
  "user_id": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "Análisis de Tickets Abiertos\n\nTotal en sistema: 1,523 tickets...",
  "data": {
    "tickets": [...],
    "total": 1523,
    "showing": 1000,
    "stats": {
      "por_estado": {
        "En Proceso (Asignado)": 456,
        "Nuevo": 312
      }
    }
  },
  "intention": "consultar_tickets",
  "confidence": 0.98
}
```

**Códigos de Estado**:
- `200`: Éxito
- `500`: Error interno

---

### POST /api/v1/chat

Chat conversacional simple (sin consultar GLPI).

**Request**:
```json
{
  "message": "¿Qué es GLPI?"
}
```

**Response**:
```json
{
  "response": "GLPI es un sistema de gestión de activos y servicios de TI..."
}
```

---

### GET /api/v1/health

Verifica el estado del sistema.

**Response**:
```json
{
  "status": "healthy",
  "glpi_connected": true,
  "groq_ai_available": true
}
```

**Estados posibles**:
- `healthy`: Todo funcionando
- `degraded`: Algún servicio con problemas
- `unhealthy`: Servicios críticos caídos

---

## Authentication Endpoints

### POST /api/v1/auth/register

Registrar nuevo usuario.

**Request**:
```json
{
  "username": "jperez",
  "email": "jperez@universidad.edu",
  "password": "SecurePass123!",
  "full_name": "Juan Pérez"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "8f7d2b3c-1a4e-5f6g-7h8i-9j0k1l2m3n4o",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "jperez",
    "email": "jperez@universidad.edu",
    "full_name": "Juan Pérez",
    "is_active": true,
    "is_admin": false
  }
}
```

**Validaciones**:
- Username: 3-50 caracteres, único
- Email: Formato válido, único
- Password: Mínimo 8 caracteres

**Códigos de Estado**:
- `201`: Usuario creado exitosamente
- `400`: Datos inválidos
- `409`: Usuario o email ya existe

---

### POST /api/v1/auth/login

Iniciar sesión.

**Request**:
```json
{
  "username": "jperez",
  "password": "SecurePass123!"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "8f7d2b3c-1a4e-5f6g-7h8i-9j0k1l2m3n4o",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "jperez",
    "email": "jperez@universidad.edu",
    "full_name": "Juan Pérez"
  }
}
```

**Códigos de Estado**:
- `200`: Login exitoso
- `401`: Credenciales inválidas
- `403`: Usuario inactivo

---

### POST /api/v1/auth/refresh

Renovar access token usando refresh token.

**Request**:
```json
{
  "refresh_token": "8f7d2b3c-1a4e-5f6g-7h8i-9j0k1l2m3n4o"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

---

### POST /api/v1/auth/logout

Cerrar sesión (invalida tokens).

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "message": "Logout successful"
}
```

---

### GET /api/v1/auth/me

Obtener información del usuario autenticado.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "id": 1,
  "username": "jperez",
  "email": "jperez@universidad.edu",
  "full_name": "Juan Pérez",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-11-20T10:30:00Z",
  "last_login": "2024-11-25T14:20:00Z"
}
```

---

## Tickets Endpoints

### GET /api/v1/tickets

Obtener lista de tickets con filtros opcionales.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Query Parameters**:
- `status` (opcional): `new`, `assigned`, `in_progress`, `pending`, `solved`, `closed`
- `priority` (opcional): `very_low`, `low`, `medium`, `high`, `very_high`
- `category` (opcional): Nombre de categoría
- `search` (opcional): Búsqueda en título/descripción

**Ejemplo**:
```http
GET /api/v1/tickets?status=new&priority=high
```

**Response**:
```json
[
  {
    "id": 123,
    "title": "Problema con impresora",
    "description": "La impresora del piso 3 no imprime",
    "status": "new",
    "priority": "high",
    "category": "Hardware",
    "requester_name": "Juan Pérez",
    "assigned_to": null,
    "created_at": "2024-11-25T10:30:00Z",
    "updated_at": "2024-11-25T14:20:00Z",
    "due_date": "2024-11-26T18:00:00Z"
  },
  ...
]
```

**Códigos de Estado**:
- `200`: Éxito
- `401`: No autenticado
- `500`: Error al obtener tickets

---

### GET /api/v1/tickets/{ticket_id}

Obtener detalle de un ticket específico.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "id": 123,
  "title": "Problema con impresora",
  "description": "La impresora del piso 3 no imprime desde ayer...",
  "status": "assigned",
  "priority": "high",
  "category": "Hardware",
  "type": "incident",
  "urgency": "high",
  "impact": "medium",
  "requester_name": "Juan Pérez",
  "assigned_to": "María García",
  "created_at": "2024-11-25T10:30:00Z",
  "updated_at": "2024-11-25T14:20:00Z",
  "due_date": "2024-11-26T18:00:00Z",
  "followups": [
    {
      "content": "Se revisó la impresora, problema de tinta",
      "created_by": "María García",
      "created_at": "2024-11-25T11:00:00Z"
    }
  ],
  "tasks": []
}
```

**Códigos de Estado**:
- `200`: Éxito
- `404`: Ticket no encontrado
- `401`: No autenticado

---

## Inventory Endpoints

### GET /api/v1/inventory

Obtener inventario de computadoras.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Query Parameters**:
- `status` (opcional): `in_use`, `available`, `maintenance`, `broken`, `retired`
- `location` (opcional): Ubicación
- `search` (opcional): Búsqueda en nombre

**Response**:
```json
[
  {
    "id": 45,
    "name": "PC-ADMIN-01",
    "type": "computer",
    "status": "in_use",
    "location": "Edificio A - Piso 3",
    "manufacturer": "HP",
    "model": "EliteDesk 800",
    "serial": "XYZ123456",
    "inventory_number": "INV-2024-045",
    "assigned_to": "Juan Pérez",
    "specifications": {
      "Modelo": "HP EliteDesk 800",
      "Tipo": "Desktop",
      "Red": "Ethernet 1Gbps"
    },
    "created_at": "2024-01-15T09:00:00Z",
    "updated_at": "2024-11-20T10:30:00Z"
  },
  ...
]
```

---

### GET /api/v1/inventory/{item_id}

Obtener detalle de un item de inventario.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "id": 45,
  "name": "PC-ADMIN-01",
  "type": "computer",
  "status": "in_use",
  "location": "Edificio A - Piso 3 - Oficina 301",
  "manufacturer": "HP",
  "model": "EliteDesk 800 G4",
  "serial": "XYZ123456",
  "inventory_number": "INV-2024-045",
  "assigned_to": "Juan Pérez",
  "specifications": {
    "Modelo": "HP EliteDesk 800 G4",
    "Tipo": "Desktop",
    "CPU": "Intel Core i7-8700",
    "RAM": "16 GB DDR4",
    "Disco": "512 GB SSD",
    "Red": "Ethernet 1Gbps",
    "Sistema Operativo": "Windows 11 Pro"
  },
  "warranty_expiration": "2026-01-15",
  "purchase_date": "2024-01-15",
  "comments": "Equipo asignado al departamento de contabilidad",
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-11-20T10:30:00Z"
}
```

---

## Conversations Endpoints

### GET /api/v1/conversations

Obtener lista de conversaciones del usuario.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
[
  {
    "id": 1,
    "title": "Conversación 25/11/2024 14:30",
    "created_at": "2024-11-25T14:30:00Z",
    "updated_at": "2024-11-25T15:45:00Z",
    "message_count": 12,
    "is_archived": false
  },
  ...
]
```

---

### GET /api/v1/conversations/{conversation_id}

Obtener detalle de una conversación con mensajes.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "id": 1,
  "title": "Conversación 25/11/2024 14:30",
  "created_at": "2024-11-25T14:30:00Z",
  "updated_at": "2024-11-25T15:45:00Z",
  "is_archived": false,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "¿Cuántos tickets hay abiertos?",
      "created_at": "2024-11-25T14:30:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "📊 Análisis de Tickets Abiertos...",
      "created_at": "2024-11-25T14:30:15Z",
      "tokens_used": 523
    }
  ]
}
```

---

### POST /api/v1/conversations

Crear nueva conversación.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request**:
```json
{
  "title": "Mi nueva conversación"
}
```

**Response**:
```json
{
  "id": 5,
  "title": "Mi nueva conversación",
  "created_at": "2024-11-25T16:00:00Z",
  "updated_at": "2024-11-25T16:00:00Z",
  "message_count": 0,
  "is_archived": false
}
```

---

### POST /api/v1/conversations/{conversation_id}/messages

Agregar mensaje a una conversación.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request**:
```json
{
  "role": "user",
  "content": "¿Cuántos tickets hay abiertos?"
}
```

**Response**:
```json
{
  "id": 10,
  "conversation_id": 1,
  "role": "user",
  "content": "¿Cuántos tickets hay abiertos?",
  "created_at": "2024-11-25T16:05:00Z"
}
```

---

### DELETE /api/v1/conversations/{conversation_id}

Eliminar una conversación.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "message": "Conversation deleted successfully"
}
```

---

## Statistics Endpoints

### GET /api/v1/statistics/dashboard

Obtener estadísticas del dashboard.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "tickets": {
    "total": 1523,
    "open": 856,
    "closed": 667,
    "by_status": {
      "Nuevo": 312,
      "En Proceso": 456,
      "En Espera": 88
    },
    "by_priority": {
      "Alta": 298,
      "Media": 512,
      "Baja": 190
    }
  },
  "inventory": {
    "total_computers": 234,
    "in_use": 198,
    "available": 20,
    "maintenance": 10,
    "broken": 6
  },
  "conversations": {
    "total": 45,
    "this_month": 12
  },
  "queries_today": 87
}
```

---

## Settings Endpoints

### GET /api/v1/settings

Obtener configuración del usuario.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "theme": "dark",
  "language": "es",
  "notifications_enabled": true,
  "email_notifications": false,
  "default_view": "chat",
  "items_per_page": 20
}
```

---

### PUT /api/v1/settings

Actualizar configuración del usuario.

**Headers**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request**:
```json
{
  "theme": "light",
  "language": "es",
  "notifications_enabled": true,
  "items_per_page": 50
}
```

**Response**:
```json
{
  "message": "Settings updated successfully",
  "settings": {
    "theme": "light",
    "language": "es",
    "notifications_enabled": true,
    "items_per_page": 50
  }
}
```

---

## SSO Endpoints

### GET /api/v1/sso/providers

Listar proveedores SSO disponibles.

**Response**:
```json
[
  {
    "name": "microsoft",
    "display_name": "Microsoft",
    "is_active": true
  }
]
```

---

### GET /api/v1/sso/authorize/{provider}

Iniciar flujo SSO (redirige a proveedor).

**Ejemplo**:
```http
GET /api/v1/sso/authorize/microsoft
```

**Response**: Redirección 302 a URL de autorización del proveedor.

---

### GET /api/v1/sso/callback/{provider}

Callback de SSO (maneja respuesta del proveedor).

**Query Parameters**:
- `code`: Código de autorización
- `state`: Token CSRF

**Response**: Redirección al frontend con tokens JWT.

---

## Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| `200` | Éxito |
| `201` | Recurso creado |
| `204` | Éxito sin contenido |
| `400` | Petición inválida |
| `401` | No autenticado |
| `403` | No autorizado |
| `404` | Recurso no encontrado |
| `409` | Conflicto (duplicado) |
| `422` | Entidad no procesable (validación) |
| `500` | Error interno del servidor |
| `503` | Servicio no disponible |

---

## Ejemplos con cURL

### Login y Obtener Token

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jperez",
    "password": "SecurePass123!"
  }'

# Guardar token en variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Consultar Tickets

```bash
curl -X GET "http://localhost:8000/api/v1/tickets?status=new" \
  -H "Authorization: Bearer $TOKEN"
```

### Hacer Query al Chatbot

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuántos tickets hay abiertos?",
    "user_id": 1
  }'
```

---

## Ejemplos con Python

### Usar la API con Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Login
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={
        "username": "jperez",
        "password": "SecurePass123!"
    }
)
token = login_response.json()["access_token"]

# Headers con autenticación
headers = {
    "Authorization": f"Bearer {token}"
}

# Obtener tickets
tickets_response = requests.get(
    f"{BASE_URL}/api/v1/tickets",
    headers=headers,
    params={"status": "new"}
)
tickets = tickets_response.json()
print(f"Tickets nuevos: {len(tickets)}")

# Query al chatbot
query_response = requests.post(
    f"{BASE_URL}/api/v1/query",
    json={
        "query": "¿Cuántos tickets hay abiertos?",
        "user_id": 1
    }
)
result = query_response.json()
print(result["message"])
```

---

## Rate Limiting

**Límites actuales** (configurables):
- Endpoints públicos: 100 peticiones/minuto por IP
- Endpoints autenticados: 1000 peticiones/minuto por usuario
- Query endpoint: 60 peticiones/minuto por usuario (costo IA)

**Headers de respuesta**:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1732567890
```

---

## Seguridad

### Mejores Prácticas

1. **Siempre usar HTTPS** en producción
2. **No compartir tokens** JWT
3. **Renovar tokens** regularmente
4. **Invalidar tokens** al cerrar sesión
5. **Validar entrada** en el cliente también
6. **Monitorear rate limits**

### Headers de Seguridad

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## WebSocket (Futuro)

**Planeado para v2.0**:
- Actualizaciones en tiempo real de tickets
- Notificaciones push
- Chat en vivo con múltiples usuarios

---

## Resumen

### Endpoints Principales

- `POST /api/v1/query` - Chatbot IA
- `POST /api/v1/auth/login` - Autenticación
- `GET /api/v1/tickets` - Lista de tickets
- `GET /api/v1/inventory` - Inventario
- `GET /api/v1/conversations` - Historial de chat

### Autenticación

- JWT Bearer Token
- Expiración: 30 minutos (access token)
- Refresh token: 7 días

### Documentación Interactiva

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**¡La API está lista para ser consumida!** 
