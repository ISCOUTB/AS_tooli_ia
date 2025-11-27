"""
Aplicación principal - Agente Inteligente para GLPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from api.routes import router
from auth.auth_routes import router as auth_router
from auth.sso_routes import router as sso_router
from api.conversation_routes import router as conversation_router
from api.settings_routes import router as settings_router
from api.statistics_routes import router as statistics_router
from api.tickets_routes import router as tickets_router
from api.inventory_routes import router as inventory_router
from config import settings


# Configurar logger
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level="DEBUG"
)


# Crear aplicación FastAPI
app = FastAPI(
    title="🤖 Agente Inteligente GLPI (Tooli)",
    description="""
    API REST para consultar información de GLPI mediante lenguaje natural.
    
    ## Características
    
    * **Procesamiento de Lenguaje Natural**: Entiende preguntas en español
    * **Consulta de Tickets**: Busca y filtra tickets automáticamente
    * **Inventario**: Consulta equipos y activos
    * **Reportes Inteligentes**: Genera estadísticas y análisis
    * **IA con Groq**: Respuestas contextuales y precisas con LLaMA 3.3
    
    ## Ejemplos de Uso
    
    Puedes hacer preguntas como:
    - "¿Cuántos tickets tengo abiertos?"
    - "Busca el ticket número 123"
    - "Muéstrame las computadoras del inventario"
    - "Dame un reporte de tickets del mes"
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir rutas
app.include_router(router, prefix="/api/v1")
app.include_router(auth_router)  # Authentication routes (already has /api/v1/auth prefix)
app.include_router(sso_router)  # SSO routes (already has /api/v1/sso prefix)
app.include_router(conversation_router)  # Conversation routes (already has /api/v1/conversations prefix)
app.include_router(settings_router)  # Settings routes (already has /api/v1/settings prefix)
app.include_router(statistics_router)  # Statistics routes (already has /api/v1/statistics prefix)
app.include_router(tickets_router, prefix="/api/v1/tickets", tags=["tickets"])  # Tickets routes
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["inventory"])  # Inventory routes


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("🚀 Iniciando Agente Inteligente GLPI...")
    logger.info(f"📍 GLPI URL: {settings.glpi_url or 'No configurado'}")
    logger.info("🧠 Proveedor de IA: Groq")
    logger.info(f"🤖 Modelo: {settings.groq_model}")
    logger.info("✅ Aplicación iniciada correctamente")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("👋 Cerrando Agente Inteligente GLPI...")


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🌐 Servidor iniciando en http://{settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
