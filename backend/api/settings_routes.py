"""
User Settings Routes - API endpoints for user preferences
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from auth.database import get_db
from auth.models import UserSettings, User, AuditLog
from auth.jwt_auth import get_current_user as get_current_user_jwt

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


# =====================================================
# PYDANTIC SCHEMAS
# =====================================================

class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    default_view: Optional[str] = None
    items_per_page: Optional[int] = None


class UserSettingsResponse(BaseModel):
    user_id: int
    theme: str
    language: str
    notifications_enabled: bool
    default_view: str
    items_per_page: int

    class Config:
        from_attributes = True


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from Bearer token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    user = get_current_user_jwt(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user


# =====================================================
# ENDPOINTS
# =====================================================

@router.get("/", response_model=UserSettingsResponse)
def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user settings (creates default if not exists)"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings
        settings = UserSettings(
            user_id=current_user.id,
            theme="light",
            language="es",
            notifications_enabled=True,
            default_view="chat",
            items_per_page=20
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/", response_model=UserSettingsResponse)
def update_user_settings(
    settings_data: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user settings"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create if not exists
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Update provided fields
    if settings_data.theme is not None:
        settings.theme = settings_data.theme
    
    if settings_data.language is not None:
        settings.language = settings_data.language
    
    if settings_data.notifications_enabled is not None:
        settings.notifications_enabled = settings_data.notifications_enabled
    
    if settings_data.default_view is not None:
        settings.default_view = settings_data.default_view
    
    if settings_data.items_per_page is not None:
        settings.items_per_page = settings_data.items_per_page
    
    # Log action
    audit = AuditLog(
        user_id=current_user.id,
        action="update_settings",
        entity_type="user_settings",
        entity_id=current_user.id,
        details=settings_data.model_dump_json()
    )
    db.add(audit)
    
    db.commit()
    db.refresh(settings)
    
    return settings
