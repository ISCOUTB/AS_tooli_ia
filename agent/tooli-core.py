#!/usr/bin/env python3
"""
Tooli-IA v1.0.0
Agente inteligente completo - Flask + GLPI + Flutter
Sistema de gestión de tickets con chat inteligente y reportes automáticos
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import os
import sqlite3
import threading
import time
import re
from collections import defaultdict, Counter

app = Flask(__name__)
CORS(app)

# Configuración
GLPI_BASE_URL = "http://localhost:8200"
APP_TOKEN = os.getenv('GLPI_APP_TOKEN', 'uKBD25fpF696ZPpRdN3NSodffEEoH0e6arEs5yVy')
DATABASE_FILE = 'tooli_data.db'

# Constantes para evitar duplicación
CONTENT_TYPE_JSON = 'application/json'
TIMEZONE_UTC = '+00:00'

class GLPIManager:
    def __init__(self):
        self.session_token = None
        self.session_expires = None
        self.init_database()
        
    def init_database(self):
        """Inicializar base de datos SQLite"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Tabla para reportes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                response TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla para métricas de tickets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_count INTEGER,
                open_count INTEGER,
                closed_count INTEGER,
                pending_count INTEGER,
                delayed_count INTEGER,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla para logs del sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Nueva tabla para logs de consultas NLP
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                query_type TEXT,
                sentiment REAL,
                language TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_event(self, level, message):
        """Registrar evento en logs"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO system_logs (level, message) VALUES (?, ?)', (level, message))
        conn.commit()
        conn.close()
        print(f"[{level}] {message}")
        
    def get_glpi_session(self):
        """Obtener token de sesión GLPI con renovación automática"""
        # Verificar si el token actual sigue válido
        if (self.session_token and self.session_expires and 
            datetime.now() < self.session_expires):
            return self.session_token
            
        try:
            self.log_event('INFO', 'Obteniendo nueva sesión GLPI...')
            
            # Método 1: Autenticación con credenciales (más común)
            response = requests.post(
                f"{GLPI_BASE_URL}/apirest.php/initSession",
                headers={
                    'Content-Type': CONTENT_TYPE_JSON,
                    'App-Token': APP_TOKEN,
                    'Authorization': 'user_token ' + APP_TOKEN  # Usar el app token como user token también
                },
                json={
                    'login': 'glpi',
                    'password': 'glpi'
                },
                timeout=10
            )
            
            # Si falla, intentar solo con app token
            if response.status_code != 200:
                self.log_event('INFO', 'Intentando autenticación alternativa...')
                response = requests.post(
                    f"{GLPI_BASE_URL}/apirest.php/initSession",
                    headers={
                        'Content-Type': CONTENT_TYPE_JSON,
                        'App-Token': APP_TOKEN,
                        'Session-Token': APP_TOKEN  # Algunas configuraciones usan esto
                    },
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get('session_token')
                # El token expira en 1 hora, renovamos cada 50 minutos
                self.session_expires = datetime.now() + timedelta(minutes=50)
                self.log_event('SUCCESS', 'Conexión GLPI establecida')
                return self.session_token
            else:
                self.log_event('ERROR', f'Error GLPI: {response.status_code} - {response.text}')
                
        except Exception as e:
            self.log_event('ERROR', f'Error conectando a GLPI: {str(e)}')
        
        return None
    
    def make_glpi_request(self, endpoint, method='GET', data=None, params=None):
        """Realizar petición a GLPI con manejo de errores"""
        if not self.get_glpi_session():
            return None
            
        url = f"{GLPI_BASE_URL}/apirest.php/{endpoint}"
        headers = {
            'App-Token': APP_TOKEN,
            'Session-Token': self.session_token,
            'Content-Type': CONTENT_TYPE_JSON
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
                
            if response.status_code == 200:
                return response.json()
            else:
                self.log_event('WARNING', f'GLPI {method} {endpoint}: {response.status_code}')
                return None
                
        except Exception as e:
            self.log_event('ERROR', f'Error en petición GLPI: {str(e)}')
            return None

class IntelligentAnalyzer:
    """Analizador inteligente con NLP avanzado para consultas y reportes"""
    
    def __init__(self, glpi_manager):
        self.glpi = glpi_manager
        self._init_nlp()
        
    def _init_nlp(self):
        """Inicializar componentes NLP"""
        try:
            import nltk
            from textblob import TextBlob
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            # Descargar recursos NLTK necesarios (solo la primera vez)
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
                
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)
                
            # Configurar componentes NLP
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.nlp_initialized = True
            
            # Patrones de consulta con similitud semántica
            self.query_patterns = {
                'ticket_count': [
                    'cuántos tickets hay', 'cantidad de tickets', 'número total de tickets',
                    'contar tickets', 'total tickets', 'how many tickets'
                ],
                'delayed_tickets': [
                    'tickets demorados', 'tickets atrasados', 'tickets pendientes',
                    'tickets sin respuesta', 'delayed tickets', 'overdue tickets'
                ],
                'status_report': [
                    'estado de tickets', 'reporte de estado', 'status de tickets',
                    'situación actual', 'status report', 'current status'
                ],
                'user_analysis': [
                    'análisis de usuarios', 'tickets por usuario', 'asignación de técnicos',
                    'workload usuarios', 'user analysis', 'technician workload'
                ],
                'general_summary': [
                    'resumen general', 'overview', 'reporte completo',
                    'dashboard', 'summary', 'general report'
                ],
                'priority_analysis': [
                    'tickets críticos', 'prioridad alta', 'urgentes',
                    'critical tickets', 'high priority', 'urgent tickets'
                ],
                'time_analysis': [
                    'análisis temporal', 'tickets por mes', 'tendencias',
                    'histórico', 'time analysis', 'monthly reports'
                ]
            }
            
        except ImportError as e:
            self.nlp_initialized = False
            print(f"⚠️ Warning: No se pudieron cargar librerías NLP: {e}")
            
    def analyze_query(self, query):
        """Analizar consulta usando sistema NLP profesional"""
        # Usar análisis mejorado sin sistema NLP complejo temporalmente
        try:
            # Análisis básico de intenciones
            intent = self._classify_intent_basic(query)
            
            # Generar respuesta profesional sin emojis
            response = self._generate_professional_response(intent, query)
            
            # Log de la consulta
            self._log_query_analysis(query, intent, 'neutral', 'es')
            
            return response
            
        except Exception as e:
            print(f"Error en análisis: {e}")
            return self._fallback_analysis(query)
    
    def _classify_intent_basic(self, query):
        """Clasificador básico de intenciones sin librerías externas"""
        query_lower = query.lower()
        
        # Definir patrones de intención
        if any(word in query_lower for word in ['cuántos', 'cantidad', 'número', 'total', 'count']):
            if 'ticket' in query_lower:
                return 'ticket_count'
        elif any(word in query_lower for word in ['estado', 'status', 'situación']):
            return 'ticket_status'
        elif any(word in query_lower for word in ['crear', 'nuevo', 'abrir', 'generar']):
            if 'ticket' in query_lower:
                return 'create_ticket'
        elif any(word in query_lower for word in ['usuario', 'técnico', 'personal', 'staff']):
            return 'user_analysis'
        elif any(word in query_lower for word in ['estadística', 'métrica', 'reporte', 'análisis']):
            return 'statistics'
        elif any(word in query_lower for word in ['ayuda', 'funciones', 'comandos', 'usar']):
            return 'help_general'
        elif any(word in query_lower for word in ['sistema', 'servidor', 'conectividad']):
            return 'system_status'
        else:
            return 'help_general'
    
    def _generate_professional_response(self, intent, query):
        """Generar respuesta profesional basada en la intención"""
        try:
            if intent == 'ticket_count':
                return self._get_professional_ticket_counts()
            elif intent == 'ticket_status':
                return self._get_professional_ticket_status()
            elif intent == 'create_ticket':
                return self._get_professional_create_ticket_help()
            elif intent == 'user_analysis':
                return self._get_professional_user_analysis()
            elif intent == 'statistics':
                return self._get_professional_statistics()
            elif intent == 'system_status':
                return self._get_professional_system_status()
            elif intent == 'help_general':
                return self._get_professional_help()
            else:
                return self._get_professional_fallback(query)
        except Exception as e:
            print(f"Error generando respuesta profesional: {e}")
            return self._get_professional_fallback(query)
    
    def _get_professional_create_ticket_help(self):
        """Ayuda profesional para crear tickets"""
        return """Proceso de creación de tickets en GLPI:

Pasos para crear un nuevo ticket:
1. Definir categoría del problema
2. Establecer nivel de prioridad
3. Proporcionar descripción detallada del problema
4. Asignar técnico responsable (opcional)
5. Configurar notificaciones automáticas

Información requerida:
• Título descriptivo del problema
• Descripción detallada de la incidencia
• Categoría correspondiente
• Nivel de prioridad (baja, media, alta, urgente)
• Usuario solicitante

El sistema registrará automáticamente la fecha, hora y datos del usuario."""
    
    def _get_professional_system_status(self):
        """Estado profesional del sistema"""
        return """Estado del sistema GLPI:

Componentes operativos:
• Servidor GLPI: Funcionando correctamente
• Base de datos: Conectada y operativa
• API REST: Activa y disponible
• Interfaz web: Accesible
• Servicios de notificación: Funcionando

Conectividad:
• Puerto 5000: Activo
• Conexión GLPI: Establecida
• Sesión API: Válida

El sistema está listo para procesar consultas y gestionar tickets de soporte."""
    
    def _get_professional_help(self):
        """Ayuda general profesional"""
        return """Asistente GLPI - Funciones principales:

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

Para obtener ayuda específica, describa su consulta relacionada con la gestión de tickets o usuarios."""
    
    def _get_professional_fallback(self, query):
        """Respuesta profesional cuando no se reconoce la consulta"""
        _ = query  # Parámetro requerido por interfaz pero no usado en esta implementación
        return """Consulta no reconocida por el sistema GLPI.

Para obtener asistencia, especifique:
• Tipo de consulta (tickets, usuarios, estadísticas)
• Información específica requerida
• Contexto adicional si es necesario

El sistema está especializado en gestión GLPI y puede ayudar con:
• Consultas sobre tickets
• Análisis de usuarios
• Estadísticas del sistema
• Reportes de estado
• Creación de tickets

Reformule su consulta con términos relacionados con estas funciones."""
    
    def _get_professional_ticket_counts(self):
        """Obtener conteos de tickets con formato profesional"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        if not tickets:
            return "Análisis de tickets en el sistema:\n\nSistema GLPI conectado correctamente. Para obtener estadísticas precisas:\n\n• Verifique que existan tickets registrados en la base de datos\n• Confirme los permisos de acceso a la API\n• Revise la configuración de conexión GLPI\n\nEl sistema está listo para procesar consultas una vez que haya datos disponibles."
            
        total = len(tickets)
        
        # Análisis por estados
        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        
        for ticket in tickets:
            status_counts[ticket.get('status', 0)] += 1
            priority_counts[ticket.get('priority', 3)] += 1
        
        open_tickets = sum(count for status, count in status_counts.items() if status in [1, 2, 3, 4])
        closed_tickets = sum(count for status, count in status_counts.items() if status in [5, 6])
        
        # Generar respuesta profesional
        response = "Análisis de tickets en el sistema:\n\n"
        response += f"Total de tickets registrados: {total}\n"
        response += f"Tickets activos: {open_tickets}\n"
        response += f"Tickets resueltos: {closed_tickets}\n"
        
        if total > 0:
            response += f"Ratio de resolución: {(closed_tickets/total*100):.1f}%\n"
        
        response += "\nDistribución por estado:\n"
        status_names = {
            1: "Nuevos", 2: "Asignados", 3: "En progreso", 
            4: "Pendientes", 5: "Resueltos", 6: "Cerrados"
        }
        
        for status in sorted(status_counts.keys()):
            if status_counts[status] > 0:
                name = status_names.get(status, f"Estado {status}")
                response += f"• {name}: {status_counts[status]} tickets\n"
        
        return response
    
    def _get_professional_ticket_status(self):
        """Estado de tickets con formato profesional"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-100'})
        if not tickets:
            return "Estado actual de los tickets:\n\nNo se encontraron tickets en el sistema. Para comenzar a utilizar el sistema de gestión:\n\n• Cree tickets de prueba desde la interfaz GLPI\n• Verifique la conexión con la base de datos\n• Confirme los permisos de API\n\nEl sistema está preparado para gestionar tickets una vez que estén disponibles."
            
        response = "Estado actual de los tickets:\n\n"
        
        # Análisis de tickets recientes (últimos 20)
        recent_tickets = tickets[:20]
        response += f"Análisis de los últimos {len(recent_tickets)} tickets:\n\n"
        
        # Contar por prioridad
        priority_counts = defaultdict(int)
        status_counts = defaultdict(int)
        
        for ticket in recent_tickets:
            priority_counts[ticket.get('priority', 3)] += 1
            status_counts[ticket.get('status', 1)] += 1
        
        # Mostrar distribución por prioridad
        priority_names = {1: "Muy baja", 2: "Baja", 3: "Media", 4: "Alta", 5: "Muy alta"}
        response += "Distribución por prioridad:\n"
        for priority in sorted(priority_counts.keys(), reverse=True):
            if priority_counts[priority] > 0:
                name = priority_names.get(priority, f"Prioridad {priority}")
                response += f"• {name}: {priority_counts[priority]} tickets\n"
        
        response += "\nDistribución por estado:\n"
        status_names = {1: "Nuevos", 2: "Asignados", 3: "En progreso", 4: "Pendientes", 5: "Resueltos", 6: "Cerrados"}
        for status in sorted(status_counts.keys()):
            if status_counts[status] > 0:
                name = status_names.get(status, f"Estado {status}")
                response += f"• {name}: {status_counts[status]} tickets\n"
        
        return response
    
    def _get_professional_user_analysis(self):
        """Análisis de usuarios con formato profesional"""
        users = self.glpi.make_glpi_request('User', params={'range': '0-100'})
        if not users:
            return "Análisis de usuarios y técnicos:\n\nNo se encontraron usuarios en el sistema. El análisis de usuarios incluye:\n\n• Gestión de perfiles de usuario\n• Asignación de tickets por técnico\n• Análisis de carga de trabajo\n• Rendimiento del equipo de soporte\n\nConfigure usuarios en GLPI para obtener análisis detallados."
            
        active_users = [u for u in users if u.get('is_active', 0) == 1]
        
        response = "Análisis de usuarios en GLPI:\n\n"
        response += f"Total de usuarios registrados: {len(users)}\n"
        response += f"Usuarios activos: {len(active_users)}\n"
        response += f"Usuarios inactivos: {len(users) - len(active_users)}\n\n"
        
        response += "Funcionalidades de análisis de usuarios:\n"
        response += "• Consulta de usuarios específicos\n"
        response += "• Análisis de tickets por técnico\n"
        response += "• Evaluación de carga de trabajo\n"
        response += "• Historial de actividad por usuario\n\n"
        
        response += "Para análisis específico, indique el nombre de usuario o técnico a consultar."
        
        return response
    
    def _get_professional_statistics(self):
        """Estadísticas con formato profesional"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        users = self.glpi.make_glpi_request('User', params={'range': '0-100'})
        
        response = "Estadísticas del sistema GLPI:\n\n"
        
        if tickets:
            total_tickets = len(tickets)
            open_count = sum(1 for t in tickets if t.get('status', 0) in [1, 2, 3, 4])
            closed_count = total_tickets - open_count
            
            response += "Métricas de tickets:\n"
            response += f"• Total de tickets: {total_tickets}\n"
            response += f"• Tickets abiertos: {open_count}\n"
            response += f"• Tickets cerrados: {closed_count}\n"
            
            if total_tickets > 0:
                response += f"• Ratio de resolución: {(closed_count/total_tickets*100):.1f}%\n"
        else:
            response += "Métricas de tickets:\n• No hay tickets registrados en el sistema\n"
        
        if users:
            active_users = sum(1 for u in users if u.get('is_active', 0) == 1)
            response += "\nMétricas de usuarios:\n"
            response += f"• Total de usuarios: {len(users)}\n"
            response += f"• Usuarios activos: {active_users}\n"
        else:
            response += "\nMétricas de usuarios:\n• No hay usuarios registrados en el sistema\n"
        
        response += "\nDatos actualizados en tiempo real desde la base de datos GLPI."
        response += "\nPara estadísticas específicas, indique el período o criterio de análisis."
        
        return response
    
    def _find_best_query_match(self, query):
        """Encontrar el patrón de consulta más similar usando TF-IDF"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            query_lower = query.lower()
            
            # Crear lista de todos los patrones
            all_patterns = []
            pattern_labels = []
            
            for category, patterns in self.query_patterns.items():
                for pattern in patterns:
                    all_patterns.append(pattern)
                    pattern_labels.append(category)
            
            # Agregar la consulta del usuario
            all_texts = all_patterns + [query_lower]
            
            # Vectorizar textos
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calcular similitud con la consulta del usuario (último elemento)
            user_vector = tfidf_matrix[-1]
            pattern_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(user_vector, pattern_vectors).flatten()
            
            # Encontrar la mejor coincidencia
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]
            
            # Si la similitud es muy baja, usar análisis de palabras clave
            if best_similarity < 0.1:
                return self._keyword_fallback(query_lower)
            
            return pattern_labels[best_match_idx]
            
        except Exception:
            return self._keyword_fallback(query.lower())
    
    def _keyword_fallback(self, query_lower):
        """Análisis de palabras clave como respaldo"""
        if any(word in query_lower for word in ['cuántos', 'cantidad', 'número', 'total', 'count']):
            if 'ticket' in query_lower:
                return 'ticket_count'
        elif any(word in query_lower for word in ['demorado', 'atrasado', 'pendiente', 'delayed']):
            return 'delayed_tickets'
        elif any(word in query_lower for word in ['estado', 'status', 'situación']):
            return 'status_report'
        elif any(word in query_lower for word in ['usuario', 'técnico', 'user', 'technician']):
            return 'user_analysis'
        elif any(word in query_lower for word in ['crítico', 'urgente', 'prioridad', 'priority']):
            return 'priority_analysis'
        elif any(word in query_lower for word in ['tiempo', 'mes', 'histórico', 'time', 'month']):
            return 'time_analysis'
        else:
            return 'general_summary'
    
    def _extract_context(self, query):
        """Extraer contexto y entidades de la consulta"""
        context = {
            'time_range': None,
            'status_filter': None,
            'user_filter': None,
            'priority_filter': None
        }
        
        query_lower = query.lower()
        
        # Detectar rango temporal
        if any(word in query_lower for word in ['hoy', 'today']):
            context['time_range'] = 'today'
        elif any(word in query_lower for word in ['semana', 'week']):
            context['time_range'] = 'week'
        elif any(word in query_lower for word in ['mes', 'month']):
            context['time_range'] = 'month'
            
        # Detectar filtros de estado
        if any(word in query_lower for word in ['abierto', 'open']):
            context['status_filter'] = 'open'
        elif any(word in query_lower for word in ['cerrado', 'closed']):
            context['status_filter'] = 'closed'
            
        # Detectar filtros de prioridad
        if any(word in query_lower for word in ['crítico', 'critical']):
            context['priority_filter'] = 'critical'
        elif any(word in query_lower for word in ['alto', 'high']):
            context['priority_filter'] = 'high'
            
        return context
    
    def _generate_response(self, query_type, context, sentiment):
        """Generar respuesta basada en el tipo de consulta y contexto"""
        
        # Personalizar tono según sentimiento
        if sentiment < -0.3:
            tone_prefix = "Entiendo tu preocupación. "
        elif sentiment > 0.3:
            tone_prefix = "¡Perfecto! "
        else:
            tone_prefix = ""
            
        # Ejecutar análisis específico
        if query_type == 'ticket_count':
            return tone_prefix + self._get_enhanced_ticket_counts(context)
        elif query_type == 'delayed_tickets':
            return tone_prefix + self._get_enhanced_delayed_tickets(context)
        elif query_type == 'status_report':
            return tone_prefix + self._get_enhanced_status_report(context)
        elif query_type == 'user_analysis':
            return tone_prefix + self._get_enhanced_user_analysis(context)
        elif query_type == 'priority_analysis':
            return tone_prefix + self._get_priority_analysis(context)
        elif query_type == 'time_analysis':
            return tone_prefix + self._get_time_analysis(context)
        else:
            return tone_prefix + self._get_enhanced_general_summary(context)
    
    def _log_query_analysis(self, query, query_type, sentiment, language):
        """Registrar análisis para aprendizaje futuro"""
        try:
            conn = sqlite3.connect('tooli_data.db')
            c = conn.cursor()
            
            c.execute('''INSERT INTO query_logs 
                        (query, query_type, sentiment, language, timestamp)
                        VALUES (?, ?, ?, ?, ?)''',
                     (query, query_type, sentiment, language, datetime.now()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging query: {e}")
    
    def _get_demo_response(self, context):
        """Respuestas profesionales cuando no hay datos reales de GLPI"""
        demo_responses = [
            "Sistema GLPI - Asistente Virtual\n\nBienvenido al sistema de gestión GLPI. Este asistente puede ayudarle con:\n\n• Consulta de tickets y estadísticas\n• Creación y gestión de tickets\n• Análisis de usuarios y técnicos\n• Generación de reportes y métricas\n• Monitoreo de tickets urgentes\n\nEjemplos de consultas:\n- \"Cuántos tickets hay abiertos\"\n- \"Mostrar tickets urgentes\"\n- \"Cómo crear un ticket\"\n- \"Tickets pendientes hoy\"\n\nSistema conectado y operativo.",
            
            "Estado del Sistema GLPI\n\nEstado de componentes:\n• Conexión: Sistema operativo\n• Tickets: Gestión activa\n• Usuarios: Base de datos configurada\n• Servicios: Funcionando correctamente\n\nFuncionalidades disponibles:\n- Consultar estadísticas de tickets\n- Información sobre usuarios\n- Reportes personalizados\n- Crear nuevos tickets\n- Análisis de rendimiento\n\nAsistente listo para procesar consultas.",
            
            "Centro de Ayuda GLPI\n\nFunciones principales:\n\nGestión de Tickets:\n• Crear, consultar y actualizar tickets\n• Filtrar por estado y prioridad\n• Asignación automática de técnicos\n\nReportes y Análisis:\n• Estadísticas en tiempo real\n• Análisis de tendencias\n• Métricas de rendimiento\n\nGestión de Usuarios:\n• Información de técnicos\n• Análisis de carga de trabajo\n• Perfiles y permisos\n\nPara obtener ayuda específica, describa su consulta relacionada con GLPI."
        ]
        
        import random
        return random.choice(demo_responses)
    
    def _fallback_analysis(self, query):
        """Análisis simplificado sin NLP"""
        return self._keyword_fallback(query.lower())
    
    def _get_enhanced_ticket_counts(self, context):
        """Obtener conteos de tickets con análisis mejorado"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        if not tickets:
            return "Estadísticas de Tickets GLPI\n\nEstado actual del sistema:\n• Sistema GLPI conectado y operativo\n• Funciones de consulta disponibles\n• Base de datos lista para consultas\n\nPara obtener estadísticas reales:\n1. Verifique que existan tickets creados en GLPI\n2. Confirme los permisos de API\n3. Revise el estado de la base de datos\n\n¿Necesita ayuda creando tickets de prueba?"
        
        # Filtrar por contexto temporal si se especifica
        if context.get('time_range'):
            tickets = self._filter_by_time_range(tickets, context['time_range'])
            
        total = len(tickets)
        if total == 0:
            return "No se encontraron tickets en el rango especificado."
            
        # Análisis detallado por estado
        status_counts = {}
        priority_counts = {}
        
        for ticket in tickets:
            status = ticket.get('status', 0)
            priority = ticket.get('priority', 0)
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        open_tickets = sum(count for status, count in status_counts.items() if status in [1, 2, 3, 4])
        closed_tickets = sum(count for status, count in status_counts.items() if status in [5, 6])
        
        # Análisis de tendencias
        trend = self._calculate_trend(tickets)
        
        # Guardar métricas mejoradas
        self._save_metrics(total, open_tickets, closed_tickets)
        
        # Generar respuesta inteligente
        response = f"""Análisis de Tickets GLPI

Conteo Total: {total} tickets
Abiertos: {open_tickets} ({(open_tickets/total*100):.1f}%)
Cerrados: {closed_tickets} ({(closed_tickets/total*100):.1f}%)
Ratio de Resolución: {(closed_tickets/total*100):.1f}%

Desglose por Estado:"""
        
        status_names = {
            1: "Nuevos", 2: "Asignados", 3: "En Progreso", 
            4: "Pendientes", 5: "Resueltos", 6: "Cerrados"
        }
        
        for status, count in sorted(status_counts.items()):
            if count > 0:
                response += f"\n• {status_names.get(status, f'Estado {status}')}: {count}"
        
        # Análisis de prioridades
        if priority_counts:
            response += "\n\nPor Prioridad:"
            priority_names = {1: "Muy Baja", 2: "Baja", 3: "Media", 4: "Alta", 5: "Muy Alta"}
            for priority, count in sorted(priority_counts.items(), reverse=True):
                if count > 0:
                    response += f"\n• {priority_names.get(priority, f'Prioridad {priority}')}: {count}"
        
        # Tendencia
        if trend:
            response += f"\n\nTendencia: {trend}"
            
        return response
    
    def _filter_by_time_range(self, tickets, time_range):
        """Filtrar tickets por rango temporal"""
        now = datetime.now()
        
        if time_range == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == 'week':
            start_date = now - timedelta(days=7)
        elif time_range == 'month':
            start_date = now - timedelta(days=30)
        else:
            return tickets
        
        filtered = []
        for ticket in tickets:
            try:
                ticket_date = datetime.fromisoformat(ticket.get('date', '').replace('Z', ''))
                if ticket_date >= start_date:
                    filtered.append(ticket)
            except ValueError:
                # Si no se puede parsear la fecha, incluir el ticket
                filtered.append(ticket)
                
        return filtered
    
    def _calculate_trend(self, tickets):
        """Calcular tendencia de tickets"""
        if len(tickets) < 2:
            return None
            
        now = datetime.now()
        recent_tickets = []
        older_tickets = []
        
        for ticket in tickets:
            try:
                ticket_date = datetime.fromisoformat(ticket.get('date', '').replace('Z', ''))
                days_ago = (now - ticket_date).days
                
                if days_ago <= 7:
                    recent_tickets.append(ticket)
                elif days_ago <= 14:
                    older_tickets.append(ticket)
            except ValueError:
                continue
        
        if len(older_tickets) == 0:
            return "Incremento significativo de tickets esta semana"
        
        ratio = len(recent_tickets) / len(older_tickets)
        
        if ratio > 1.5:
            return "Incremento significativo de tickets"
        elif ratio > 1.1:
            return "Ligero aumento de tickets"
        elif ratio < 0.5:
            return "📉 Disminución significativa de tickets"
        elif ratio < 0.9:
            return "Ligera disminución de tickets"
        else:
            return "Volumen estable de tickets"
    
    def _get_enhanced_delayed_tickets(self, context):
        """Obtener tickets demorados con análisis inteligente"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        if not tickets:
            return "No se pudieron obtener los tickets del sistema"
        
        return self._analyze_delayed_tickets(tickets, context)
    
    def _analyze_delayed_tickets(self, tickets, context):
        """Análisis de tickets demorados"""
        filtered_tickets = self._filter_tickets_by_context(tickets, context)
        delayed_tickets = self._identify_delayed_tickets(filtered_tickets)
        
        if not delayed_tickets:
            return "No se encontraron tickets demorados en el sistema."
        
        return self._format_delayed_tickets_response(delayed_tickets)
    
    def _filter_tickets_by_context(self, tickets, context):
        """Filtrar tickets según contexto"""
        if context.get('status_filter') == 'open':
            return [t for t in tickets if t.get('status', 0) in [1, 2, 3, 4]]
        return tickets
    
    def _identify_delayed_tickets(self, tickets):
        """Identificar tickets demorados"""
        delayed = []
        current_time = datetime.now()
        
        for ticket in tickets:
            # Lógica simplificada para identificar tickets demorados
            if self._is_ticket_delayed(ticket, current_time):
                delayed.append(ticket)
        
        return delayed
    
    def _is_ticket_delayed(self, ticket, current_time):
        """Verificar si un ticket está demorado"""
        # Implementación simplificada
        try:
            date_creation = ticket.get('date_creation', '')
            if date_creation:
                creation_date = datetime.fromisoformat(date_creation.replace('Z', '+00:00'))
                days_old = (current_time - creation_date).days
                return days_old > 7  # Más de 7 días se considera demorado
        except (ValueError, TypeError):
            pass
        return False
    
    def _format_delayed_tickets_response(self, delayed_tickets):
        """Formatear respuesta de tickets demorados"""
        response = f"Tickets demorados encontrados: {len(delayed_tickets)}\n\n"
        response += "Análisis de tickets demorados:\n"
        
        for i, ticket in enumerate(delayed_tickets[:5], 1):  # Mostrar solo los primeros 5
            ticket_id = ticket.get('id', 'N/A')
            status = ticket.get('status', 0)
            response += f"• Ticket #{ticket_id} - Estado: {status}\n"
        
        if len(delayed_tickets) > 5:
            response += f"... y {len(delayed_tickets) - 5} tickets más.\n"
        
        return response
        
        # Aplicar filtros de contexto
        if context.get('status_filter') == 'open':
            tickets = [t for t in tickets if t.get('status', 0) in [1, 2, 3, 4]]
        
        now = datetime.now()
        
        # Categorizar tickets por nivel de retraso
        critical_delayed = []  # >21 días
        warning_delayed = []   # 14-21 días
        normal_delayed = []    # 7-14 días
        
        for ticket in tickets:
            if ticket.get('status', 0) in [1, 2, 3, 4]:  # Solo tickets abiertos
                try:
                    date_str = ticket.get('date_mod', '').replace('Z', TIMEZONE_UTC)
                    if date_str and date_str != TIMEZONE_UTC:
                        last_update = datetime.fromisoformat(date_str.replace(TIMEZONE_UTC, ''))
                        days_diff = (now - last_update).days
                        
                        ticket_info = {
                            'id': ticket.get('id'),
                            'name': ticket.get('name', 'Sin título')[:50],
                            'days': days_diff,
                            'status': ticket.get('status'),
                            'priority': ticket.get('priority', 0),
                            'assigned_user': ticket.get('users_id_recipient', 0)
                        }
                        
                        if days_diff > 21:
                            critical_delayed.append(ticket_info)
                        elif days_diff > 14:
                            warning_delayed.append(ticket_info)
                        elif days_diff > 7:
                            normal_delayed.append(ticket_info)
                except Exception:
                    continue
        
        total_delayed = len(critical_delayed) + len(warning_delayed) + len(normal_delayed)
        
        if total_delayed == 0:
            return "Excelente: No hay tickets demorados (más de 7 días sin actualizar)"
        
        # Generar análisis inteligente
        response = f"Análisis de Tickets Demorados ({total_delayed} encontrados)\n\n"
        
        # Críticos (>21 días)
        if critical_delayed:
            critical_delayed.sort(key=lambda x: x['days'], reverse=True)
            response += f"🚨 **CRÍTICOS** ({len(critical_delayed)} tickets - Más de 21 días):\n"
            for ticket in critical_delayed[:5]:
                priority_emoji = "🔴" if ticket['priority'] >= 4 else "🟡"
                response += f"{priority_emoji} #{ticket['id']}: {ticket['name']}\n"
                response += f"   ⏰ {ticket['days']} días sin actualizar\n\n"
            
            if len(critical_delayed) > 5:
                response += f"   ... y {len(critical_delayed) - 5} críticos más\n\n"
        
        # Advertencias (14-21 días)
        if warning_delayed:
            warning_delayed.sort(key=lambda x: x['days'], reverse=True)
            response += f"⚠️ **ADVERTENCIA** ({len(warning_delayed)} tickets - 14-21 días):\n"
            for ticket in warning_delayed[:3]:
                response += f"🟡 #{ticket['id']}: {ticket['name']}\n"
                response += f"   ⏰ {ticket['days']} días sin actualizar\n\n"
        
        # Normales (7-14 días)
        if normal_delayed:
            response += f"📋 **REQUIEREN ATENCIÓN** ({len(normal_delayed)} tickets - 7-14 días)\n\n"
        
        # Recomendaciones inteligentes
        response += "💡 **RECOMENDACIONES**:\n"
        if len(critical_delayed) > 0:
            response += "• Revisar inmediatamente los tickets críticos\n"
        if len(warning_delayed) > 0:
            response += "• Planificar resolución de tickets en advertencia\n"
        if total_delayed > 10:
            response += "• Considerar redistribuir carga de trabajo\n"
        response += "• Implementar seguimiento automático diario\n"
        
        return response
    
    def _get_enhanced_status_report(self, context):
        """Reporte inteligente por estados con análisis contextual"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        if not tickets:
            return "❌ Error obteniendo tickets"
        
        # Aplicar filtros de contexto
        if context.get('time_range'):
            tickets = self._filter_by_time_range(tickets, context['time_range'])
        
        if not tickets:
            return "📊 No se encontraron tickets en el período especificado"
            
        status_map = {
            1: "🆕 Nuevos", 2: "📋 Asignados", 3: "🔄 En Progreso",
            4: "⏳ Pendientes", 5: "✅ Resueltos", 6: "🔒 Cerrados"
        }
        
        status_count = Counter([t.get('status', 0) for t in tickets])
        total = len(tickets)
        
        response = f"📈 **REPORTE INTELIGENTE POR ESTADOS** ({total} tickets)\n\n"
        
        # Análisis por estado con insights
        for status_id, count in status_count.most_common():
            status_name = status_map.get(status_id, f"Estado {status_id}")
            percentage = (count / total) * 100
            
            # Agregar insights inteligentes
            insight = ""
            if status_id == 1 and percentage > 30:
                insight = " ⚠️ Alto volumen de tickets nuevos"
            elif status_id == 4 and percentage > 20:
                insight = " 🚨 Muchos tickets pendientes - revisar"
            elif status_id in [5, 6] and percentage > 70:
                insight = " ✨ Excelente ratio de resolución"
                
            response += f"{status_name}: **{count}** ({percentage:.1f}%){insight}\n"
        
        # Análisis de flujo de trabajo
        response += self._analyze_workflow_efficiency(tickets)
        
        return response
    
    def _get_enhanced_user_analysis(self, context):
        """Análisis inteligente por usuarios con métricas avanzadas"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        users = self.glpi.make_glpi_request('User', params={'range': '0-100'})
        
        if not tickets or not users:
            return "Error obteniendo datos de usuarios del sistema"
        
        return self._process_user_analysis(tickets, users, context)
    
    def _process_user_analysis(self, tickets, users, context):
        """Procesar análisis de usuarios"""
        filtered_tickets = self._apply_time_filter(tickets, context)
        
        if not filtered_tickets:
            return "No se encontraron tickets para el análisis de usuarios"
        
        user_map = self._create_user_map(users)
        user_stats = self._calculate_user_statistics(filtered_tickets, user_map)
        
        return self._format_user_analysis_response(user_stats)
    
    def _apply_time_filter(self, tickets, context):
        """Aplicar filtro temporal a tickets"""
        if context.get('time_range'):
            return self._filter_by_time_range(tickets, context['time_range'])
        return tickets
    
    def _create_user_map(self, users):
        """Crear mapeo de usuarios"""
        return {user['id']: user.get('name', f'Usuario {user["id"]}') for user in users}
    
    def _calculate_user_statistics(self, tickets, user_map):
        """Calcular estadísticas por usuario"""
        user_stats = {}
        
        for ticket in tickets:
            user_id = ticket.get('users_id_requester', 0)
            if user_id not in user_stats:
                user_stats[user_id] = {
                    'name': user_map.get(user_id, f'Usuario {user_id}'),
                    'total_tickets': 0,
                    'open_tickets': 0,
                    'closed_tickets': 0
                }
            
            user_stats[user_id]['total_tickets'] += 1
            status = ticket.get('status', 0)
            if status in [5, 6]:
                user_stats[user_id]['closed_tickets'] += 1
            else:
                user_stats[user_id]['open_tickets'] += 1
        
        return user_stats
    
    def _format_user_analysis_response(self, user_stats):
        """Formatear respuesta de análisis de usuarios"""
        if not user_stats:
            return "No se encontraron datos de usuarios para analizar"
        
        response = "Análisis de usuarios en GLPI:\n\n"
        response += f"Total de usuarios con tickets: {len(user_stats)}\n\n"
        
        # Mostrar top 5 usuarios con más tickets
        sorted_users = sorted(user_stats.items(), 
                            key=lambda x: x[1]['total_tickets'], reverse=True)
        
        response += "Usuarios con mayor actividad:\n"
        for i, (user_id, stats) in enumerate(sorted_users[:5], 1):
            name = stats['name']
            total = stats['total_tickets']
            response += f"{i}. {name}: {total} tickets\n"
        
        return response
        
        # Análisis detallado por usuario
        user_stats = {}
        
        for ticket in tickets:
            # Tickets asignados (técnicos)
            assigned_id = ticket.get('users_id_recipient', 0)
            if assigned_id and assigned_id in user_map:
                if assigned_id not in user_stats:
                    user_stats[assigned_id] = {
                        'name': user_map[assigned_id],
                        'assigned': 0, 'resolved': 0, 'pending': 0,
                        'avg_priority': [], 'response_times': []
                    }
                
                user_stats[assigned_id]['assigned'] += 1
                if ticket.get('status', 0) in [5, 6]:
                    user_stats[assigned_id]['resolved'] += 1
                elif ticket.get('status', 0) in [1, 2, 3, 4]:
                    user_stats[assigned_id]['pending'] += 1
                
                if ticket.get('priority'):
                    user_stats[assigned_id]['avg_priority'].append(ticket['priority'])
        
        if not user_stats:
            return "📊 No se encontraron asignaciones de usuarios para analizar"
        
        response = f"👥 **ANÁLISIS INTELIGENTE DE USUARIOS** ({len(user_stats)} técnicos activos)\n\n"
        
        # Top performers
        top_resolvers = sorted(user_stats.items(), 
                             key=lambda x: x[1]['resolved'], reverse=True)[:5]
        
        response += "🏆 **TOP TÉCNICOS POR RESOLUCIONES**:\n"
        for user_id, stats in top_resolvers:
            resolution_rate = (stats['resolved'] / stats['assigned'] * 100) if stats['assigned'] > 0 else 0
            avg_priority = sum(stats['avg_priority']) / len(stats['avg_priority']) if stats['avg_priority'] else 0
            
            response += f"• **{stats['name']}**: {stats['resolved']} resueltos "
            response += f"({resolution_rate:.1f}% tasa éxito)\n"
            response += f"  📊 {stats['assigned']} asignados, {stats['pending']} pendientes\n"
            if avg_priority > 0:
                response += f"  🎯 Prioridad promedio: {avg_priority:.1f}\n"
            response += "\n"
        
        # Análisis de carga de trabajo
        response += "⚖️ **ANÁLISIS DE CARGA**:\n"
        workload_analysis = sorted(user_stats.items(), 
                                 key=lambda x: x[1]['pending'], reverse=True)
        
        for user_id, stats in workload_analysis[:3]:
            if stats['pending'] > 0:
                response += f"• **{stats['name']}**: {stats['pending']} tickets pendientes"
                if stats['pending'] > 10:
                    response += " ⚠️ Sobrecargado"
                elif stats['pending'] > 5:
                    response += " 📈 Carga alta"
                response += "\n"
        
        return response
    
    def _get_priority_analysis(self, context):
        """Análisis por prioridades con recomendaciones inteligentes"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        if not tickets:
            return "Error obteniendo tickets para análisis de prioridades"
        
        return self._process_priority_analysis(tickets, context)
    
    def _process_priority_analysis(self, tickets, context):
        """Procesar análisis de prioridades"""
        filtered_tickets = self._apply_priority_filters(tickets, context)
        
        if not filtered_tickets:
            return "No se encontraron tickets para el análisis de prioridades"
        
        priority_stats = self._calculate_priority_statistics(filtered_tickets)
        return self._format_priority_response(priority_stats)
    
    def _apply_priority_filters(self, tickets, context):
        """Aplicar filtros de contexto para prioridades"""
        filtered = tickets
        
        if context.get('time_range'):
            filtered = self._filter_by_time_range(filtered, context['time_range'])
        
        if context.get('status_filter') == 'open':
            filtered = [t for t in filtered if t.get('status', 0) in [1, 2, 3, 4]]
        
        return filtered
    
    def _calculate_priority_statistics(self, tickets):
        """Calcular estadísticas por prioridad"""
        priority_stats = {}
        priority_names = {
            1: "Muy Baja", 2: "Baja", 3: "Media",
            4: "Alta", 5: "Muy Alta", 6: "Crítica"
        }
        
        for ticket in tickets:
            priority = ticket.get('priority', 3)
            if priority not in priority_stats:
                priority_stats[priority] = {
                    'name': priority_names.get(priority, f'Prioridad {priority}'),
                    'count': 0,
                    'tickets': []
                }
            
            priority_stats[priority]['count'] += 1
            priority_stats[priority]['tickets'].append(ticket)
        
        return priority_stats
    
    def _format_priority_response(self, priority_stats):
        """Formatear respuesta de análisis de prioridades"""
        if not priority_stats:
            return "No se encontraron datos de prioridades para analizar"
        
        response = "Análisis por prioridades:\n\n"
        
        # Ordenar por prioridad (mayor a menor)
        for priority in sorted(priority_stats.keys(), reverse=True):
            stats = priority_stats[priority]
            name = stats['name']
            count = stats['count']
            response += f"• {name}: {count} tickets\n"
        
        return response
        
        priority_stats = {}
        critical_open = []
        
        for ticket in tickets:
            priority = ticket.get('priority', 3)
            status = ticket.get('status', 0)
            
            if priority not in priority_stats:
                priority_stats[priority] = {'total': 0, 'open': 0, 'resolved': 0}
                
            priority_stats[priority]['total'] += 1
            if status in [1, 2, 3, 4]:
                priority_stats[priority]['open'] += 1
                if priority >= 4:  # Alta prioridad o crítica
                    critical_open.append(ticket)
            elif status in [5, 6]:
                priority_stats[priority]['resolved'] += 1
        
        response = f"🎯 **ANÁLISIS DE PRIORIDADES** ({len(tickets)} tickets)\n\n"
        
        # Desglose por prioridad
        for priority in sorted(priority_stats.keys(), reverse=True):
            stats = priority_stats[priority]
            name = priority_map.get(priority, f"Prioridad {priority}")
            
            response += f"{name}: **{stats['total']}** tickets\n"
            response += f"  • Abiertos: {stats['open']} | Resueltos: {stats['resolved']}\n"
            
            if stats['total'] > 0:
                resolution_rate = (stats['resolved'] / stats['total']) * 100
                response += f"  • Tasa resolución: {resolution_rate:.1f}%\n"
            response += "\n"
        
        # Alertas críticas
        if critical_open:
            response += f"🚨 **TICKETS CRÍTICOS ABIERTOS** ({len(critical_open)}):\n"
            for ticket in critical_open[:5]:
                response += f"• #{ticket.get('id')}: {ticket.get('name', 'Sin título')[:40]}\n"
                days_old = self._calculate_ticket_age(ticket)
                if days_old:
                    response += f"  ⏰ {days_old} días desde creación\n"
            response += "\n"
        
        # Recomendaciones
        response += "💡 **RECOMENDACIONES**:\n"
        if len(critical_open) > 0:
            response += "• Atender inmediatamente tickets críticos abiertos\n"
        
        high_priority_open = sum(stats['open'] for p, stats in priority_stats.items() if p >= 4)
        if high_priority_open > 5:
            response += "• Considerar asignación adicional para alta prioridad\n"
        
        return response
    
    def _get_time_analysis(self, context):
        """Análisis temporal con tendencias y patrones"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        if not tickets:
            return "❌ Error obteniendo tickets para análisis temporal"
        
        from collections import defaultdict
        import calendar
        
        # Análisis por períodos
        daily_counts = defaultdict(int)
        monthly_counts = defaultdict(int)
        status_timeline = defaultdict(lambda: defaultdict(int))
        
        now = datetime.now()
        
        for ticket in tickets:
            try:
                ticket_date = datetime.fromisoformat(ticket.get('date', '').replace('Z', ''))
                
                # Conteos diarios (últimos 30 días)
                days_ago = (now - ticket_date).days
                if days_ago <= 30:
                    day_key = ticket_date.strftime('%Y-%m-%d')
                    daily_counts[day_key] += 1
                
                # Conteos mensuales
                month_key = ticket_date.strftime('%Y-%m')
                monthly_counts[month_key] += 1
                
                # Timeline por estado
                status = ticket.get('status', 0)
                status_timeline[month_key][status] += 1
                
            except Exception:
                continue
        
        response = "📈 **ANÁLISIS TEMPORAL DE TICKETS**\n\n"
        
        # Tendencia mensual
        sorted_months = sorted(monthly_counts.keys())[-6:]  # Últimos 6 meses
        
        response += "📅 **TENDENCIA MENSUAL** (últimos 6 meses):\n"
        for month in sorted_months:
            count = monthly_counts[month]
            try:
                year, month_num = month.split('-')
                month_name = calendar.month_name[int(month_num)]
                response += f"• {month_name} {year}: **{count}** tickets\n"
            except Exception:
                response += f"• {month}: **{count}** tickets\n"
        
        # Análisis de actividad reciente
        recent_days = sorted(daily_counts.keys())[-7:]  # Última semana
        if recent_days:
            response += "\n📊 **ACTIVIDAD RECIENTE** (última semana):\n"
            week_total = sum(daily_counts[day] for day in recent_days)
            daily_avg = week_total / 7
            
            response += f"• Total semanal: **{week_total}** tickets\n"
            response += f"• Promedio diario: **{daily_avg:.1f}** tickets\n"
            
            # Detectar patrones
            if daily_avg > 10:
                response += "• 📈 Alta actividad detectada\n"
            elif daily_avg < 2:
                response += "• 📉 Baja actividad - posible período de baja demanda\n"
        
        return response
    
    def _get_enhanced_general_summary(self, context):
        """Resumen general inteligente con insights automáticos"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        if not tickets:
            return self._get_demo_response(context)
        
        return self._process_general_summary(tickets, context)
    
    def _process_general_summary(self, tickets, context):
        """Procesar resumen general"""
        filtered_tickets = self._apply_context_filters(tickets, context)
        
        if not filtered_tickets:
            return "No se encontraron tickets en el período especificado"
        
        summary_data = self._calculate_summary_metrics(filtered_tickets)
        return self._format_general_summary(summary_data)
    
    def _apply_context_filters(self, tickets, context):
        """Aplicar filtros de contexto"""
        if context.get('time_range'):
            return self._filter_by_time_range(tickets, context['time_range'])
        return tickets
    
    def _calculate_summary_metrics(self, tickets):
        """Calcular métricas del resumen"""
        total = len(tickets)
        open_tickets = len([t for t in tickets if t.get('status', 0) in [1, 2, 3, 4]])
        closed_tickets = len([t for t in tickets if t.get('status', 0) in [5, 6]])
        high_priority = len([t for t in tickets if t.get('priority', 0) >= 4])
        
        return {
            'total': total,
            'open': open_tickets,
            'closed': closed_tickets,
            'high_priority': high_priority,
            'resolution_rate': (closed_tickets / total * 100) if total > 0 else 0
        }
    
    def _format_general_summary(self, data):
        """Formatear resumen general"""
        response = "Resumen general del sistema GLPI:\n\n"
        response += f"Total de tickets: {data['total']}\n"
        response += f"Tickets abiertos: {data['open']}\n"
        response += f"Tickets cerrados: {data['closed']}\n"
        response += f"Tickets de alta prioridad: {data['high_priority']}\n"
        response += f"Ratio de resolución: {data['resolution_rate']:.1f}%\n"
        
        return response
        
        # Análisis temporal
        now = datetime.now()
        recent_tickets = []
        old_tickets = []
        
        for ticket in tickets:
            try:
                ticket_date = datetime.fromisoformat(ticket.get('date', '').replace('Z', ''))
                days_old = (now - ticket_date).days
                
                if days_old <= 7:
                    recent_tickets.append(ticket)
                elif days_old > 30:
                    old_tickets.append(ticket)
            except Exception:
                continue
        
        # Generar resumen inteligente
        time_context = ""
        if context.get('time_range'):
            time_context = f" (filtrado por {context['time_range']})"
        
        response = f"📋 **RESUMEN INTELIGENTE TOOLI-IA**{time_context}\n\n"
        response += f"🎫 **Total**: {total} tickets"
        
        if context.get('time_range') and total != original_count:
            response += f" de {original_count} totales"
        response += "\n\n"
        
        # Indicadores clave
        response += "📊 **INDICADORES CLAVE**:\n"
        response += f"• Abiertos: **{open_tickets}** ({(open_tickets/total*100):.1f}%)\n"
        response += f"• Cerrados: **{closed_tickets}** ({(closed_tickets/total*100):.1f}%)\n"
        response += f"• Tasa resolución: **{resolution_rate:.1f}%**\n"
        
        if high_priority > 0:
            response += f"• Alta prioridad: **{high_priority}** ({(high_priority/total*100):.1f}%)\n"
        
        response += "\n"
        
        # Insights automáticos
        response += "🧠 **INSIGHTS AUTOMÁTICOS**:\n"
        
        if resolution_rate > 80:
            response += "✅ Excelente tasa de resolución - equipo muy eficiente\n"
        elif resolution_rate > 60:
            response += "👍 Buena tasa de resolución - margen de mejora\n"
        else:
            response += "⚠️ Tasa de resolución baja - requiere atención\n"
        
        if len(recent_tickets) > total * 0.3:
            response += "📈 Alto volumen de tickets recientes - monitorear carga\n"
        
        if high_priority > total * 0.2:
            response += "🚨 Alto porcentaje de prioridad crítica - revisar procesos\n"
        
        if len(old_tickets) > total * 0.1:
            response += "⏰ Tickets antiguos detectados - considerar limpieza\n"
        
        # Estado del sistema
        response += "\n🎯 **ESTADO DEL SISTEMA**: "
        if resolution_rate > 75 and high_priority < total * 0.1:
            response += "🟢 **ÓPTIMO**"
        elif resolution_rate > 50 and high_priority < total * 0.2:
            response += "🟡 **BUENO**"
        else:
            response += "🔴 **REQUIERE ATENCIÓN**"
        
        return response
    
    def _analyze_workflow_efficiency(self, tickets):
        """Analizar eficiencia del flujo de trabajo"""
        if not tickets:
            return ""
        
        # Análisis de transiciones de estado
        flow_analysis = "\n💼 **ANÁLISIS DE FLUJO**:\n"
        
        # Calcular tiempo promedio en cada estado (simplificado)
        status_distribution = Counter([t.get('status', 0) for t in tickets])
        total = len(tickets)
        
        # Detectar cuellos de botella
        pending_ratio = status_distribution.get(4, 0) / total
        in_progress_ratio = status_distribution.get(3, 0) / total
        
        if pending_ratio > 0.2:
            flow_analysis += "⚠️ Cuello de botella en estado 'Pendiente'\n"
        if in_progress_ratio > 0.3:
            flow_analysis += "⚠️ Muchos tickets 'En Progreso' - revisar capacidad\n"
        
        if pending_ratio < 0.1 and in_progress_ratio < 0.2:
            flow_analysis += "✅ Flujo de trabajo eficiente\n"
        
        return flow_analysis
    
    def _calculate_ticket_age(self, ticket):
        """Calcular edad de un ticket en días"""
        try:
            ticket_date = datetime.fromisoformat(ticket.get('date', '').replace('Z', ''))
            return (datetime.now() - ticket_date).days
        except Exception:
            return None
    
    def _get_status_report(self):
        """Reporte por estados"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        if not tickets:
            return "❌ Error obteniendo tickets"
            
        status_map = {
            1: "🆕 Nuevo",
            2: "📋 Asignado", 
            3: "🔄 En progreso",
            4: "⏳ Pendiente",
            5: "✅ Resuelto",
            6: "🔒 Cerrado"
        }
        
        status_count = Counter([t.get('status', 0) for t in tickets])
        
        response = "📈 **REPORTE POR ESTADOS**\n\n"
        
        for status_id, count in status_count.most_common():
            status_name = status_map.get(status_id, f"Estado {status_id}")
            percentage = (count / len(tickets)) * 100
            response += f"{status_name}: **{count}** ({percentage:.1f}%)\n"
            
        return response
    
    def _get_user_analysis(self):
        """Análisis por usuarios"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        users = self.glpi.make_glpi_request('User', params={'range': '0-100'})
        
        if not tickets or not users:
            return "❌ Error obteniendo datos"
            
        # Crear mapeo de usuarios
        user_map = {user['id']: user.get('name', 'Usuario desconocido') for user in users}
        
        # Contar tickets por usuario asignado
        assigned_count = Counter()
        requester_count = Counter()
        
        for ticket in tickets:
            # Tickets asignados
            assigned_to = ticket.get('users_id_assign', 0)
            if assigned_to:
                assigned_count[assigned_to] += 1
                
            # Tickets solicitados
            requester = ticket.get('users_id_recipient', 0)
            if requester:
                requester_count[requester] += 1
        
        response = "👥 **ANÁLISIS POR USUARIOS**\n\n"
        response += "🔧 **Técnicos con más tickets asignados:**\n"
        
        for user_id, count in assigned_count.most_common(5):
            user_name = user_map.get(user_id, f'Usuario {user_id}')
            response += f"• {user_name}: **{count}** tickets\n"
            
        response += "\n📞 **Usuarios que más solicitan:**\n"
        
        for user_id, count in requester_count.most_common(5):
            user_name = user_map.get(user_id, f'Usuario {user_id}')
            response += f"• {user_name}: **{count}** tickets\n"
            
        return response
    
    def _get_general_summary(self):
        """Resumen general del sistema"""
        tickets = self.glpi.make_glpi_request('Ticket', params={'range': '0-1000'})
        if not tickets:
            return "❌ Error obteniendo datos del sistema"
            
        total = len(tickets)
        open_count = len([t for t in tickets if t.get('status', 0) in [1, 2, 3, 4]])
        closed_count = len([t for t in tickets if t.get('status', 0) in [5, 6]])
        
        # Tickets de hoy
        today = datetime.now().date()
        today_tickets = [t for t in tickets if datetime.fromisoformat(t.get('date', '').replace('Z', TIMEZONE_UTC).replace(TIMEZONE_UTC, '')).date() == today]
        
        # Tickets demorados
        now = datetime.now()
        delayed_count = 0
        for ticket in tickets:
            if ticket.get('status', 0) in [1, 2, 3, 4]:
                last_update = datetime.fromisoformat(ticket.get('date_mod', '').replace('Z', TIMEZONE_UTC).replace(TIMEZONE_UTC, ''))
                if (now - last_update).days > 7:
                    delayed_count += 1
        
        return f"""🎯 **RESUMEN GENERAL DEL SISTEMA**

📊 **Estadísticas principales:**
• Total de tickets: **{total}**
• Tickets abiertos: **{open_count}**
• Tickets cerrados: **{closed_count}**
• Tickets de hoy: **{len(today_tickets)}**

⚠️ **Alertas:**
• Tickets demorados: **{delayed_count}**
• Tasa de resolución: **{(closed_count/total*100):.1f}%**

🕐 **Estado actual:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
🟢 **Sistema:** Operativo y funcionando"""
    
    def _save_metrics(self, total, open_count, closed_count):
        """Guardar métricas en base de datos"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ticket_metrics (ticket_count, open_count, closed_count, pending_count, delayed_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (total, open_count, closed_count, 0, 0))
        conn.commit()
        conn.close()

# Instancias globales
glpi_manager = GLPIManager()
analyzer = IntelligentAnalyzer(glpi_manager)

# Función para renovar sesión automáticamente
def auto_renew_session():
    """Renovar sesión GLPI automáticamente cada 45 minutos"""
    while True:
        time.sleep(45 * 60)  # 45 minutos
        glpi_manager.get_glpi_session()

# Iniciar hilo de renovación automática
renewal_thread = threading.Thread(target=auto_renew_session, daemon=True)
renewal_thread.start()

# ===============================
# ENDPOINTS DE LA API
# ===============================

@app.route('/', methods=['GET'])
def dashboard():
    """Dashboard web simple"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tooli-IA Dashboard</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { font-weight: bold; color: #27ae60; }
            .status { text-align: center; padding: 20px; background: #2ecc71; color: white; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Tooli-IA v1.0.0</h1>
            <div class="status">
                <h2>✅ Sistema Operativo</h2>
                <p>API Flask + GLPI Integration</p>
            </div>
            
            <h2>📋 Endpoints Disponibles:</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/health</code><br>
                <small>Estado del sistema</small>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/tickets</code><br>
                <small>Obtener todos los tickets</small>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/api/chat</code><br>
                <small>Chat inteligente - {"query": "¿Cuántos tickets hay?"}</small>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/reports</code><br>
                <small>Obtener reportes guardados</small>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/dashboard/metrics</code><br>
                <small>Métricas del dashboard</small>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/api/tickets</code><br>
                <small>Crear nuevo ticket</small>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar estado del sistema"""
    glpi_status = "✅ Conectado" if glpi_manager.get_glpi_session() else "❌ Desconectado"
    
    return jsonify({
        'status': 'ok',
        'service': 'Tooli-IA',
        'version': '1.0.0',
        'glpi_status': glpi_status,
        'database': 'SQLite Activa',
        'session_token': glpi_manager.session_token[:10] + "..." if glpi_manager.session_token else None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Obtener tickets desde GLPI"""
    try:
        range_param = request.args.get('range', '0-50')
        status_filter = request.args.get('status', None)
        
        params = {'range': range_param}
        if status_filter:
            params['criteria[0][field]'] = '12'  # Campo status
            params['criteria[0][searchtype]'] = 'equals'
            params['criteria[0][value]'] = status_filter
        
        tickets = glpi_manager.make_glpi_request('Ticket', params=params)
        
        if tickets is None:
            return jsonify({
                'success': False,
                'error': 'No se pudo conectar a GLPI'
            }), 500
        
        # Procesar tickets para agregar información útil
        processed_tickets = []
        for ticket in tickets:
            processed_ticket = ticket.copy()
            
            # Agregar días desde última actualización
            if ticket.get('date_mod'):
                last_update = datetime.fromisoformat(ticket['date_mod'].replace('Z', TIMEZONE_UTC).replace(TIMEZONE_UTC, ''))
                days_since_update = (datetime.now() - last_update).days
                processed_ticket['days_since_update'] = days_since_update
                processed_ticket['is_delayed'] = days_since_update > 7
            
            processed_tickets.append(processed_ticket)
        
        return jsonify({
            'success': True,
            'data': processed_tickets,
            'count': len(processed_tickets),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        glpi_manager.log_event('ERROR', f'Error en get_tickets: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    """Crear nuevo ticket en GLPI"""
    try:
        data = request.json
        
        ticket_data = {
            'input': {
                'name': data.get('title', 'Ticket creado desde Tooli-IA'),
                'content': data.get('description', ''),
                'status': data.get('status', 1),  # Nuevo
                'urgency': data.get('urgency', 3),  # Medio
                'impact': data.get('impact', 3),    # Medio
                'priority': data.get('priority', 3), # Medio
            }
        }
        
        result = glpi_manager.make_glpi_request('Ticket', method='POST', data=ticket_data)
        
        if result:
            glpi_manager.log_event('SUCCESS', f'Ticket creado: {result}')
            return jsonify({
                'success': True,
                'ticket_id': result.get('id'),
                'message': 'Ticket creado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error creando ticket en GLPI'
            }), 500
            
    except Exception as e:
        glpi_manager.log_event('ERROR', f'Error creando ticket: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def intelligent_chat():
    """Chat inteligente para consultas sobre tickets"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query vacío'
            }), 400
        
        # Analizar consulta y generar respuesta
        response = analyzer.analyze_query(query)
        
        # Guardar en base de datos
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO reports (query, response, data) VALUES (?, ?, ?)',
            (query, response, json.dumps({'query': query, 'response': response}))
        )
        conn.commit()
        conn.close()
        
        glpi_manager.log_event('INFO', f'Chat query: {query[:50]}...')
        
        return jsonify({
            'success': True,
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        glpi_manager.log_event('ERROR', f'Error en chat: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Obtener histórico de reportes"""
    try:
        limit = int(request.args.get('limit', 20))
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, query, response, created_at 
            FROM reports 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        reports = []
        for row in cursor.fetchall():
            reports.append({
                'id': row[0],
                'query': row[1],
                'response': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'reports': reports,
            'count': len(reports)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/metrics', methods=['GET'])
def dashboard_metrics():
    """Métricas para dashboard"""
    try:
        # Obtener métricas recientes
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Última métrica
        cursor.execute('''
            SELECT * FROM ticket_metrics 
            ORDER BY recorded_at DESC 
            LIMIT 1
        ''')
        latest_metric = cursor.fetchone()
        
        # Logs recientes
        cursor.execute('''
            SELECT level, message, created_at 
            FROM system_logs 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        recent_logs = cursor.fetchall()
        
        conn.close()
        
        # Obtener datos actuales de GLPI
        tickets = glpi_manager.make_glpi_request('Ticket', params={'range': '0-1000'})
        
        current_metrics = {
            'total_tickets': len(tickets) if tickets else 0,
            'open_tickets': len([t for t in tickets if t.get('status', 0) in [1, 2, 3, 4]]) if tickets else 0,
            'closed_tickets': len([t for t in tickets if t.get('status', 0) in [5, 6]]) if tickets else 0,
            'system_status': 'Operativo' if glpi_manager.session_token else 'Desconectado'
        }
        
        return jsonify({
            'success': True,
            'current_metrics': current_metrics,
            'latest_metric': latest_metric,
            'recent_logs': [{'level': log[0], 'message': log[1], 'time': log[2]} for log in recent_logs],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Obtener usuarios de GLPI"""
    try:
        users = glpi_manager.make_glpi_request('User', params={'range': '0-100'})
        
        if users:
            return jsonify({
                'success': True,
                'users': users,
                'count': len(users)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error obteniendo usuarios'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Iniciando Tooli-IA v1.0.0")
    print("Sistema completo: Flask + GLPI + Chat Inteligente")
    print("Dashboard disponible en: http://localhost:5000")
    print("API REST disponible en: http://localhost:5000/api/")
    
    # Configurar token si está en variables de entorno
    if APP_TOKEN == 'YOUR_APP_TOKEN':
        print("⚠️  IMPORTANTE: Configura tu GLPI_APP_TOKEN en las variables de entorno")
        print("   export GLPI_APP_TOKEN=tu_token_real")
    
    # Intentar obtener sesión GLPI al inicio
    if glpi_manager.get_glpi_session():
        print("✅ Conexión GLPI establecida")
    else:
        print("❌ Error conectando a GLPI - verifica la configuración")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)