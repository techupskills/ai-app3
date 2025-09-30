#!/usr/bin/env python3
# Lab 5: Simple Streamlit Dashboard - Create a web interface

import streamlit as st
import requests
import json

class SimpleDashboard:
    """A basic Streamlit dashboard for AI chat"""
    
    def __init__(self):
        # TODO: Set up AI service connection
        self.llm_url = ""
        self.model = ""
    
    def call_ai(self, message):
        """Call the AI service"""
        try:
            # TODO: Create the request data for the LLM
            data = {
                # Fill in model, prompt, stream fields
            }
            
            # TODO: Make POST request to AI service
            response = requests.post(
                # Complete the URL and parameters
            )
            
            # TODO: Return AI response or error message
            if response.status_code == 200:
                return  # Extract response from JSON
            else:
                return "AI service error. Please try again."
                
        except Exception as e:
            return "Unable to connect to AI service."

# Create dashboard instance
dashboard = SimpleDashboard()

# TODO: Create Streamlit UI
st.title("")  # Add a title
st.write("")  # Add description

# TODO: Initialize chat history in session state
if "messages" not in st.session_state:
    pass  # Initialize empty messages list

# TODO: Display chat messages from history
for message in st.session_state.messages:
    # Display each message with appropriate role
    pass

# TODO: Create chat input
if prompt := st.chat_input(""):  # Add placeholder text
    # Add user message to chat history
    
    # Display user message
    
    # Get and display AI response
    
    # Add AI response to chat history
    pass

# TODO: Create sidebar with information
st.sidebar.title("")
st.sidebar.info("")

# TODO: Add clear chat button
if st.sidebar.button(""):
    # Clear the chat history
    pass