"""Query domain entity for user requests."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any


class QueryIntent(Enum):
    """Query intent classification."""
    
    LIST_TICKETS = "list_tickets"
    GET_TICKET = "get_ticket"
    GET_STATISTICS = "get_statistics"
    LIST_COMPUTERS = "list_computers"
    GET_COMPUTER = "get_computer"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


@dataclass
class Query:
    """User query domain entity."""
    
    text: str
    user_id: Optional[int] = None
    intent: Optional[QueryIntent] = None
    parameters: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.parameters is None:
            self.parameters = {}
    
    @property
    def has_high_confidence(self) -> bool:
        """Check if confidence is high enough."""
        return self.confidence is not None and self.confidence >= 0.85
    
    def to_dict(self) -> dict:
        """Convert query to dictionary representation."""
        return {
            "text": self.text,
            "user_id": self.user_id,
            "intent": self.intent.value if self.intent else None,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }
