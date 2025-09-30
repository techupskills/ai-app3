#!/usr/bin/env python3
# Lab 5: Simple Streamlit Dashboard - Build a web interface for your AI

import streamlit as st
import requests
import json

class SimpleDashboard:
    """A basic Streamlit dashboard for AI chat"""
    
    def __init__(self):
        self.llm_url = "http://localhost:11434"
        self.model = "llama3.2"
    
    def call_ai(self, message):
        """Call the AI service"""
        try:
            data = {
                "model": self.model,
                "prompt": f"You are a helpful assistant. User: {message}",
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
                return "AI service error. Please try again."
                
        except Exception as e:
            return "Unable to connect to AI service."

# Create dashboard instance
dashboard = SimpleDashboard()

# Streamlit UI
st.title("🤖 TechCorp AI Assistant")
st.write("Ask me anything!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = dashboard.call_ai(prompt)
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with info
st.sidebar.title("About")
st.sidebar.info("This is a simple AI chat interface built with Streamlit.")
st.sidebar.write(f"Model: {dashboard.model}")

# Clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()