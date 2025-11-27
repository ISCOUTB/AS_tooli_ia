"""Response domain entity for assistant responses."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any


@dataclass
class ResponseMetadata:
    """Metadata for response tracking."""
    
    processing_time_ms: float
    tokens_used: Optional[int] = None
    model_version: Optional[str] = None
    confidence_score: Optional[float] = None


@dataclass
class Response:
    """Assistant response domain entity."""
    
    content: str
    success: bool
    intent: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[ResponseMetadata] = None
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
    
    @property
    def is_error(self) -> bool:
        """Check if response indicates an error."""
        return not self.success or self.error_message is not None
    
    def to_dict(self) -> dict:
        """Convert response to dictionary representation."""
        result = {
            "content": self.content,
            "success": self.success,
            "intent": self.intent,
            "data": self.data,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }
        
        if self.metadata:
            result["metadata"] = {
                "processing_time_ms": self.metadata.processing_time_ms,
                "tokens_used": self.metadata.tokens_used,
                "model_version": self.metadata.model_version,
                "confidence_score": self.metadata.confidence_score,
            }
        
        return result
