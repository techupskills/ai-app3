#!/usr/bin/env python3
# Lab 3: Simple MCP Server - Create a basic AI service API

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

# Create the FastAPI app
app = FastAPI(title="Simple MCP Server", version="1.0.0")

# Request model
class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"

# Response model  
class ChatResponse(BaseModel):
    response: str
    user_id: str

class SimpleMCPService:
    """A simple Model Context Protocol service"""
    
    def __init__(self):
        self.llm_url = "http://localhost:11434"
        self.model = "llama3.2"
    
    def process_message(self, message: str, user_id: str) -> str:
        """Process a chat message through the LLM"""
        try:
            # Call the LLM
            data = {
                "model": self.model,
                "prompt": f"You are a helpful assistant. User message: {message}",
                "stream": False
            }
            
            response = requests.post(
                f"{self.llm_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return "Sorry, I'm having technical difficulties."
                
        except Exception as e:
            return "I'm currently unavailable. Please try again later."

# Create service instance
mcp_service = SimpleMCPService()

# API endpoints
@app.get("/")
async def root():
    return {"message": "Simple MCP Server is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the AI and get a response"""
    try:
        ai_response = mcp_service.process_message(request.message, request.user_id)
        return ChatResponse(response=ai_response, user_id=request.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Simple MCP Server"}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)