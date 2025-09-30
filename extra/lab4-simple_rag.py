#!/usr/bin/env python3
# Lab 4: Simple RAG (Retrieval-Augmented Generation) - Add smart document search

import requests
import json

class SimpleRAGService:
    """A basic RAG service using simple text matching"""
    
    def __init__(self):
        self.llm_url = "http://localhost:11434"
        self.model = "llama3.2"
        
        # Simple document store (in real apps, use a vector database)
        self.documents = [
            {
                "id": "doc1",
                "title": "Company Policy",
                "content": "TechCorp offers 30-day returns, free shipping over $50, and 24/7 support."
            },
            {
                "id": "doc2", 
                "title": "Product Info",
                "content": "Our flagship product is the TechWidget 3000, featuring AI-powered automation."
            },
            {
                "id": "doc3",
                "title": "Support Hours",
                "content": "Customer support is available Monday-Friday 9AM-5PM EST via phone and email."
            }
        ]
    
    def search_documents(self, query: str, max_results: int = 2):
        """Simple text-based document search"""
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            # Simple keyword matching
            if any(word in doc["content"].lower() or word in doc["title"].lower() 
                   for word in query_lower.split()):
                results.append(doc)
        
        return results[:max_results]
    
    def generate_rag_response(self, question: str):
        """Generate response using retrieved documents"""
        
        # Step 1: Retrieve relevant documents
        relevant_docs = self.search_documents(question)
        
        # Step 2: Build context from documents
        context = ""
        if relevant_docs:
            context = "Relevant information:\n"
            for doc in relevant_docs:
                context += f"- {doc['title']}: {doc['content']}\n"
        
        # Step 3: Generate response with context
        prompt = f"""You are a helpful assistant for TechCorp. Use the provided information to answer the question.

{context}

Question: {question}
Answer:"""
        
        try:
            data = {
                "model": self.model,
                "prompt": prompt,
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
                return "I'm having trouble accessing information right now."
                
        except Exception as e:
            return "Service temporarily unavailable. Please try again."

# Example usage
if __name__ == "__main__":
    rag = SimpleRAGService()
    
    questions = [
        "What's your return policy?",
        "Tell me about TechWidget 3000",
        "What are your support hours?"
    ]
    
    for question in questions:
        print(f"Question: {question}")
        print(f"Answer: {rag.generate_rag_response(question)}")
        print("-" * 50)