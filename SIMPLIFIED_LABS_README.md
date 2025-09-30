# Simplified Labs - Student-Friendly Version

## Overview
This branch contains dramatically simplified versions of the AI workshop labs, designed for 10-12 minute learning sessions.

## Simplification Changes

### Lab 1: Basic LLM Integration
- **Before**: 150+ lines with circuit breakers, enterprise logging, config management
- **After**: 30 lines - just basic API call to Ollama
- **Focus**: Learn how to call an LLM API

### Lab 2: Customer Service Agent  
- **Before**: 100+ lines with interfaces, dependency injection, complex architecture
- **After**: 35 lines - simple knowledge base + LLM calls
- **Focus**: Add context to AI responses

### Lab 3: MCP Server
- **Before**: 200+ lines with enterprise patterns, service discovery, monitoring
- **After**: 40 lines - basic FastAPI server with one endpoint
- **Focus**: Create a simple API for your AI

### Lab 4: RAG Implementation
- **Before**: 150+ lines with vector databases, embeddings, complex retrieval
- **After**: 35 lines - simple text matching and context injection
- **Focus**: Learn retrieval-augmented generation basics

### Lab 5: Streamlit Dashboard
- **Before**: 200+ lines with authentication, components, complex state management
- **After**: 30 lines - basic chat interface
- **Focus**: Build a simple web UI for AI

### Lab 6: Containerization
- **Before**: 50+ line multi-stage Dockerfile with production optimizations
- **After**: 10 lines - basic container setup
- **Focus**: Package your AI service

## Key Benefits

1. **Comprehensible**: Students can read and understand the entire implementation
2. **Focused**: Each lab teaches one core concept without distractions
3. **Fast**: Can be completed in 10-12 minutes including explanation
4. **Practical**: Students build working code they can actually use
5. **Progressive**: Each lab builds on the previous one

## File Structure

```
lab1/simple_llm_service.py          # Skeleton with TODOs
extra/lab1-simple_llm_service.py    # Complete implementation

lab2/simple_customer_agent.py       # Skeleton with TODOs  
extra/lab2-simple_customer_agent.py # Complete implementation

... (same pattern for all labs)
```

## Usage

Students work on the skeleton files in `labX/` directories and can use `code -d` to compare with complete implementations in `extra/` directory when needed.