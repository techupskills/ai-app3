#!/usr/bin/env python3

# Lab 1: Basic LLM coding with Python
# Complete implementation

import requests
import json

def call_ollama(prompt, model="llama3.2:3b", temperature=0.7, max_tokens=100):
    """
    Call the local Ollama API with a prompt
    
    Args:
        prompt: The text prompt to send to the model
        model: The model name to use
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum number of tokens to generate
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response received")
    except requests.exceptions.RequestException as e:
        return f"Error calling Ollama: {e}"

def main():
    """Main function to demonstrate LLM interaction"""
    print("=== Basic LLM Client ===")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("Enter your prompt: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
            
        if not user_input:
            continue
            
        print("\nCalling LLM...")
        response = call_ollama(user_input)
        print(f"\nResponse: {response}\n")
        print("-" * 50)

if __name__ == "__main__":
    main()