#!/usr/bin/env python3

# Lab 4: RAG-Enhanced Customer Service Agent
# Complete implementation integrating RAG with customer service

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import enterprise RAG service
from enterprise_rag_service import EnterpriseRAGService, SearchResult

@dataclass 
class CustomerContext:
    """Customer context for personalized service"""
    customer_id: str
    subscription_tier: str
    conversation_history: List[Dict[str, Any]]
    session_id: str

class RAGEnhancedCustomerAgent:
    """
    Customer Service Agent enhanced with Enterprise RAG
    
    Features:
    - Integration with enterprise knowledge base
    - Context-aware response generation
    - Citation tracking and source attribution
    - Performance monitoring and optimization
    - Role-based knowledge access
    """
    
    def __init__(self):
        # Initialize RAG service
        try:
            self.rag_service = EnterpriseRAGService()
            self.rag_available = True
        except Exception as e:
            logging.error(f"RAG service initialization failed: {e}")
            self.rag_available = False
        
        # Setup logging
        self.setup_logging()
        
        # Agent metrics
        self.metrics = {
            "total_conversations": 0,
            "rag_enhanced_responses": 0,
            "knowledge_base_queries": 0,
            "average_response_time": 0.0,
            "customer_satisfaction": 0.0
        }
        
        self.logger.info("RAG-Enhanced Customer Service Agent initialized")
    
    def setup_logging(self):
        """Setup structured logging for agent operations"""
        # Setup logger
        self.logger = logging.getLogger("rag_enhanced_agent")
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(console_handler)
    
    def handle_customer_query(self, 
                            query: str, 
                            customer_context: CustomerContext,
                            user_role: str = "customer_service") -> Dict[str, Any]:
        """
        Handle customer query with RAG enhancement
        
        Process:
        1. Analyze query for knowledge base relevance
        2. Search enterprise knowledge base
        3. Generate context-aware response
        4. Include citations and source attribution
        5. Track performance and satisfaction
        """
        
        conversation_id = str(uuid.uuid4())
        start_time = time.time()
        
        self.logger.info(f"Processing RAG-enhanced query", extra={
            "conversation_id": conversation_id,
            "customer_id": customer_context.customer_id,
            "query_length": len(query)
        })
        
        try:
            # Step 1: Determine if query would benefit from knowledge base
            needs_knowledge = self._analyze_query_for_knowledge_needs(query)
            
            knowledge_results = []
            if needs_knowledge and self.rag_available:
                # Step 2: Search enterprise knowledge base
                self.logger.info(f"Searching knowledge base for query: {query[:50]}...")
                self.metrics["knowledge_base_queries"] += 1
                
                knowledge_results = self.rag_service.search_knowledge(
                    query, 
                    user_role=user_role,
                    max_results=3,
                    relevance_threshold=0.6
                )
            
            # Step 3: Generate enhanced response
            response_data = self._generate_enhanced_response(
                query, 
                customer_context, 
                knowledge_results,
                conversation_id
            )
            
            # Step 4: Track metrics
            response_time = time.time() - start_time
            self._update_metrics(response_time, len(knowledge_results) > 0)
            
            # Step 5: Add performance metadata
            response_data.update({
                "conversation_id": conversation_id,
                "response_time": response_time,
                "knowledge_enhanced": len(knowledge_results) > 0,
                "knowledge_sources_count": len(knowledge_results),
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"RAG-enhanced response generated", extra={
                "conversation_id": conversation_id,
                "response_time": response_time,
                "knowledge_enhanced": len(knowledge_results) > 0
            })
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error in RAG-enhanced processing: {str(e)}", extra={
                "conversation_id": conversation_id
            })
            
            # Fallback to basic response
            return self._generate_fallback_response(query, conversation_id, str(e))
    
    def _analyze_query_for_knowledge_needs(self, query: str) -> bool:
        """Analyze if query would benefit from knowledge base search"""
        
        # Keywords that indicate knowledge base relevance
        knowledge_keywords = [
            'policy', 'procedure', 'how to', 'instructions', 'steps',
            'documentation', 'guide', 'manual', 'requirements',
            'return', 'refund', 'billing', 'payment', 'API',
            'integration', 'setup', 'configuration', 'troubleshooting'
        ]
        
        query_lower = query.lower()
        
        # Check for knowledge-relevant keywords
        for keyword in knowledge_keywords:
            if keyword in query_lower:
                return True
        
        # Check for question patterns that suggest information retrieval
        question_patterns = [
            'what is', 'how do', 'how can', 'where is', 'when does',
            'what are the steps', 'how to', 'what\'s the process'
        ]
        
        for pattern in question_patterns:
            if pattern in query_lower:
                return True
        
        return False
    
    def _generate_enhanced_response(self, 
                                  query: str, 
                                  customer_context: CustomerContext,
                                  knowledge_results: List[SearchResult],
                                  conversation_id: str) -> Dict[str, Any]:
        """Generate response enhanced with knowledge base information"""
        
        if knowledge_results:
            # RAG-enhanced response with knowledge base information
            return self._create_knowledge_enhanced_response(
                query, customer_context, knowledge_results, conversation_id
            )
        else:
            # Standard response without knowledge enhancement
            return self._create_standard_response(
                query, customer_context, conversation_id
            )
    
    def _create_knowledge_enhanced_response(self, 
                                          query: str,
                                          customer_context: CustomerContext,
                                          knowledge_results: List[SearchResult],
                                          conversation_id: str) -> Dict[str, Any]:
        """Create response enhanced with knowledge base content"""
        
        # Build context from knowledge base results
        knowledge_context = []
        citations = []
        
        for result in knowledge_results:
            knowledge_context.append(result.content)
            citations.append({
                "source": result.citation,
                "relevance": result.relevance_score,
                "classification": result.metadata.classification,
                "department": result.metadata.department
            })
        
        # Generate response based on query type and knowledge
        response = self._generate_contextual_response(query, knowledge_context, customer_context)
        
        # Track that this was RAG-enhanced
        self.metrics["rag_enhanced_responses"] += 1
        
        return {
            "success": True,
            "response": response,
            "knowledge_enhanced": True,
            "sources": citations,
            "knowledge_base_used": True,
            "escalated": False
        }
    
    def _create_standard_response(self, 
                                query: str,
                                customer_context: CustomerContext,
                                conversation_id: str) -> Dict[str, Any]:
        """Create standard response without knowledge enhancement"""
        
        # Generate response based on query patterns
        query_lower = query.lower()
        
        if "password" in query_lower or "login" in query_lower:
            response = f"Hi {customer_context.customer_id}, I can help you with password issues. To reset your password, please visit our self-service portal or use the 'Forgot Password' link on the login page. You'll receive a reset email within 5 minutes."
        
        elif "billing" in query_lower or "charge" in query_lower:
            tier_message = f"As a {customer_context.subscription_tier} customer, " if customer_context.subscription_tier != "Standard" else ""
            response = f"I understand your billing concern. {tier_message}For billing inquiries, I recommend checking your account dashboard first. If you still need assistance, I can escalate this to our billing specialists who can provide detailed account information."
        
        elif "technical" in query_lower or "error" in query_lower or "crash" in query_lower:
            response = "I'm sorry you're experiencing technical difficulties. Let's troubleshoot this together: 1) Try refreshing the application, 2) Clear your browser cache, 3) Restart the app. If the problem persists, I'll connect you with our technical support team for further assistance."
        
        else:
            response = f"Thank you for contacting TechCorp support, {customer_context.customer_id}. I'm here to help with any questions or concerns. Could you please provide more details about your specific issue so I can assist you better?"
        
        return {
            "success": True,
            "response": response,
            "knowledge_enhanced": False,
            "sources": [],
            "knowledge_base_used": False,
            "escalated": False
        }
    
    def _generate_contextual_response(self, 
                                    query: str, 
                                    knowledge_context: List[str],
                                    customer_context: CustomerContext) -> str:
        """Generate contextual response using knowledge base information"""
        
        # Combine knowledge context into coherent information
        relevant_info = "\n".join(knowledge_context[:2])  # Use top 2 most relevant
        
        query_lower = query.lower()
        
        # Generate response based on query type with knowledge enhancement
        if "return" in query_lower or "refund" in query_lower:
            response = f"Based on our current policies, here's what I can tell you about returns and refunds:\n\n{relevant_info[:300]}..."
            
            if customer_context.subscription_tier == "Enterprise":
                response += "\n\nAs an Enterprise customer, you may have additional return options. Let me connect you with our Enterprise support team for personalized assistance."
        
        elif "api" in query_lower or "integration" in query_lower:
            response = f"Here's the information about our API integration:\n\n{relevant_info[:300]}..."
            response += "\n\nFor additional technical support with API integration, I can connect you with our developer relations team."
        
        elif "billing" in query_lower or "payment" in query_lower:
            response = f"Here's information about our billing and payment processes:\n\n{relevant_info[:300]}..."
            response += "\n\nIf you need specific account assistance, I can escalate this to our billing specialists."
        
        elif "password" in query_lower or "login" in query_lower:
            response = f"Here are the current password reset procedures:\n\n{relevant_info[:300]}..."
            response += "\n\nIf you continue to have trouble accessing your account, I can escalate this to our technical support team."
        
        else:
            # General knowledge-based response
            response = f"Based on our documentation, here's relevant information for your question:\n\n{relevant_info[:300]}..."
            response += "\n\nIf you need additional assistance or have specific questions about your account, please let me know."
        
        return response
    
    def _generate_fallback_response(self, query: str, conversation_id: str, error: str) -> Dict[str, Any]:
        """Generate fallback response when RAG enhancement fails"""
        
        response = "I'm currently experiencing some technical difficulties accessing our knowledge base. However, I'm still here to help you. For immediate assistance, please contact our support team directly, or I can escalate your request to a human agent."
        
        return {
            "success": True,
            "response": response,
            "knowledge_enhanced": False,
            "sources": [],
            "knowledge_base_used": False,
            "escalated": True,
            "fallback": True,
            "error": error
        }
    
    def _update_metrics(self, response_time: float, knowledge_enhanced: bool):
        """Update agent performance metrics"""
        
        self.metrics["total_conversations"] += 1
        
        # Update average response time
        total_conversations = self.metrics["total_conversations"]
        current_avg = self.metrics["average_response_time"]
        self.metrics["average_response_time"] = (
            (current_avg * (total_conversations - 1) + response_time) / total_conversations
        )
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Get current agent performance metrics"""
        
        # Calculate enhancement rate
        enhancement_rate = 0.0
        if self.metrics["total_conversations"] > 0:
            enhancement_rate = self.metrics["rag_enhanced_responses"] / self.metrics["total_conversations"]
        
        return {
            **self.metrics,
            "rag_enhancement_rate": enhancement_rate,
            "rag_service_available": self.rag_available,
            "last_updated": datetime.now().isoformat()
        }

def main():
    """Main function for RAG-enhanced customer service agent"""
    print("=== TechCorp RAG-Enhanced Customer Service Agent ===")
    print("Features: Enterprise Knowledge Base, Citation Tracking, Performance Monitoring")
    print("Commands: 'metrics' for performance stats, 'quit' to exit\n")
    
    # Initialize RAG-enhanced agent
    try:
        agent = RAGEnhancedCustomerAgent()
        print("✅ RAG-Enhanced Customer Service Agent initialized successfully")
        
        if agent.rag_available:
            print("✅ Enterprise Knowledge Base connected and ready")
        else:
            print("⚠️  Knowledge Base unavailable - using fallback responses")
            
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Interactive agent testing
    session_id = str(uuid.uuid4())
    print("\n🎯 Ready to handle customer queries with enterprise knowledge!")
    print("Try queries about: policies, API integration, billing, troubleshooting")
    
    while True:
        try:
            query = input("\nCustomer Query: ").strip()
            
            if query.lower() in ['quit', 'exit']:
                print("\n📊 Final Agent Metrics:")
                metrics = agent.get_agent_metrics()
                print(f"Total Conversations: {metrics['total_conversations']}")
                print(f"RAG-Enhanced Responses: {metrics['rag_enhanced_responses']}")
                print(f"Knowledge Base Queries: {metrics['knowledge_base_queries']}")
                print(f"Average Response Time: {metrics['average_response_time']:.2f}s")
                print(f"RAG Enhancement Rate: {metrics['rag_enhancement_rate']:.1%}")
                print("Goodbye!")
                break
            
            if query.lower() == 'metrics':
                print("\n📈 Current Agent Performance:")
                metrics = agent.get_agent_metrics()
                for key, value in metrics.items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.3f}")
                    else:
                        print(f"  {key}: {value}")
                continue
            
            if not query:
                continue
            
            # Get user role for testing access control
            user_role = input("User Role (customer_service): ").strip() or "customer_service"
            
            # Create customer context
            customer_context = CustomerContext(
                customer_id=f"CUST-{uuid.uuid4().hex[:8].upper()}",
                subscription_tier="Premium",
                conversation_history=[],
                session_id=session_id
            )
            
            print(f"🔄 Processing query with RAG enhancement (role: {user_role})...")
            
            # Process query with RAG enhancement
            start_time = time.time()
            result = agent.handle_customer_query(query, customer_context, user_role)
            total_time = time.time() - start_time
            
            # Display results
            print(f"\n💬 Agent Response:")
            print(result['response'])
            
            # Show enhancement details
            if result.get('knowledge_enhanced', False):
                print(f"\n📚 Knowledge Enhancement:")
                print(f"  ✅ Enhanced with {result['knowledge_sources_count']} knowledge sources")
                print(f"  📖 Sources used:")
                for i, source in enumerate(result.get('sources', []), 1):
                    print(f"    {i}. {source['source']} (relevance: {source['relevance']:.2f})")
                    print(f"       Department: {source['department']}, Classification: {source['classification']}")
            else:
                print(f"\n📝 Standard Response:")
                if agent.rag_available:
                    print("  ℹ️  Query didn't require knowledge base enhancement")
                else:
                    print("  ⚠️  Knowledge base unavailable - using standard responses")
            
            # Show performance metrics
            print(f"\n⏱️  Performance:")
            print(f"  Response Time: {total_time:.2f}s")
            print(f"  Service Response Time: {result.get('response_time', 0):.2f}s")
            print(f"  Conversation ID: {result.get('conversation_id', 'N/A')}")
            
            if result.get('escalated', False):
                print(f"  🚀 Escalated: {result.get('fallback', False) and 'Technical issues' or 'Complex query'}")
                
        except KeyboardInterrupt:
            print("\n\nShutting down agent...")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()