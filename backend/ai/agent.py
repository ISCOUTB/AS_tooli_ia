"""
Agente de IA que procesa lenguaje natural y genera respuestas
utilizando Groq AI para entender las consultas del usuario.
"""

from groq import Groq
from typing import Dict, List, Optional, Any
from loguru import logger
import json


class AIAgent:
    """Agente de IA para procesar consultas en lenguaje natural con Groq"""
    
    def __init__(
        self,
        groq_api_key: str,
        groq_model: str = "llama-3.3-70b-versatile"
    ):
        """
        Inicializa el agente de IA con Groq
        
        Args:
            groq_api_key: Clave API de Groq
            groq_model: Modelo de Groq a usar
        """
        if not groq_api_key:
            raise ValueError("groq_api_key es requerido")
        
        self.client = Groq(api_key=groq_api_key)
        self.model = groq_model
        logger.info(f"AIAgent inicializado con Groq (modelo: {groq_model})")
        
        # Professional system prompt for the agent (bilingual: Spanish/English)
        self.system_prompt = """Eres un asistente de IA profesional para el sistema GLPI IT Service Management.
Tu rol es ayudar a los usuarios a acceder y analizar información sobre:
- Tickets de soporte (abiertos, cerrados, pendientes, estadísticas)
- Inventario de TI (computadoras, hardware, activos)
- Reportes y análisis

Cuando un usuario hace una solicitud, debes:
1. Identificar la INTENCIÓN (qué quiere lograr)
2. Extraer PARÁMETROS (filtros, IDs, rangos de fechas)
3. Responder en formato JSON estructurado

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

Ejemplos:

Usuario: "¿Cuántos tickets hay abiertos actualmente?"
Respuesta:
{
    "intencion": "consultar_tickets",
    "parametros": {
        "status": "open",
        "usuario": "todos"
    },
    "respuesta_usuario": "Consultando tickets abiertos.",
    "confianza": 0.98
}

Usuario: "Busca la computadora asignada a Juan"
Respuesta:
{
    "intencion": "buscar_equipo",
    "parametros": {
        "nombre": "juan",
        "tipo": "Computer"
    },
    "respuesta_usuario": "Buscando la computadora de Juan.",
    "confianza": 0.92
}

Usuario: "Muéstrame el ticket 123"
Respuesta:
{
    "intencion": "buscar_ticket",
    "parametros": {
        "ticket_id": 123
    },
    "respuesta_usuario": "Recuperando ticket #123.",
    "confianza": 0.99
}

Usuario: "Show me open tickets" (English)
Respuesta:
{
    "intencion": "consultar_tickets",
    "parametros": {
        "status": "open"
    },
    "respuesta_usuario": "Retrieving open tickets.",
    "confianza": 0.97
}

Sé preciso y extrae todos los parámetros relevantes. Acepta consultas en español e inglés."""
    
    def understand_query(self, user_query: str) -> Dict[str, Any]:
        """
        Procesa una consulta del usuario y extrae la intención y parámetros
        
        Args:
            user_query: Pregunta del usuario en lenguaje natural
            
        Returns:
            Diccionario con intención, parámetros y respuesta
        """
        try:
            logger.info(f"🤔 Procesando consulta: {user_query}")
            
            # Enviar consulta a Groq
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
            
            # Extraer respuesta
            content = response.choices[0].message.content
            result = json.loads(content)
            
            logger.info(f"✅ Intención identificada: {result.get('intencion')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error al procesar consulta: {e}")
            return {
                "intencion": "error",
                "parametros": {},
                "respuesta_usuario": "Lo siento, no pude entender tu consulta. ¿Podrías reformularla?",
                "confianza": 0.0
            }
    
    def generate_response(
        self,
        user_query: str,
        data: Any,
        intention: str
    ) -> str:
        """
        Genera una respuesta en lenguaje natural basada en los datos obtenidos
        
        Args:
            user_query: Consulta original del usuario
            data: Datos obtenidos de GLPI
            intention: Intención identificada
            
        Returns:
            Respuesta en lenguaje natural
        """
        try:
            # Preparar resumen de datos (evitar exceder límite de tokens)
            data_summary = data
            total_count = None
            
            # CASO ESPECIAL: Si hay estadísticas, usar SOLO las estadísticas
            if isinstance(data, dict) and "stats" in data and data.get("stats"):
                total_count = data.get("total", 0)
                showing_count = data.get("showing", 0)
                stats = data["stats"]
                
                logger.info(f"📊 Generando respuesta con estadísticas: {showing_count}/{total_count} tickets")
                
                # Crear un resumen para enviar a la IA con SOLO estadísticas
                context_prompt = f"""User Query: "{user_query}"

GLPI SYSTEM ANALYSIS - {total_count} TOTAL TICKETS

Dataset: {showing_count} tickets analyzed from {total_count} total records

STATISTICAL BREAKDOWN:

Status Distribution:
{self._format_stats_section(stats.get("por_estado", {}))}

Priority Distribution:
{self._format_stats_section(stats.get("por_prioridad", {}))}

Type Distribution:
{self._format_stats_section(stats.get("por_tipo", {}))}

Urgency Distribution:
{self._format_stats_section(stats.get("por_urgencia", {}))}

Impact Distribution:
{self._format_stats_section(stats.get("por_impacto", {}))}

RESPONSE GUIDELINES:
1. Provide a professional, clear response in Spanish
2. Use the statistics above to deliver comprehensive insights
3. Minimal emoji usage (max 2-3 total, only for critical highlights)
4. Reference the {total_count} total tickets in the system
5. Provide data-driven insights (e.g., "Most tickets are in X status")
6. Structure with clear sections and bullet points
7. Base response ONLY on provided statistics - no assumptions
8. Keep tone professional and business-appropriate
9. Suggest actionable recommendations based on patterns observed"""
                
            # Si hay datos con tickets pero no estadísticas
            elif isinstance(data, dict) and "tickets" in data:
                total_count = data.get("total", 0)
                showing = data.get("showing", 0)
                tickets = data["tickets"]
                
                # Resumir si hay muchos tickets
                if len(tickets) > 5:
                    data_summary = {
                        "total_tickets": total_count,
                        "mostrando": showing,
                        "primeros_5_tickets": tickets[:5],
                        "nota": f"Mostrando primeros 5 tickets de {showing} obtenidos (total en sistema: {total_count})"
                    }
                else:
                    data_summary = {
                        "total_tickets": total_count,
                        "mostrando": showing,
                        "tickets": tickets
                    }
                
                context_prompt = f"""User Query: "{user_query}"

Intent: {intention}

GLPI Data Retrieved:
{json.dumps(data_summary, indent=2, ensure_ascii=False)}

Response Requirements:
1. Answer the user's question directly and professionally
2. IMPORTANT: If total_tickets differs from displayed count, mention there are MORE tickets in the system
3. Present data in organized sections with clear structure
4. Minimal emoji use (max 2-3 for key highlights only)
5. Summarize the most important information if dataset is large
6. Suggest next steps or relevant actions when appropriate
7. Maintain professional business tone throughout
8. Provide actionable insights based on the data

Respond in Spanish with professional formatting."""
                
            # Format for list of items
            elif isinstance(data, list) and len(data) > 10:
                # If more than 10 items, send only summary
                data_summary = {
                    "total": len(data),
                    "first_5": data[:5],
                    "note": f"Showing first 5 of {len(data)} total results"
                }
                
                context_prompt = f"""User Query: "{user_query}"

Intent: {intention}

GLPI Data Retrieved:
{json.dumps(data_summary, indent=2, ensure_ascii=False)}

Provide a clear, professional response in Spanish."""
            else:
                context_prompt = f"""User Query: "{user_query}"

Intent: {intention}

GLPI Data Retrieved:
{json.dumps(data_summary, indent=2, ensure_ascii=False)}

Provide a clear, professional response in Spanish."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional GLPI assistant providing clear, accurate, and business-appropriate information. Keep responses concise and well-structured."},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error al generar respuesta: {e}")
            return "Lo siento, hubo un error al procesar la información."
    
    def chat(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Conversación general con el agente (sin consultar GLPI)
        
        Args:
            user_query: Mensaje del usuario
            conversation_history: Historial de conversación
            
        Returns:
            Respuesta del agente
        """
        try:
            messages = [
                {"role": "system", "content": "Eres un asistente útil especializado en GLPI. Ayudas a usuarios a entender y usar el sistema."}
            ]
            
            # Agregar historial si existe
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": user_query})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error en chat: {e}")
            return "Lo siento, hubo un error al procesar tu mensaje."
    
    def _format_stats_section(self, stats_dict: Dict[str, int]) -> str:
        """Format statistics section in a professional, readable way."""
        if not stats_dict:
            return "  - No data available"
        
        lines = []
        total = sum(stats_dict.values())
        
        # Sort by count (descending)
        sorted_items = sorted(stats_dict.items(), key=lambda x: x[1], reverse=True)
        
        for key, value in sorted_items:
            percentage = (value / total * 100) if total > 0 else 0
            lines.append(f"  • {key}: {value} ({percentage:.1f}%)")
        
        return "\n".join(lines)
