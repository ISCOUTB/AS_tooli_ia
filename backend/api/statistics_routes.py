"""
Statistics Routes - API endpoints for dashboard statistics
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import json

from auth.database import get_db
from auth.models import User, Conversation, Message, StatisticsCache
from auth.jwt_auth import get_current_user as get_current_user_jwt

router = APIRouter(prefix="/api/v1/statistics", tags=["statistics"])


# =====================================================
# PYDANTIC SCHEMAS
# =====================================================

class DashboardStats(BaseModel):
    total_conversations: int
    active_conversations: int
    archived_conversations: int
    total_messages: int
    total_tokens_used: int
    conversations_today: int
    messages_today: int
    average_messages_per_conversation: float
    last_activity: str


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


def get_cached_stats(db: Session, user_id: int, stat_key: str) -> Dict[str, Any]:
    """Get cached statistics if available and not expired"""
    cache = db.query(StatisticsCache).filter(
        StatisticsCache.user_id == user_id,
        StatisticsCache.stat_key == stat_key,
        StatisticsCache.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if cache:
        return json.loads(cache.stat_value)
    
    return None


def cache_stats(db: Session, user_id: int, stat_key: str, stat_value: Dict[str, Any], ttl_minutes: int = 15):
    """Cache statistics for specified TTL"""
    cache = db.query(StatisticsCache).filter(
        StatisticsCache.user_id == user_id,
        StatisticsCache.stat_key == stat_key
    ).first()
    
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    
    if cache:
        cache.stat_value = json.dumps(stat_value)
        cache.expires_at = expires_at
    else:
        cache = StatisticsCache(
            user_id=user_id,
            stat_key=stat_key,
            stat_value=json.dumps(stat_value),
            expires_at=expires_at
        )
        db.add(cache)
    
    db.commit()


# =====================================================
# ENDPOINTS
# =====================================================

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard statistics for current user"""
    try:
        # Check cache first
        cached = get_cached_stats(db, current_user.id, "dashboard")
        if cached:
            return DashboardStats(**cached)
        
        # Calculate statistics
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Total conversations
        total_conversations = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == current_user.id
        ).scalar()
        
        # Active conversations
        active_conversations = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == current_user.id,
            Conversation.is_archived == False
        ).scalar()
        
        # Archived conversations
        archived_conversations = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == current_user.id,
            Conversation.is_archived == True
        ).scalar()
        
        # Total messages
        total_messages = db.query(func.count(Message.id)).join(Conversation).filter(
            Conversation.user_id == current_user.id
        ).scalar()
        
        # Total tokens used
        total_tokens = db.query(func.sum(Message.tokens_used)).join(Conversation).filter(
            Conversation.user_id == current_user.id
        ).scalar() or 0
        
        # Today's conversations
        conversations_today = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == current_user.id,
            Conversation.created_at >= today_start
        ).scalar()
        
        # Today's messages
        messages_today = db.query(func.count(Message.id)).join(Conversation).filter(
            Conversation.user_id == current_user.id,
            Message.created_at >= today_start
        ).scalar()
        
        # Average messages per conversation
        avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
        
        # Last activity
        last_message = db.query(Message).join(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Message.created_at.desc()).first()
        
        last_activity = last_message.created_at.isoformat() if last_message else None
        
        stats_dict = {
            "total_conversations": total_conversations or 0,
            "active_conversations": active_conversations or 0,
            "archived_conversations": archived_conversations or 0,
            "total_messages": total_messages or 0,
            "total_tokens_used": int(total_tokens),
            "conversations_today": conversations_today or 0,
            "messages_today": messages_today or 0,
            "average_messages_per_conversation": round(avg_messages, 2),
            "last_activity": last_activity or "Never"
        }
        
        # Cache for 15 minutes
        cache_stats(db, current_user.id, "dashboard", stats_dict, ttl_minutes=15)
        
        return DashboardStats(**stats_dict)
    except Exception as e:
        import traceback
        print(f"❌ Error getting dashboard stats: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting dashboard statistics: {str(e)}"
        )


@router.get("/conversations/timeline")
def get_conversation_timeline(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation creation timeline for the last N days"""
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get daily conversation counts
    results = db.query(
        func.date(Conversation.created_at).label('date'),
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.user_id == current_user.id,
        Conversation.created_at >= start_date
    ).group_by(
        func.date(Conversation.created_at)
    ).order_by(
        func.date(Conversation.created_at)
    ).all()
    
    timeline = [
        {
            "date": result.date.isoformat(),
            "count": result.count
        }
        for result in results
    ]
    
    return {"timeline": timeline}


@router.get("/messages/by-hour")
def get_messages_by_hour(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get message distribution by hour of day"""
    
    results = db.query(
        func.extract('hour', Message.created_at).label('hour'),
        func.count(Message.id).label('count')
    ).join(Conversation).filter(
        Conversation.user_id == current_user.id
    ).group_by(
        func.extract('hour', Message.created_at)
    ).order_by(
        func.extract('hour', Message.created_at)
    ).all()
    
    distribution = [
        {
            "hour": int(result.hour),
            "count": result.count
        }
        for result in results
    ]
    
    return {"distribution": distribution}


@router.delete("/cache")
def clear_statistics_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear cached statistics for current user"""
    
    db.query(StatisticsCache).filter(
        StatisticsCache.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {"message": "Statistics cache cleared"}
