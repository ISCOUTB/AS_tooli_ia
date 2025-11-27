"""
Configuración y modelos de datos para la aplicación
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Servidor
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Groq AI
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", env="GROQ_MODEL")
    
    # GLPI
    glpi_url: Optional[str] = Field(default=None, env="GLPI_URL")
    glpi_app_token: Optional[str] = Field(default=None, env="GLPI_APP_TOKEN")
    glpi_user_token: Optional[str] = Field(default=None, env="GLPI_USER_TOKEN")
    
    # Database (MariaDB/MySQL)
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=3306, env="DB_PORT")
    db_user: str = Field(default="root", env="DB_USER")
    db_password: str = Field(default="", env="DB_PASSWORD")
    db_name: str = Field(default="glpi_sso", env="DB_NAME")
    
    # SSO Configuration (Microsoft Entra ID / Azure AD)
    sso_client_id: Optional[str] = Field(default=None, env="SSO_CLIENT_ID")
    sso_client_secret: Optional[str] = Field(default=None, env="SSO_CLIENT_SECRET")
    sso_tenant_id: Optional[str] = Field(default=None, env="SSO_TENANT_ID")
    sso_redirect_uri: str = Field(
        default="https://apps.unitecnologica.edu.co/tooli_ia/api/v1/sso/callback",
        env="SSO_REDIRECT_URI"
    )
    
    # Security (JWT)
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY",
        description="Secret key for JWT token generation. MUST be changed in production!"
    )
    
    # Agente
    max_tokens: int = Field(default=1500, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuración
settings = Settings()
