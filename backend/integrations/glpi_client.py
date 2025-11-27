"""
Cliente para interactuar con la API REST de GLPI.
Maneja autenticación, sesiones y todas las operaciones CRUD.
"""

import requests
from typing import Dict, List, Optional, Any
from loguru import logger
import json


class GLPIClient:
    """Cliente para la API REST de GLPI"""
    
    def __init__(self, url: str, app_token: str, user_token: str):
        """
        Inicializa el cliente GLPI
        
        Args:
            url: URL base de la API de GLPI (ej: http://glpi.com/apirest.php)
            app_token: Token de aplicación de GLPI
            user_token: Token de usuario de GLPI
        """
        self.base_url = url.rstrip('/')
        self.app_token = app_token
        self.user_token = user_token
        self.session_token = None
        
    def _get_headers(self) -> Dict[str, str]:
        """Construye los headers para las peticiones"""
        headers = {
            "Content-Type": "application/json",
            "App-Token": self.app_token
        }
        
        if self.session_token:
            headers["Session-Token"] = self.session_token
        else:
            headers["Authorization"] = f"user_token {self.user_token}"
            
        return headers
    
    def init_session(self) -> bool:
        """
        Inicializa una sesión con GLPI
        
        Returns:
            True si la sesión se inició correctamente
        """
        try:
            url = f"{self.base_url}/initSession"
            headers = {
                "Content-Type": "application/json",
                "App-Token": self.app_token,
                "Authorization": f"user_token {self.user_token}"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.session_token = data.get("session_token")
            
            logger.info("✅ Sesión GLPI iniciada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al iniciar sesión GLPI: {e}")
            return False
    
    def kill_session(self) -> bool:
        """Cierra la sesión con GLPI"""
        try:
            if not self.session_token:
                return True
                
            url = f"{self.base_url}/killSession"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            self.session_token = None
            logger.info("✅ Sesión GLPI cerrada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al cerrar sesión GLPI: {e}")
            return False
    
    def get_tickets(self, filters: Optional[Dict] = None, limit: int = None) -> Dict[str, Any]:
        """
        Obtiene tickets de GLPI con información de paginación
        
        Args:
            filters: Filtros para aplicar (status, assigned_to, etc.)
            limit: Número máximo de tickets a obtener (None = hasta 10,000)
            
        Returns:
            Diccionario con 'tickets', 'total', 'showing' y 'stats'
        """
        try:
            if not self.session_token:
                self.init_session()
            
            url = f"{self.base_url}/Ticket"
            
            # Construir parámetros de búsqueda
            params = {"expand_dropdowns": "true"}
            if filters and filters.get("status") == "open":
                params["criteria[0][field]"] = "12"
                params["criteria[0][searchtype]"] = "equals"
                params["criteria[0][value]"] = "notold"
            
            # Obtener primera página para conocer el total
            params["range"] = "0-99"  # 100 items por página para ser más eficiente
            response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
            response.raise_for_status()
            
            # Extraer total de tickets del header Content-Range
            content_range = response.headers.get('Content-Range', '0-0/0')
            total_tickets = int(content_range.split('/')[-1]) if '/' in content_range else 0
            
            tickets = response.json()
            
            # Límite máximo de seguridad: 10,000 tickets
            if limit is None:
                max_tickets = min(total_tickets, 10000)
            else:
                max_tickets = min(limit, total_tickets, 10000)
            
            logger.info(f"📊 Total en GLPI: {total_tickets}, límite de descarga: {max_tickets}")
            
            # Si necesitamos más tickets, paginar
            if len(tickets) < max_tickets:
                all_tickets = list(tickets)
                page = 1
                
                while len(all_tickets) < max_tickets:
                    start = page * 100  # 100 tickets por página
                    end = min(start + 99, max_tickets - 1)
                    
                    if start >= max_tickets:
                        break
                    
                    params["range"] = f"{start}-{end}"
                    logger.info(f"📥 Solicitando tickets {start}-{end}...")
                    
                    try:
                        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
                        
                        if response.status_code == 200 or response.status_code == 206:
                            page_tickets = response.json()
                            if not page_tickets:
                                logger.warning("⚠️ No hay más tickets disponibles")
                                break
                            all_tickets.extend(page_tickets)
                            logger.info(f"📥 Descargados {len(all_tickets)}/{max_tickets} tickets...")
                            page += 1
                        else:
                            logger.warning(f"⚠️ Error en paginación: status {response.status_code}")
                            break
                    except requests.exceptions.Timeout:
                        logger.warning(f"⚠️ Timeout al solicitar tickets {start}-{end}, continuando con los ya descargados")
                        break
                    except Exception as e:
                        logger.error(f"❌ Error al solicitar tickets {start}-{end}: {e}")
                        break
                
                tickets = all_tickets
            
            # Generar estadísticas
            stats = self._generate_ticket_stats(tickets)
            
            logger.info(f"✅ Obtenidos {len(tickets)} tickets de {total_tickets} totales")
            
            return {
                "tickets": tickets,
                "total": total_tickets,
                "showing": len(tickets),
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error al obtener tickets: {e}")
            return {
                "tickets": [],
                "total": 0,
                "showing": 0,
                "stats": {}
            }
    
    def _generate_ticket_stats(self, tickets: List[Dict]) -> Dict[str, Any]:
        """Genera estadísticas de los tickets"""
        if not tickets:
            return {}
        
        stats = {
            "total": len(tickets),
            "por_estado": {},
            "por_prioridad": {},
            "por_tipo": {},
            "por_urgencia": {},
            "por_impacto": {},
        }
        
        # Mapeos de valores
        estados = {
            1: "Nuevo", 2: "En Proceso (Asignado)", 3: "En Proceso (Planificado)",
            4: "En Espera", 5: "Resuelto", 6: "Cerrado"
        }
        prioridades = {1: "Muy Baja", 2: "Baja", 3: "Media", 4: "Alta", 5: "Muy Alta", 6: "Mayor"}
        tipos = {1: "Incidente", 2: "Solicitud"}
        urgencias = {1: "Muy Baja", 2: "Baja", 3: "Media", 4: "Alta", 5: "Muy Alta"}
        impactos = {1: "Muy Bajo", 2: "Bajo", 3: "Medio", 4: "Alto", 5: "Muy Alto"}
        
        # Contar por categorías
        for ticket in tickets:
            # Por estado
            estado = ticket.get('status', 0)
            estado_nombre = estados.get(estado, f"Estado {estado}")
            stats["por_estado"][estado_nombre] = stats["por_estado"].get(estado_nombre, 0) + 1
            
            # Por prioridad
            prioridad = ticket.get('priority', 0)
            prioridad_nombre = prioridades.get(prioridad, f"Prioridad {prioridad}")
            stats["por_prioridad"][prioridad_nombre] = stats["por_prioridad"].get(prioridad_nombre, 0) + 1
            
            # Por tipo
            tipo = ticket.get('type', 0)
            tipo_nombre = tipos.get(tipo, f"Tipo {tipo}")
            stats["por_tipo"][tipo_nombre] = stats["por_tipo"].get(tipo_nombre, 0) + 1
            
            # Por urgencia
            urgencia = ticket.get('urgency', 0)
            urgencia_nombre = urgencias.get(urgencia, f"Urgencia {urgencia}")
            stats["por_urgencia"][urgencia_nombre] = stats["por_urgencia"].get(urgencia_nombre, 0) + 1
            
            # Por impacto
            impacto = ticket.get('impact', 0)
            impacto_nombre = impactos.get(impacto, f"Impacto {impacto}")
            stats["por_impacto"][impacto_nombre] = stats["por_impacto"].get(impacto_nombre, 0) + 1
        
        return stats
    
    def get_ticket_by_id(self, ticket_id: int) -> Optional[Dict]:
        """
        Obtiene un ticket específico por ID
        
        Args:
            ticket_id: ID del ticket
            
        Returns:
            Datos del ticket o None
        """
        try:
            if not self.session_token:
                self.init_session()
            
            url = f"{self.base_url}/Ticket/{ticket_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Ticket {ticket_id} obtenido")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error al obtener ticket {ticket_id}: {e}")
            return None
    
    def get_computers(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Obtiene computadoras del inventario
        
        Args:
            filters: Filtros para aplicar
            
        Returns:
            Lista de computadoras
        """
        try:
            if not self.session_token:
                self.init_session()
            
            url = f"{self.base_url}/Computer"
            params = {"expand_dropdowns": "true"}
            
            if filters and filters.get("name"):
                params["criteria[0][field]"] = "1"  # Nombre
                params["criteria[0][searchtype]"] = "contains"
                params["criteria[0][value]"] = filters["name"]
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Obtenidas {len(data)} computadoras")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error al obtener computadoras: {e}")
            return []
    
    def search_items(self, item_type: str, criteria: List[Dict]) -> List[Dict]:
        """
        Búsqueda genérica de items en GLPI
        
        Args:
            item_type: Tipo de item (Ticket, Computer, User, etc.)
            criteria: Lista de criterios de búsqueda
            
        Returns:
            Lista de items encontrados
        """
        try:
            if not self.session_token:
                self.init_session()
            
            url = f"{self.base_url}/search/{item_type}"
            
            # Construir parámetros de búsqueda
            params = {}
            for i, criterion in enumerate(criteria):
                params[f"criteria[{i}][field]"] = criterion.get("field")
                params[f"criteria[{i}][searchtype]"] = criterion.get("searchtype", "contains")
                params[f"criteria[{i}][value]"] = criterion.get("value")
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("data", [])
            logger.info(f"✅ Búsqueda completada: {len(items)} items")
            return items
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            return []
    
    def get_my_tickets(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        Obtiene tickets del usuario actual o de un usuario específico
        
        Args:
            user_id: ID del usuario (opcional)
            
        Returns:
            Lista de tickets del usuario
        """
        try:
            if not self.session_token:
                self.init_session()
            
            # Si no se proporciona user_id, obtener el del usuario actual
            if not user_id:
                profile = self.get_full_session()
                user_id = profile.get("session", {}).get("glpiID")
            
            criteria = [
                {
                    "field": "5",  # Campo de usuario asignado
                    "searchtype": "equals",
                    "value": user_id
                }
            ]
            
            return self.search_items("Ticket", criteria)
            
        except Exception as e:
            logger.error(f"❌ Error al obtener mis tickets: {e}")
            return []
    
    def get_full_session(self) -> Dict:
        """
        Obtiene información completa de la sesión actual
        
        Returns:
            Información de la sesión
        """
        try:
            if not self.session_token:
                self.init_session()
            
            url = f"{self.base_url}/getFullSession"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Error al obtener sesión completa: {e}")
            return {}
    
    def __enter__(self):
        """Context manager entry"""
        self.init_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.kill_session()
