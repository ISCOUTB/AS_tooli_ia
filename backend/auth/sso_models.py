"""
SSO (Single Sign-On) Models for OAuth2/OpenID Connect
Compatible with institutional requirements (@unitecnologica.edu.co domain)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from auth.database import Base


class SSOProvider(Base):
    """
    SSO Provider Configuration
    Stores OAuth2/OpenID Connect provider settings
    """
    __tablename__ = "sso_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "AS_espacios_UTB"
    provider_type = Column(String(50), nullable=False)  # oauth2, openid_connect, saml2
    
    # OAuth2/OpenID Connect Configuration
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(255), nullable=False)
    tenant_id = Column(String(255), nullable=True)  # For Azure AD / Microsoft
    
    # URLs
    authorization_url = Column(Text, nullable=False)  # Authorization endpoint
    token_url = Column(Text, nullable=False)  # Token endpoint
    userinfo_url = Column(Text, nullable=True)  # UserInfo endpoint (OpenID Connect)
    redirect_uri = Column(Text, nullable=False)  # Callback URL
    
    # Scopes and Configuration
    scopes = Column(JSON, nullable=False, default=["openid", "profile", "email"])
    
    # Domain Restriction (CRITICAL for institutional SSO)
    allowed_domains = Column(JSON, nullable=False, default=["unitecnologica.edu.co"])
    enforce_domain = Column(Boolean, default=True)  # Enforce domain restriction
    
    # Application Type
    app_type = Column(String(50), default="web")  # web, mobile, spa
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SSOProvider(name='{self.name}', type='{self.provider_type}')>"


class SSOConnection(Base):
    """
    User SSO Connections
    Links local users with SSO provider identities
    """
    __tablename__ = "sso_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # References users.id
    provider_id = Column(Integer, nullable=False, index=True)  # References sso_providers.id
    
    # SSO Provider Identity
    provider_user_id = Column(String(255), nullable=False, index=True)  # Sub claim from provider
    provider_email = Column(String(255), nullable=False, index=True)
    provider_name = Column(String(255), nullable=True)
    
    # OAuth2 Tokens (optional, for calling provider APIs)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional Claims
    claims = Column(JSON, nullable=True)  # Store additional OIDC claims
    
    # Metadata
    first_login = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    login_count = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<SSOConnection(user_id={self.user_id}, provider_id={self.provider_id})>"


class SSOAuditLog(Base):
    """
    SSO Audit Log
    Tracks all SSO authentication attempts and events
    """
    __tablename__ = "sso_audit_log"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, nullable=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    
    # Event Details
    event_type = Column(String(50), nullable=False, index=True)  # login, register, error, etc.
    event_status = Column(String(20), nullable=False)  # success, failure
    
    # Request Info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Error Details (if applicable)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Additional Data
    event_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<SSOAuditLog(type='{self.event_type}', status='{self.event_status}')>"
