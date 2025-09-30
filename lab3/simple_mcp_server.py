#!/usr/bin/env python3
# Lab 3: Simple MCP Server - Build an API for your AI service

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

# TODO: Create the FastAPI app with title and version
app = FastAPI()

# TODO: Define request model with message and user_id fields
class ChatRequest(BaseModel):
    pass

# TODO: Define response model with response and user_id fields
class ChatResponse(BaseModel):
    pass

class SimpleMCPService:
    """A simple Model Context Protocol service"""
    
    def __init__(self):
        # TODO: Set up LLM connection details
        self.llm_url = ""
        self.model = ""
    
    def process_message(self, message: str, user_id: str) -> str:
        """Process a chat message through the LLM"""
        try:
            # TODO: Create the LLM request data
            data = {
                # Fill in model, prompt, and stream fields
            }
            
            # TODO: Make POST request to LLM
            response = requests.post(
                # Complete the URL and parameters
            )
            
            # TODO: Return the LLM response or error message
            if response.status_code == 200:
                return  # Extract response from JSON
            else:
                return "Sorry, I'm having technical difficulties."
                
        except Exception as e:
            return "I'm currently unavailable. Please try again later."

# Create service instance
mcp_service = SimpleMCPService()

# TODO: Create API endpoints
@app.get("/")
async def root():
    # Return a welcome message
    pass

@app.post("/chat")  # TODO: Add response_model
async def chat(request: ChatRequest):
    """Send a message to the AI and get a response"""
    # TODO: Process the message and return ChatResponse
    pass

@app.get("/health")
async def health_check():
    # Return health status
    pass

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)