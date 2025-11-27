"""
JWT Authentication Service
Handles token generation, validation, and user authentication
"""
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from auth.models import User, Session as DBSession, LoginAttempt, RefreshToken
import hashlib
import logging
from config import settings

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary with user data to encode
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4())  # Unique token identifier
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int, db: Session) -> str:
    """
    Create and store refresh token
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        Refresh token string
    """
    # Generate random token
    token = str(uuid.uuid4())
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Store in database
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token)
    db.commit()
    
    return token


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


def authenticate_user(db: Session, username: str, password: str, ip_address: str = None) -> Optional[User]:
    """
    Authenticate user with username and password
    
    Args:
        db: Database session
        username: Username or email
        password: Plain text password
        ip_address: Client IP address for logging
    
    Returns:
        User object if authenticated, None otherwise
    """
    # Try to find user by username or email
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    # Log login attempt
    success = False
    if user and verify_password(password, user.password_hash) and user.is_active:
        success = True
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.commit()
    
    # Record attempt
    attempt = LoginAttempt(
        username=username,
        ip_address=ip_address or "unknown",
        success=success
    )
    db.add(attempt)
    db.commit()
    
    return user if success else None


def create_user_tokens(user: User, db: Session, ip_address: str = None, user_agent: str = None) -> Dict[str, str]:
    """
    Create access and refresh tokens for user
    
    Args:
        user: User object
        db: Database session
        ip_address: Client IP address
        user_agent: Client user agent
    
    Returns:
        Dictionary with access_token and refresh_token
    """
    # Create access token
    access_token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }
    access_token = create_access_token(access_token_data)
    
    # Decode to get JTI
    payload = decode_token(access_token)
    jti = payload.get("jti")
    exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
    
    # Store session
    session = DBSession(
        user_id=user.id,
        token_jti=jti,
        expires_at=exp,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(session)
    
    # Create refresh token
    refresh_token = create_refresh_token(user.id, db)
    
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


def get_current_user(db: Session, token: str) -> Optional[User]:
    """
    Get current user from JWT token
    
    Args:
        db: Database session
        token: JWT token string
    
    Returns:
        User object if valid, None otherwise
    """
    payload = decode_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # Check if session is valid
    jti = payload.get("jti")
    session = db.query(DBSession).filter(
        DBSession.token_jti == jti,
        DBSession.is_revoked == False
    ).first()
    
    if not session:
        logger.warning(f"Session not found or revoked for JTI: {jti}")
        return None
    
    # Get user
    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    return user


def revoke_token(db: Session, token: str) -> bool:
    """
    Revoke a token (logout)
    
    Args:
        db: Database session
        token: JWT token string
    
    Returns:
        True if revoked successfully, False otherwise
    """
    payload = decode_token(token)
    if not payload:
        return False
    
    jti = payload.get("jti")
    session = db.query(DBSession).filter(DBSession.token_jti == jti).first()
    
    if session:
        session.is_revoked = True
        db.commit()
        return True
    
    return False


def create_user(db: Session, username: str, email: str, password: str, full_name: str, is_admin: bool = False) -> User:
    """
    Create a new user
    
    Args:
        db: Database session
        username: Unique username
        email: Unique email
        password: Plain text password
        full_name: User's full name
        is_admin: Whether user is admin
    
    Returns:
        Created User object
    """
    hashed_password = hash_password(password)
    user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        full_name=full_name,
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"✅ User created: {username} ({email})")
    return user


if __name__ == "__main__":
    # Test password hashing
    print("Testing password hashing...")
    password = "Admin123!"
    hashed = hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verify correct: {verify_password(password, hashed)}")
    print(f"Verify wrong: {verify_password('wrong', hashed)}")
