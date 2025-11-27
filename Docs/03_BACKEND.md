# Documentación del Backend

## 📂 Estructura del Backend

```
backend/
├── main.py                    # Punto de entrada de la aplicación FastAPI
├── config.py                  # Configuración global (settings)
├── requirements.txt           # Dependencias Python
│
├── ai/                        # Módulo de Inteligencia Artificial
│   ├── __init__.py
│   └── agent.py               # AI Agent con Groq (LLaMA 3.3)
│
├── api/                       # Endpoints REST API
│   ├── __init__.py
│   ├── routes.py              # Rutas principales (/query, /chat, /health)
│   ├── schemas.py             # Modelos Pydantic para validación
│   ├── chat_schemas.py        # Schemas de chat
│   ├── conversation_routes.py # Gestión de conversaciones
│   ├── settings_routes.py     # Configuración de usuario
│   ├── statistics_routes.py   # Estadísticas del sistema
│   ├── tickets_routes.py      # CRUD de tickets
│   └── inventory_routes.py    # Consulta de inventario
│
├── application/               # Lógica de aplicación
│   └── prompts.py             # System prompts para la IA
│
├── auth/                      # Sistema de autenticación
│   ├── __init__.py
│   ├── auth_routes.py         # Login, registro, logout
│   ├── jwt_auth.py            # Generación y validación JWT
│   ├── database.py            # Conexión a DB de autenticación
│   ├── models.py              # Modelos ORM (User, Session, etc.)
│   ├── sso_routes.py          # OAuth/OIDC endpoints
│   ├── sso_service.py         # Lógica de SSO
│   ├── sso_models.py          # Modelos de SSO
│   └── chat_models.py         # Modelos de chat
│
├── database/                  # Scripts de base de datos
│   ├── chat_schema.sql        # Schema para chat
│   ├── sso_schema.sql         # Schema para SSO
│   ├── complete_schema.sql    # Schema completo
│   ├── apply_chat_schema.py   # Aplicar schema
│   └── test_connection.py     # Test de conexión
│
├── domain/                    # Entidades de dominio
│   └── entities/
│       ├── __init__.py
│       ├── query.py           # Entidad Query
│       ├── response.py        # Entidad Response
│       └── ticket.py          # Entidad Ticket
│
├── infrastructure/            # Capa de infraestructura
│   ├── database.py            # Interfaz de base de datos
│   ├── mysql_database.py      # Implementación MySQL
│   └── sqlite_database.py     # Implementación SQLite
│
├── integrations/              # Integraciones externas
│   ├── __init__.py
│   └── glpi_client.py         # Cliente API REST de GLPI
│
└── services/                  # Servicios de negocio
    ├── __init__.py
    ├── agent_service.py       # Orquestador principal (IA + GLPI)
    └── conversation_service.py # Gestión de conversaciones
```

---

## Punto de Entrada: main.py

```python
# Archivo: backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Crear aplicación FastAPI
app = FastAPI(
    title="Agente Inteligente GLPI (Tooli)",
    description="API REST para consultar GLPI mediante lenguaje natural",
    version="1.0.0",
    docs_url="/docs",        # Documentación Swagger UI
    redoc_url="/redoc"       # Documentación ReDoc
)

# Configurar CORS (permitir peticiones desde frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # En producción: especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(router, prefix="/api/v1")
app.include_router(auth_router)
app.include_router(sso_router)
app.include_router(conversation_router)
app.include_router(settings_router)
app.include_router(statistics_router)
app.include_router(tickets_router, prefix="/api/v1/tickets")
app.include_router(inventory_router, prefix="/api/v1/inventory")

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    logger.info(" Iniciando Agente Inteligente GLPI...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(" Cerrando Agente Inteligente GLPI...")
```

**Ejecución**:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

##  Configuración: config.py

```python
# Archivo: backend/config.py

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Configuración centralizada de la aplicación"""
    
    # Servidor
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Groq AI
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", env="GROQ_MODEL")
    
    # GLPI
    glpi_url: Optional[str] = Field(default=None, env="GLPI_URL")
    glpi_app_token: Optional[str] = Field(default=None, env="GLPI_APP_TOKEN")
    glpi_user_token: Optional[str] = Field(default=None, env="GLPI_USER_TOKEN")
    
    # Security (JWT)
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instancia global
settings = Settings()
```

**Archivo .env**:
```bash
# GLPI
GLPI_URL=http://20.151.72.161:8200/apirest.php
GLPI_APP_TOKEN=tu_app_token
GLPI_USER_TOKEN=tu_user_token

# Groq AI
GROQ_API_KEY=tu_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# Security
SECRET_KEY=tu_clave_secreta_super_segura_cambiar_en_produccion
```

---

## Módulo AI: agent.py

### Clase AIAgent

```python
# Archivo: backend/ai/agent.py

from groq import Groq
import json

class AIAgent:
    """Agente de IA para procesar consultas en lenguaje natural"""
    
    def __init__(self, groq_api_key: str, groq_model: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = groq_model
        self.system_prompt = """..."""  # Prompt detallado
    
    def understand_query(self, user_query: str) -> Dict[str, Any]:
        """
        Analiza una consulta y extrae intención + parámetros
        
        Returns:
            {
                "intencion": "consultar_tickets",
                "parametros": {"status": "open"},
                "respuesta_usuario": "Consultando tickets abiertos.",
                "confianza": 0.98
            }
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    def generate_response(
        self,
        user_query: str,
        data: Any,
        intention: str
    ) -> str:
        """
        Genera respuesta en lenguaje natural basada en datos de GLPI
        """
        # Preparar contexto (evitar exceder límite de tokens)
        if isinstance(data, dict) and "stats" in data:
            # Usar estadísticas en lugar de enviar todos los tickets
            context = self._build_stats_context(data)
        else:
            context = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Generar respuesta
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional GLPI assistant."},
                {"role": "user", "content": f"User Query: {user_query}\n\nData: {context}"}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
```

### Intenciones Soportadas

| Intención | Descripción | Parámetros |
|-----------|-------------|------------|
| `consultar_tickets` | Ver lista de tickets o estadísticas | `status`, `usuario` |
| `buscar_ticket` | Buscar ticket específico por ID | `ticket_id` |
| `consultar_inventario` | Ver inventario de computadoras | - |
| `buscar_equipo` | Buscar computadora específica | `nombre` |
| `generar_reporte` | Generar reportes | `tipo` |
| `consulta_general` | Preguntas generales sobre GLPI | - |

---

## 🔌 Integración GLPI: glpi_client.py

### Clase GLPIClient

```python
# Archivo: backend/integrations/glpi_client.py

import requests

class GLPIClient:
    """Cliente para la API REST de GLPI"""
    
    def __init__(self, url: str, app_token: str, user_token: str):
        self.base_url = url.rstrip('/')
        self.app_token = app_token
        self.user_token = user_token
        self.session_token = None
    
    def init_session(self) -> bool:
        """Inicializa sesión con GLPI"""
        url = f"{self.base_url}/initSession"
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token,
            "Authorization": f"user_token {self.user_token}"
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        self.session_token = data.get("session_token")
        return True
    
    def kill_session(self) -> bool:
        """Cierra la sesión con GLPI"""
        if not self.session_token:
            return True
        
        url = f"{self.base_url}/killSession"
        response = requests.get(url, headers=self._get_headers())
        self.session_token = None
        return True
    
    def get_tickets(self, filters: Optional[Dict] = None, limit: int = None) -> Dict[str, Any]:
        """
        Obtiene tickets con paginación automática
        
        Returns:
            {
                "tickets": [...],
                "total": 1523,
                "showing": 1000,
                "stats": {...}
            }
        """
        if not self.session_token:
            self.init_session()
        
        url = f"{self.base_url}/Ticket"
        params = {"expand_dropdowns": "true"}
        
        # Aplicar filtros
        if filters and filters.get("status") == "open":
            params["criteria[0][field]"] = "12"
            params["criteria[0][searchtype]"] = "equals"
            params["criteria[0][value]"] = "notold"
        
        # Paginación automática
        # ... (ver código completo en glpi_client.py)
        
        return {
            "tickets": tickets,
            "total": total_tickets,
            "showing": len(tickets),
            "stats": self._generate_ticket_stats(tickets)
        }
    
    def get_ticket_by_id(self, ticket_id: int) -> Optional[Dict]:
        """Obtiene un ticket específico"""
        url = f"{self.base_url}/Ticket/{ticket_id}"
        response = requests.get(url, headers=self._get_headers())
        return response.json()
    
    def get_computers(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Obtiene computadoras del inventario"""
        url = f"{self.base_url}/Computer"
        params = {"expand_dropdowns": "true"}
        
        if filters and filters.get("name"):
            params["criteria[0][field]"] = "1"
            params["criteria[0][searchtype]"] = "contains"
            params["criteria[0][value]"] = filters["name"]
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        return response.json()
```

### Métodos Principales

| Método | Descripción | Retorno |
|--------|-------------|---------|
| `init_session()` | Inicia sesión en GLPI | `bool` |
| `kill_session()` | Cierra sesión | `bool` |
| `get_tickets()` | Obtiene tickets con paginación | `Dict[tickets, total, showing, stats]` |
| `get_ticket_by_id()` | Obtiene ticket por ID | `Dict` |
| `get_computers()` | Obtiene inventario de computadoras | `List[Dict]` |
| `search_items()` | Búsqueda genérica | `List[Dict]` |
| `get_my_tickets()` | Tickets del usuario actual | `List[Dict]` |

---

##  Servicios: agent_service.py

### Clase AgentService (Orquestador)

```python
# Archivo: backend/services/agent_service.py

class AgentService:
    """Servicio que coordina el agente IA y GLPI"""
    
    def __init__(self, glpi_client: GLPIClient, ai_agent: AIAgent):
        self.glpi = glpi_client
        self.ai = ai_agent
    
    async def process_query(self, user_query: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Procesa una consulta completa (pipeline completo)
        
        Flujo:
        1. Entender intención (IA)
        2. Ejecutar acción en GLPI
        3. Generar respuesta (IA)
        """
        
        # Paso 1: Entender intención
        understanding = self.ai.understand_query(user_query)
        intention = understanding.get("intencion")
        params = understanding.get("parametros", {})
        confidence = understanding.get("confianza", 0.0)
        
        # Validar confianza
        if confidence < 0.6:
            return {
                "success": False,
                "message": understanding.get("respuesta_usuario"),
                "data": None,
                "intention": "low_confidence"
            }
        
        # Paso 2: Ejecutar acción en GLPI
        glpi_data = await self._execute_glpi_action(intention, params, user_id)
        
        # Paso 3: Generar respuesta
        response_message = self.ai.generate_response(
            user_query,
            glpi_data,
            intention
        )
        
        return {
            "success": True,
            "message": response_message,
            "data": glpi_data,
            "intention": intention,
            "confidence": confidence
        }
    
    async def _execute_glpi_action(
        self,
        intention: str,
        params: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Any:
        """Ejecuta la acción correspondiente en GLPI según la intención"""
        
        if intention == "consultar_tickets":
            status = params.get("status", "open")
            return self.glpi.get_tickets({"status": status})
        
        elif intention == "buscar_ticket":
            ticket_id = params.get("ticket_id")
            return self.glpi.get_ticket_by_id(ticket_id)
        
        elif intention == "consultar_inventario":
            return self.glpi.get_computers()
        
        elif intention == "buscar_equipo":
            nombre = params.get("nombre")
            return self.glpi.get_computers({"name": nombre})
        
        # ... más intenciones
        
        return None
```

---

## API REST: routes.py

### Endpoints Principales

```python
# Archivo: backend/api/routes.py

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.post("/query", response_model=QueryResponse, tags=["Agent"])
async def process_query(
    request: QueryRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Procesa una consulta en lenguaje natural
    
    Request:
        {
            "query": "¿Cuántos tickets hay abiertos?",
            "user_id": 123
        }
    
    Response:
        {
            "success": true,
            "message": " Análisis de Tickets...",
            "data": {...},
            "intention": "consultar_tickets",
            "confidence": 0.98
        }
    """
    result = await agent_service.process_query(
        user_query=request.query,
        user_id=request.user_id
    )
    return QueryResponse(**result)


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(
    glpi_client: GLPIClient = Depends(get_glpi_client),
    ai_agent: AIAgent = Depends(get_ai_agent)
):
    """
    Verifica el estado del sistema
    
    Comprueba:
    - Conexión con GLPI
    - Disponibilidad de Groq AI
    """
    glpi_ok = glpi_client.init_session()
    if glpi_ok:
        glpi_client.kill_session()
    
    return HealthResponse(
        status="healthy" if glpi_ok else "degraded",
        glpi_connected=glpi_ok,
        groq_ai_available=True
    )
```

### Dependencias (Dependency Injection)

```python
def get_glpi_client() -> GLPIClient:
    """Crea una instancia del cliente GLPI"""
    return GLPIClient(
        url=settings.glpi_url,
        app_token=settings.glpi_app_token,
        user_token=settings.glpi_user_token
    )

def get_ai_agent() -> AIAgent:
    """Obtiene una instancia del agente de IA"""
    return AIAgent(
        groq_api_key=settings.groq_api_key,
        groq_model=settings.groq_model
    )

def get_agent_service(
    glpi_client: GLPIClient = Depends(get_glpi_client),
    ai_agent: AIAgent = Depends(get_ai_agent)
) -> AgentService:
    """Crea una instancia del servicio de agente"""
    return AgentService(glpi_client, ai_agent)
```

---

## Endpoints de Tickets: tickets_routes.py

```python
# Archivo: backend/api/tickets_routes.py

router = APIRouter()

@router.get("/")
def get_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los tickets de GLPI con filtros opcionales
    
    Query Parameters:
    - status: new, assigned, in_progress, pending, solved, closed
    - priority: very_low, low, medium, high, very_high
    - category: nombre de categoría
    - search: búsqueda en título/descripción
    """
    # Autenticar usuario
    user = get_user_from_token(authorization, db)
    
    # Obtener tickets de GLPI
    glpi = get_glpi_client()
    glpi_response = glpi.get_tickets(limit=1000)
    glpi_tickets = glpi_response.get("tickets", [])
    
    # Convertir a formato frontend
    tickets = [map_glpi_ticket_to_frontend(t) for t in glpi_tickets]
    
    # Aplicar filtros
    if status:
        tickets = [t for t in tickets if t["status"] == status]
    if priority:
        tickets = [t for t in tickets if t["priority"] == priority]
    # ... más filtros
    
    return tickets

@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Obtiene un ticket específico por ID"""
    user = get_user_from_token(authorization, db)
    glpi = get_glpi_client()
    ticket = glpi.get_ticket_by_id(ticket_id)
    return map_glpi_ticket_to_frontend(ticket)
```

---

## Endpoints de Inventario: inventory_routes.py

```python
# Archivo: backend/api/inventory_routes.py

router = APIRouter()

@router.get("/")
def get_inventory(
    status: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Obtiene inventario de computadoras con filtros
    """
    user = get_user_from_token(authorization, db)
    
    glpi = get_glpi_client()
    computers = glpi.get_computers()
    
    # Convertir a formato frontend
    inventory = [map_glpi_computer_to_frontend(c) for c in computers]
    
    # Aplicar filtros
    if status:
        inventory = [i for i in inventory if i["status"] == status]
    # ... más filtros
    
    return inventory

@router.get("/{item_id}")
def get_inventory_item(
    item_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Obtiene detalles de un item de inventario"""
    # ... implementación
```

---

## Autenticación: jwt_auth.py

```python
# Archivo: backend/auth/jwt_auth.py

import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password con bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica password contra hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crea JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica y valida JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Autentica usuario con username y password"""
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if user and verify_password(password, user.password_hash) and user.is_active:
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        return user
    
    return None
```

---

## Modelos de Datos: models.py

```python
# Archivo: backend/auth/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """Modelo de usuario"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
    last_login = Column(DateTime)

class Session(Base):
    """Modelo de sesión"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

class LoginAttempt(Base):
    """Modelo de intento de login"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=False)
    success = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, nullable=False)
```

---

## Schemas Pydantic: schemas.py

```python
# Archivo: backend/api/schemas.py

from pydantic import BaseModel
from typing import Optional, Any

class QueryRequest(BaseModel):
    """Request para consulta en lenguaje natural"""
    query: str
    user_id: Optional[int] = None

class QueryResponse(BaseModel):
    """Response de consulta"""
    success: bool
    message: str
    data: Optional[Any] = None
    intention: Optional[str] = None
    confidence: Optional[float] = None

class HealthResponse(BaseModel):
    """Response de health check"""
    status: str
    glpi_connected: bool
    groq_ai_available: bool
```

---

## Logging: Loguru

```python
# Archivo: backend/main.py

from loguru import logger
import sys

# Configurar logger
logger.remove()

# Console output
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)

# File output
logger.add(
    "logs/app.log",
    rotation="10 MB",      # Rotar cada 10 MB
    retention="7 days",    # Mantener logs por 7 días
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level="DEBUG"
)
```

---

## Resumen del Backend

### Tecnologías Clave
- **Framework**: FastAPI (async, rápido, documentación automática)
- **IA**: Groq API (LLaMA 3.3-70B)
- **Integración**: GLPI API REST
- **Autenticación**: JWT + bcrypt
- **Base de Datos**: MariaDB (para SSO y autenticación)
- **Logging**: Loguru
- **Validación**: Pydantic

### Flujo de Petición
1. **Request** → FastAPI endpoint
2. **Autenticación** → JWT validation
3. **Dependency Injection** → Servicios instanciados
4. **Agent Service** → Orquesta IA + GLPI
5. **AI Agent** → Procesa con Groq
6. **GLPI Client** → Extrae datos
7. **Response** → JSON estructurado

### Características
- Arquitectura modular y escalable
- Dependency injection para testing
- Documentación automática (Swagger/ReDoc)
- Logging estructurado
- Manejo de errores robusto
- CORS configurado
- Validación de datos con Pydantic
