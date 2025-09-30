#!/usr/bin/env python3
# Lab 1: Simple LLM Integration - Learn the basics in 10 minutes

import requests
import json

class SimpleLLMService:
    """A basic LLM service that talks to Ollama"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3.2"
    
    def generate_response(self, prompt):
        """Send a prompt to the LLM and get a response"""
        try:
            # Prepare the request
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            # Make the API call
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=30
            )
            
            # Return the response
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Connection error: {str(e)}"

# Example usage
if __name__ == "__main__":
    llm = SimpleLLMService()
    
    # Test the service
    prompt = "What is artificial intelligence?"
    print(f"Question: {prompt}")
    print(f"Answer: {llm.generate_response(prompt)}")