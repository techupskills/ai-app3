# Lab 2: Production Agent Architecture

**Purpose:** Build a customer service agent using enterprise architecture patterns with proper separation of concerns, dependency injection, and comprehensive error handling.

**Time:** 15 minutes

**Business Context:** Create TechCorp's intelligent customer service agent that can handle common support requests, escalate complex issues, and maintain audit trails for compliance.

## Steps

1. **Review the enterprise architecture** - Examine the service layer pattern:
   ```bash
   ls -la services/
   cat services/__init__.py
   ```

2. **Create the customer service agent** - Build with clean architecture:
   ```bash
   code customer_service_agent.py
   ```

3. **Implement enterprise patterns** - Use diff view to understand production architecture:
   ```bash
   code -d ../extra/lab2-customer_service_agent.py customer_service_agent.py
   ```
   **Key enterprise patterns to observe:**
   - Dependency injection for testability
   - Service layer separation of concerns
   - Comprehensive error handling with fallbacks
   - Structured logging for audit trails
   - Performance monitoring and metrics
   - Input validation and security checks

4. **Test the customer service agent**
   ```bash
   python customer_service_agent.py
   ```
   
5. **Try enterprise scenarios:**
   - **Account Issues:** "I can't access my account"
   - **Billing Questions:** "Why was I charged twice?"
   - **Technical Support:** "My application keeps crashing"
   - **Escalation Test:** "I want to speak to your manager immediately!"

6. **Review audit logs and metrics:**
   ```bash
   tail logs/customer_service.log
   cat metrics/agent_performance.json
   ```

7. **Test error handling** - Try invalid inputs, simulate service failures

8. **Run unit tests** (optional):
   ```bash
   python -m pytest tests/test_customer_service_agent.py -v
   ```

**Enterprise Architecture Patterns Demonstrated:**
- **Service Layer Pattern:** Clear separation between business logic and infrastructure
- **Dependency Injection:** Loose coupling for testability and flexibility  
- **Repository Pattern:** Abstract data access for different knowledge sources
- **Circuit Breaker:** Resilience against downstream service failures
- **Observer Pattern:** Event-driven logging and monitoring
- **Strategy Pattern:** Different escalation strategies based on issue type
- **Decorator Pattern:** Cross-cutting concerns like logging and metrics

**Production Features:**
- Role-based access control simulation
- Session management and conversation context
- Performance SLA monitoring (response time < 2s)
- Automatic escalation rules
- Compliance audit logging
- Cost tracking per conversation

**Expected Outcome:** Enterprise-grade customer service agent that demonstrates clean architecture, handles real business scenarios, and includes production monitoring and compliance features.

**Business Value:** This agent architecture enables TechCorp to automate 80% of routine customer inquiries while maintaining enterprise standards for security, compliance, and performance monitoring.

---
**[END OF LAB]**