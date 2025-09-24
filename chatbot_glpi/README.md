# Tooli-IA Chatbot

## Descripción

Tooli-IA es un chatbot inteligente desarrollado con Flutter para la interfaz de usuario y Flask con NLP para el backend. Está diseñado para integrarse con sistemas GLPI y proporcionar asistencia automatizada mediante inteligencia artificial.

## Arquitectura

### Backend (Flask + NLP)
- **Ubicación**: `../agent/tooli-core.py`
- **Puerto**: 5000
- **Características**:
  - API REST con 8 endpoints
  - Integración con GLPI usando token de API
  - Inteligencia artificial con NLTK, TextBlob y scikit-learn
  - Base de datos SQLite para gestión de datos
  - Análisis de confianza en respuestas

### Frontend (Flutter)
- **Tecnologías**:
  - Flutter con Material Design 3
  - Provider para gestión de estado
  - HTTP client para comunicación con API
  - Interfaz de chat responsiva y moderna

## Instalación y Configuración

### Backend
1. Instalar dependencias de Python:
   ```bash
   pip install flask requests sqlite3 nltk textblob scikit-learn
   ```

2. Ejecutar el servidor Flask:
   ```bash
   python ../agent/tooli-core.py
   ```

### Frontend
1. Instalar dependencias de Flutter:
   ```bash
   flutter pub get
   ```

2. Ejecutar la aplicación:
   ```bash
   flutter run -d chrome
   ```

## Uso

1. Asegúrate de que el backend Flask esté ejecutándose en `http://localhost:5000`
2. Abre la aplicación Flutter en el navegador
3. El indicador de conexión mostrará el estado (Online/Offline)
4. Escribe consultas en el chat para interactuar con el asistente IA
5. Las respuestas incluyen indicadores de confianza del análisis NLP

## Características Principales

- **Interfaz de chat moderna** con Material Design 3
- **Indicador de estado de conexión** en tiempo real
- **Mensajes con timestamp** y avatares personalizados
- **Indicadores de confianza** en las respuestas de la IA
- **Botones de acción rápida** para consultas comunes
- **Scroll automático** y manejo de estados de carga
- **Integración completa** con backend de inteligencia artificial

## Configuración GLPI

El sistema utiliza el token GLPI configurado en el backend para la integración con el sistema de tickets.

## Tecnologías Utilizadas

- **Frontend**: Flutter, Dart, Material Design 3, Provider
- **Backend**: Python, Flask, NLTK, TextBlob, scikit-learn
- **Base de Datos**: SQLite
- **API**: REST con integración GLPI
- **Inteligencia Artificial**: NLP con análisis de sentimientos y confianza
