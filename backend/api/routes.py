"""
Endpoints de la API REST
"""

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from api.schemas import (
    QueryRequest,
    QueryResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse
)
from services.agent_service import AgentService
from integrations.glpi_client import GLPIClient
from ai.agent import AIAgent
from config import settings


router = APIRouter()


# Dependencias
def get_glpi_client() -> GLPIClient:
    """Crea una instancia del cliente GLPI"""
    return GLPIClient(
        url=settings.glpi_url,
        app_token=settings.glpi_app_token,
        user_token=settings.glpi_user_token
    )


def get_ai_agent():
    """Obtiene una instancia del agente de IA con Groq"""
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


@router.post("/query", response_model=QueryResponse, tags=["Agent"])
async def process_query(
    request: QueryRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Procesa una consulta en lenguaje natural
    
    El agente identificará la intención, consultará GLPI si es necesario,
    y generará una respuesta en lenguaje natural.
    
    **Ejemplos de consultas:**
    - "¿Cuántos tickets tengo abiertos?"
    - "Busca el ticket 123"
    - "Muéstrame las computadoras del inventario"
    - "Dame un reporte de tickets del mes"
    """
    try:
        logger.info(f"📨 Recibida consulta: {request.query}")
        
        result = await agent_service.process_query(
            user_query=request.query,
            user_id=request.user_id
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Error en /query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse, tags=["Agent"])
async def chat(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Chat simple con el agente (sin consultar GLPI)
    
    Útil para preguntas generales sobre GLPI o el sistema.
    """
    try:
        response = agent_service.chat_simple(request.message)
        return ChatResponse(response=response)
        
    except Exception as e:
        logger.error(f"❌ Error en /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(
    glpi_client: GLPIClient = Depends(get_glpi_client),
    ai_agent: AIAgent = Depends(get_ai_agent)
):
    """
    Verifica el estado del sistema
    
    Comprueba la conexión con GLPI y la disponibilidad de Groq AI.
    """
    try:
        # Verificar GLPI
        glpi_ok = glpi_client.init_session()
        if glpi_ok:
            glpi_client.kill_session()
        
        # Verificar Groq AI (intento simple)
        groq_ok = True
        try:
            ai_agent.chat("test")
        except Exception:
            groq_ok = False
        
        status = "healthy" if (glpi_ok and groq_ok) else "degraded"
        
        return HealthResponse(
            status=status,
            glpi_connected=glpi_ok,
            groq_ai_available=groq_ok
        )
        
    except Exception as e:
        logger.error(f"❌ Error en health check: {e}")
        return HealthResponse(
            status="unhealthy",
            glpi_connected=False,
            groq_ai_available=False
        )


@router.get("/", tags=["System"])
async def root():
    """Endpoint raíz - Información de la API"""
    return {
        "name": "Agente Inteligente GLPI (Tooli)",
        "version": "1.0.0",
        "description": "API para consultar información de GLPI mediante lenguaje natural",
        "endpoints": {
            "POST /query": "Procesar consulta en lenguaje natural",
            "POST /chat": "Chat simple con el agente",
            "GET /health": "Estado del sistema",
            "GET /docs": "Documentación interactiva (Swagger)"
        }
    }
