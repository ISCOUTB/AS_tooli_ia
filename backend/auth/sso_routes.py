"""
SSO Authentication Routes
OAuth2/OpenID Connect endpoints for institutional Single Sign-On
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
import secrets

from auth.database import get_db
from auth.sso_service import SSOService
from auth.sso_models import SSOProvider
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sso", tags=["SSO Authentication"])


# =====================================================
# Request/Response Models
# =====================================================

class SSOProviderInfo(BaseModel):
    """SSO Provider Information"""
    name: str
    provider_type: str
    app_type: str
    redirect_uri: str
    required_domain: str
    is_active: bool


class SSOInitiateResponse(BaseModel):
    """SSO Login Initiation Response"""
    authorization_url: str
    state: str
    provider: str


class SSOCallbackResponse(BaseModel):
    """SSO Callback Response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


# =====================================================
# Session Storage for OAuth2 State (In-Memory)
# In production, use Redis or database
# =====================================================

oauth_states = {}  # {state: {provider, code_verifier, created_at}}


def store_oauth_state(state: str, provider_name: str, code_verifier: Optional[str] = None):
    """Store OAuth2 state for CSRF protection"""
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    oauth_states[state] = {
        'provider': provider_name,
        'code_verifier': code_verifier,
        'created_at': now,
        'expires_at': now + timedelta(minutes=10)
    }
    
    # Clean old states
    expired_states = [s for s, data in oauth_states.items() if data['expires_at'] < now]
    for s in expired_states:
        del oauth_states[s]


def verify_oauth_state(state: str) -> Optional[dict]:
    """Verify and retrieve OAuth2 state"""
    from datetime import datetime, timezone
    
    state_data = oauth_states.get(state)
    if not state_data:
        return None
    
    # Check if expired
    if state_data['expires_at'] < datetime.now(timezone.utc):
        del oauth_states[state]
        return None
    
    return state_data


# =====================================================
# Helper Functions
# =====================================================

def get_client_info(request: Request) -> tuple:
    """Get client IP and user agent"""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return ip_address, user_agent


# =====================================================
# Endpoints
# =====================================================

@router.get("/providers", response_model=list[SSOProviderInfo])
async def list_sso_providers(db: Session = Depends(get_db)):
    """
    List available SSO providers
    
    Returns list of active SSO providers configured in the system.
    Shows redirect URIs and domain requirements for registration.
    """
    providers = db.query(SSOProvider).filter(SSOProvider.is_active == True).all()
    
    return [
        SSOProviderInfo(
            name=p.name,
            provider_type=p.provider_type,
            app_type=p.app_type,
            redirect_uri=p.redirect_uri,
            required_domain=SSOService.REQUIRED_DOMAIN,
            is_active=p.is_active
        )
        for p in providers
    ]


@router.get("/login/{provider_name}", response_model=SSOInitiateResponse)
async def initiate_sso_login(
    provider_name: str,
    db: Session = Depends(get_db),
    use_pkce: bool = True
):
    """
    Initiate SSO login flow
    
    **Parameters:**
    - provider_name: Name of SSO provider (e.g., "AS_espacios_UTB")
    - use_pkce: Enable PKCE for enhanced security (recommended)
    
    **Returns:**
    - authorization_url: URL to redirect user for authentication
    - state: CSRF protection token (store in session)
    
    **Flow:**
    1. Call this endpoint to get authorization URL
    2. Redirect user to authorization_url
    3. User authenticates with provider (must have @unitecnologica.edu.co email)
    4. Provider redirects back to callback URL with code
    5. Call /sso/callback endpoint with code and state
    """
    # Get provider configuration
    provider = await SSOService.get_provider(db, provider_name)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SSO provider '{provider_name}' not found"
        )
    
    if not provider.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSO provider '{provider_name}' is not active"
        )
    
    # Generate state for CSRF protection
    state = SSOService.generate_state()
    
    # Generate PKCE code verifier if enabled
    code_verifier = SSOService.generate_code_verifier() if use_pkce else None
    
    # Store state
    store_oauth_state(state, provider_name, code_verifier)
    
    # Generate authorization URL
    authorization_url = SSOService.get_authorization_url(provider, state, code_verifier)
    
    logger.info(f"🚀 SSO login initiated for provider: {provider_name}")
    
    # Redirect directly to authorization URL instead of returning JSON
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=authorization_url, status_code=302)


@router.get("/callback")
async def sso_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
    db: Session = Depends(get_db)
):
    """
    SSO OAuth2 callback endpoint
    
    This is where the SSO provider redirects after user authentication.
    
    **Query Parameters:**
    - code: Authorization code from provider
    - state: State parameter for CSRF protection
    - error: Error code if authentication failed
    - error_description: Human-readable error description
    
    **Domain Validation:**
    Only emails with @unitecnologica.edu.co domain are allowed.
    Other domains will be rejected with 403 Forbidden.
    """
    ip_address, user_agent = get_client_info(request)
    
    # Check for errors
    if error:
        logger.error(f"❌ SSO callback error: {error} - {error_description}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSO authentication failed: {error_description or error}"
        )
    
    # Validate required parameters
    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required parameters: code and state"
        )
    
    # Verify state (CSRF protection)
    state_data = verify_oauth_state(state)
    if not state_data:
        logger.error(f"❌ Invalid or expired OAuth state: {state}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter"
        )
    
    provider_name = state_data['provider']
    code_verifier = state_data.get('code_verifier')
    
    # Get provider
    provider = await SSOService.get_provider(db, provider_name)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SSO provider '{provider_name}' not found"
        )
    
    try:
        # Exchange code for tokens
        tokens = await SSOService.exchange_code_for_token(provider, code, code_verifier)
        
        # Process SSO login (validate domain, create/update user)
        user, jwt_tokens = await SSOService.process_sso_login(
            db=db,
            provider=provider,
            tokens=tokens,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Clean up state
        del oauth_states[state]
        
        logger.info(f"✅ SSO login successful for user: {user.username}")
        
        # Redirect to frontend with tokens
        from fastapi.responses import RedirectResponse
        import urllib.parse
        
        frontend_url = "http://localhost:8080"  # Flutter web URL
        redirect_params = {
            'access_token': jwt_tokens['access_token'],
            'refresh_token': jwt_tokens['refresh_token'],
            'token_type': 'bearer',
            'expires_in': str(jwt_tokens['expires_in']),
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email
        }
        
        redirect_url = f"{frontend_url}/auth/callback?{urllib.parse.urlencode(redirect_params)}"
        return RedirectResponse(url=redirect_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ SSO callback processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SSO authentication failed"
        )


@router.get("/config/{provider_name}")
async def get_sso_config(provider_name: str, db: Session = Depends(get_db)):
    """
    Get SSO provider configuration details
    
    **Use this endpoint to get information for SSO registration:**
    - Redirect URI (callback URL)
    - Application type
    - Required domain
    - Scopes
    
    **Example for registration form:**
    ```
    Nombre del SSO: AS_tooli_ia
    SSO TYPE: OAuth2, OpenID Connect, SAML 2
    URL de callback: https://apps.unitecnologica.edu.co/tooli_ia/api/v1/sso/callback
    Tipo de APP: Aplicación Web
    Requiere dominio: @unitecnologica.edu.co
    ```
    """
    provider = await SSOService.get_provider(db, provider_name)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SSO provider '{provider_name}' not found"
        )
    
    return {
        "name": provider.name,
        "provider_type": provider.provider_type,
        "app_type": provider.app_type,
        "redirect_uri": provider.redirect_uri,
        "authorization_url": provider.authorization_url,
        "token_url": provider.token_url,
        "userinfo_url": provider.userinfo_url,
        "scopes": provider.scopes,
        "allowed_domains": provider.allowed_domains,
        "required_domain": SSOService.REQUIRED_DOMAIN,
        "enforce_domain": provider.enforce_domain,
        "is_active": provider.is_active,
        
        # Registration help
        "registration_info": {
            "nombre_sso": provider.name,
            "sso_type": "OAuth2, OpenID Connect",
            "url_callback": provider.redirect_uri,
            "tipo_app": "Aplicación Web" if provider.app_type == "web" else provider.app_type,
            "requiere_dominio": f"@{SSOService.REQUIRED_DOMAIN}",
            "scopes_requeridos": ", ".join(provider.scopes)
        }
    }
