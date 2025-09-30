#!/usr/bin/env python3
# Lab 2: Simple Customer Service Agent - Add knowledge to your AI

import requests
import json

class CustomerServiceAgent:
    """A simple AI customer service agent"""
    
    def __init__(self):
        # TODO: Set up connection to LLM
        self.base_url = ""
        self.model = ""
        
        # TODO: Create a simple knowledge base dictionary
        self.knowledge = {
            # Add company information here
            # "topic": "information about topic"
        }
    
    def get_response(self, customer_question):
        """Get AI response with knowledge base context"""
        
        # TODO: Search knowledge base for relevant info
        context = ""
        for topic, info in self.knowledge.items():
            if topic.lower() in customer_question.lower():
                # Add the relevant info to context
                pass
        
        # TODO: Create a prompt that includes:
        # - Role (customer service agent for TechCorp)
        # - Context (relevant company info)
        # - Customer question
        # - Request for helpful response
        prompt = """
        
        """
        
        # TODO: Call the LLM with your prompt
        try:
            data = {
                # Fill in the request data
            }
            
            response = requests.post(
                # Complete the API call
            )
            
            # TODO: Return the LLM response or error message
            if response.status_code == 200:
                return  # Extract response from JSON
            else:
                return "I'm having technical difficulties. Please try again."
                
        except Exception as e:
            return "I'm currently unavailable. Please email support@techcorp.com"

# Test your agent
if __name__ == "__main__":
    agent = CustomerServiceAgent()
    
    question = "What are your hours?"
    print(f"Customer: {question}")
    print(f"Agent: {agent.get_response(question)}")