from fastapi import APIRouter, Depends, Query, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
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

def map_glpi_computer_to_frontend(computer: Dict) -> Dict:
    """Convert GLPI computer format to frontend inventory format"""
    # Map status - expand_dropdowns devuelve nombres de texto
    status_map = {
        "En uso": "in_use",
        "Disponible": "available",
        "Mantenimiento": "maintenance",
        "Averiado": "broken",
        "Retirado": "retired",
        "Activo": "in_use",  # Estado común en GLPI
        "Inactivo": "retired"
    }
    
    # Get computer type from name or default to computer
    comp_name = computer.get("name", "").lower()
    if "laptop" in comp_name or "portátil" in comp_name:
        item_type = "laptop"
    elif "servidor" in comp_name or "server" in comp_name:
        item_type = "server"
    else:
        item_type = "computer"
    
    # Build specifications dict with all available info
    specs = {}
    
    # Modelo (viene expandido como texto)
    model = computer.get("computermodels_id")
    if model and str(model) not in ["0", ""]:
        specs["Modelo"] = model
    
    # Tipo de computadora
    comp_type = computer.get("computertypes_id")
    if comp_type and str(comp_type) not in ["0", ""]:
        specs["Tipo"] = comp_type
    
    # Red/Network
    network = computer.get("networks_id")
    if network and str(network) not in ["0", ""]:
        specs["Red"] = network
    
    # Entidad
    entity = computer.get("entities_id")
    if entity and str(entity) not in ["0", ""]:
        specs["Entidad"] = entity
    
    # Serial alternativo
    other_serial = computer.get("otherserial")
    if other_serial:
        specs["Serial Alternativo"] = other_serial
    
    # UUID
    uuid = computer.get("uuid")
    if uuid:
        specs["UUID"] = uuid
    
    # Contacto
    contact = computer.get("contact")
    if contact:
        specs["Contacto"] = contact
    
    # Número de contacto
    contact_num = computer.get("contact_num")
    if contact_num and contact_num != contact:
        specs["Teléfono"] = contact_num
    
    # Comentarios
    comment = computer.get("comment")
    if comment:
        specs["Comentarios"] = comment
    
    # Última actualización
    last_inv = computer.get("last_inventory_update")
    if last_inv:
        specs["Última Actualización"] = last_inv
    
    # Último boot
    last_boot = computer.get("last_boot")
    if last_boot:
        specs["Último Reinicio"] = last_boot
    
    # Extraer datos expandidos (vienen como texto ahora)
    location = computer.get("locations_id")
    if not location or str(location) in ["0", ""]:
        location = None
    
    assigned_user = computer.get("users_id")
    if not assigned_user or str(assigned_user) in ["0", ""]:
        assigned_user = None
    
    manufacturer = computer.get("manufacturers_id")
    if not manufacturer or str(manufacturer) in ["0", ""]:
        manufacturer = None
    
    state = computer.get("states_id", "Activo")
    status = status_map.get(str(state), "in_use")
    
    # Fechas importantes
    date_creation = computer.get("date_creation")
    date_mod = computer.get("date_mod")
    
    return {
        "id": computer.get("id"),
        "name": computer.get("name", "Sin nombre"),
        "type": item_type,
        "manufacturer": manufacturer,
        "model": model if model and str(model) not in ["0", ""] else None,
        "serial_number": computer.get("serial"),
        "status": status,
        "location": location,
        "assigned_to": assigned_user,
        "purchase_date": date_creation,  # Fecha de creación como compra
        "warranty_expiration": None,  # GLPI no tiene campo directo
        "specifications": specs if specs else None,
        "created_at": date_creation,  # Fecha de creación en GLPI
        "updated_at": date_mod  # Última modificación
    }

# Real GLPI data endpoints


@router.get("/")
def get_inventory(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get all inventory items from GLPI"""
    # Authenticate user
    get_user_from_token(authorization, db)
    
    try:
        glpi = get_glpi_client()
        glpi_computers = glpi.get_computers()
        
        logger.info(f"💻 Obtenidos {len(glpi_computers)} equipos de GLPI")
        
        # Convert to frontend format
        items = [map_glpi_computer_to_frontend(c) for c in glpi_computers]
        
        # Apply filters
        if type:
            items = [i for i in items if i["type"] == type]
        if status:
            items = [i for i in items if i["status"] == status]
        if location:
            items = [i for i in items if i["location"] and location.lower() in i["location"].lower()]
        if search:
            search_lower = search.lower()
            items = [
                i for i in items 
                if search_lower in i["name"].lower() or 
                   (i["manufacturer"] and search_lower in i["manufacturer"].lower()) or
                   (i["model"] and search_lower in i["model"].lower())
            ]
        
        logger.info(f"✅ Devolviendo {len(items)} elementos después de filtros")
        return items
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo inventario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inventario de GLPI: {str(e)}"
        )


@router.get("/{item_id}")
def get_inventory_item(
    item_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get a specific inventory item by ID from GLPI"""
    # Authenticate user
    get_user_from_token(authorization, db)
    
    try:
        glpi = get_glpi_client()
        
        # Try to get the computer from GLPI
        # We need to fetch all and filter because GLPI doesn't have a direct get_computer_by_id
        computers = glpi.get_computers()
        computer = next((c for c in computers if c.get("id") == item_id), None)
        
        if not computer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Elemento no encontrado"
            )
        
        return map_glpi_computer_to_frontend(computer)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo elemento {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener elemento: {str(e)}"
        )


@router.get("/stats/summary")
def get_inventory_stats(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get inventory statistics from GLPI"""
    # Authenticate user
    get_user_from_token(authorization, db)
    
    try:
        glpi = get_glpi_client()
        glpi_computers = glpi.get_computers()
        
        # Convert and count
        items = [map_glpi_computer_to_frontend(c) for c in glpi_computers]
        
        total = len(items)
        available = len([i for i in items if i["status"] == "available"])
        in_use = len([i for i in items if i["status"] == "in_use"])
        maintenance = len([i for i in items if i["status"] == "maintenance"])
        broken = len([i for i in items if i["status"] == "broken"])
        retired = len([i for i in items if i["status"] == "retired"])
        
        # Count by type
        computers = len([i for i in items if i["type"] == "computer"])
        laptops = len([i for i in items if i["type"] == "laptop"])
        servers = len([i for i in items if i["type"] == "server"])
        
        return {
            "total": total,
            "available": available,
            "in_use": in_use,
            "maintenance": maintenance,
            "broken": broken,
            "retired": retired,
            "by_type": {
                "computers": computers,
                "laptops": laptops,
                "servers": servers
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas de inventario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
