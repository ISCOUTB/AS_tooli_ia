"""
SSO Service - OAuth2/OpenID Connect Implementation
Handles institutional SSO with domain validation (@unitecnologica.edu.co)
"""
import secrets
import hashlib
import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import httpx
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from auth.sso_models import SSOProvider, SSOConnection, SSOAuditLog
from auth.models import User
from auth import jwt_auth
import logging

logger = logging.getLogger(__name__)


class SSOService:
    """
    Single Sign-On Service
    Implements OAuth2/OpenID Connect flow with institutional domain validation
    """
    
    # Domain whitelist (institutional requirement)
    REQUIRED_DOMAIN = "unitecnologica.edu.co"
    ALLOWED_DOMAINS = ["unitecnologica.edu.co"]
    
    @staticmethod
    def validate_email_domain(email: str) -> bool:
        """
        Validate that email belongs to allowed institutional domain
        CRITICAL: Enforces @unitecnologica.edu.co requirement
        """
        if not email or '@' not in email:
            return False
        
        domain = email.split('@')[1].lower()
        is_valid = domain in SSOService.ALLOWED_DOMAINS
        
        logger.info(f"📧 Domain validation for {email}: {'✅ VALID' if is_valid else '❌ INVALID'}")
        return is_valid
    
    @staticmethod
    def generate_state() -> str:
        """Generate secure random state parameter for OAuth2"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_code_verifier() -> str:
        """Generate PKCE code verifier"""
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def generate_code_challenge(verifier: str) -> str:
        """Generate PKCE code challenge from verifier"""
        digest = hashlib.sha256(verifier.encode()).digest()
        import base64
        return base64.urlsafe_b64encode(digest).decode().rstrip('=')
    
    @staticmethod
    async def get_provider(db: Session, provider_name: str) -> Optional[SSOProvider]:
        """Get active SSO provider by name"""
        return db.query(SSOProvider).filter(
            SSOProvider.name == provider_name,
            SSOProvider.is_active == True
        ).first()
    
    @staticmethod
    def get_authorization_url(
        provider: SSOProvider,
        state: str,
        code_verifier: Optional[str] = None
    ) -> str:
        """
        Generate OAuth2 authorization URL
        
        Args:
            provider: SSO provider configuration
            state: CSRF protection state parameter
            code_verifier: Optional PKCE code verifier
        
        Returns:
            Authorization URL to redirect user
        """
        params = {
            'client_id': provider.client_id,
            'response_type': 'code',
            'redirect_uri': provider.redirect_uri,
            'scope': ' '.join(provider.scopes),
            'state': state,
        }
        
        # Add tenant if Microsoft/Azure AD
        if provider.tenant_id:
            # For Azure AD, authorization URL includes tenant
            auth_url = provider.authorization_url.replace('{tenant}', provider.tenant_id)
        else:
            auth_url = provider.authorization_url
        
        # Add PKCE challenge if provided
        if code_verifier:
            code_challenge = SSOService.generate_code_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        url = f"{auth_url}?{urlencode(params)}"
        logger.info(f"🔗 Generated authorization URL for {provider.name}")
        return url
    
    @staticmethod
    async def exchange_code_for_token(
        provider: SSOProvider,
        code: str,
        code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            provider: SSO provider configuration
            code: Authorization code from callback
            code_verifier: Optional PKCE code verifier
        
        Returns:
            Token response with access_token, id_token, etc.
        """
        token_url = provider.token_url
        if provider.tenant_id:
            token_url = token_url.replace('{tenant}', provider.tenant_id)
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': provider.client_id,
            'client_secret': provider.client_secret,
            'code': code,
            'redirect_uri': provider.redirect_uri,
        }
        
        # Add PKCE verifier if used
        if code_verifier:
            data['code_verifier'] = code_verifier
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    token_url,
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                response.raise_for_status()
                tokens = response.json()
                
            logger.info(f"✅ Successfully exchanged code for tokens from {provider.name}")
            return tokens
            
        except httpx.HTTPError as e:
            logger.error(f"❌ Token exchange failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code: {str(e)}"
            )
    
    @staticmethod
    def decode_id_token(id_token: str) -> Dict[str, Any]:
        """
        Decode JWT ID token (without verification for now)
        In production, you should verify signature with provider's public key
        """
        import base64
        
        try:
            # JWT format: header.payload.signature
            parts = id_token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")
            
            # Decode payload (add padding if needed)
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            
            claims = json.loads(decoded)
            return claims
            
        except Exception as e:
            logger.error(f"❌ Failed to decode ID token: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID token"
            )
    
    @staticmethod
    async def get_user_info(provider: SSOProvider, access_token: str) -> Dict[str, Any]:
        """
        Fetch user information from provider's UserInfo endpoint
        """
        if not provider.userinfo_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider does not support UserInfo endpoint"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    provider.userinfo_url,
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                response.raise_for_status()
                user_info = response.json()
                
            logger.info(f"✅ Retrieved user info from {provider.name}")
            return user_info
            
        except httpx.HTTPError as e:
            logger.error(f"❌ UserInfo request failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user information"
            )
    
    @staticmethod
    async def process_sso_login(
        db: Session,
        provider: SSOProvider,
        tokens: Dict[str, Any],
        ip_address: str = "unknown",
        user_agent: str = "unknown"
    ) -> Tuple[User, Dict[str, Any]]:
        """
        Process SSO login and create/update user
        
        Args:
            db: Database session
            provider: SSO provider
            tokens: OAuth2 tokens from provider
            ip_address: Client IP
            user_agent: Client user agent
        
        Returns:
            Tuple of (User, JWT tokens)
        """
        try:
            # Extract user info from ID token or UserInfo endpoint
            if 'id_token' in tokens:
                claims = SSOService.decode_id_token(tokens['id_token'])
            else:
                claims = await SSOService.get_user_info(provider, tokens['access_token'])
            
            # Extract required fields
            provider_user_id = claims.get('sub')
            email = claims.get('email')
            name = claims.get('name', email.split('@')[0] if email else 'User')
            
            if not provider_user_id or not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing required user information from provider"
                )
            
            # CRITICAL: Validate email domain
            logger.info(f"🔍 SSO Callback - Email recibido: {email}, enforce_domain={provider.enforce_domain}")
            if provider.enforce_domain and not SSOService.validate_email_domain(email):
                logger.warning(f"❌ Domain validation failed for email: {email}")
                
                # Log failed attempt
                audit_log = SSOAuditLog(
                    provider_id=provider.id,
                    event_type="login",
                    event_status="failure",
                    error_code="DOMAIN_NOT_ALLOWED",
                    error_message=f"Email domain not allowed. Required: @{SSOService.REQUIRED_DOMAIN}",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    event_metadata={'email': email}
                )
                db.add(audit_log)
                db.commit()
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Solo se permiten cuentas con dominio @{SSOService.REQUIRED_DOMAIN}"
                )
            logger.info(f"✅ Validación de dominio pasada para: {email}")
            
            # Check if SSO connection exists
            sso_connection = db.query(SSOConnection).filter(
                SSOConnection.provider_id == provider.id,
                SSOConnection.provider_user_id == provider_user_id
            ).first()
            
            logger.info(f"🔍 Buscando conexión SSO existente para provider_user_id={provider_user_id}")
            if sso_connection:
                logger.info(f"✅ Usuario SSO existente encontrado: user_id={sso_connection.user_id}")
                # Existing user - update connection
                user = db.query(User).filter(User.id == sso_connection.user_id).first()
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                
                # Update SSO connection
                sso_connection.last_login = datetime.now(timezone.utc)
                sso_connection.login_count += 1
                sso_connection.access_token = tokens.get('access_token')
                sso_connection.refresh_token = tokens.get('refresh_token')
                
                if 'expires_in' in tokens:
                    sso_connection.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=tokens['expires_in'])
                
                logger.info(f"✅ Existing SSO user logged in: {user.username}")
                
            else:
                # New user - create account and SSO connection
                username = email.split('@')[0]  # Use email prefix as username
                
                # Check if username exists, add number if needed
                base_username = username
                counter = 1
                while db.query(User).filter(User.username == username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                logger.info(f"🆕 Usuario SSO nuevo - Creando usuario: username={username}, email={email}")
                # Create user with random password (SSO users don't need password)
                random_password = secrets.token_urlsafe(32)
                user = jwt_auth.create_user(
                    db=db,
                    username=username,
                    email=email,
                    password=random_password,
                    full_name=name
                )
                logger.info(f"✅ Usuario creado con ID={user.id}")
                
                # Create SSO connection
                sso_connection = SSOConnection(
                    user_id=user.id,
                    provider_id=provider.id,
                    provider_user_id=provider_user_id,
                    provider_email=email,
                    provider_name=name,
                    access_token=tokens.get('access_token'),
                    refresh_token=tokens.get('refresh_token'),
                    claims=claims
                )
                
                if 'expires_in' in tokens:
                    sso_connection.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=tokens['expires_in'])
                
                db.add(sso_connection)
                logger.info(f"✅ New SSO user registered: {user.username}")
            
            # Update user last login
            user.last_login = datetime.now(timezone.utc)
            
            # Generate JWT tokens for our system
            jwt_tokens = jwt_auth.create_tokens(db=db, user=user, ip_address=ip_address, user_agent=user_agent)
            
            # Log successful SSO login
            audit_log = SSOAuditLog(
                provider_id=provider.id,
                user_id=user.id,
                event_type="login",
                event_status="success",
                ip_address=ip_address,
                user_agent=user_agent,
                event_metadata={'email': email, 'provider_user_id': provider_user_id}
            )
            db.add(audit_log)
            
            db.commit()
            db.refresh(user)
            
            return user, jwt_tokens
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ SSO login processing failed: {e}")
            db.rollback()
            
            # Log error
            audit_log = SSOAuditLog(
                provider_id=provider.id,
                event_type="login",
                event_status="failure",
                error_code="PROCESSING_ERROR",
                error_message=str(e),
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(audit_log)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SSO login processing failed"
            )
