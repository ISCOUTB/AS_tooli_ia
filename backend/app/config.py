import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret')
    N8N_WEBHOOK_URL_CHAT = os.getenv('N8N_WEBHOOK_URL_CHAT', 'http://20.151.72.161:5678/webhook/ai-chat-test-v2')
    N8N_WEBHOOK_URL_GLPI = os.getenv('N8N_WEBHOOK_URL_GLPI', 'http://localhost:5678/webhook/tooli-glpi')
    N8N_TIMEOUT = int(os.getenv('N8N_TIMEOUT', 15))
    API_PORT = int(os.getenv('API_PORT', 5000))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')