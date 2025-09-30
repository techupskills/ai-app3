#!/usr/bin/env python3

# Lab 3: MCP Architecture for Enterprise Scalability
# Complete implementation - MCP Customer Service Server

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os

# MCP and FastAPI imports
from fastmcp import FastMCP
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import jwt
from pathlib import Path

@dataclass
class ServiceConfig:
    """Configuration for MCP service"""
    service_name: str = "customer_service"
    host: str = "localhost"
    port: int = 8000
    max_requests_per_minute: int = 100
    health_check_interval: int = 30

class AuthenticationMiddleware:
    """Enterprise authentication middleware for MCP services"""
    
    def __init__(self, secret_key: str = "mcp-service-secret"):
        self.secret_key = secret_key
        self.logger = logging.getLogger("mcp_auth")
        
    def authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Validate authentication tokens and return user context"""
        # For demo purposes, we'll use a simple token validation
        # In production, this would integrate with enterprise identity systems
        
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            # For demo, allow requests without auth but with limited permissions
            return {
                "user_id": "anonymous",
                "role": "guest",
                "permissions": ["basic_query"]
            }
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            # In production, validate against enterprise identity provider
            # For demo, accept any non-empty token
            if token:
                return {
                    "user_id": "demo_user",
                    "role": "customer_service",
                    "permissions": ["customer_query", "escalation", "knowledge_search"]
                }
        except Exception as e:
            self.logger.warning(f"Token validation failed: {e}")
        
        raise HTTPException(status_code=401, detail="Invalid authentication token")

class RateLimitMiddleware:
    """Rate limiting middleware for enterprise MCP services"""
    
    def __init__(self, max_requests: int = 100):
        self.max_requests = max_requests
        self.request_counts = {}
        self.window_start = time.time()
        
    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limits"""
        current_time = time.time()
        
        # Reset window every minute
        if current_time - self.window_start > 60:
            self.request_counts.clear()
            self.window_start = current_time
        
        # Count requests for this client
        current_count = self.request_counts.get(client_id, 0)
        
        if current_count >= self.max_requests:
            return False
        
        self.request_counts[client_id] = current_count + 1
        return True

class CircuitBreakerMiddleware:
    """Circuit breaker for downstream service calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def call_with_circuit_breaker(self, service_call):
        """Execute service call with circuit breaker protection"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = service_call()
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e

class MCPCustomerServiceServer:
    """
    Enterprise MCP Server for Customer Service
    
    Features:
    - Service registration and discovery
    - Authentication and authorization
    - Rate limiting and circuit breakers
    - Distributed tracing and monitoring
    - Health checks and metrics
    """
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.app = FastAPI(title="TechCorp Customer Service MCP Server")
        self.mcp = FastMCP()
        
        # Initialize middleware
        self.auth_middleware = AuthenticationMiddleware()
        self.rate_limiter = RateLimitMiddleware(config.max_requests_per_minute)
        self.circuit_breaker = CircuitBreakerMiddleware()
        
        # Setup logging
        self.setup_logging()
        
        # Setup FastAPI middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup MCP tools and endpoints
        self.setup_mcp_tools()
        self.setup_health_endpoints()
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }
        
        self.logger.info(f"MCP Customer Service Server initialized on port {config.port}")
    
    def setup_logging(self):
        """Setup structured logging for enterprise monitoring"""
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("mcp_server")
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # File handler
        file_handler = logging.FileHandler('logs/mcp_server.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def setup_mcp_tools(self):
        """Register MCP tools for customer service operations"""
        
        @self.mcp.tool()
        async def handle_customer_query(query: str, customer_id: str = "unknown", correlation_id: str = None) -> Dict[str, Any]:
            """MCP tool implementation for customer query handling"""
            if not correlation_id:
                correlation_id = str(uuid.uuid4())
            
            start_time = time.time()
            
            self.logger.info(f"Processing customer query", extra={
                "correlation_id": correlation_id,
                "customer_id": customer_id,
                "query_length": len(query)
            })
            
            try:
                # Simulate customer service processing
                response = await self.process_customer_query(query, customer_id, correlation_id)
                
                # Update metrics
                response_time = time.time() - start_time
                self.update_metrics(True, response_time)
                
                return {
                    "success": True,
                    "response": response,
                    "correlation_id": correlation_id,
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                # Handle errors gracefully
                self.logger.error(f"Error processing query: {str(e)}", extra={
                    "correlation_id": correlation_id,
                    "error_type": type(e).__name__
                })
                
                self.update_metrics(False, time.time() - start_time)
                
                return {
                    "success": False,
                    "error": str(e),
                    "correlation_id": correlation_id,
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.mcp.tool()
        async def escalate_to_human(conversation_id: str, reason: str) -> Dict[str, Any]:
            """MCP tool for escalating conversations to human agents"""
            
            self.logger.info(f"Escalating conversation {conversation_id}: {reason}")
            
            # Simulate escalation process
            ticket_id = f"ESC-{int(time.time())}"
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "estimated_wait_time": "2-3 minutes",
                "escalation_reason": reason,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.mcp.tool()
        async def search_knowledge_base(query: str, max_results: int = 5) -> Dict[str, Any]:
            """MCP tool for searching enterprise knowledge base"""
            
            self.logger.info(f"Searching knowledge base: {query}")
            
            # Simulate knowledge base search
            mock_results = [
                {
                    "content": "Password reset instructions: Use forgot password link, check email, follow reset instructions",
                    "source": "KB-001-Password-Reset",
                    "relevance": 0.9
                },
                {
                    "content": "Billing support: Check account dashboard, contact billing team for disputes",
                    "source": "KB-002-Billing-Support",
                    "relevance": 0.8
                }
            ]
            
            return {
                "success": True,
                "results": mock_results[:max_results],
                "total_found": len(mock_results),
                "query": query
            }
    
    def setup_health_endpoints(self):
        """Setup health check and metrics endpoints"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint for load balancers"""
            return {
                "status": "healthy",
                "service": self.config.service_name,
                "version": "1.0.0",
                "uptime": time.time() - self.start_time,
                "circuit_breaker_state": self.circuit_breaker.state,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/metrics")
        async def get_metrics():
            """Metrics endpoint for monitoring systems"""
            return {
                "service_metrics": self.metrics,
                "circuit_breaker": {
                    "state": self.circuit_breaker.state,
                    "failure_count": self.circuit_breaker.failure_count
                },
                "rate_limiting": {
                    "max_requests_per_minute": self.config.max_requests_per_minute,
                    "current_requests": sum(self.rate_limiter.request_counts.values())
                },
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/ready")
        async def readiness_check():
            """Readiness check for Kubernetes"""
            # Check if service is ready to handle requests
            if self.circuit_breaker.state == "OPEN":
                raise HTTPException(status_code=503, detail="Service not ready - circuit breaker open")
            
            return {"status": "ready", "timestamp": datetime.now().isoformat()}
    
    async def process_customer_query(self, query: str, customer_id: str, correlation_id: str) -> str:
        """Process customer query with enterprise patterns"""
        
        # Simulate different types of responses based on query content
        query_lower = query.lower()
        
        if "password" in query_lower or "login" in query_lower:
            return "To reset your password, please visit our self-service portal or use the 'Forgot Password' link on the login page. You'll receive a reset email within 5 minutes."
        
        elif "billing" in query_lower or "charge" in query_lower:
            return "I understand your billing concern. For billing inquiries, I recommend checking your account dashboard first. If you still need assistance, I can escalate this to our billing specialists."
        
        elif "technical" in query_lower or "error" in query_lower or "crash" in query_lower:
            return "I'm sorry you're experiencing technical difficulties. Let's troubleshoot: 1) Try refreshing the application, 2) Clear your browser cache, 3) Restart the app. If the problem persists, I'll connect you with technical support."
        
        else:
            return "Thank you for contacting TechCorp support. I'm here to help with any questions or concerns. Could you please provide more details about your specific issue?"
    
    def update_metrics(self, success: bool, response_time: float):
        """Update service performance metrics"""
        self.metrics["total_requests"] += 1
        
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
        
        # Update average response time
        total_requests = self.metrics["total_requests"]
        current_avg = self.metrics["average_response_time"]
        self.metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def register_with_service_registry(self):
        """Register this service instance with the service registry"""
        registration_data = {
            "service_name": self.config.service_name,
            "host": self.config.host,
            "port": self.config.port,
            "health_check_url": f"http://{self.config.host}:{self.config.port}/health",
            "metrics_url": f"http://{self.config.host}:{self.config.port}/metrics",
            "capabilities": ["customer_query_handling", "escalation_management", "knowledge_search"],
            "timestamp": datetime.now().isoformat()
        }
        
        # In production, this would register with actual service discovery system
        self.logger.info(f"Service registered: {registration_data}")
        
        # Save registration info for client discovery
        Path("mcp_services").mkdir(exist_ok=True)
        with open("mcp_services/active_services.json", "w") as f:
            json.dump({"services": [registration_data]}, f, indent=2)
    
    async def start_server(self):
        """Start the MCP server with enterprise configuration"""
        self.start_time = time.time()
        
        # Register with service discovery
        self.register_with_service_registry()
        
        # Mount MCP application
        self.app.mount("/mcp", self.mcp.create_app())
        
        # Start server
        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        
        self.logger.info(f"Starting MCP server on {self.config.host}:{self.config.port}")
        await server.serve()

def main():
    """Main function to start enterprise MCP customer service server"""
    print("=== TechCorp MCP Customer Service Server ===")
    print("Enterprise Features: Auth, Rate Limiting, Circuit Breakers, Monitoring")
    
    # Get port from environment variable for multiple instances
    port = int(os.environ.get("MCP_PORT", 8000))
    
    # Initialize server configuration
    config = ServiceConfig(
        service_name="customer_service",
        host="localhost",
        port=port,
        max_requests_per_minute=100
    )
    
    # Create and start server
    server = MCPCustomerServiceServer(config)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\nShutting down MCP server...")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()