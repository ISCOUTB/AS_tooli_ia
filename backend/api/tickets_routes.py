from fastapi import APIRouter, Depends, Query, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime
from auth.database import get_db
from auth.models import User
from auth.jwt_auth import get_current_user as get_current_user_jwt
from integrations.glpi_client import GLPIClient
from config import settings
from loguru import logger

router = APIRouter()

def get_user_from_token(authorization: str, db: Session) -> User:
    """Get current authenticated user from Bearer token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    user = get_current_user_jwt(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user

def get_glpi_client() -> GLPIClient:
    """Create GLPI client instance"""
    return GLPIClient(
        url=settings.glpi_url,
        app_token=settings.glpi_app_token,
        user_token=settings.glpi_user_token
    )

def map_glpi_ticket_to_frontend(ticket: Dict) -> Dict:
    """Convert GLPI ticket format to frontend format"""
    # Map GLPI status to frontend status
    status_map = {
        1: "new",           # Nuevo
        2: "assigned",      # En Proceso (Asignado)
        3: "in_progress",   # En Proceso (Planificado)
        4: "pending",       # En Espera
        5: "solved",        # Resuelto
        6: "closed"         # Cerrado
    }
    
    # Map GLPI priority to frontend priority
    priority_map = {
        1: "very_low",
        2: "low",
        3: "medium",
        4: "high",
        5: "very_high",
        6: "very_high"  # Mayor -> Muy Alta
    }
    
    return {
        "id": ticket.get("id"),
        "title": ticket.get("name", "Sin título"),
        "description": ticket.get("content", "Sin descripción"),
        "status": status_map.get(ticket.get("status", 1), "new"),
        "priority": priority_map.get(ticket.get("priority", 3), "medium"),
        "category": ticket.get("itilcategories_id_friendlyname", "Sin categoría"),
        "requester_name": ticket.get("users_id_recipient_friendlyname", "Desconocido"),
        "assigned_to": ticket.get("users_id_assign_friendlyname"),
        "created_at": ticket.get("date_creation", ticket.get("date")),
        "updated_at": ticket.get("date_mod"),
        "due_date": ticket.get("time_to_resolve")
    }

# Get real GLPI data
@router.get("/")
def get_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get all tickets from GLPI with optional filters"""
    # Authenticate user
    get_user_from_token(authorization, db)
    
    try:
        # Get GLPI client and fetch tickets
        glpi = get_glpi_client()
        logger.info("🔄 Llamando a glpi.get_tickets()...")
        glpi_response = glpi.get_tickets(limit=1000)  # Limit to 1000 for performance
        logger.info(f"📦 Respuesta de GLPI: type={type(glpi_response)}, keys={list(glpi_response.keys()) if isinstance(glpi_response, dict) else 'not a dict'}")
        glpi_tickets = glpi_response.get("tickets", [])
        
        logger.info(f"📋 Obtenidos {len(glpi_tickets)} tickets de GLPI")
        
        # Convert to frontend format
        tickets = [map_glpi_ticket_to_frontend(t) for t in glpi_tickets]
        
        # Apply filters
        if status:
            tickets = [t for t in tickets if t["status"] == status]
        if priority:
            tickets = [t for t in tickets if t["priority"] == priority]
        if category and category.lower() != "sin categoría":
            tickets = [t for t in tickets if category.lower() in t["category"].lower()]
        if search:
            search_lower = search.lower()
            tickets = [
                t for t in tickets 
                if search_lower in t["title"].lower() or 
                   search_lower in t["description"].lower() or
                   search_lower in t["category"].lower()
            ]
        
        logger.info(f"✅ Devolviendo {len(tickets)} tickets después de filtros")
        return tickets
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tickets de GLPI: {str(e)}"
        )


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get a specific ticket by ID from GLPI"""
    # Authenticate user
    get_user_from_token(authorization, db)
    
    try:
        glpi = get_glpi_client()
        ticket = glpi.get_ticket_by_id(ticket_id)
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )
        
        return map_glpi_ticket_to_frontend(ticket)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ticket: {str(e)}"
        )


@router.get("/stats/summary")
def get_ticket_stats(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get ticket statistics from GLPI"""
    # Authenticate user
    get_user_from_token(authorization, db)
    
    try:
        glpi = get_glpi_client()
        glpi_response = glpi.get_tickets(limit=1000)
        glpi_tickets = glpi_response.get("tickets", [])
        
        # Convert and count
        tickets = [map_glpi_ticket_to_frontend(t) for t in glpi_tickets]
        
        total = len(tickets)
        new_count = len([t for t in tickets if t["status"] == "new"])
        in_progress = len([t for t in tickets if t["status"] in ["assigned", "in_progress"]])
        solved = len([t for t in tickets if t["status"] == "solved"])
        closed = len([t for t in tickets if t["status"] == "closed"])
        pending = len([t for t in tickets if t["status"] == "pending"])
        
        high_priority = len([t for t in tickets if t["priority"] in ["high", "very_high"]])
        
        return {
            "total": total,
            "new": new_count,
            "in_progress": in_progress,
            "pending": pending,
            "solved": solved,
            "closed": closed,
            "high_priority": high_priority
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
