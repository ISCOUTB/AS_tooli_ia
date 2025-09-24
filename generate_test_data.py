#!/usr/bin/env python3
"""
Script para generar datos de prueba en GLPI
Crea usuarios, tickets y datos realistas para probar Tooli-IA
"""

import requests
import json
import random
from datetime import datetime, timedelta

# Configuración
GLPI_BASE_URL = "http://localhost:8200"
APP_TOKEN = "uKBD25fpF696ZPpRdN3NSodffEEoH0e6arEs5yVy"  # Token configurado

class GLPITestDataGenerator:
    def __init__(self):
        self.session_token = None
        self.get_session()
        
    def get_session(self):
        """Obtener sesión GLPI"""
        try:
            response = requests.post(
                f"{GLPI_BASE_URL}/apirest.php/initSession",
                headers={
                    'Content-Type': 'application/json',
                    'App-Token': APP_TOKEN
                }
            )
            if response.status_code == 200:
                self.session_token = response.json().get('session_token')
                print(f"✅ Sesión GLPI obtenida: {self.session_token[:10]}...")
                return True
            else:
                print(f"❌ Error obteniendo sesión: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def make_request(self, endpoint, method='GET', data=None):
        """Hacer petición a GLPI"""
        url = f"{GLPI_BASE_URL}/apirest.php/{endpoint}"
        headers = {
            'App-Token': APP_TOKEN,
            'Session-Token': self.session_token,
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'GET':
                response = requests.get(url, headers=headers)
                
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                print(f"❌ Error en {method} {endpoint}: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error en petición: {e}")
            return None
    
    def create_test_users(self):
        """Crear usuarios de prueba"""
        print("\n👥 Creando usuarios de prueba...")
        
        test_users = [
            {'name': 'Ana García', 'login': 'ana.garcia', 'email': 'ana.garcia@empresa.com'},
            {'name': 'Carlos López', 'login': 'carlos.lopez', 'email': 'carlos.lopez@empresa.com'},
            {'name': 'María Rodríguez', 'login': 'maria.rodriguez', 'email': 'maria.rodriguez@empresa.com'},
            {'name': 'Juan Pérez', 'login': 'juan.perez', 'email': 'juan.perez@empresa.com'},
            {'name': 'Laura Martín', 'login': 'laura.martin', 'email': 'laura.martin@empresa.com'},
        ]
        
        created_users = []
        
        for user_data in test_users:
            user_payload = {
                'input': {
                    'name': user_data['name'],
                    'login': user_data['login'],
                    'password': 'test123',
                    'password2': 'test123',
                    '_useremails': [user_data['email']],
                    'is_active': 1
                }
            }
            
            result = self.make_request('User', method='POST', data=user_payload)
            if result:
                created_users.append(result)
                print(f"✅ Usuario creado: {user_data['name']} (ID: {result.get('id')})")
            else:
                print(f"❌ Error creando usuario: {user_data['name']}")
        
        return created_users
    
    def create_test_tickets(self):
        """Crear tickets de prueba realistas"""
        print("\n🎫 Creando tickets de prueba...")
        
        # Títulos realistas de tickets
        ticket_titles = [
            "Problema con acceso al sistema de email",
            "Solicitud de nueva cuenta de usuario",
            "Error en aplicación de nómina",
            "Computadora no enciende en oficina 203",
            "Solicitud de instalación de software",
            "Impresora HP LaserJet no funciona",
            "Cambio de contraseña de usuario",
            "Error 404 en página web corporativa",
            "Solicitud de permisos especiales",
            "Virus detectado en equipo de contabilidad",
            "Backup de servidor falló anoche",
            "WiFi intermitente en sala de juntas",
            "Solicitud de aumento de espacio en disco",
            "Aplicación CRM se cierra inesperadamente",
            "Configuración de nuevo empleado",
            "Problema con VPN desde casa",
            "Solicitud de licencia adicional de Office",
            "Error en sistema de punto de venta",
            "Actualización de antivirus urgente",
            "Problema con proyector sala de conferencias"
        ]
        
        # Descripciones correspondientes
        ticket_descriptions = [
            "El usuario no puede acceder a su bandeja de entrada desde ayer por la tarde.",
            "Nuevo empleado requiere acceso al sistema principal y aplicaciones.",
            "La aplicación de nómina muestra error al generar reportes mensuales.",
            "El equipo de escritorio no responde, led de power no enciende.",
            "Solicitar instalación de AutoCAD 2024 para el departamento de diseño.",
            "La impresora muestra error 'Toner Low' pero el toner está lleno.",
            "Usuario olvidó su contraseña y necesita restablecerla urgentemente.",
            "Los clientes reportan error 404 al acceder a la sección de productos.",
            "Solicitar permisos de administrador para instalar software especializado.",
            "Antivirus detectó malware en el equipo, requiere limpieza inmediata.",
            "El backup programado falló, verificar configuración del servidor.",
            "Conexión WiFi se pierde constantemente durante reuniones importantes.",
            "El servidor de archivos está al 95% de capacidad, ampliar almacenamiento.",
            "El CRM se cierra sin guardar cambios, pérdida de información de clientes.",
            "Configurar email, accesos y herramientas para nuevo empleado del área comercial.",
            "No se puede establecer conexión VPN desde ubicación remota.",
            "Requerimos 5 licencias adicionales de Office para nuevos empleados.",
            "El sistema POS no procesa pagos con tarjeta desde esta mañana.",
            "Actualizar antivirus en todos los equipos, detectada nueva amenaza.",
            "El proyector no se conecta con laptops, verificar cables y configuración."
        ]
        
        created_tickets = []
        
        for i in range(len(ticket_titles)):
            # Estados: 1=Nuevo, 2=Asignado, 3=En progreso, 4=Pendiente, 5=Resuelto, 6=Cerrado
            status = random.choices([1, 2, 3, 4, 5, 6], weights=[20, 25, 20, 15, 15, 5])[0]
            
            # Urgencia e impacto aleatorios pero realistas
            urgency = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 50, 25, 5])[0]
            impact = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 50, 25, 5])[0]
            
            # Fecha aleatoria en los últimos 30 días
            days_ago = random.randint(0, 30)
            created_date = datetime.now() - timedelta(days=days_ago)
            
            ticket_data = {
                'input': {
                    'name': ticket_titles[i],
                    'content': ticket_descriptions[i],
                    'status': status,
                    'urgency': urgency,
                    'impact': impact,
                    'priority': min(urgency, impact),  # Prioridad basada en urgencia e impacto
                    'type': random.choice([1, 2]),  # 1=Incidente, 2=Solicitud
                    'category': random.randint(1, 10),
                    'date': created_date.isoformat(),
                }
            }
            
            result = self.make_request('Ticket', method='POST', data=ticket_data)
            if result:
                created_tickets.append(result)
                status_names = {1: "Nuevo", 2: "Asignado", 3: "En progreso", 4: "Pendiente", 5: "Resuelto", 6: "Cerrado"}
                print(f"✅ Ticket #{result.get('id')}: {ticket_titles[i][:30]}... - {status_names.get(status, 'Desconocido')}")
            else:
                print(f"❌ Error creando ticket: {ticket_titles[i]}")
        
        return created_tickets
    
    def generate_all_test_data(self):
        """Generar todos los datos de prueba"""
        print("🚀 Iniciando generación de datos de prueba para GLPI...")
        
        if not self.session_token:
            print("❌ No se pudo obtener sesión GLPI")
            return False
        
        # Crear usuarios
        users = self.create_test_users()
        
        # Crear tickets
        tickets = self.create_test_tickets()
        
        print(f"\n🎉 Datos de prueba generados exitosamente:")
        print(f"   👥 Usuarios creados: {len(users)}")
        print(f"   🎫 Tickets creados: {len(tickets)}")
        print(f"\n✅ Ya puedes probar Tooli-IA con datos realistas!")
        
        return True

def main():
    print("🔧 Generador de Datos de Prueba para GLPI")
    print("=" * 50)
    
    # Verificar configuración
    if APP_TOKEN == "YOUR_APP_TOKEN":
        print("❌ ERROR: Debes configurar tu APP_TOKEN real")
        print("   1. Ve a GLPI: http://localhost:8200")
        print("   2. Setup > General > API REST > Activar")
        print("   3. Tu perfil > API tokens > Crear nuevo")
        print("   4. Reemplaza YOUR_APP_TOKEN en este script")
        return
    
    # Generar datos
    generator = GLPITestDataGenerator()
    generator.generate_all_test_data()

if __name__ == "__main__":
    main()