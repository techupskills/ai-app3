"""
TechCorp Customer Service - Enterprise Service Layer

This module implements the service layer pattern for clean architecture:
- Business logic separated from infrastructure concerns
- Dependency injection for testability
- Interface-based design for flexibility
"""

from .llm_service import LLMService
from .knowledge_service import KnowledgeService
from .escalation_service import EscalationService
from .audit_service import AuditService

__all__ = [
    'LLMService',
    'KnowledgeService', 
    'EscalationService',
    'AuditService'
]