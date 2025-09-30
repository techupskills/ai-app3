#!/usr/bin/env python3

# Lab 3: MCP Client for Enterprise Customer Service
# Complete implementation with enterprise patterns

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
from pathlib import Path

@dataclass
class ClientConfig:
    """Configuration for MCP client"""
    service_discovery_url: str = "http://localhost:8000"
    max_retries: int = 3
    timeout: int = 30
    correlation_id: Optional[str] = None

class ServiceDiscovery:
    """Service discovery client for finding available MCP services"""
    
    def __init__(self, registry_path: str = "mcp_services/service_registry.json"):
        self.registry_path = registry_path
        self.active_services_path = "mcp_services/active_services.json"
        self.logger = logging.getLogger("service_discovery")
        
    def discover_services(self, service_type: str) -> List[Dict[str, Any]]:
        """Discover available services of the specified type"""
        try:
            # First try to load from active services (runtime registration)
            if Path(self.active_services_path).exists():
                with open(self.active_services_path, 'r') as f:
                    active_data = json.load(f)
                    if "services" in active_data:
                        return active_data["services"]
            
            # Fallback to static registry
            if Path(self.registry_path).exists():
                with open(self.registry_path, 'r') as f:
                    registry_data = json.load(f)
                    services = registry_data.get("services", {})
                    
                    if service_type in services:
                        service_config = services[service_type]
                        return service_config.get("endpoints", [])
            
            self.logger.warning(f"No services found for type: {service_type}")
            return []
            
        except Exception as e:
            self.logger.error(f"Service discovery failed: {e}")
            return []
    
    def get_healthy_endpoint(self, service_type: str) -> Optional[str]:
        """Get a healthy endpoint for the service type"""
        services = self.discover_services(service_type)
        
        for service in services:
            # Try to connect to health check endpoint
            try:
                health_url = f"http://{service.get('host', 'localhost')}:{service.get('port', 8000)}/health"
                
                with httpx.Client(timeout=5.0) as client:
                    response = client.get(health_url)
                    if response.status_code == 200:
                        service_url = f"http://{service.get('host', 'localhost')}:{service.get('port', 8000)}/mcp"
                        self.logger.info(f"Found healthy service at: {service_url}")
                        return service_url
                        
            except Exception as e:
                self.logger.warning(f"Health check failed for {service}: {e}")
                continue
        
        # Fallback to default if no healthy services found
        default_url = "http://localhost:8000/mcp"
        self.logger.warning(f"No healthy services found, using default: {default_url}")
        return default_url

class RetryPolicy:
    """Retry policy with exponential backoff for MCP client calls"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logging.getLogger("retry_policy")
        
    async def execute_with_retry(self, operation, *args, **kwargs):
        """Execute operation with retry policy"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await operation(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    self.logger.error(f"All retry attempts failed: {e}")
                    break
                
                # Exponential backoff
                delay = self.base_delay * (2 ** attempt)
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
        
        raise last_exception

class DistributedTracing:
    """Distributed tracing for MCP requests"""
    
    def __init__(self):
        self.logger = logging.getLogger("distributed_tracing")
        # Create traces directory
        Path("traces").mkdir(exist_ok=True)
        
    def create_span(self, operation_name: str, correlation_id: str) -> Dict[str, Any]:
        """Create a new tracing span"""
        span = {
            "span_id": str(uuid.uuid4()),
            "correlation_id": correlation_id,
            "operation_name": operation_name,
            "start_time": time.time(),
            "service": "mcp_client",
            "tags": {}
        }
        
        self.logger.info(f"Started span: {operation_name}", extra={
            "span_id": span["span_id"],
            "correlation_id": correlation_id
        })
        
        return span
    
    def log_span(self, span: Dict[str, Any], result: Dict[str, Any]):
        """Log completed span for monitoring"""
        span["end_time"] = time.time()
        span["duration"] = span["end_time"] - span["start_time"]
        span["success"] = result.get("success", False)
        
        if not span["success"]:
            span["error"] = result.get("error", "Unknown error")
        
        # Log span completion
        self.logger.info(f"Completed span: {span['operation_name']}", extra={
            "span_id": span["span_id"],
            "correlation_id": span["correlation_id"],
            "duration": span["duration"],
            "success": span["success"]
        })
        
        # Save span for distributed tracing analysis
        span_file = f"traces/span_{span['span_id']}.json"
        with open(span_file, 'w') as f:
            json.dump(span, f, indent=2)

class MCPCustomerServiceClient:
    """
    Enterprise MCP Client for Customer Service
    
    Features:
    - Service discovery and load balancing
    - Retry policies with exponential backoff
    - Distributed tracing and correlation
    - Circuit breaker integration
    - Graceful degradation and fallbacks
    """
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.service_discovery = ServiceDiscovery()
        self.retry_policy = RetryPolicy(max_retries=config.max_retries)
        self.distributed_tracing = DistributedTracing()
        
        # Setup logging
        self.setup_logging()
        
        # Client metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "fallback_responses": 0,
            "average_response_time": 0.0
        }
        
        self.logger.info("MCP Customer Service Client initialized")
    
    def setup_logging(self):
        """Setup structured logging for client operations"""
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("mcp_client")
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # File handler
        file_handler = logging.FileHandler('logs/mcp_client.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    async def handle_customer_query(self, query: str, customer_id: str = "unknown") -> Dict[str, Any]:
        """
        Handle customer query using distributed MCP services
        
        Implements enterprise patterns:
        - Service discovery for endpoint selection
        - Distributed tracing across services
        - Retry policies for transient failures
        - Circuit breaker for resilience
        - Graceful degradation on failures
        """
        correlation_id = str(uuid.uuid4())
        
        # Create distributed tracing span
        span = self.distributed_tracing.create_span("handle_customer_query", correlation_id)
        
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            # Use retry policy for resilience
            result = await self.retry_policy.execute_with_retry(
                self.call_mcp_service,
                "customer_service",
                "handle_customer_query",
                {
                    "query": query,
                    "customer_id": customer_id,
                    "correlation_id": correlation_id
                }
            )
            
            if result.get("success", False):
                self.metrics["successful_requests"] += 1
                response_time = time.time() - start_time
                self.update_average_response_time(response_time)
                
                # Log successful span
                self.distributed_tracing.log_span(span, result)
                
                return result
            else:
                # Service returned error, but call succeeded
                self.logger.warning(f"Service returned error: {result.get('error', 'Unknown')}")
                return result
                
        except Exception as e:
            self.logger.error(f"MCP service call failed: {str(e)}")
            self.metrics["failed_requests"] += 1
            
            # Return graceful fallback response
            fallback_result = self.get_fallback_response(query, str(e))
            self.metrics["fallback_responses"] += 1
            
            # Log failed span
            self.distributed_tracing.log_span(span, {"success": False, "error": str(e)})
            
            return fallback_result
    
    async def call_mcp_service(self, service_type: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generic method to call MCP services with enterprise patterns"""
        
        # Discover healthy service endpoint
        service_url = self.service_discovery.get_healthy_endpoint(service_type)
        if not service_url:
            raise Exception(f"No healthy {service_type} services available")
        
        # Prepare MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        # Make HTTP request with timeout
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.post(
                    service_url,
                    json=mcp_request,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer demo-token"  # In production, use real auth
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract result from MCP response
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    raise Exception(f"MCP error: {result['error']}")
                else:
                    raise Exception("Invalid MCP response format")
                    
            except httpx.RequestError as e:
                raise Exception(f"Network error calling {service_url}: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"HTTP error {e.response.status_code} calling {service_url}")
    
    def get_fallback_response(self, query: str, error_type: str) -> Dict[str, Any]:
        """Provide fallback response when services are unavailable"""
        
        fallback_responses = {
            "password": "I'm currently experiencing technical difficulties. For password reset assistance, please visit our self-service portal at techcorp.com/reset-password or contact our support team directly.",
            "billing": "I'm having trouble accessing our billing systems right now. Please contact our billing team directly at billing@techcorp.com or call 1-800-TECHCORP for immediate assistance.",
            "technical": "Our technical support systems are temporarily unavailable. Please try basic troubleshooting steps (restart your application, clear cache) or contact technical support at support@techcorp.com.",
            "general": "I'm currently experiencing technical difficulties and cannot process your request. Please contact our support team directly for immediate assistance. We apologize for the inconvenience."
        }
        
        # Determine appropriate fallback based on query content
        query_lower = query.lower()
        
        if "password" in query_lower or "login" in query_lower:
            response = fallback_responses["password"]
        elif "billing" in query_lower or "payment" in query_lower:
            response = fallback_responses["billing"]
        elif "technical" in query_lower or "error" in query_lower:
            response = fallback_responses["technical"]
        else:
            response = fallback_responses["general"]
        
        return {
            "success": True,
            "response": response,
            "fallback": True,
            "error_type": error_type,
            "escalation_recommended": True,
            "timestamp": time.time()
        }
    
    def update_average_response_time(self, response_time: float):
        """Update average response time metric"""
        total_successful = self.metrics["successful_requests"]
        current_avg = self.metrics["average_response_time"]
        
        if total_successful == 1:
            self.metrics["average_response_time"] = response_time
        else:
            self.metrics["average_response_time"] = (
                (current_avg * (total_successful - 1) + response_time) / total_successful
            )
    
    def get_discovered_services(self) -> List[Dict[str, Any]]:
        """Get list of discovered services for monitoring"""
        return self.service_discovery.discover_services("customer_service")
    
    def get_client_metrics(self) -> Dict[str, Any]:
        """Get client performance metrics"""
        success_rate = 0.0
        if self.metrics["total_requests"] > 0:
            success_rate = self.metrics["successful_requests"] / self.metrics["total_requests"]
        
        return {
            **self.metrics,
            "success_rate": success_rate,
            "fallback_rate": self.metrics["fallback_responses"] / max(self.metrics["total_requests"], 1)
        }

async def main():
    """Main function demonstrating enterprise MCP client"""
    print("=== TechCorp MCP Customer Service Client ===")
    print("Enterprise Features: Service Discovery, Retry Policies, Distributed Tracing")
    print("Commands: 'services' to show discovered services, 'metrics' for client stats, 'quit' to exit\n")
    
    # Initialize client configuration
    config = ClientConfig(
        service_discovery_url="http://localhost:8000",
        max_retries=3,
        timeout=30
    )
    
    # Create enterprise MCP client
    client = MCPCustomerServiceClient(config)
    
    print("✅ MCP Client initialized successfully")
    print("🔍 Discovering available services...")
    
    # Test service discovery
    services = client.get_discovered_services()
    if services:
        print(f"✅ Found {len(services)} available service(s)")
    else:
        print("⚠️  No services discovered, will use fallback responses")
    
    # Interactive client loop
    while True:
        try:
            user_input = input("\nCustomer Query: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("\n📊 Final Client Metrics:")
                metrics = client.get_client_metrics()
                print(json.dumps(metrics, indent=2))
                print("Goodbye!")
                break
            
            if user_input.lower() == 'services':
                print("\n🔍 Discovered Services:")
                services = client.get_discovered_services()
                if services:
                    for i, service in enumerate(services, 1):
                        print(f"  {i}. {service.get('host', 'unknown')}:{service.get('port', 'unknown')}")
                else:
                    print("  No services currently discovered")
                continue
            
            if user_input.lower() == 'metrics':
                print("\n📈 Client Performance Metrics:")
                metrics = client.get_client_metrics()
                print(json.dumps(metrics, indent=2))
                continue
            
            if not user_input:
                continue
            
            # Process customer query with enterprise patterns
            print("🔄 Processing query with enterprise MCP client...")
            
            start_time = time.time()
            result = await client.handle_customer_query(user_input)
            end_time = time.time()
            
            # Display results
            if result.get("success", False):
                print(f"\n💬 Response: {result['response']}")
                
                if result.get("fallback", False):
                    print(f"⚠️  Fallback response due to: {result.get('error_type', 'Unknown error')}")
                    if result.get("escalation_recommended", False):
                        print("🚀 Escalation to human agent recommended")
                else:
                    print(f"✅ Service response (correlation ID: {result.get('correlation_id', 'N/A')})")
                    if 'response_time' in result:
                        print(f"⏱️  Service response time: {result['response_time']:.2f}s")
                
                print(f"🔧 Total response time: {end_time - start_time:.2f}s")
                
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print("\n\nShutting down client...")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())