#!/bin/bash

# Enterprise AI Applications Workshop Setup Script
# Initializes complete workshop environment with sample data and configurations

echo "🚀 Setting up Enterprise AI Applications Workshop..."
echo "This script will prepare your environment with enterprise sample data and configurations."

# Create directory structure
echo "📁 Creating workshop directory structure..."

# Create missing directories
mkdir -p logs metrics data/backups scripts tests docs

# Create sample metrics files
echo "📊 Creating sample metrics and monitoring data..."

cat > metrics/usage_stats.json << EOF
{
  "total_requests": 1247,
  "total_tokens": 89432,
  "total_cost": 0.178,
  "average_response_time": 1.24,
  "successful_requests": 1198,
  "error_rate": 0.039,
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

cat > metrics/agent_performance.json << EOF
{
  "total_conversations": 456,
  "escalated_conversations": 23,
  "successful_resolutions": 433,
  "average_response_time": 1.85,
  "customer_satisfaction": 4.7,
  "cost_per_conversation": 0.12,
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

cat > metrics/rag_performance.json << EOF
{
  "total_queries": 789,
  "average_retrieval_time": 0.145,
  "cache_hit_rate": 0.83,
  "relevance_score": 0.91,
  "documents_indexed": 42,
  "last_index_update": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

# Create sample log files
echo "📝 Creating sample log files..."

cat > logs/app.log << EOF
$(date -u +%Y-%m-%d\ %H:%M:%S) - enterprise_llm - INFO - Enterprise LLM Service initialized
$(date -u +%Y-%m-%d\ %H:%M:%S) - enterprise_llm - INFO - LLM request initiated - correlation_id: req-123 - prompt_length: 45
$(date -u +%Y-%m-%d\ %H:%M:%S) - enterprise_llm - INFO - LLM request completed successfully - correlation_id: req-123 - tokens_used: 67 - cost: 0.000134
$(date -u +%Y-%m-%d\ %H:%M:%S) - customer_service_agent - INFO - Customer Service Agent initialized with enterprise architecture
$(date -u +%Y-%m-%d\ %H:%M:%S) - customer_service_agent - INFO - Starting conversation conv-456 - customer_id: CUST-789 - query_length: 52
EOF

cat > logs/customer_service.log << EOF
$(date -u +%Y-%m-%d\ %H:%M:%S) - customer_service_agent - INFO - Customer Service Agent initialized with enterprise architecture
$(date -u +%Y-%m-%d\ %H:%M:%S) - customer_service_agent - INFO - Starting conversation conv-123 - customer_id: CUST-ABC123 - query_length: 38
$(date -u +%Y-%m-%d\ %H:%M:%S) - customer_service_agent - INFO - LLM request completed successfully - correlation_id: conv-123 - tokens_used: 89 - cost: 0.000178 
$(date -u +%Y-%m-%d\ %H:%M:%S) - customer_service_agent - WARNING - SLA violation: Response time 2.34s exceeds 2s threshold - conversation_id: conv-124 - response_time: 2.34
EOF

cat > logs/audit.log << EOF
{"timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "conversation_id": "conv-123", "event_type": "customer_interaction", "status": "completed", "customer_id": "CUST-ABC123", "response_time": 1.25}
{"timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "conversation_id": "conv-124", "event_type": "customer_interaction", "status": "escalated", "customer_id": "CUST-DEF456", "escalation_reason": "Complex query"}
{"timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)", "conversation_id": "conv-125", "event_type": "customer_interaction", "status": "completed", "customer_id": "CUST-GHI789", "response_time": 0.89}
EOF

# Create additional enterprise documentation
echo "📚 Creating additional enterprise documentation..."

cat > data/enterprise_docs/security_policies.md << EOF
# TechCorp Security Policies

## Information Security Framework

### Data Classification
- **Public:** Marketing materials, public documentation
- **Internal:** Employee handbook, internal procedures  
- **Confidential:** Customer data, financial information
- **Restricted:** Trade secrets, strategic plans

### Access Control Requirements
- Multi-factor authentication for all systems
- Role-based access control with least privilege principle
- Regular access reviews and certification
- Automated deprovisioning for terminated employees

### Incident Response
- 24/7 security operations center monitoring
- Incident response team activation within 30 minutes
- Customer notification within 72 hours for data breaches
- Post-incident review and remediation tracking

## AI System Security

### Model Security
- Model versioning and integrity verification
- Input validation and sanitization for AI safety
- Output filtering for sensitive information
- Regular security assessments and penetration testing

### Data Protection
- Encryption in transit and at rest (AES-256)
- Tokenization of sensitive customer data
- Secure model training with differential privacy
- Regular backup and disaster recovery testing

Last Updated: January 2024
Classification: Internal
Owner: Chief Information Security Officer
EOF

cat > data/enterprise_docs/compliance_procedures.md << EOF
# TechCorp Compliance Procedures

## Regulatory Compliance

### SOC 2 Type II Compliance
- Annual third-party audits of security controls
- Continuous monitoring of control effectiveness
- Quarterly management review of compliance status
- Employee training on security awareness

### GDPR Compliance
- Data protection impact assessments for new systems
- Customer consent management and tracking
- Right to erasure and data portability procedures
- Data protection officer oversight and reporting

### Industry Standards
- ISO 27001 information security management
- NIST Cybersecurity Framework implementation
- PCI DSS for payment card data protection
- HIPAA compliance for healthcare customers

## AI Ethics and Governance

### Responsible AI Principles
- Fairness and bias mitigation in AI models
- Transparency in AI decision-making processes
- Accountability for AI system outcomes
- Privacy protection in AI data processing

### Model Governance
- AI model approval and change management
- Performance monitoring and drift detection
- Regular model retraining and validation
- Documentation of model decisions and impacts

Last Updated: January 2024
Classification: Internal
Owner: Chief Compliance Officer
EOF

# Create test data for RAG system
echo "🔍 Creating test data for knowledge base..."

cat > data/enterprise_docs/product_documentation.md << EOF
# TechCorp Product Documentation

## Platform Overview

TechCorp's cloud platform provides enterprise customers with scalable, secure infrastructure for business applications.

### Core Services
- **Compute:** Virtual machines, containers, serverless functions
- **Storage:** Object storage, block storage, database services
- **Networking:** Load balancers, VPNs, content delivery networks
- **Security:** Identity management, encryption, monitoring

### Service Level Agreements
- **Uptime:** 99.9% availability guarantee
- **Performance:** Sub-100ms response times for API calls
- **Support:** 24/7 technical support for enterprise customers
- **Recovery:** 4-hour recovery time objective for critical systems

## Integration Guide

### API Authentication
All TechCorp APIs require OAuth 2.0 authentication with JWT tokens.

### Rate Limiting
- Standard tier: 1,000 requests per hour
- Professional tier: 10,000 requests per hour  
- Enterprise tier: Custom limits based on contract

### Error Handling
APIs return standard HTTP status codes with detailed error messages in JSON format.

## Troubleshooting

### Common Issues
- **Authentication failures:** Check token expiration and scopes
- **Rate limiting:** Implement exponential backoff retry logic
- **Network errors:** Verify firewall and proxy configurations
- **Performance issues:** Monitor API response times and optimize queries

Last Updated: January 2024
Classification: Public
Maintained by: Product Engineering Team
EOF

# Create startup verification script
echo "🔧 Creating environment verification script..."

cat > scripts/verify_environment.sh << 'EOF'
#!/bin/bash

echo "🔍 Verifying Enterprise AI Workshop Environment..."

# Check Python installation
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 is installed: $(python3 --version)"
else
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check Ollama installation
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    
    # Check if Llama model is available
    if ollama list | grep -q "llama3.2"; then
        echo "✅ Llama 3.2 model is available"
    else
        echo "⚠️  Llama 3.2 model not found. Run: ollama pull llama3.2:3b"
    fi
else
    echo "❌ Ollama is not installed"
fi

# Check required Python packages
echo "🐍 Checking Python dependencies..."
python3 -c "import streamlit, fastapi, chromadb, sentence_transformers, transformers" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Required Python packages are installed"
else
    echo "⚠️  Some Python packages may be missing. Run: pip install -r requirements.txt"
fi

# Check directory structure
echo "📁 Verifying directory structure..."
for dir in logs metrics data/enterprise_docs config lab1 lab2 lab3 lab4 lab5 lab6; do
    if [ -d "$dir" ]; then
        echo "✅ Directory exists: $dir"
    else
        echo "❌ Missing directory: $dir"
    fi
done

# Check sample data files
echo "📊 Verifying sample data..."
for file in data/enterprise_docs/company_policies.md data/enterprise_docs/technical_documentation.md data/enterprise_docs/faq.md; do
    if [ -f "$file" ]; then
        echo "✅ Sample data exists: $file"
    else
        echo "❌ Missing sample data: $file"
    fi
done

echo ""
echo "🎯 Environment verification complete!"
echo "If all checks passed, you're ready to start the workshop with Lab 1."
EOF

chmod +x scripts/verify_environment.sh

# Create workshop completion tracker
echo "📋 Creating workshop progress tracker..."

cat > scripts/workshop_progress.json << EOF
{
  "workshop_started": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "labs_completed": [],
  "current_lab": null,
  "total_labs": 6,
  "estimated_completion_time": "7 hours",
  "participant_info": {
    "name": "",
    "role": "",
    "company": "",
    "experience_level": ""
  }
}
EOF

# Set permissions
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo "✅ Enterprise AI Applications Workshop setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Run './scripts/verify_environment.sh' to verify your setup"
echo "2. Start with Lab 1: Enterprise LLM Integration"
echo "3. Follow the README.md for detailed instructions"
echo ""
echo "🎯 Workshop Overview:"
echo "- 6 hands-on labs building a complete customer service AI system"
echo "- Enterprise patterns, security, and production deployment"
echo "- Estimated completion time: 7 hours"
echo ""
echo "Happy learning! 🚀"