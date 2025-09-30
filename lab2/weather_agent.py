#!/usr/bin/env python3

# Lab 2: Building an AI Agent
# This is the skeleton file - merge with ../extra/lab2-weather_agent.py to complete

import requests
import json
import re

class WeatherAgent:
    """A ReAct agent that can get weather information for cities"""
    
    def __init__(self):
        self.model = "llama3.2:3b"
        self.ollama_url = "http://localhost:11434/api/generate"
        
    def get_weather(self, city):
        """
        Tool: Get current weather for a city
        Uses OpenWeatherMap-like API format
        """
        # TODO: Implement weather API call
        # For demo purposes, we'll simulate weather data
        pass
    
    def call_llm(self, prompt):
        """Call the local Ollama LLM"""
        # TODO: Implement LLM call similar to Lab 1
        pass
    
    def extract_action(self, response):
        """Extract action and parameters from LLM response"""
        # TODO: Parse Action: and Action Input: from response
        pass
    
    def run_agent(self, user_query):
        """
        Main agent loop implementing ReAct pattern:
        1. Thought: What should I do?
        2. Action: Use a tool
        3. Observation: See the result
        4. Repeat until done
        """
        # TODO: Implement ReAct loop
        # Use this system prompt:
        system_prompt = """You are a helpful weather assistant. You can get weather information for cities.

Available tools:
- get_weather(city): Get current weather for a city

Use this format:
Thought: [your reasoning]
Action: tool_name
Action Input: {"parameter": "value"}
Observation: [you will see the result here]
... (repeat Thought/Action/Observation as needed)
Final Answer: [your final response to the user]

Begin!"""
        pass

def main():
    """Main function to run the weather agent"""
    # TODO: Create agent instance and run interactive loop
    pass

if __name__ == "__main__":
    main()