# Flujo de Datos y Extracción de Información

##  Objetivo de este Documento

Explicar en detalle **cómo se extrae la información de GLPI**, **cómo funciona el chatbot con IA**, y el **flujo completo de datos** desde que el usuario hace una pregunta hasta que recibe una respuesta.

---

##  ¿Cómo se Extrae la Información de GLPI?

### Método de Extracción: **API REST de GLPI**

**IMPORTANTE**: El sistema **NO accede directamente a la base de datos de GLPI**. En su lugar, utiliza la **API REST oficial de GLPI** para extraer información de manera segura y estructurada.

### ¿Por Qué API REST y No Base de Datos Directa?

| Método | Ventajas | Desventajas |
|--------|----------|-------------|
| **API REST**  | • Método oficial y soportado<br>• Respeta la lógica de negocio de GLPI<br>• No rompe permisos ni integridad<br>• Más seguro<br>• Independiente de la estructura de DB | • Ligeramente más lento<br>• Limitado por API |
| **Acceso Directo a DB** ❌ | • Más rápido<br>• Acceso a todo | • No es oficial<br>• Puede romper permisos<br>• Inseguro<br>• Dependiente de la estructura de DB<br>• No recomendado |

**Decisión del proyecto**: Se usa **API REST** por ser el método oficial, seguro y mantenible.

---

## Autenticación con GLPI API

### Proceso de Autenticación

```python
# Archivo: backend/integrations/glpi_client.py

class GLPIClient:
    def init_session(self) -> bool:
        """Inicializa sesión con GLPI"""
        
        # 1. Hacer petición a /initSession
        url = f"{self.base_url}/initSession"
        
        # 2. Headers requeridos
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token,        # Token de la aplicación
            "Authorization": f"user_token {self.user_token}"  # Token del usuario
        }
        
        # 3. Enviar petición GET
        response = requests.get(url, headers=headers)
        
        # 4. Extraer session_token
        data = response.json()
        self.session_token = data.get("session_token")
        
        # 5. Usar session_token en todas las peticiones subsecuentes
        return True
```

### Tokens Requeridos

1. **App-Token**: Identifica la aplicación (se crea en GLPI)
2. **User-Token**: Identifica al usuario (se crea en GLPI)
3. **Session-Token**: Token temporal de sesión (se obtiene al iniciar sesión)

**Configuración** (archivo `.env`):
```bash
GLPI_URL=http://ip-vm:8200/apirest.php
GLPI_APP_TOKEN=tu_app_token_aqui
GLPI_USER_TOKEN=tu_user_token_aqui
```

---

## 📡 Extracción de Tickets

### Endpoint de GLPI

```
GET /apirest.php/Ticket
```

### Proceso Completo

```python
# Archivo: backend/integrations/glpi_client.py

def get_tickets(self, filters: Optional[Dict] = None, limit: int = None) -> Dict[str, Any]:
    """
    Obtiene tickets de GLPI con paginación automática
    """
    
    # 1. Construir URL
    url = f"{self.base_url}/Ticket"
    
    # 2. Parámetros de consulta
    params = {
        "expand_dropdowns": "true"  # Convierte IDs a nombres legibles
    }
    
    # 3. Aplicar filtros (ejemplo: tickets abiertos)
    if filters and filters.get("status") == "open":
        # Campo 12 = status, "notold" = todos los estados menos cerrado
        params["criteria[0][field]"] = "12"
        params["criteria[0][searchtype]"] = "equals"
        params["criteria[0][value]"] = "notold"
    
    # 4. Solicitar primera página (0-99 = 100 tickets)
    params["range"] = "0-99"
    response = requests.get(url, headers=self._get_headers(), params=params)
    
    # 5. GLPI devuelve header Content-Range con el total
    # Ejemplo: "Content-Range: 0-99/1523"
    content_range = response.headers.get('Content-Range', '0-0/0')
    total_tickets = int(content_range.split('/')[-1])
    
    # 6. Obtener JSON de tickets
    tickets = response.json()
    
    # 7. Si hay más tickets, paginar automáticamente
    if len(tickets) < total_tickets and len(tickets) < 10000:  # Límite: 10k
        all_tickets = list(tickets)
        page = 1
        
        while len(all_tickets) < min(total_tickets, 10000):
            start = page * 100
            end = start + 99
            params["range"] = f"{start}-{end}"
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            page_tickets = response.json()
            
            if not page_tickets:
                break
            
            all_tickets.extend(page_tickets)
            page += 1
        
        tickets = all_tickets
    
    # 8. Generar estadísticas
    stats = self._generate_ticket_stats(tickets)
    
    # 9. Devolver estructura completa
    return {
        "tickets": tickets,        # Lista de tickets
        "total": total_tickets,    # Total en GLPI
        "showing": len(tickets),   # Cantidad descargada
        "stats": stats             # Estadísticas calculadas
    }
```

### Estructura de Respuesta de GLPI

```json
[
  {
    "id": 123,
    "name": "Problema con impresora",
    "status": 2,                              // ID numérico
    "status_friendlyname": "En Proceso",      // Texto (por expand_dropdowns)
    "priority": 3,
    "priority_friendlyname": "Media",
    "type": 1,
    "content": "La impresora no imprime...",
    "date_creation": "2024-11-20 10:30:00",
    "date_mod": "2024-11-25 14:20:00",
    "users_id_recipient_friendlyname": "Juan Pérez",
    "entities_id_friendlyname": "TI - Sede Central"
  },
  ...
]
```

---

##  Extracción de Inventario (Computadoras)

### Endpoint de GLPI

```
GET /apirest.php/Computer
```

### Proceso

```python
def get_computers(self, filters: Optional[Dict] = None) -> List[Dict]:
    """Obtiene computadoras del inventario"""
    
    url = f"{self.base_url}/Computer"
    params = {"expand_dropdowns": "true"}
    
    # Filtro por nombre (opcional)
    if filters and filters.get("name"):
        params["criteria[0][field]"] = "1"  # Campo nombre
        params["criteria[0][searchtype]"] = "contains"
        params["criteria[0][value]"] = filters["name"]
    
    response = requests.get(url, headers=self._get_headers(), params=params)
    return response.json()
```

### Estructura de Respuesta

```json
[
  {
    "id": 45,
    "name": "PC-ADMIN-01",
    "computermodels_id_friendlyname": "HP EliteDesk 800",
    "locations_id_friendlyname": "Edificio A - Piso 3",
    "manufacturers_id_friendlyname": "HP",
    "states_id_friendlyname": "En uso",
    "serial": "XYZ123456",
    "otherserial": "INV-2024-045",
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "users_id_friendlyname": "María García",
    "comment": "Equipo asignado a contabilidad"
  },
  ...
]
```

---

##  ¿Cómo Funciona el Chatbot con IA?

### Componentes del Sistema de IA

1. **Groq API**: Servicio cloud que proporciona acceso a modelos LLaMA
2. **Modelo**: LLaMA 3.3-70B-Versatile (70 mil millones de parámetros)
3. **AI Agent**: Clase Python que orquesta las llamadas a Groq

### Arquitectura del AI Agent

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Agent (Python)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. understand_query()                                 │ │
│  │     • Recibe pregunta del usuario                      │ │
│  │     • Envía a Groq con system prompt                   │ │
│  │     • Extrae intención y parámetros                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  2. generate_response()                                │ │
│  │     • Recibe datos de GLPI + consulta                  │ │
│  │     • Envía a Groq con contexto                        │ │
│  │     • Genera respuesta en lenguaje natural             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

##  Fase 1: Comprensión de Intención (understand_query)

### System Prompt

El AI Agent tiene un **system prompt** que define su comportamiento:

```python
# Archivo: backend/ai/agent.py

system_prompt = """
Eres un asistente de IA profesional para el sistema GLPI IT Service Management.

Intenciones disponibles:
- "consultar_tickets": Ver lista de tickets o estadísticas
- "buscar_ticket": Buscar un ticket específico por ID
- "consultar_inventario": Ver inventario de computadoras
- "buscar_equipo": Buscar una computadora específica
- "generar_reporte": Generar reportes
- "consulta_general": Preguntas generales sobre GLPI

Formato de respuesta JSON:
{
    "intencion": "tipo_intencion",
    "parametros": {
        "clave": "valor"
    },
    "respuesta_usuario": "mensaje de confirmación profesional",
    "confianza": 0.95
}
"""
```

### Proceso de Comprensión

```python
def understand_query(self, user_query: str) -> Dict[str, Any]:
    """
    Procesa una consulta del usuario y extrae intención + parámetros
    """
    
    # 1. Enviar a Groq API
    response = self.client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.3,              # Baja temperatura = más preciso
        max_tokens=500,
        response_format={"type": "json_object"}  # Forzar JSON
    )
    
    # 2. Extraer respuesta
    content = response.choices[0].message.content
    result = json.loads(content)
    
    # 3. Resultado
    return result
```

### Ejemplos de Procesamiento

#### Ejemplo 1: Consulta Simple

**Input Usuario**: `"¿Cuántos tickets hay abiertos?"`

**Salida del AI Agent**:
```json
{
  "intencion": "consultar_tickets",
  "parametros": {
    "status": "open",
    "usuario": "todos"
  },
  "respuesta_usuario": "Consultando tickets abiertos.",
  "confianza": 0.98
}
```

#### Ejemplo 2: Búsqueda Específica

**Input Usuario**: `"Muéstrame el ticket 456"`

**Salida del AI Agent**:
```json
{
  "intencion": "buscar_ticket",
  "parametros": {
    "ticket_id": 456
  },
  "respuesta_usuario": "Recuperando ticket #456.",
  "confianza": 0.99
}
```

#### Ejemplo 3: Inventario

**Input Usuario**: `"Busca la computadora de María"`

**Salida del AI Agent**:
```json
{
  "intencion": "buscar_equipo",
  "parametros": {
    "nombre": "maría",
    "tipo": "Computer"
  },
  "respuesta_usuario": "Buscando la computadora de María.",
  "confianza": 0.92
}
```

---

## Orquestación: Agent Service

El **Agent Service** coordina el AI Agent con el GLPI Client:

```python
# Archivo: backend/services/agent_service.py

async def process_query(self, user_query: str) -> Dict[str, Any]:
    """
    Procesa una consulta completa
    """
    
    # PASO 1: Entender la intención con IA
    understanding = self.ai.understand_query(user_query)
    intention = understanding.get("intencion")
    params = understanding.get("parametros", {})
    
    # PASO 2: Ejecutar acción en GLPI según la intención
    if intention == "consultar_tickets":
        glpi_data = self.glpi.get_tickets({"status": params.get("status")})
    
    elif intention == "buscar_ticket":
        ticket_id = params.get("ticket_id")
        glpi_data = self.glpi.get_ticket_by_id(ticket_id)
    
    elif intention == "consultar_inventario":
        glpi_data = self.glpi.get_computers()
    
    elif intention == "buscar_equipo":
        nombre = params.get("nombre")
        glpi_data = self.glpi.get_computers({"name": nombre})
    
    # PASO 3: Generar respuesta en lenguaje natural
    response_message = self.ai.generate_response(
        user_query,
        glpi_data,
        intention
    )
    
    return {
        "success": True,
        "message": response_message,
        "data": glpi_data,
        "intention": intention
    }
```

---

## Fase 2: Generación de Respuesta Natural (generate_response)

### Proceso

```python
def generate_response(self, user_query: str, data: Any, intention: str) -> str:
    """
    Genera respuesta en lenguaje natural basada en datos de GLPI
    """
    
    # 1. Preparar contexto para la IA
    # Si hay estadísticas, usarlas (evita enviar miles de tickets)
    if isinstance(data, dict) and "stats" in data:
        total = data.get("total", 0)
        showing = data.get("showing", 0)
        stats = data["stats"]
        
        context_prompt = f"""
User Query: "{user_query}"

GLPI SYSTEM ANALYSIS - {total} TOTAL TICKETS
Dataset: {showing} tickets analyzed from {total} total records

STATISTICAL BREAKDOWN:

Status Distribution:
{self._format_stats_section(stats.get("por_estado", {}))}

Priority Distribution:
{self._format_stats_section(stats.get("por_prioridad", {}))}

Type Distribution:
{self._format_stats_section(stats.get("por_tipo", {}))}

Provide a professional response in Spanish.
"""
    
    # 2. Enviar a Groq con el contexto
    response = self.client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a professional GLPI assistant."},
            {"role": "user", "content": context_prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    
    # 3. Devolver respuesta generada
    return response.choices[0].message.content
```

### Ejemplo de Respuesta Generada

**Query**: `"¿Cuántos tickets hay abiertos?"`

**Datos GLPI**: 1523 tickets totales, 1000 analizados, estadísticas por estado

**Respuesta Generada por IA**:
```
 Análisis de Tickets Abiertos

Total en sistema: 1,523 tickets
Analizados: 1,000 tickets

**Distribución por Estado:**
• En Proceso (Asignado): 456 tickets (45.6%)
• Nuevo: 312 tickets (31.2%)
• En Espera: 232 tickets (23.2%)

**Distribución por Prioridad:**
• Media: 512 tickets (51.2%)
• Alta: 298 tickets (29.8%)
• Baja: 190 tickets (19.0%)

**Insights:**
- La mayoría de tickets están en proceso de resolución
- Más del 50% tienen prioridad media
- Se recomienda revisar los 312 tickets nuevos pendientes de asignación

¿Necesitas más detalles sobre algún estado específico?
```

---

## Flujo Completo: De Pregunta a Respuesta

```
┌──────────────────────────────────────────────────────────────────┐
│  Usuario pregunta: "¿Cuántos tickets hay abiertos?"              │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Frontend → POST /api/v1/query                                    │
│  { "query": "¿Cuántos tickets hay abiertos?" }                    │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Backend: Agent Service → AIAgent.understand_query()             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  AI Agent → Groq API (LLaMA 3.3)                                 │
│  "Analiza esta pregunta y extrae intención + parámetros"         │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Groq devuelve JSON:                                             │
│  { "intencion": "consultar_tickets",                             │
│    "parametros": {"status": "open"} }                            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Agent Service → GLPIClient.get_tickets({"status": "open"})      │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  GLPI Client → API REST de GLPI                                  │
│  GET /apirest.php/Ticket?criteria[0][field]=12&...               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  GLPI devuelve JSON con tickets + header Content-Range           │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  GLPI Client procesa y pagina (si hay más de 100 tickets)        │
│  Genera estadísticas automáticas                                 │
│  Devuelve: { tickets, total, showing, stats }                    │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Agent Service → AIAgent.generate_response()                     │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  AI Agent → Groq API (LLaMA 3.3)                                  │
│  "Genera respuesta profesional con estos datos estadísticos"      │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Groq devuelve texto en lenguaje natural                         │
│  " Análisis de Tickets Abiertos..."                              │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Backend → Frontend: JSON con respuesta                          │
│  { "success": true, "message": "...", "data": {...} }            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Frontend renderiza mensaje en el chat                           │
│  Usuario ve la respuesta formateada                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Resumen: Extracción de Información

1. **Método**: API REST de GLPI
2. **Autenticación**: App-Token + User-Token → Session-Token
3. **Endpoints principales**:
   - `/Ticket` - Tickets
   - `/Computer` - Inventario
   - `/search/{itemType}` - Búsquedas avanzadas
4. **Paginación**: Automática (100 items por página, hasta 10,000 máximo)
5. **Optimización**: Genera estadísticas localmente para reducir tokens enviados a IA

## Resumen: Funcionamiento del Bot

1. **IA utilizada**: Groq API con modelo LLaMA 3.3-70B-Versatile
2. **Dos fases**:
   - **Comprensión**: Extrae intención y parámetros del texto del usuario
   - **Generación**: Crea respuesta en lenguaje natural basada en datos de GLPI
3. **Orquestación**: Agent Service coordina IA + GLPI
4. **Formato**: System prompts definen el comportamiento de la IA
5. **JSON estructurado**: La IA devuelve datos estructurados, no texto libre

---

## Notas Importantes

- **Seguridad**: Nunca se accede directamente a la base de datos de GLPI
- **Escalabilidad**: El sistema puede manejar miles de tickets gracias a paginación y estadísticas
- **Flexibilidad**: System prompts se pueden ajustar para cambiar el comportamiento de la IA
- **Costo**: Groq API es gratuita hasta cierto límite de uso
- **Latencia**: Típicamente 1-3 segundos por consulta completa (IA + GLPI)
