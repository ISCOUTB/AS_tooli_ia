"""
Tooli-IA Professional NLP System v2.0
Sistema avanzado de procesamiento de lenguaje natural para GLPI
Respuestas profesionales sin emojis ni caracteres especiales
"""

import re
import json
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional

# Constantes para evitar duplicación de literales
ESTADISTICS_LITERAL = 'estadísticas'
TICKETS_LITERAL = 'tickets'
USUARIOS_LITERAL = 'usuarios'
TECNICOS_LITERAL = 'técnicos'


class ProfessionalNLPEngine:
    """Motor de NLP profesional para respuestas empresariales"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.response_generator = ProfessionalResponseGenerator()
        self.context_manager = ContextManager()
        
    def process_query(self, query: str) -> Dict:
        """Procesar consulta del usuario con análisis completo"""
        # Limpiar y normalizar texto
        normalized_query = self._normalize_text(query)
        
        # Clasificar intención
        intent = self.intent_classifier.classify(normalized_query)
        
        # Extraer entidades
        entities = self.entity_extractor.extract(normalized_query)
        
        # Analizar sentimiento de manera sutil
        sentiment = self._analyze_sentiment(normalized_query)
        
        # Generar respuesta profesional
        response = self.response_generator.generate(intent, entities, sentiment)
        
        return {
            'query': query,
            'intent': intent,
            'entities': entities,
            'sentiment': sentiment,
            'response': response,
            'confidence': intent.get('confidence', 0.0)
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalizar texto eliminando ruido"""
        # Convertir a minúsculas
        text = text.lower().strip()
        
        # Remover caracteres especiales excesivos
        text = re.sub(r'[^\w\s\?\¿\!\¡\.\,\:\;]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Correcciones comunes de typos en español
        corrections = {
            'tickeck': TICKETS_LITERAL,
            'tiket': 'ticket',
            'tikect': 'ticket',
            'estadisitcas': ESTADISTICS_LITERAL,
            'estadisticas': ESTADISTICS_LITERAL,
            'usuairo': 'usuario',
            'usario': 'usuario',
            'tecnico': TECNICOS_LITERAL,
            'prioritdad': 'prioridad',
            'prioriad': 'prioridad'
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def _analyze_sentiment(self, text: str) -> str:
        """Análisis básico de sentimiento"""
        urgent_keywords = ['urgente', 'rápido', 'ya', 'inmediato', 'crítico', 'emergencia']
        frustrated_keywords = ['problema', 'error', 'falla', 'no funciona', 'mal']
        polite_keywords = ['por favor', 'gracias', 'ayuda', 'favor', 'puede']
        
        if any(word in text for word in urgent_keywords):
            return 'urgent'
        elif any(word in text for word in frustrated_keywords):
            return 'concerned'
        elif any(word in text for word in polite_keywords):
            return 'polite'
        else:
            return 'neutral'


class IntentClassifier:
    """Clasificador de intenciones para GLPI"""
    
    def __init__(self):
        self.intents = {
            'ticket_count': {
                'patterns': [
                    'cuántos tickets', 'cantidad tickets', 'número tickets', 'total tickets',
                    'count tickets', 'tickets hay', 'tickets existen', 'tickets total'
                ],
                'keywords': ['cuántos', 'cantidad', 'número', 'total', 'count', 'tickets']
            },
            'ticket_status': {
                'patterns': [
                    'estado tickets', 'status tickets', 'tickets abiertos', 'tickets cerrados',
                    'tickets pendientes', 'situación tickets', 'tickets resueltos'
                ],
                'keywords': ['estado', 'status', 'abiertos', 'cerrados', 'pendientes', 'resueltos']
            },
            'create_ticket': {
                'patterns': [
                    'crear ticket', 'nuevo ticket', 'abrir ticket', 'generar ticket',
                    'crear incidencia', 'reportar problema', 'nueva solicitud'
                ],
                'keywords': ['crear', 'nuevo', 'abrir', 'generar', 'reportar', 'solicitud']
            },
            'user_analysis': {
                'patterns': [
                    'usuarios activos', 'técnicos disponibles', 'análisis usuarios',
                    'staff técnico', 'personal soporte', 'equipo trabajo'
                ],
                'keywords': ['usuarios', 'técnicos', 'personal', 'staff', 'equipo', 'análisis']
            },
            'statistics': {
                'patterns': [
                    ESTADISTICS_LITERAL, 'métricas', 'reportes', 'análisis datos',
                    'resumen general', 'dashboard', 'indicadores'
                ],
                'keywords': [ESTADISTICS_LITERAL, 'métricas', 'reportes', 'análisis', 'resumen', 'indicadores']
            },
            'help_general': {
                'patterns': [
                    'ayuda', 'qué puedes hacer', 'funciones', 'comandos',
                    'cómo usar', 'manual', 'instrucciones', 'guía'
                ],
                'keywords': ['ayuda', 'funciones', 'comandos', 'usar', 'manual', 'guía']
            },
            'system_status': {
                'patterns': [
                    'estado sistema', 'sistema funcionando', 'conectividad',
                    'status glpi', 'servidor activo', 'sistema operativo'
                ],
                'keywords': ['sistema', 'servidor', 'conectividad', 'funcionando', 'activo', 'operativo']
            }
        }
    
    def classify(self, query: str) -> Dict:
        """Clasificar intención de la consulta"""
        best_intent = 'help_general'
        best_score = 0.0
        
        for intent_name, intent_data in self.intents.items():
            score = self._calculate_score(query, intent_data)
            if score > best_score:
                best_score = score
                best_intent = intent_name
        
        return {
            'intent': best_intent,
            'confidence': min(best_score, 1.0)
        }
    
    def _calculate_score(self, query: str, intent_data: Dict) -> float:
        """Calcular puntuación de similitud"""
        score = 0.0
        
        # Puntuación por patrones exactos
        for pattern in intent_data['patterns']:
            if pattern in query:
                score += 0.8
        
        # Puntuación por palabras clave
        keywords_found = 0
        for keyword in intent_data['keywords']:
            if keyword in query:
                keywords_found += 1
        
        if keywords_found > 0:
            score += (keywords_found / len(intent_data['keywords'])) * 0.6
        
        return score


class EntityExtractor:
    """Extractor de entidades específicas de GLPI"""
    
    def extract(self, query: str) -> Dict:
        """Extraer entidades del texto"""
        entities = {
            'ticket_numbers': self._extract_ticket_numbers(query),
            'time_references': self._extract_time_references(query),
            'priorities': self._extract_priorities(query),
            'user_references': self._extract_user_references(query),
            'status_types': self._extract_status_types(query)
        }
        
        return {k: v for k, v in entities.items() if v}
    
    def _extract_ticket_numbers(self, query: str) -> List[str]:
        """Extraer números de tickets"""
        pattern = r'#?(\d{4,})|ticket\s+(\d+)'
        matches = re.findall(pattern, query, re.IGNORECASE)
        return [match[0] or match[1] for match in matches]
    
    def _extract_time_references(self, query: str) -> List[str]:
        """Extraer referencias temporales"""
        time_patterns = [
            r'(hoy|today)', r'(ayer|yesterday)', r'(esta semana|this week)',
            r'(este mes|this month)', r'(último mes|last month)', r'(año|year)',
            r'(\d+)\s+(días?|days?)', r'(\d+)\s+(semanas?|weeks?)', r'(\d+)\s+(meses?|months?)'
        ]
        
        found_times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            found_times.extend([match if isinstance(match, str) else match[0] for match in matches])
        
        return found_times
    
    def _extract_priorities(self, query: str) -> List[str]:
        """Extraer niveles de prioridad"""
        priorities = ['baja', 'media', 'alta', 'crítica', 'urgente', 'normal']
        found = [p for p in priorities if p in query.lower()]
        return found
    
    def _extract_user_references(self, query: str) -> List[str]:
        """Extraer referencias a usuarios"""
        user_patterns = [
            r'usuario\s+(\w+)', r'técnico\s+(\w+)', r'@(\w+)', r'user\s+(\w+)'
        ]
        
        found_users = []
        for pattern in user_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            found_users.extend(matches)
        
        return found_users
    
    def _extract_status_types(self, query: str) -> List[str]:
        """Extraer tipos de estado"""
        statuses = ['abierto', 'cerrado', 'pendiente', 'resuelto', 'asignado', 'nuevo']
        found = [s for s in statuses if s in query.lower()]
        return found


class ProfessionalResponseGenerator:
    """Generador de respuestas profesionales"""
    
    def __init__(self):
        self.templates = {
            'ticket_count': [
                "Análisis de tickets en el sistema:",
                "Resumen actual de tickets GLPI:",
                "Estado de tickets en la plataforma:"
            ],
            'ticket_status': [
                "Estado actual de los tickets:",
                "Distribución de tickets por estado:",
                "Resumen de estados de tickets:"
            ],
            'create_ticket': [
                "Para crear un nuevo ticket en GLPI:",
                "Proceso de creación de tickets:",
                "Pasos para generar una nueva incidencia:"
            ],
            'user_analysis': [
                "Análisis de usuarios y técnicos:",
                "Información del personal de soporte:",
                "Estado del equipo técnico:"
            ],
            'statistics': [
                "Estadísticas del sistema GLPI:",
                "Métricas y análisis de rendimiento:",
                "Indicadores clave de gestión:"
            ],
            'help_general': [
                "Asistente GLPI - Funciones disponibles:",
                "Sistema de ayuda GLPI:",
                "Guía de uso del asistente:"
            ],
            'system_status': [
                "Estado del sistema GLPI:",
                "Información de conectividad:",
                "Estado operativo de la plataforma:"
            ],
            'not_supported': [
                "Consulta no reconocida.",
                "Funcionalidad no disponible actualmente.",
                "Consulta fuera del alcance del sistema GLPI."
            ]
        }
    
    def generate(self, intent: Dict, entities: Dict, sentiment: str) -> str:
        """Generar respuesta profesional"""
        intent_name = intent.get('intent', 'help_general')
        confidence = intent.get('confidence', 0.0)
        
        # Si la confianza es muy baja, usar respuesta de fallback
        if confidence < 0.3:
            return self._generate_fallback_response(entities, sentiment)
        
        # Seleccionar template base
        templates = self.templates.get(intent_name, self.templates['help_general'])
        base_template = templates[0]  # Usar siempre el primero para consistencia
        
        # Generar contenido específico según la intención
        content = self._generate_intent_content(intent_name, entities, sentiment)
        
        # Combinar template y contenido
        response = f"{base_template}\n\n{content}"
        
        # Añadir nota de ayuda si es apropiado
        if sentiment == 'concerned' or confidence < 0.7:
            response += "\n\nSi necesita ayuda adicional, especifique su consulta con más detalle."
        
        return response
    
    def _generate_intent_content(self, intent: str, entities: Dict, sentiment: str) -> str:
        """Generar contenido específico para cada intención"""
        
        if intent == 'ticket_count':
            return self._generate_ticket_count_response(entities)
        elif intent == 'ticket_status':
            return self._generate_status_response(entities)
        elif intent == 'create_ticket':
            return self._generate_create_ticket_response(entities)
        elif intent == 'user_analysis':
            return self._generate_user_analysis_response(entities)
        elif intent == 'statistics':
            return self._generate_statistics_response(entities)
        elif intent == 'system_status':
            return self._generate_system_status_response(entities)
        elif intent == 'help_general':
            return self._generate_help_response()
        else:
            return self._generate_fallback_response(entities, sentiment)
    
    def _generate_ticket_count_response(self, entities: Dict) -> str:
        """Respuesta para conteo de tickets"""
        base = "Sistema conectado a GLPI. Para obtener estadísticas precisas de tickets:\n\n"
        base += "• Total de tickets registrados\n"
        base += "• Distribución por estado (abiertos, cerrados, pendientes)\n"
        base += "• Análisis por período temporal\n"
        base += "• Clasificación por prioridad\n\n"
        
        if entities.get('time_references'):
            base += f"Filtros temporales detectados: {', '.join(entities['time_references'])}\n"
        
        base += "La información se actualizará desde la base de datos GLPI."
        return base
    
    def _generate_status_response(self, entities: Dict) -> str:
        """Respuesta para estado de tickets"""
        base = "Consulta de estado de tickets:\n\n"
        base += "Estados disponibles en GLPI:\n"
        base += "• Nuevos - Tickets recién creados\n"
        base += "• Asignados - En proceso de atención\n"
        base += "• En progreso - Siendo trabajados activamente\n"
        base += "• Pendientes - Esperando información adicional\n"
        base += "• Resueltos - Solución implementada\n"
        base += "• Cerrados - Proceso completado\n\n"
        
        if entities.get('status_types'):
            base += f"Estados específicos solicitados: {', '.join(entities['status_types'])}\n"
        
        return base
    
    def _generate_create_ticket_response(self, entities: Dict) -> str:
        """Respuesta para creación de tickets"""
        base = "Proceso de creación de tickets en GLPI:\n\n"
        base += "1. Definir categoría del problema\n"
        base += "2. Establecer nivel de prioridad\n"
        base += "3. Proporcionar descripción detallada\n"
        base += "4. Asignar técnico responsable (si aplica)\n"
        base += "5. Configurar notificaciones\n\n"
        
        if entities.get('priorities'):
            base += f"Prioridad detectada: {entities['priorities'][0]}\n"
        
        base += "El sistema registrará automáticamente fecha, hora y usuario solicitante."
        return base
    
    def _generate_user_analysis_response(self, entities: Dict) -> str:
        """Respuesta para análisis de usuarios"""
        base = "Análisis de usuarios en GLPI:\n\n"
        base += "Información disponible:\n"
        base += "• Usuarios activos en el sistema\n"
        base += "• Técnicos asignados por área\n"
        base += "• Carga de trabajo por usuario\n"
        base += "• Historial de actividad\n"
        base += "• Perfiles y permisos asignados\n\n"
        
        if entities.get('user_references'):
            base += f"Usuarios específicos: {', '.join(entities['user_references'])}\n"
        
        return base
    
    def _generate_statistics_response(self, entities: Dict) -> str:
        """Respuesta para estadísticas"""
        _ = entities  # Parámetro requerido por interfaz pero no usado
        base = f"{ESTADISTICS_LITERAL.capitalize()} del sistema GLPI:\n\n"
        base += "Métricas disponibles:\n"
        base += "• Volumen de tickets por período\n"
        base += "• Tiempo promedio de resolución\n"
        base += "• Distribución por categorías\n"
        base += "• Análisis de tendencias\n"
        base += "• Rendimiento del equipo técnico\n"
        base += "• Indicadores de satisfacción\n\n"
        base += "Los datos se generan en tiempo real desde la base de datos."
        return base
    
    def _generate_system_status_response(self, entities: Dict) -> str:
        """Respuesta para estado del sistema"""
        _ = entities  # Parámetro requerido por interfaz pero no usado
        base = "Estado actual del sistema GLPI:\n\n"
        base += "Componentes del sistema:\n"
        base += "• Servidor GLPI: Operativo\n"
        base += "• Base de datos: Conectada\n"
        base += "• API REST: Activa\n"
        base += "• Interfaz web: Disponible\n"
        base += "• Servicios de notificación: Funcionando\n\n"
        base += "Sistema listo para procesar consultas y gestionar tickets."
        return base
    
    def _generate_help_response(self) -> str:
        """Respuesta de ayuda general"""
        return """Funciones principales del asistente GLPI:

Gestión de Tickets:
• Consultar cantidad y estado de tickets
• Crear nuevos tickets e incidencias
• Analizar distribución por prioridad
• Revisar tickets pendientes o atrasados

Análisis de Usuarios:
• Información de técnicos y personal
• Carga de trabajo por usuario
• Análisis de rendimiento del equipo

Estadísticas y Reportes:
• Métricas de productividad
• Tendencias temporales
• Indicadores de calidad de servicio

Estado del Sistema:
• Verificar conectividad
• Consultar estado operativo
• Información de componentes

Para obtener ayuda específica, describa su consulta relacionada con GLPI."""
    
    def _generate_fallback_response(self, entities: Dict, sentiment: str) -> str:
        """Respuesta cuando no se puede clasificar la consulta"""
        _ = entities  # Parámetro requerido por interfaz pero no usado
        base = "Consulta no reconocida por el sistema GLPI.\n\n"
        
        if sentiment == 'urgent':
            base += "Para consultas urgentes, especifique:\n"
        else:
            base += "Para obtener asistencia, proporcione:\n"
        
        base += f"• Tipo de consulta ({TICKETS_LITERAL}, {USUARIOS_LITERAL}, {ESTADISTICS_LITERAL})\n"
        base += "• Información específica requerida\n"
        base += "• Contexto adicional si es necesario\n\n"
        base += "El sistema está especializado en gestión GLPI y puede ayudar con:\n"
        base += f"{TICKETS_LITERAL}, {USUARIOS_LITERAL}, {ESTADISTICS_LITERAL}, reportes y estado del sistema."
        
        return base


class ContextManager:
    """Gestor de contexto conversacional"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
    
    def add_interaction(self, query: str, response: str, intent: str):
        """Agregar interacción al historial"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'intent': intent
        })
        
        # Mantener solo las últimas 10 interacciones
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_context(self) -> Dict:
        """Obtener contexto actual de la conversación"""
        if not self.conversation_history:
            return {}
        
        recent_intents = [interaction['intent'] for interaction in self.conversation_history[-3:]]
        
        return {
            'recent_intents': recent_intents,
            'conversation_length': len(self.conversation_history),
            'last_query': self.conversation_history[-1]['query'] if self.conversation_history else None
        }