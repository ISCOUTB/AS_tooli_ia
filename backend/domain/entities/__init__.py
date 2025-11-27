"""Domain entities for GLPI Assistant."""

from .ticket import Ticket, TicketStatus, TicketPriority, TicketType
from .query import Query, QueryIntent
from .response import Response, ResponseMetadata

__all__ = [
    "Ticket",
    "TicketStatus",
    "TicketPriority",
    "TicketType",
    "Query",
    "QueryIntent",
    "Response",
    "ResponseMetadata",
]
