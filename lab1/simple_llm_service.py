#!/usr/bin/env python3
# Lab 1: Simple LLM Integration - Build your first AI service

import requests
import json

class SimpleLLMService:
    """A basic LLM service that talks to Ollama"""
    
    def __init__(self):
        # TODO: Set the base URL for Ollama
        self.base_url = ""
        # TODO: Set the model name  
        self.model = ""
    
    def generate_response(self, prompt):
        """Send a prompt to the LLM and get a response"""
        try:
            # TODO: Create the data payload with model, prompt, and stream=False
            data = {
                # Fill in the required fields
            }
            
            # TODO: Make a POST request to /api/generate
            response = requests.post(
                # Complete the URL and parameters
            )
            
            # TODO: Check if response is successful and return the response text
            if response.status_code == 200:
                return  # Extract the "response" field from JSON
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Connection error: {str(e)}"

# Test your service
if __name__ == "__main__":
    llm = SimpleLLMService()
    
    prompt = "What is artificial intelligence?"
    print(f"Question: {prompt}")
    print(f"Answer: {llm.generate_response(prompt)}")