"""Ticket domain entity with clean business logic."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TicketStatus(Enum):
    """Ticket status enumeration."""
    
    NEW = 1
    ASSIGNED = 2
    PLANNED = 3
    WAITING = 4
    SOLVED = 5
    CLOSED = 6

    @property
    def display_name(self) -> str:
        """Get human-readable status name."""
        names = {
            self.NEW: "New",
            self.ASSIGNED: "In Progress (Assigned)",
            self.PLANNED: "In Progress (Planned)",
            self.WAITING: "Waiting",
            self.SOLVED: "Solved",
            self.CLOSED: "Closed",
        }
        return names.get(self, "Unknown")


class TicketPriority(Enum):
    """Ticket priority enumeration."""
    
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    MAJOR = 6

    @property
    def display_name(self) -> str:
        """Get human-readable priority name."""
        names = {
            self.VERY_LOW: "Very Low",
            self.LOW: "Low",
            self.MEDIUM: "Medium",
            self.HIGH: "High",
            self.VERY_HIGH: "Very High",
            self.MAJOR: "Major",
        }
        return names.get(self, "Unknown")


class TicketType(Enum):
    """Ticket type enumeration."""
    
    INCIDENT = 1
    REQUEST = 2

    @property
    def display_name(self) -> str:
        """Get human-readable type name."""
        return "Incident" if self == self.INCIDENT else "Request"


@dataclass
class Ticket:
    """Ticket domain entity representing a GLPI ticket."""
    
    id: int
    name: str
    content: str
    status: TicketStatus
    priority: TicketPriority
    type: TicketType
    date_created: datetime
    date_modified: datetime
    requester_id: Optional[int] = None
    assigned_to: Optional[int] = None
    urgency: int = 3
    impact: int = 3
    
    @property
    def is_open(self) -> bool:
        """Check if ticket is still open."""
        return self.status not in [TicketStatus.SOLVED, TicketStatus.CLOSED]
    
    @property
    def is_critical(self) -> bool:
        """Check if ticket has critical priority."""
        return self.priority in [TicketPriority.VERY_HIGH, TicketPriority.MAJOR]
    
    def to_dict(self) -> dict:
        """Convert ticket to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "status": self.status.display_name,
            "priority": self.priority.display_name,
            "type": self.type.display_name,
            "date_created": self.date_created.isoformat(),
            "date_modified": self.date_modified.isoformat(),
            "requester_id": self.requester_id,
            "assigned_to": self.assigned_to,
            "urgency": self.urgency,
            "impact": self.impact,
            "is_open": self.is_open,
            "is_critical": self.is_critical,
        }
