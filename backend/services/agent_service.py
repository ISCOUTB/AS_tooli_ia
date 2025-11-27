"""
Servicio principal que orquesta la comunicación entre
el agente IA y el cliente GLPI.
"""

from typing import Dict, Any, Optional
from loguru import logger

from integrations.glpi_client import GLPIClient
from ai.agent import AIAgent


class AgentService:
    """Servicio que coordina el agente IA y GLPI"""
    
    def __init__(self, glpi_client: GLPIClient, ai_agent: AIAgent):
        """
        Inicializa el servicio
        
        Args:
            glpi_client: Cliente de GLPI
            ai_agent: Agente de IA
        """
        self.glpi = glpi_client
        self.ai = ai_agent
    
    async def process_query(self, user_query: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Procesa una consulta del usuario de principio a fin
        
        Args:
            user_query: Pregunta del usuario
            user_id: ID del usuario (opcional)
            
        Returns:
            Respuesta completa con datos y mensaje generado
        """
        try:
            logger.info(f"📨 Nueva consulta: {user_query}")
            
            # Paso 1: Entender la intención del usuario con IA
            understanding = self.ai.understand_query(user_query)
            intention = understanding.get("intencion")
            params = understanding.get("parametros", {})
            confidence = understanding.get("confianza", 0.0)
            
            # Si la confianza es muy baja, pedir aclaración
            if confidence < 0.6:
                return {
                    "success": False,
                    "message": understanding.get("respuesta_usuario"),
                    "data": None,
                    "intention": "low_confidence"
                }
            
            # Paso 2: Ejecutar la acción en GLPI según la intención
            logger.info(f"🔍 Ejecutando acción GLPI con intención: {intention}")
            logger.debug(f"📋 Parámetros: {params}")
            
            glpi_data = await self._execute_glpi_action(intention, params, user_id)
            
            logger.info(f"📊 Datos de GLPI recibidos: {type(glpi_data)} - {bool(glpi_data)}")
            
            # Paso 3: Generar respuesta en lenguaje natural
            if glpi_data is not None:
                # Si hay datos (incluso si está vacío pero no es None)
                response_message = self.ai.generate_response(
                    user_query,
                    glpi_data,
                    intention
                )
            else:
                # Si glpi_data es None, hubo un error
                logger.warning(f"⚠️ No se obtuvieron datos de GLPI para intención: {intention}")
                response_message = "No se encontraron resultados para tu consulta."
            
            return {
                "success": True,
                "message": response_message,
                "data": glpi_data,
                "intention": intention,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            return {
                "success": False,
                "message": "Lo siento, ocurrió un error al procesar tu consulta.",
                "data": None,
                "intention": "error"
            }
    
    async def _execute_glpi_action(
        self,
        intention: str,
        params: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Any:
        """
        Ejecuta la acción correspondiente en GLPI
        
        Args:
            intention: Intención identificada
            params: Parámetros extraídos
            user_id: ID del usuario
            
        Returns:
            Datos obtenidos de GLPI
        """
        try:
            logger.info(f"🎯 Ejecutando acción para intención: {intention}")
            
            # Consultar tickets
            if intention == "consultar_tickets":
                status = params.get("status", "open")
                logger.info(f"📋 Consultando tickets con status: {status}")
                
                if params.get("usuario") == "actual" and user_id:
                    result = self.glpi.get_my_tickets(user_id)
                    logger.info(f"✅ Tickets del usuario obtenidos: {len(result) if result else 0}")
                    return result
                else:
                    # Obtener TODOS los tickets disponibles (hasta 10k) con estadísticas
                    result = self.glpi.get_tickets({"status": status}, limit=None)
                    # Calcular cantidad de tickets
                    count = 0
                    if isinstance(result, dict):
                        count = result.get('total', 0)
                    elif result:
                        count = len(result)
                    logger.info(f"✅ Tickets obtenidos: {count}")
                    return result  # Devuelve dict con tickets, total, showing, stats
            
            # Buscar ticket específico
            elif intention == "buscar_ticket":
                ticket_id = params.get("ticket_id")
                if ticket_id:
                    return self.glpi.get_ticket_by_id(ticket_id)
            
            # Consultar inventario
            elif intention == "consultar_inventario":
                return self.glpi.get_computers()
            
            # Buscar equipo específico
            elif intention == "buscar_equipo":
                nombre = params.get("nombre")
                if nombre:
                    return self.glpi.get_computers({"name": nombre})
            
            # Generar reporte
            elif intention == "generar_reporte":
                return await self._generate_report(params)
            
            # Consulta general (no requiere GLPI)
            elif intention == "consulta_general":
                return {"message": "Esta es una consulta general que no requiere datos de GLPI"}
            
            else:
                logger.warning(f"⚠️ Intención no reconocida: {intention}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando acción GLPI: {e}")
            return None
    
    async def _generate_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera reportes basados en datos de GLPI
        
        Args:
            params: Parámetros del reporte
            
        Returns:
            Datos del reporte
        """
        try:
            tipo_reporte = params.get("tipo", "tickets")
            
            if tipo_reporte == "tickets":
                tickets = self.glpi.get_tickets()
                
                # Calcular estadísticas
                total = len(tickets)
                abiertos = sum(1 for t in tickets if t.get("status") in [1, 2, 3, 4])
                cerrados = total - abiertos
                
                return {
                    "tipo": "tickets",
                    "total": total,
                    "abiertos": abiertos,
                    "cerrados": cerrados,
                    "detalles": tickets[:10]  # Primeros 10
                }
            
            elif tipo_reporte == "inventario":
                computers = self.glpi.get_computers()
                
                return {
                    "tipo": "inventario",
                    "total_equipos": len(computers),
                    "detalles": computers[:10]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
            return None
    
    def chat_simple(self, message: str) -> str:
        """
        Chat simple sin consultar GLPI
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Respuesta del agente
        """
        return self.ai.chat(message)
