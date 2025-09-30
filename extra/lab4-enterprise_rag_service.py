#!/usr/bin/env python3

# Lab 4: Enterprise Knowledge Base with RAG
# Complete implementation with enterprise patterns

import os
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml
import hashlib

# RAG and ML imports
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

@dataclass
class DocumentMetadata:
    """Metadata for enterprise document management"""
    source_file: str
    classification: str
    access_roles: List[str]
    department: str
    last_updated: str
    version: str
    chunk_id: str

@dataclass
class SearchResult:
    """Search result with enterprise metadata"""
    content: str
    relevance_score: float
    metadata: DocumentMetadata
    citation: str
    access_granted: bool

class DocumentProcessor:
    """Enterprise document processing with validation and classification"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("document_processor")
        
    def process_document(self, file_path: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process document into chunks with enterprise metadata"""
        
        self.logger.info(f"Processing document: {file_path}")
        
        # Validate document before processing
        if not self.validate_document(file_path, metadata):
            raise ValueError(f"Document validation failed: {file_path}")
        
        # Read document content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Failed to read document {file_path}: {e}")
            raise
        
        # Extract title and sections
        lines = content.split('\n')
        title = ""
        sections = []
        current_section = []
        
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
            elif line.startswith('## ') or line.startswith('### '):
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
                current_section.append(line)
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            sections.append('\n'.join(current_section))
        
        # Create chunks with enterprise metadata
        chunks = []
        chunk_size = self.config.get('processing_config', {}).get('chunk_size', 500)
        
        for i, section in enumerate(sections):
            # Skip empty sections
            if not section.strip():
                continue
            
            # Create chunk with metadata
            chunk_metadata = DocumentMetadata(
                source_file=file_path,
                classification=metadata.get('classification', 'internal'),
                access_roles=metadata.get('access_roles', ['customer_service']),
                department=metadata.get('department', 'unknown'),
                last_updated=metadata.get('last_updated', datetime.now().isoformat()),
                version=metadata.get('version', '1.0'),
                chunk_id=f"{file_path}:chunk:{i}"
            )
            
            chunks.append({
                'content': section.strip(),
                'metadata': chunk_metadata,
                'document_title': title,
                'chunk_index': i
            })
        
        self.logger.info(f"Created {len(chunks)} chunks from {file_path}")
        return chunks
    
    def validate_document(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """Validate document content and metadata"""
        
        # Check file exists and is readable
        if not Path(file_path).exists():
            self.logger.error(f"Document not found: {file_path}")
            return False
        
        # Check required metadata fields
        required_fields = ['classification', 'access_roles', 'department']
        for field in required_fields:
            if field not in metadata:
                self.logger.error(f"Missing required metadata field: {field}")
                return False
        
        # Validate classification levels
        valid_classifications = ['public', 'internal', 'confidential', 'restricted']
        if metadata['classification'] not in valid_classifications:
            self.logger.error(f"Invalid classification: {metadata['classification']}")
            return False
        
        return True

class AccessControlManager:
    """Role-based access control for knowledge base"""
    
    def __init__(self):
        self.role_hierarchy = {
            'admin': ['admin', 'supervisor', 'customer_service', 'guest'],
            'supervisor': ['supervisor', 'customer_service', 'guest'],
            'customer_service': ['customer_service', 'guest'],
            'guest': ['guest']
        }
        
        self.classification_access = {
            'public': ['admin', 'supervisor', 'customer_service', 'guest'],
            'internal': ['admin', 'supervisor', 'customer_service'],
            'confidential': ['admin', 'supervisor'],
            'restricted': ['admin']
        }
        
        self.logger = logging.getLogger("access_control")
        
    def check_access(self, user_role: str, document_classification: str, required_roles: List[str]) -> bool:
        """Check if user has access to document"""
        
        # Check classification-based access
        allowed_roles = self.classification_access.get(document_classification, [])
        if user_role not in allowed_roles:
            return False
        
        # Check if user role is in required roles for this document
        user_allowed_roles = self.role_hierarchy.get(user_role, [user_role])
        
        for required_role in required_roles:
            if required_role in user_allowed_roles:
                return True
        
        return False
    
    def log_access(self, user_id: str, document_id: str, action: str, granted: bool):
        """Log access attempts for audit trail"""
        
        access_log = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "document_id": document_id,
            "action": action,
            "access_granted": granted
        }
        
        # Write to access log
        Path("logs").mkdir(exist_ok=True)
        with open("logs/knowledge_access.log", "a") as f:
            f.write(json.dumps(access_log) + "\n")

class PerformanceMonitor:
    """Performance monitoring for RAG operations"""
    
    def __init__(self):
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_retrieval_time": 0.0,
            "average_relevance_score": 0.0
        }
        self.query_cache = {}
        
    def track_query(self, query: str, response_time: float, results_count: int, relevance_scores: List[float]):
        """Track query performance metrics"""
        
        self.metrics["total_queries"] += 1
        
        # Update average retrieval time
        total_queries = self.metrics["total_queries"]
        current_avg_time = self.metrics["average_retrieval_time"]
        self.metrics["average_retrieval_time"] = (
            (current_avg_time * (total_queries - 1) + response_time) / total_queries
        )
        
        # Update average relevance score
        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            current_avg_relevance = self.metrics["average_relevance_score"]
            self.metrics["average_relevance_score"] = (
                (current_avg_relevance * (total_queries - 1) + avg_relevance) / total_queries
            )
    
    def track_cache_hit(self, query: str):
        """Track cache hit for performance metrics"""
        self.metrics["cache_hits"] += 1
    
    def track_cache_miss(self, query: str):
        """Track cache miss for performance metrics"""
        self.metrics["cache_misses"] += 1
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        cache_hit_rate = 0.0
        total_cache_queries = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        
        if total_cache_queries > 0:
            cache_hit_rate = self.metrics["cache_hits"] / total_cache_queries
        
        return {
            **self.metrics,
            "cache_hit_rate": cache_hit_rate,
            "last_updated": datetime.now().isoformat()
        }

class EnterpriseRAGService:
    """
    Enterprise RAG Service with:
    - Document ingestion pipeline with validation
    - Role-based access control
    - Performance monitoring and optimization
    - Citation tracking and governance
    - Multi-modal document support
    """
    
    def __init__(self, config_path: str = "knowledge_base/data_sources.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.document_processor = DocumentProcessor(self.config)
        self.access_control = AccessControlManager()
        self.performance_monitor = PerformanceMonitor()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize vector database
        self.vector_db = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.vector_db.get_or_create_collection(
            name="enterprise_knowledge",
            metadata={"description": "TechCorp Enterprise Knowledge Base"}
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(
            self.config.get('processing_config', {}).get('embedding_model', 
                                                        'sentence-transformers/all-MiniLM-L6-v2')
        )
        
        self.logger.info("Enterprise RAG Service initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {self.config_path}")
            return {"data_sources": []}
    
    def setup_logging(self):
        """Setup structured logging for enterprise monitoring"""
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("enterprise_rag")
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # File handler
        file_handler = logging.FileHandler('logs/rag_service.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def ingest_documents(self) -> Dict[str, Any]:
        """
        Ingest documents from configured sources
        
        Enterprise features:
        - Batch processing with progress tracking
        - Validation and error handling
        - Metadata preservation
        - Access control setup
        - Version tracking
        """
        
        self.logger.info("Starting document ingestion pipeline")
        
        ingestion_results = {
            "total_documents": 0,
            "processed_documents": 0,
            "failed_documents": 0,
            "total_chunks": 0,
            "errors": []
        }
        
        data_sources = self.config.get('data_sources', [])
        
        for source in data_sources:
            try:
                self.logger.info(f"Processing data source: {source['name']}")
                
                # Process document
                chunks = self.document_processor.process_document(
                    source['path'], 
                    source
                )
                
                # Generate embeddings and store in vector database
                for chunk in chunks:
                    # Generate embedding
                    embedding = self.embedding_model.encode(chunk['content'])
                    
                    # Store in vector database with metadata
                    self.collection.add(
                        embeddings=[embedding.tolist()],
                        documents=[chunk['content']],
                        metadatas=[{
                            "source_file": chunk['metadata'].source_file,
                            "classification": chunk['metadata'].classification,
                            "access_roles": json.dumps(chunk['metadata'].access_roles),
                            "department": chunk['metadata'].department,
                            "last_updated": chunk['metadata'].last_updated,
                            "chunk_id": chunk['metadata'].chunk_id,
                            "document_title": chunk['document_title']
                        }],
                        ids=[chunk['metadata'].chunk_id]
                    )
                
                ingestion_results["processed_documents"] += 1
                ingestion_results["total_chunks"] += len(chunks)
                
            except Exception as e:
                error_msg = f"Failed to process {source['name']}: {str(e)}"
                self.logger.error(error_msg)
                ingestion_results["failed_documents"] += 1
                ingestion_results["errors"].append(error_msg)
        
        ingestion_results["total_documents"] = len(data_sources)
        
        self.logger.info(f"Ingestion complete: {ingestion_results}")
        return ingestion_results
    
    def search_knowledge(self, 
                        query: str, 
                        user_role: str = "customer_service",
                        max_results: int = 5,
                        relevance_threshold: float = 0.7) -> List[SearchResult]:
        """
        Search knowledge base with enterprise controls
        
        Features:
        - Semantic and keyword search combination
        - Role-based result filtering
        - Citation generation
        - Performance tracking
        - Access logging
        """
        
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        self.logger.info(f"Knowledge search query: {query[:100]}...", extra={
            "query_id": query_id,
            "user_role": user_role
        })
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Search vector database
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=max_results * 2,  # Get more results for filtering
                include=["documents", "metadatas", "distances"]
            )
            
            # Process and filter results
            search_results = []
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            )):
                # Convert distance to similarity score
                relevance_score = 1.0 - distance
                
                # Skip results below threshold
                if relevance_score < relevance_threshold:
                    continue
                
                # Create document metadata object
                doc_metadata = DocumentMetadata(
                    source_file=metadata['source_file'],
                    classification=metadata['classification'],
                    access_roles=json.loads(metadata['access_roles']),
                    department=metadata['department'],
                    last_updated=metadata['last_updated'],
                    version="1.0",
                    chunk_id=metadata['chunk_id']
                )
                
                # Check access control
                access_granted = self.access_control.check_access(
                    user_role,
                    doc_metadata.classification,
                    doc_metadata.access_roles
                )
                
                if access_granted:
                    # Create citation
                    citation = self._create_citation(doc_metadata, doc)
                    
                    # Create search result
                    search_result = SearchResult(
                        content=doc,
                        relevance_score=relevance_score,
                        metadata=doc_metadata,
                        citation=citation,
                        access_granted=True
                    )
                    
                    search_results.append(search_result)
                    
                    # Log citation usage
                    self._log_citation_usage(user_role, query_id, citation)
                
                # Log access attempt
                self.access_control.log_access(
                    user_role, 
                    metadata['chunk_id'], 
                    "search", 
                    access_granted
                )
                
                # Limit results
                if len(search_results) >= max_results:
                    break
            
            # Track performance metrics
            response_time = time.time() - start_time
            relevance_scores = [r.relevance_score for r in search_results]
            self.performance_monitor.track_query(query, response_time, len(search_results), relevance_scores)
            
            self.logger.info(f"Search completed: {len(search_results)} results", extra={
                "query_id": query_id,
                "response_time": response_time,
                "results_count": len(search_results)
            })
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}", extra={"query_id": query_id})
            return []
    
    def _create_citation(self, metadata: DocumentMetadata, chunk_content: str) -> str:
        """Create proper citation for search result"""
        # Create standardized citation format
        source_name = Path(metadata.source_file).stem
        return f"{source_name}:{metadata.department}:{metadata.last_updated[:10]}"
    
    def _log_citation_usage(self, user_role: str, query_id: str, citation: str):
        """Log citation usage for compliance tracking"""
        citation_log = {
            "timestamp": datetime.now().isoformat(),
            "query_id": query_id,
            "user_role": user_role,
            "citation": citation,
            "action": "citation_generated"
        }
        
        Path("logs").mkdir(exist_ok=True)
        with open("logs/citation_tracking.log", "a") as f:
            f.write(json.dumps(citation_log) + "\n")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health and performance status"""
        
        # Check vector database health
        try:
            collection_count = self.collection.count()
            db_healthy = True
        except Exception as e:
            collection_count = 0
            db_healthy = False
        
        # Get performance metrics
        performance_metrics = self.performance_monitor.get_metrics()
        
        # Save performance metrics to file
        Path("metrics").mkdir(exist_ok=True)
        with open("metrics/rag_performance.json", "w") as f:
            json.dump(performance_metrics, f, indent=2)
        
        return {
            "status": "healthy" if db_healthy else "degraded",
            "vector_database": {
                "healthy": db_healthy,
                "document_count": collection_count
            },
            "performance_metrics": performance_metrics,
            "embedding_model": self.embedding_model.get_sentence_embedding_dimension(),
            "last_updated": datetime.now().isoformat()
        }

def main():
    """Main function for enterprise RAG service"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TechCorp Enterprise RAG Service")
    parser.add_argument("--mode", choices=["ingest", "search", "health"], 
                       default="search", help="Operation mode")
    args = parser.parse_args()
    
    print("=== TechCorp Enterprise Knowledge Base ===")
    print("Enterprise Features: RBAC, Performance Monitoring, Citation Tracking")
    
    # Initialize RAG service
    try:
        rag_service = EnterpriseRAGService()
        print("✅ Enterprise RAG Service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG service: {e}")
        return
    
    if args.mode == "ingest":
        print("\n📚 Starting document ingestion pipeline...")
        results = rag_service.ingest_documents()
        print(f"✅ Ingestion complete: {results['processed_documents']}/{results['total_documents']} documents")
        print(f"📄 Total chunks created: {results['total_chunks']}")
        if results['errors']:
            print(f"⚠️  Errors: {len(results['errors'])}")
        
    elif args.mode == "health":
        print("\n🔍 Checking service health...")
        health = rag_service.get_health_status()
        print(json.dumps(health, indent=2))
        
    else:  # search mode
        print(f"\n🔍 Knowledge base ready for search")
        print("Available user roles: admin, supervisor, customer_service, guest")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                query = input("Search Query: ").strip()
                
                if query.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Get user role for access control testing
                user_role = input("User Role (customer_service): ").strip() or "customer_service"
                
                print(f"🔄 Searching knowledge base as '{user_role}'...")
                
                # Search knowledge base
                start_time = time.time()
                results = rag_service.search_knowledge(query, user_role, max_results=3)
                search_time = time.time() - start_time
                
                if results:
                    print(f"\n📚 Found {len(results)} relevant documents:")
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. {result.citation}")
                        print(f"   Relevance: {result.relevance_score:.2f}")
                        print(f"   Classification: {result.metadata.classification}")
                        print(f"   Content: {result.content[:200]}...")
                else:
                    print("❌ No relevant documents found or access denied")
                
                print(f"\n⏱️  Search completed in {search_time:.2f}s")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ Search error: {e}")

if __name__ == "__main__":
    main()