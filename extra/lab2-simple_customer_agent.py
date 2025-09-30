#!/usr/bin/env python3
# Lab 2: Simple Customer Service Agent - Build an AI assistant

import requests
import json

class CustomerServiceAgent:
    """A simple AI customer service agent"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3.2"
        
        # Simple knowledge base
        self.knowledge = {
            "hours": "We're open Monday-Friday 9AM-5PM EST",
            "returns": "You can return items within 30 days with receipt",
            "shipping": "Free shipping on orders over $50",
            "contact": "Email: support@techcorp.com, Phone: 1-800-TECH"
        }
    
    def get_response(self, customer_question):
        """Get AI response with knowledge base context"""
        
        # Check if we have relevant knowledge
        context = ""
        for topic, info in self.knowledge.items():
            if topic.lower() in customer_question.lower():
                context = f"Company info: {info}\n"
        
        # Create prompt with context
        prompt = f"""You are a helpful customer service agent for TechCorp.
{context}
Customer question: {customer_question}
Provide a helpful, professional response:"""
        
        # Call the LLM
        try:
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate", 
                json=data, 
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return "I'm having technical difficulties. Please try again."
                
        except Exception as e:
            return "I'm currently unavailable. Please email support@techcorp.com"

# Example usage
if __name__ == "__main__":
    agent = CustomerServiceAgent()
    
    questions = [
        "What are your hours?",
        "How do I return an item?",
        "What's your shipping policy?"
    ]
    
    for question in questions:
        print(f"Customer: {question}")
        print(f"Agent: {agent.get_response(question)}")
        print("-" * 50)