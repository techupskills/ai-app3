#!/usr/bin/env python3

# Lab 1: Enterprise LLM Integration Patterns
# Complete implementation with enterprise best practices

import requests
import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Optional, Dict, Any
import yaml
from pathlib import Path
import os
from datetime import datetime

@dataclass
class LLMConfig:
    """Configuration for LLM service with enterprise settings"""
    model: str = "llama3.2:3b"
    base_url: str = "http://localhost:11434"
    timeout: int = 30
    max_retries: int = 3
    rate_limit_per_minute: int = 60
    log_level: str = "INFO"

class CircuitBreaker:
    """Circuit breaker pattern for resilience"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
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

class EnterpriseLLMService:
    """Enterprise-grade LLM service with monitoring and resilience"""
    
    def __init__(self, config_path: str = "config/app_config.yaml"):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.get('circuit_breaker', {}).get('failure_threshold', 5),
            recovery_timeout=self.config.get('circuit_breaker', {}).get('recovery_timeout', 60)
        )
        self.usage_stats = {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}
        self.logger.info("Enterprise LLM Service initialized", extra={"service": "llm"})
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # Fallback to default configuration
            return {
                "llm": {"model": "llama3.2:3b", "base_url": "http://localhost:11434", "timeout": 30},
                "logging": {"level": "INFO"},
                "business": {"cost_per_1k_tokens": 0.002}
            }
    
    def setup_logging(self):
        """Setup structured logging with correlation IDs"""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        # Setup logger with custom formatter
        self.logger = logging.getLogger('enterprise_llm')
        self.logger.setLevel(getattr(logging, log_level))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # File handler
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def call_llm(self, prompt: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Call LLM with enterprise patterns:
        - Input validation
        - Request correlation
        - Error handling
        - Usage tracking
        """
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        self.logger.info(f"LLM request initiated", extra={
            "correlation_id": correlation_id,
            "prompt_length": len(prompt)
        })
        
        # Validate input
        if not self.validate_input(prompt):
            error_msg = "Input validation failed"
            self.logger.error(error_msg, extra={"correlation_id": correlation_id})
            return {"error": error_msg, "correlation_id": correlation_id}
        
        try:
            # Use circuit breaker for resilience
            response = self.circuit_breaker.call(self._make_llm_request, prompt)
            
            # Track usage for cost management
            tokens_used = len(prompt.split()) + len(response.get('response', '').split())
            cost = self._calculate_cost(tokens_used)
            self.track_usage(tokens_used, cost)
            
            self.logger.info("LLM request completed successfully", extra={
                "correlation_id": correlation_id,
                "tokens_used": tokens_used,
                "cost": cost
            })
            
            return {
                "response": response.get('response', ''),
                "correlation_id": correlation_id,
                "tokens_used": tokens_used,
                "cost": cost,
                "circuit_breaker_state": self.circuit_breaker.state
            }
            
        except Exception as e:
            self.logger.error(f"LLM request failed: {str(e)}", extra={
                "correlation_id": correlation_id,
                "error_type": type(e).__name__
            })
            return {
                "error": str(e),
                "correlation_id": correlation_id,
                "circuit_breaker_state": self.circuit_breaker.state
            }
    
    def _make_llm_request(self, prompt: str) -> Dict[str, Any]:
        """Make the actual LLM API request"""
        llm_config = self.config.get('llm', {})
        url = f"{llm_config.get('base_url', 'http://localhost:11434')}/api/generate"
        
        payload = {
            "model": llm_config.get('model', 'llama3.2:3b'),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 150
            }
        }
        
        response = requests.post(
            url, 
            json=payload, 
            timeout=llm_config.get('timeout', 30)
        )
        response.raise_for_status()
        return response.json()
    
    def validate_input(self, prompt: str) -> bool:
        """Validate and sanitize input"""
        security_config = self.config.get('security', {})
        max_length = security_config.get('input_max_length', 10000)
        
        if len(prompt) > max_length:
            return False
        
        # Check for potential injection attempts
        suspicious_patterns = ['<script>', '<?php', 'DROP TABLE', 'DELETE FROM']
        prompt_lower = prompt.lower()
        
        for pattern in suspicious_patterns:
            if pattern.lower() in prompt_lower:
                return False
        
        return True
    
    def track_usage(self, tokens_used: int, cost: float):
        """Track token usage for cost management"""
        self.usage_stats["total_requests"] += 1
        self.usage_stats["total_tokens"] += tokens_used
        self.usage_stats["total_cost"] += cost
        
        # Save usage stats to file for monitoring
        Path("metrics").mkdir(exist_ok=True)
        with open("metrics/usage_stats.json", "w") as f:
            json.dump({
                **self.usage_stats,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost based on token usage"""
        cost_per_1k = self.config.get('business', {}).get('cost_per_1k_tokens', 0.002)
        return (tokens_used / 1000) * cost_per_1k
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return service health status"""
        return {
            "status": "healthy" if self.circuit_breaker.state != "OPEN" else "degraded",
            "circuit_breaker_state": self.circuit_breaker.state,
            "total_requests": self.usage_stats["total_requests"],
            "total_cost": self.usage_stats["total_cost"]
        }

def main():
    """Main function demonstrating enterprise LLM service"""
    print("=== TechCorp Customer Support AI - LLM Service ===")
    print("Enterprise patterns: logging, monitoring, resilience")
    print("Type 'quit' to exit, 'health' for status, 'stats' for usage\n")
    
    # Initialize enterprise service
    try:
        service = EnterpriseLLMService()
        print("✅ Enterprise LLM Service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return
    
    # Interactive demonstration
    while True:
        user_input = input("\nCustomer Query: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("\n📊 Final Usage Statistics:")
            print(json.dumps(service.usage_stats, indent=2))
            print("Goodbye!")
            break
        
        if user_input.lower() == 'health':
            print("\n🔍 Service Health Status:")
            print(json.dumps(service.get_health_status(), indent=2))
            continue
            
        if user_input.lower() == 'stats':
            print("\n📈 Usage Statistics:")
            print(json.dumps(service.usage_stats, indent=2))
            continue
            
        if not user_input:
            continue
        
        # Process customer query with enterprise patterns
        correlation_id = str(uuid.uuid4())[:8]
        print(f"🔄 Processing query (ID: {correlation_id})...")
        
        start_time = time.time()
        result = service.call_llm(user_input, correlation_id)
        end_time = time.time()
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            print(f"Circuit Breaker State: {result.get('circuit_breaker_state', 'Unknown')}")
        else:
            print(f"\n💬 Response: {result['response']}")
            print(f"📊 Tokens: {result['tokens_used']}, Cost: ${result['cost']:.4f}")
            print(f"⏱️  Response time: {end_time - start_time:.2f}s")
            print(f"🔧 Circuit Breaker: {result['circuit_breaker_state']}")

if __name__ == "__main__":
    main()