"""
Conversation Routes - API endpoints for chat conversations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone

from auth.database import get_db
from auth.models import Conversation, Message, MessageRole, User, AuditLog
from auth.jwt_auth import get_current_user as get_current_user_jwt

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


# =====================================================
# PYDANTIC SCHEMAS
# =====================================================

class MessageCreate(BaseModel):
    role: str
    content: str

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    tokens_used: int

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_archived: Optional[bool] = None


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    message_count: int

    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


# =====================================================
# HELPER FUNCTIONS
# =====================================================

# Error messages
MSG_NOT_AUTHENTICATED = "Not authenticated"
MSG_CONVERSATION_NOT_FOUND = "Conversation not found"

def get_user_from_token(authorization: str, db: Session) -> User:
    """Get current authenticated user from Bearer token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=MSG_NOT_AUTHENTICATED
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

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation_data: ConversationCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    try:
        current_user = get_user_from_token(authorization, db)
        conversation = Conversation(
            user_id=current_user.id,
            title=conversation_data.title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        # Log action
        audit = AuditLog(
            user_id=current_user.id,
            action="create_conversation",
            entity_type="conversation",
            entity_id=conversation.id
        )
        db.add(audit)
        db.commit()
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            is_archived=conversation.is_archived,
            message_count=0
        )
    except Exception as e:
        import traceback
        print(f"❌ Error creating conversation: {e}")
        print(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )


@router.get("/", response_model=List[ConversationResponse])
def list_conversations(
    skip: int = 0,
    limit: int = 20,
    include_archived: bool = False,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """List all conversations for the current user"""
    current_user = get_user_from_token(authorization, db)
    query = db.query(Conversation).filter(Conversation.user_id == current_user.id)
    
    if not include_archived:
        query = query.filter(Conversation.is_archived == False)
    
    conversations = query.order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    
    # Add message count
    result = []
    for conv in conversations:
        message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
        result.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            is_archived=conv.is_archived,
            message_count=message_count
        ))
    
    return result


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    current_user = get_user_from_token(authorization, db)
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MSG_CONVERSATION_NOT_FOUND
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        is_archived=conversation.is_archived,
        messages=[MessageResponse(
            id=msg.id,
            role=msg.role.value,
            content=msg.content,
            created_at=msg.created_at,
            tokens_used=msg.tokens_used or 0
        ) for msg in messages]
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def add_message(
    conversation_id: int,
    message_data: MessageCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Add a message to a conversation"""
    try:
        current_user = get_user_from_token(authorization, db)
        # Verify conversation belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MSG_CONVERSATION_NOT_FOUND
            )
        
        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=MessageRole(message_data.role),
            content=message_data.content
        )
        db.add(message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(message)
        
        return MessageResponse(
            id=message.id,
            role=message.role.value,
            content=message.content,
            created_at=message.created_at,
            tokens_used=message.tokens_used or 0
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Error adding message: {e}")
        print(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding message: {str(e)}"
        )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int,
    update_data: ConversationUpdate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Update conversation title or archive status"""
    current_user = get_user_from_token(authorization, db)
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MSG_CONVERSATION_NOT_FOUND
        )
    
    if update_data.title is not None:
        conversation.title = update_data.title
    
    if update_data.is_archived is not None:
        conversation.is_archived = update_data.is_archived
    
    db.commit()
    db.refresh(conversation)
    
    message_count = db.query(Message).filter(Message.conversation_id == conversation.id).count()
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        is_archived=conversation.is_archived,
        message_count=message_count
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Delete a conversation (and all its messages)"""
    current_user = get_user_from_token(authorization, db)
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MSG_CONVERSATION_NOT_FOUND
        )
    
    # Log action before deleting
    audit = AuditLog(
        user_id=current_user.id,
        action="delete_conversation",
        entity_type="conversation",
        entity_id=conversation.id
    )
    db.add(audit)
    
    db.delete(conversation)
    db.commit()
    
    return None
