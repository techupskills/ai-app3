# Simple AI Workshop - Learn AI Development in 6 Easy Labs

**Duration**: 60-75 minutes total  
**Focus**: Core AI concepts without complexity  
**Audience**: Developers new to AI

---

## Lab 1: Basic LLM Integration (10 minutes)

**Goal**: Call an AI language model and get responses

**What you'll build**: A simple service that sends prompts to Ollama and gets AI responses

**Key concepts**: API calls, JSON handling, error handling

### Steps:
1. Navigate to `lab1/` directory
2. Open `simple_llm_service.py`
3. Fill in the TODOs:
   - Set `base_url` to `"http://localhost:11434"`
   - Set `model` to `"llama3.2"`
   - Complete the data payload
   - Make the POST request
   - Extract and return the response

4. Test your service:
```bash
cd lab1
python simple_llm_service.py
```

**Diff check**: Use `code -d simple_llm_service.py ../extra/lab1-simple_llm_service.py` to compare

---

## Lab 2: Customer Service Agent (12 minutes)

**Goal**: Add knowledge to your AI for better responses

**What you'll build**: An AI agent that knows company information and gives relevant answers

**Key concepts**: Context injection, knowledge bases, prompt engineering

### Steps:
1. Navigate to `lab2/` directory  
2. Open `simple_customer_agent.py`
3. Fill in the TODOs:
   - Set up LLM connection (copy from Lab 1)
   - Create knowledge base with company info
   - Search knowledge for relevant context
   - Build prompt with context + question
   - Call LLM and return response

4. Test your agent:
```bash
cd lab2
python simple_customer_agent.py
```

**Diff check**: `code -d simple_customer_agent.py ../extra/lab2-simple_customer_agent.py`

---

## Lab 3: MCP Server API (12 minutes)

**Goal**: Create a web API for your AI service

**What you'll build**: A FastAPI server that others can call to use your AI

**Key concepts**: REST APIs, request/response models, web services

### Steps:
1. Navigate to `lab3/` directory
2. Open `simple_mcp_server.py`
3. Fill in the TODOs:
   - Create FastAPI app with title
   - Define ChatRequest and ChatResponse models
   - Set up LLM connection
   - Complete the process_message method
   - Create API endpoints (/chat, /health, /)

4. Run your server:
```bash
cd lab3
python simple_mcp_server.py
```

5. Test in browser: `http://localhost:8000/docs`

**Diff check**: `code -d simple_mcp_server.py ../extra/lab3-simple_mcp_server.py`

---

## Lab 4: Simple RAG (12 minutes)

**Goal**: Make your AI search through documents for better answers

**What you'll build**: A Retrieval-Augmented Generation system that finds relevant docs and uses them to answer questions

**Key concepts**: Document search, context retrieval, RAG pattern

### Steps:
1. Navigate to `lab4/` directory
2. Open `simple_rag.py`
3. Fill in the TODOs:
   - Set up LLM connection
   - Add documents to the document store
   - Complete the search_documents method
   - Build context from retrieved documents
   - Create prompt with context + question
   - Generate response with LLM

4. Test your RAG system:
```bash
cd lab4
python simple_rag.py
```

**Diff check**: `code -d simple_rag.py ../extra/lab4-simple_rag.py`

---

## Lab 5: Web Dashboard (10 minutes)

**Goal**: Create a web interface for your AI

**What you'll build**: A Streamlit chat interface where users can talk to your AI

**Key concepts**: Web UIs, chat interfaces, session state

### Steps:
1. Navigate to `lab5/` directory
2. Open `simple_dashboard.py`
3. Fill in the TODOs:
   - Set up AI service connection
   - Create Streamlit title and description
   - Initialize chat history
   - Display chat messages
   - Handle chat input
   - Add sidebar with info and clear button

4. Run your dashboard:
```bash
cd lab5
streamlit run simple_dashboard.py
```

5. Open browser to `http://localhost:8501`

**Diff check**: `code -d simple_dashboard.py ../extra/lab5-simple_dashboard.py`

---

## Lab 6: Containerization (8 minutes)

**Goal**: Package your AI service in a Docker container

**What you'll build**: A Docker image that contains your AI service

**Key concepts**: Containerization, Docker, deployment

### Steps:
1. Navigate to `lab6/` directory
2. Open `simple-Dockerfile` 
3. Fill in the TODOs:
   - Choose Python base image
   - Set working directory
   - Copy and install requirements
   - Copy application code
   - Expose port
   - Set startup command

4. Build your container:
```bash
cd lab6
docker build -f simple-Dockerfile -t my-ai-service .
```

5. Run your container:
```bash
docker run -p 8000:8000 my-ai-service
```

**Diff check**: `code -d simple-Dockerfile ../extra/lab6-simple-Dockerfile`

---

## Workshop Complete! 🎉

**What you've learned**:
- ✅ How to call AI language models
- ✅ How to add knowledge/context to AI responses  
- ✅ How to create APIs for AI services
- ✅ How to implement basic RAG (document search)
- ✅ How to build web interfaces for AI
- ✅ How to containerize AI applications

**Next steps**:
- Try modifying the knowledge base in Lab 2
- Add more endpoints to your API in Lab 3
- Experiment with different document types in Lab 4
- Customize the dashboard UI in Lab 5
- Deploy your container to the cloud

**Total build time**: ~60-75 minutes  
**Lines of code written**: ~100-150 lines  
**Concepts mastered**: Core AI development patterns