#!/usr/bin/env python3
# Lab 4: Simple RAG - Add document search to your AI

import requests
import json

class SimpleRAGService:
    """A basic RAG service using simple text matching"""
    
    def __init__(self):
        # TODO: Set up LLM connection
        self.llm_url = ""
        self.model = ""
        
        # TODO: Create a simple document store
        self.documents = [
            # Add documents with id, title, and content
            {
                "id": "doc1",
                "title": "",
                "content": ""
            }
            # Add more documents...
        ]
    
    def search_documents(self, query: str, max_results: int = 2):
        """Simple text-based document search"""
        results = []
        query_lower = query.lower()
        
        # TODO: Search through documents for relevant content
        for doc in self.documents:
            # Check if query words appear in document title or content
            if any(word in doc["content"].lower() or word in doc["title"].lower() 
                   for word in query_lower.split()):
                # Add matching document to results
                pass
        
        return results[:max_results]
    
    def generate_rag_response(self, question: str):
        """Generate response using retrieved documents"""
        
        # TODO: Step 1 - Retrieve relevant documents
        relevant_docs = self.search_documents()
        
        # TODO: Step 2 - Build context from documents
        context = ""
        if relevant_docs:
            context = "Relevant information:\n"
            for doc in relevant_docs:
                # Add document info to context
                pass
        
        # TODO: Step 3 - Create prompt with context and question
        prompt = f"""
        
        """
        
        # TODO: Step 4 - Generate response with LLM
        try:
            data = {
                # Fill in the LLM request
            }
            
            response = requests.post(
                # Complete the API call
            )
            
            # TODO: Return the response or error message
            if response.status_code == 200:
                return  # Extract response from JSON
            else:
                return "I'm having trouble accessing information right now."
                
        except Exception as e:
            return "Service temporarily unavailable. Please try again."

# Test your RAG service
if __name__ == "__main__":
    rag = SimpleRAGService()
    
    question = "What's your return policy?"
    print(f"Question: {question}")
    print(f"Answer: {rag.generate_rag_response(question)}")