#!/usr/bin/env python3

# Lab 2: Production Agent Architecture  
# Complete implementation with enterprise patterns

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import logging
import time
import uuid
import json
from datetime import datetime
import requests
from pathlib import Path

# Enterprise Architecture Interfaces

class ILLMService(ABC):
    """Interface for LLM service - enables dependency injection"""
    @abstractmethod
    def call_llm(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

class IKnowledgeService(ABC):
    """Interface for knowledge base service"""
    @abstractmethod
    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        pass

class IEscalationService(ABC):
    """Interface for escalation service"""
    @abstractmethod
    def should_escalate(self, query: str, context: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def escalate_to_human(self, conversation_id: str, reason: str) -> Dict[str, Any]:
        pass

class IAuditService(ABC):
    """Interface for audit and compliance logging"""
    @abstractmethod
    def log_conversation(self, conversation_id: str, data: Dict[str, Any]) -> None:
        pass

@dataclass
class CustomerContext:
    """Customer context for personalized service"""
    customer_id: str
    subscription_tier: str
    conversation_history: List[Dict[str, Any]]
    session_id: str

class CustomerServiceAgent:
    """
    Enterprise Customer Service Agent
    
    Implements clean architecture with:
    - Dependency injection for all services
    - Comprehensive error handling
    - Performance monitoring
    - Audit logging
    - Escalation management
    """
    
    def __init__(self, 
                 llm_service: ILLMService,
                 knowledge_service: IKnowledgeService,
                 escalation_service: IEscalationService,
                 audit_service: IAuditService):
        self.llm_service = llm_service
        self.knowledge_service = knowledge_service
        self.escalation_service = escalation_service
        self.audit_service = audit_service
        
        # Setup structured logging
        self.logger = logging.getLogger('customer_service_agent')
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console_handler)
        
        # File handler for audit trail
        Path("logs").mkdir(exist_ok=True)
        file_handler = logging.FileHandler('logs/customer_service.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)
        
        # Performance metrics
        self.metrics = {
            "total_conversations": 0,
            "escalated_conversations": 0,
            "average_response_time": 0.0,
            "successful_resolutions": 0
        }
        
        self.logger.info("Customer Service Agent initialized with enterprise architecture")
    
    def handle_customer_query(self, 
                            query: str, 
                            customer_context: CustomerContext) -> Dict[str, Any]:
        """
        Main entry point for handling customer queries
        
        Implements the following enterprise patterns:
        1. Input validation and sanitization
        2. Context enrichment
        3. Knowledge base search
        4. LLM reasoning with fallbacks
        5. Escalation decision logic
        6. Audit logging
        7. Performance monitoring
        """
        conversation_id = str(uuid.uuid4())
        start_time = time.time()
        
        self.logger.info(f"Starting conversation {conversation_id}", extra={
            "customer_id": customer_context.customer_id,
            "query_length": len(query)
        })
        
        try:
            # 1. Input validation
            if not self._validate_input(query):
                error_response = {
                    "success": False,
                    "response": "I'm sorry, but I cannot process that request. Please rephrase your question.",
                    "conversation_id": conversation_id,
                    "escalated": False
                }
                self.audit_service.log_conversation(conversation_id, {
                    "status": "validation_failed",
                    "customer_id": customer_context.customer_id,
                    "query": query
                })
                return error_response
            
            # 2. Context enrichment
            enriched_context = self._enrich_context(query, customer_context)
            
            # 3. Check for immediate escalation
            if self._should_escalate_query(query, enriched_context):
                escalation_result = self.escalation_service.escalate_to_human(
                    conversation_id, "Complex query requiring human expertise"
                )
                
                self.metrics["escalated_conversations"] += 1
                
                response = {
                    "success": True,
                    "response": "I've escalated your request to a human agent who will assist you shortly. Your ticket number is " + escalation_result.get("ticket_id", "N/A"),
                    "conversation_id": conversation_id,
                    "escalated": True,
                    "escalation_reason": "Complex query"
                }
                
                self.audit_service.log_conversation(conversation_id, {
                    "status": "escalated",
                    "customer_id": customer_context.customer_id,
                    "query": query,
                    "escalation_reason": "Complex query"
                })
                
                return response
            
            # 4. Generate AI response
            ai_response = self._generate_response(enriched_context)
            
            if ai_response.get("success", False):
                self.metrics["successful_resolutions"] += 1
                
                response = {
                    "success": True,
                    "response": ai_response["response"],
                    "conversation_id": conversation_id,
                    "escalated": False,
                    "confidence": ai_response.get("confidence", 0.8),
                    "knowledge_sources": ai_response.get("sources", [])
                }
            else:
                # Fallback to escalation if AI fails
                escalation_result = self.escalation_service.escalate_to_human(
                    conversation_id, "AI service failure"
                )
                
                self.metrics["escalated_conversations"] += 1
                
                response = {
                    "success": True,
                    "response": "I'm experiencing technical difficulties. I've connected you with a human agent who will help you immediately.",
                    "conversation_id": conversation_id,
                    "escalated": True,
                    "escalation_reason": "Technical failure"
                }
            
            # 5. Performance tracking
            response_time = time.time() - start_time
            self.metrics["total_conversations"] += 1
            self.metrics["average_response_time"] = (
                (self.metrics["average_response_time"] * (self.metrics["total_conversations"] - 1) + response_time) 
                / self.metrics["total_conversations"]
            )
            
            # 6. Audit logging
            self.audit_service.log_conversation(conversation_id, {
                "status": "completed",
                "customer_id": customer_context.customer_id,
                "query": query,
                "response": response["response"],
                "escalated": response["escalated"],
                "response_time": response_time
            })
            
            # 7. SLA monitoring (enterprise requirement: < 2 seconds)
            if response_time > 2.0:
                self.logger.warning(f"SLA violation: Response time {response_time:.2f}s exceeds 2s threshold", extra={
                    "conversation_id": conversation_id,
                    "response_time": response_time
                })
            
            response["response_time"] = response_time
            return response
            
        except Exception as e:
            self.logger.error(f"Unexpected error in conversation {conversation_id}: {str(e)}", extra={
                "customer_id": customer_context.customer_id,
                "error_type": type(e).__name__
            })
            
            # Enterprise pattern: Always provide graceful degradation
            escalation_result = self.escalation_service.escalate_to_human(
                conversation_id, f"System error: {type(e).__name__}"
            )
            
            return {
                "success": True,
                "response": "I apologize for the technical issue. I've immediately connected you with a human agent for assistance.",
                "conversation_id": conversation_id,
                "escalated": True,
                "escalation_reason": "System error"
            }
    
    def _validate_input(self, query: str) -> bool:
        """Validate customer input for security"""
        if not query or len(query.strip()) == 0:
            return False
        
        if len(query) > 5000:  # Prevent DOS attacks
            return False
        
        # Check for malicious patterns
        malicious_patterns = [
            '<script>', '<?php', 'DROP TABLE', 'DELETE FROM',
            'INSERT INTO', 'UPDATE SET', '--', '/*', '*/',
            'UNION SELECT', 'OR 1=1'
        ]
        
        query_lower = query.lower()
        for pattern in malicious_patterns:
            if pattern.lower() in query_lower:
                return False
        
        return True
    
    def _enrich_context(self, query: str, customer_context: CustomerContext) -> Dict[str, Any]:
        """Enrich context with knowledge base and customer data"""
        try:
            # Search knowledge base for relevant information
            knowledge_results = self.knowledge_service.search_knowledge(query)
            
            return {
                "original_query": query,
                "customer_id": customer_context.customer_id,
                "subscription_tier": customer_context.subscription_tier,
                "conversation_history": customer_context.conversation_history[-3:],  # Last 3 interactions
                "knowledge_base_results": knowledge_results,
                "session_id": customer_context.session_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.warning(f"Failed to enrich context: {str(e)}")
            return {
                "original_query": query,
                "customer_id": customer_context.customer_id,
                "knowledge_base_results": [],
                "error": "Context enrichment failed"
            }
    
    def _generate_response(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using LLM with fallbacks"""
        try:
            # Create enterprise prompt with context
            prompt = self._build_enterprise_prompt(enriched_context)
            
            # Call LLM service with retry logic
            llm_response = self.llm_service.call_llm(prompt, enriched_context)
            
            if llm_response.get("error"):
                return {"success": False, "error": llm_response["error"]}
            
            return {
                "success": True,
                "response": llm_response.get("response", "I apologize, but I'm having trouble generating a response."),
                "confidence": 0.85,  # In production, this would be calculated
                "sources": [kb["source"] for kb in enriched_context.get("knowledge_base_results", [])]
            }
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _build_enterprise_prompt(self, context: Dict[str, Any]) -> str:
        """Build enterprise prompt with context and guardrails"""
        knowledge_context = ""
        if context.get("knowledge_base_results"):
            knowledge_context = "\n".join([
                f"- {result['content'][:200]}..." for result in context["knowledge_base_results"][:3]
            ])
        
        return f"""You are TechCorp's customer service AI assistant. Provide helpful, professional responses.

Customer Query: {context['original_query']}

Customer Tier: {context.get('subscription_tier', 'Standard')}

Relevant Knowledge Base Information:
{knowledge_context}

Guidelines:
- Be professional, empathetic, and solution-focused
- Provide specific steps when possible
- If you cannot help, clearly state limitations
- Never make promises about refunds or account changes without verification
- Always prioritize customer satisfaction within company policies

Response:"""
    
    def _should_escalate_query(self, query: str, context: Dict[str, Any]) -> bool:
        """Determine if query should be escalated to human agent"""
        return self.escalation_service.should_escalate(query, context)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Return current performance metrics for monitoring"""
        # Save metrics to file for monitoring dashboard
        Path("metrics").mkdir(exist_ok=True)
        with open("metrics/agent_performance.json", "w") as f:
            json.dump({
                **self.metrics,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
        
        return self.metrics

# Service Implementations (to be injected)

class MockLLMService(ILLMService):
    """Mock LLM service for demonstration"""
    
    def call_llm(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate LLM call - in production this would use the enterprise LLM service from Lab 1
        query = context.get("original_query", "").lower()
        
        if "password" in query or "login" in query:
            return {
                "response": "To reset your password, please visit our self-service portal at techcorp.com/reset-password or use the 'Forgot Password' link on the login page. You'll receive a reset email within 5 minutes.",
                "success": True
            }
        elif "billing" in query or "charge" in query:
            return {
                "response": "I understand your billing concern. I can see you're a valued customer. For billing inquiries, I recommend checking your account dashboard first. If you still need assistance, I can escalate this to our billing specialists.",
                "success": True
            }
        elif "crash" in query or "error" in query:
            return {
                "response": "I'm sorry you're experiencing technical difficulties. Let's troubleshoot this together: 1) Try refreshing the application, 2) Clear your browser cache, 3) Restart the app. If the problem persists, I'll connect you with our technical support team.",
                "success": True
            }
        else:
            return {
                "response": "Thank you for contacting TechCorp support. I'm here to help you with any questions or concerns. Could you please provide more details about your specific issue?",
                "success": True
            }

class MockKnowledgeService(IKnowledgeService):
    """Mock knowledge base service"""
    
    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        # Simulate knowledge base search
        knowledge_base = [
            {
                "content": "Password reset instructions: Use forgot password link, check email, follow reset instructions",
                "source": "KB-001-Password-Reset",
                "relevance": 0.9
            },
            {
                "content": "Billing support: Check account dashboard, contact billing team for disputes, 30-day refund policy",
                "source": "KB-002-Billing-Support", 
                "relevance": 0.8
            },
            {
                "content": "Technical troubleshooting: Clear cache, restart app, check network connection, contact support",
                "source": "KB-003-Tech-Support",
                "relevance": 0.85
            }
        ]
        
        # Simple keyword matching for demo
        query_lower = query.lower()
        relevant_results = []
        
        for item in knowledge_base:
            if any(keyword in item["content"].lower() for keyword in query_lower.split()):
                relevant_results.append(item)
        
        return relevant_results[:3]  # Top 3 results

class MockEscalationService(IEscalationService):
    """Mock escalation service"""
    
    def should_escalate(self, query: str, context: Dict[str, Any]) -> bool:
        escalation_keywords = [
            "manager", "supervisor", "escalate", "complaint", "lawsuit", 
            "angry", "furious", "unacceptable", "cancel account", "refund immediately"
        ]
        
        return any(keyword in query.lower() for keyword in escalation_keywords)
    
    def escalate_to_human(self, conversation_id: str, reason: str) -> Dict[str, Any]:
        ticket_id = f"TCS-{int(time.time())}"
        return {
            "ticket_id": ticket_id,
            "estimated_wait_time": "2-3 minutes",
            "agent_type": "senior_support",
            "escalation_reason": reason
        }

class MockAuditService(IAuditService):
    """Mock audit service for compliance logging"""
    
    def log_conversation(self, conversation_id: str, data: Dict[str, Any]) -> None:
        # In production, this would write to secure audit log system
        Path("logs").mkdir(exist_ok=True)
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "event_type": "customer_interaction",
            **data
        }
        
        # Append to audit log
        with open("logs/audit.log", "a") as f:
            f.write(json.dumps(audit_entry) + "\n")

class EnterpriseServices:
    """Factory for creating enterprise service implementations"""
    
    @staticmethod
    def create_llm_service() -> ILLMService:
        return MockLLMService()
    
    @staticmethod  
    def create_knowledge_service() -> IKnowledgeService:
        return MockKnowledgeService()
    
    @staticmethod
    def create_escalation_service() -> IEscalationService:
        return MockEscalationService()
    
    @staticmethod
    def create_audit_service() -> IAuditService:
        return MockAuditService()

def main():
    """Main function demonstrating enterprise agent architecture"""
    print("=== TechCorp Customer Service Agent ===")
    print("Enterprise Architecture: Clean Code, DI, Monitoring")
    print("Commands: 'metrics' for performance, 'quit' to exit\n")
    
    # Initialize agent with dependency injection (enterprise pattern)
    agent = CustomerServiceAgent(
        llm_service=EnterpriseServices.create_llm_service(),
        knowledge_service=EnterpriseServices.create_knowledge_service(),
        escalation_service=EnterpriseServices.create_escalation_service(),
        audit_service=EnterpriseServices.create_audit_service()
    )
    
    # Simulate customer sessions
    session_id = str(uuid.uuid4())
    
    while True:
        customer_query = input("\nCustomer: ").strip()
        
        if customer_query.lower() in ['quit', 'exit']:
            print("\n📊 Final Performance Metrics:")
            print(json.dumps(agent.get_performance_metrics(), indent=2))
            print("Agent session ended. Thank you!")
            break
        
        if customer_query.lower() == 'metrics':
            print("\n📈 Current Performance Metrics:")
            print(json.dumps(agent.get_performance_metrics(), indent=2))
            continue
            
        if not customer_query:
            continue
        
        # Create customer context (in production, this would come from CRM/database)
        customer_context = CustomerContext(
            customer_id=f"CUST-{uuid.uuid4().hex[:8].upper()}",
            subscription_tier="Premium",
            conversation_history=[],
            session_id=session_id
        )
        
        print("🤖 Processing your request...")
        
        # Handle customer query with enterprise patterns
        result = agent.handle_customer_query(customer_query, customer_context)
        
        print(f"\nAgent: {result['response']}")
        
        if result.get('escalated'):
            print(f"🚀 Escalated: {result.get('escalation_reason', 'Unknown')}")
        else:
            print(f"✅ Resolved | Confidence: {result.get('confidence', 'N/A')} | Time: {result.get('response_time', 0):.2f}s")
        
        if result.get('knowledge_sources'):
            print(f"📚 Sources: {', '.join(result['knowledge_sources'])}")

if __name__ == "__main__":
    main()