"""
Modelos de datos (schemas) para la API
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class QueryRequest(BaseModel):
    """Modelo para solicitudes de consulta"""
    query: str = Field(..., description="Consulta del usuario en lenguaje natural")
    user_id: Optional[int] = Field(None, description="ID del usuario en GLPI")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Cuántos tickets tengo abiertos?",
                "user_id": 2
            }
        }


class QueryResponse(BaseModel):
    """Modelo para respuestas de consulta"""
    success: bool = Field(..., description="Indica si la consulta fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta en lenguaje natural")
    data: Optional[Any] = Field(None, description="Datos obtenidos de GLPI")
    intention: str = Field(..., description="Intención identificada")
    confidence: Optional[float] = Field(None, description="Nivel de confianza (0-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Tienes 5 tickets abiertos actualmente...",
                "data": [],
                "intention": "consultar_tickets",
                "confidence": 0.95
            }
        }


class ChatRequest(BaseModel):
    """Modelo para chat simple"""
    message: str = Field(..., description="Mensaje del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "¿Qué es GLPI?"
            }
        }


class ChatResponse(BaseModel):
    """Modelo para respuesta de chat"""
    response: str = Field(..., description="Respuesta del agente")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "GLPI es un sistema de gestión de servicios de TI..."
            }
        }


class HealthResponse(BaseModel):
    """Modelo para respuesta de health check"""
    status: str = Field(..., description="Estado del servicio")
    glpi_connected: bool = Field(..., description="Estado de conexión con GLPI")
    groq_ai_available: bool = Field(..., description="Estado de Groq AI")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "glpi_connected": True,
                "groq_ai_available": True
            }
        }
