"""
Authentication API Routes
Endpoints for login, register, logout, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from auth.database import get_db
from auth import jwt_auth
from auth.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()


# =====================================================
# Request/Response Models
# =====================================================

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username or email")
    password: str = Field(..., min_length=6, description="Password")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_admin: bool
    is_active: bool
    last_login: Optional[str]


class MessageResponse(BaseModel):
    message: str
    success: bool


# =====================================================
# Helper Functions
# =====================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    """
    token = credentials.credentials
    user = jwt_auth.get_current_user(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_client_info(request: Request) -> tuple:
    """Get client IP and user agent"""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return ip_address, user_agent


# =====================================================
# Endpoints
# =====================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    **Requirements:**
    - Username: 3-50 characters, unique
    - Email: Valid email format with @unitecnologica.edu.co domain (REQUIRED)
    - Password: Minimum 8 characters
    - Full name: 2-100 characters
    
    **Domain Restriction:**
    Only emails with @unitecnologica.edu.co domain are allowed for registration.
    This is an institutional requirement.
    
    **Returns:**
    - Success message with user creation confirmation
    """
    try:
        # CRITICAL: Validate email domain (institutional requirement)
        email_str = str(request_data.email).lower()
        if not email_str.endswith("@unitecnologica.edu.co"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo se permiten cuentas con dominio @unitecnologica.edu.co"
            )
        
        # Check if username exists
        existing_user = db.query(User).filter(User.username == request_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email exists
        existing_email = db.query(User).filter(User.email == request_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = jwt_auth.create_user(
            db=db,
            username=request_data.username,
            email=request_data.email,
            password=request_data.password,
            full_name=request_data.full_name
        )
        
        logger.info(f"✅ New user registered: {user.username}")
        logger.info(f"🔍 RETURNING UserResponse WITH ID: {user.id}")  # DEBUG
        
        # Return user object (frontend expects User, not MessageResponse)
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_admin=user.is_admin,
            is_active=user.is_active,
            last_login=None
        )
        logger.info(f"🔍 UserResponse object created: {user_response}")  # DEBUG
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens
    
    **Requirements:**
    - Username or email
    - Password
    
    **Returns:**
    - access_token: JWT token for API authentication (expires in 30 minutes)
    - refresh_token: Token for refreshing access token (expires in 7 days)
    - user: User information
    """
    try:
        ip_address, user_agent = get_client_info(request)
        
        # Authenticate user
        user = jwt_auth.authenticate_user(
            db=db,
            username=login_data.username,
            password=login_data.password,
            ip_address=ip_address
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        tokens = jwt_auth.create_user_tokens(
            user=user,
            db=db,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"✅ User logged in: {user.username} from {ip_address}")
        
        return TokenResponse(
            **tokens,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_admin": user.is_admin
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later."
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking current token
    
    **Requires:** Valid JWT token in Authorization header
    
    **Returns:**
    - Success message confirming logout
    """
    try:
        token = credentials.credentials
        success = jwt_auth.revoke_token(db, token)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to logout"
            )
        
        logger.info("✅ User logged out successfully")
        
        return MessageResponse(
            message="Logged out successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed. Please try again later."
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    
    **Requires:** Valid JWT token in Authorization header
    
    **Returns:**
    - User profile information
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_admin=current_user.is_admin,
        is_active=current_user.is_active,
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )


@router.get("/health", response_model=MessageResponse)
async def auth_health_check(db: Session = Depends(get_db)):
    """
    Health check for authentication system
    
    **Returns:**
    - System status and database connectivity
    """
    try:
        # Test database connection
        user_count = db.query(User).count()
        
        return MessageResponse(
            message=f"Authentication system healthy. Users: {user_count}",
            success=True
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication system unavailable"
        )
