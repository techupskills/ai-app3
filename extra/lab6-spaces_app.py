#!/usr/bin/env python3

# Lab 6: Production GitHub Spaces Deployment Application
# Complete enterprise deployment with monitoring and scaling

import os
import sys
import logging
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import subprocess
import signal
import threading
import queue

# Import application components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ProductionLogger:
    """Enterprise logging system for production deployment"""
    
    def __init__(self, log_level: str = "INFO"):
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup structured logging with JSON format"""
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('logs/production.log')
            ]
        )
        
        self.logger = logging.getLogger("production_deployment")
        
        # Log startup
        self.logger.info("Production logging system initialized", extra={
            "component": "ProductionLogger",
            "log_level": logging.getLevelName(self.log_level)
        })

class HealthChecker:
    """Health check system for production monitoring"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.logger = logging.getLogger("health_checker")
        self.health_status = {
            "status": "unknown",
            "last_check": None,
            "checks": {}
        }
        self.running = False
    
    def start_health_checks(self):
        """Start continuous health checking"""
        self.running = True
        health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        health_thread.start()
        self.logger.info("Health check system started", extra={
            "check_interval": self.check_interval
        })
    
    def _health_check_loop(self):
        """Continuous health checking loop"""
        while self.running:
            try:
                self._perform_health_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                time.sleep(self.check_interval)
    
    def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        checks = {}
        
        # Check application status
        checks["app_status"] = self._check_app_status()
        
        # Check disk space
        checks["disk_space"] = self._check_disk_space()
        
        # Check memory usage
        checks["memory"] = self._check_memory()
        
        # Check dependencies
        checks["dependencies"] = self._check_dependencies()
        
        # Determine overall status
        overall_status = "healthy" if all(
            check["status"] == "healthy" for check in checks.values()
        ) else "unhealthy"
        
        self.health_status = {
            "status": overall_status,
            "last_check": datetime.now().isoformat(),
            "checks": checks
        }
        
        self.logger.info("Health check completed", extra={
            "status": overall_status,
            "checks_passed": sum(1 for c in checks.values() if c["status"] == "healthy"),
            "total_checks": len(checks)
        })
    
    def _check_app_status(self) -> Dict[str, Any]:
        """Check if main application is running"""
        try:
            # Check if streamlit process is running
            result = subprocess.run(
                ["pgrep", "-f", "streamlit"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {"status": "healthy", "message": "Application running"}
            else:
                return {"status": "unhealthy", "message": "Application not found"}
                
        except Exception as e:
            return {"status": "unhealthy", "message": f"Check failed: {e}"}
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/app")
            
            free_percent = (free / total) * 100
            
            if free_percent > 20:
                status = "healthy"
            elif free_percent > 10:
                status = "warning"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "free_percent": round(free_percent, 1),
                "free_gb": round(free / (1024**3), 2)
            }
            
        except Exception as e:
            return {"status": "unhealthy", "message": f"Check failed: {e}"}
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            available_percent = memory.available / memory.total * 100
            
            if available_percent > 20:
                status = "healthy"
            elif available_percent > 10:
                status = "warning"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "available_percent": round(available_percent, 1),
                "used_percent": round(memory.percent, 1)
            }
            
        except Exception as e:
            return {"status": "unhealthy", "message": f"Check failed: {e}"}
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check critical dependencies"""
        try:
            # Test imports
            import streamlit
            import pandas
            import plotly
            
            return {"status": "healthy", "message": "All dependencies available"}
            
        except ImportError as e:
            return {"status": "unhealthy", "message": f"Missing dependency: {e}"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Check failed: {e}"}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_status

class MetricsCollector:
    """Collect and export application metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger("metrics_collector")
        self.metrics = {
            "startup_time": time.time(),
            "requests_total": 0,
            "requests_by_endpoint": {},
            "response_times": [],
            "errors_total": 0,
            "active_users": 0,
            "system_metrics": {}
        }
        
        # Create metrics directory
        Path("metrics").mkdir(exist_ok=True)
        
        self.logger.info("Metrics collector initialized")
    
    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """Record request metrics"""
        self.metrics["requests_total"] += 1
        
        if endpoint not in self.metrics["requests_by_endpoint"]:
            self.metrics["requests_by_endpoint"][endpoint] = 0
        self.metrics["requests_by_endpoint"][endpoint] += 1
        
        self.metrics["response_times"].append(response_time)
        
        if status_code >= 400:
            self.metrics["errors_total"] += 1
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil
            
            self.metrics["system_metrics"] = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
                "load_average": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export metrics in Prometheus format"""
        self.collect_system_metrics()
        
        # Calculate derived metrics
        avg_response_time = (
            sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            if self.metrics["response_times"] else 0
        )
        
        uptime = time.time() - self.metrics["startup_time"]
        
        exported_metrics = {
            "techcorp_requests_total": self.metrics["requests_total"],
            "techcorp_errors_total": self.metrics["errors_total"],
            "techcorp_response_time_avg": round(avg_response_time, 3),
            "techcorp_uptime_seconds": round(uptime),
            "techcorp_active_users": self.metrics["active_users"],
            **{f"techcorp_system_{k}": v for k, v in self.metrics["system_metrics"].items()}
        }
        
        # Save metrics to file
        with open("metrics/app_metrics.json", "w") as f:
            json.dump(exported_metrics, f, indent=2)
        
        return exported_metrics

class ProcessManager:
    """Manage application processes with graceful shutdown"""
    
    def __init__(self):
        self.logger = logging.getLogger("process_manager")
        self.processes = {}
        self.shutdown_event = threading.Event()
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self.logger.info("Signal handlers configured")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.shutdown_event.set()
        self.graceful_shutdown()
    
    def start_process(self, name: str, command: list, env: Dict[str, str] = None):
        """Start a managed process"""
        try:
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            process = subprocess.Popen(
                command,
                env=process_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes[name] = process
            
            # Start output monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_process_output,
                args=(name, process),
                daemon=True
            )
            monitor_thread.start()
            
            self.logger.info(f"Started process: {name}", extra={
                "pid": process.pid,
                "command": " ".join(command)
            })
            
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start process {name}: {e}")
            return None
    
    def _monitor_process_output(self, name: str, process: subprocess.Popen):
        """Monitor process output and log it"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    self.logger.info(f"[{name}] {line.strip()}")
                
                if self.shutdown_event.is_set():
                    break
                    
        except Exception as e:
            self.logger.error(f"Error monitoring {name}: {e}")
    
    def graceful_shutdown(self):
        """Perform graceful shutdown of all processes"""
        self.logger.info("Starting graceful shutdown")
        
        shutdown_timeout = 30  # seconds
        
        for name, process in self.processes.items():
            if process.poll() is None:  # Process is still running
                self.logger.info(f"Terminating process: {name}")
                
                try:
                    # Send TERM signal first
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=shutdown_timeout // 2)
                        self.logger.info(f"Process {name} terminated gracefully")
                    except subprocess.TimeoutExpired:
                        # Force kill if timeout
                        self.logger.warning(f"Force killing process: {name}")
                        process.kill()
                        process.wait()
                        
                except Exception as e:
                    self.logger.error(f"Error shutting down {name}: {e}")
        
        self.logger.info("Graceful shutdown completed")

class ProductionOrchestrator:
    """Main orchestrator for production deployment"""
    
    def __init__(self):
        # Initialize logging first
        log_level = os.getenv("LOG_LEVEL", "INFO")
        self.prod_logger = ProductionLogger(log_level)
        self.logger = logging.getLogger("production_orchestrator")
        
        # Initialize components
        self.health_checker = HealthChecker(int(os.getenv("HEALTH_CHECK_INTERVAL", "30")))
        self.metrics_collector = MetricsCollector()
        self.process_manager = ProcessManager()
        
        self.logger.info("Production orchestrator initialized", extra={
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "environment": os.getenv("APP_ENV", "production")
        })
    
    def validate_environment(self) -> bool:
        """Validate production environment configuration"""
        
        self.logger.info("Validating production environment")
        
        # Required environment variables
        required_vars = [
            "APP_ENV", "APP_VERSION", "PORT"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            self.logger.error(f"Missing required environment variables: {missing_vars}")
            return False
        
        # Validate directories
        required_dirs = ["logs", "data", "temp", "metrics"]
        for directory in required_dirs:
            Path(directory).mkdir(exist_ok=True)
            
        # Check Python dependencies
        try:
            import streamlit
            import pandas
            import plotly
            import sentence_transformers
            self.logger.info("All Python dependencies validated")
        except ImportError as e:
            self.logger.error(f"Missing Python dependency: {e}")
            return False
        
        self.logger.info("Environment validation completed successfully")
        return True
    
    def start_services(self):
        """Start all production services"""
        
        self.logger.info("Starting production services")
        
        # Start health checker
        self.health_checker.start_health_checks()
        
        # Start metrics collection (background thread)
        metrics_thread = threading.Thread(target=self._metrics_collection_loop, daemon=True)
        metrics_thread.start()
        
        # Start main application based on mode
        app_mode = os.getenv("APP_MODE", "dashboard")
        
        if app_mode == "dashboard":
            self._start_dashboard()
        elif app_mode == "mcp-server":
            self._start_mcp_server()
        elif app_mode == "rag-service":
            self._start_rag_service()
        else:
            self.logger.error(f"Unknown APP_MODE: {app_mode}")
            sys.exit(1)
    
    def _start_dashboard(self):
        """Start Streamlit dashboard"""
        
        port = os.getenv("PORT", "8501")
        
        command = [
            "streamlit", "run", "techcorp_dashboard.py",
            "--server.port", port,
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.serverAddress", "0.0.0.0",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "light"
        ]
        
        env = {
            "STREAMLIT_SERVER_ENABLE_CORS": "false",
            "STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION": "true"
        }
        
        process = self.process_manager.start_process("streamlit-dashboard", command, env)
        
        if process:
            self.logger.info(f"Streamlit dashboard started on port {port}")
            
            # Wait for process to finish or shutdown signal
            try:
                process.wait()
            except KeyboardInterrupt:
                self.logger.info("Shutdown initiated by user")
        else:
            self.logger.error("Failed to start dashboard")
            sys.exit(1)
    
    def _start_mcp_server(self):
        """Start MCP server"""
        
        command = ["python", "mcp_customer_service_server.py"]
        process = self.process_manager.start_process("mcp-server", command)
        
        if process:
            self.logger.info("MCP server started")
            try:
                process.wait()
            except KeyboardInterrupt:
                self.logger.info("Shutdown initiated by user")
        else:
            self.logger.error("Failed to start MCP server")
            sys.exit(1)
    
    def _start_rag_service(self):
        """Start RAG service"""
        
        command = ["python", "enterprise_rag_service.py", "--mode=search"]
        process = self.process_manager.start_process("rag-service", command)
        
        if process:
            self.logger.info("RAG service started")
            try:
                process.wait()
            except KeyboardInterrupt:
                self.logger.info("Shutdown initiated by user")
        else:
            self.logger.error("Failed to start RAG service")
            sys.exit(1)
    
    def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        
        collection_interval = int(os.getenv("METRICS_COLLECTION_INTERVAL", "60"))
        
        while not self.process_manager.shutdown_event.is_set():
            try:
                # Collect and export metrics
                metrics = self.metrics_collector.export_metrics()
                
                self.logger.debug("Metrics collected", extra={
                    "total_requests": metrics.get("techcorp_requests_total", 0),
                    "uptime": metrics.get("techcorp_uptime_seconds", 0)
                })
                
                time.sleep(collection_interval)
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                time.sleep(collection_interval)
    
    def setup_health_endpoints(self):
        """Setup health check endpoints for load balancers"""
        
        # Create simple health check files that external systems can monitor
        def write_health_status():
            while not self.process_manager.shutdown_event.is_set():
                try:
                    health_status = self.health_checker.get_health_status()
                    
                    # Write health status file
                    with open("temp/health.json", "w") as f:
                        json.dump(health_status, f, indent=2)
                    
                    # Write readiness status
                    readiness_status = {
                        "ready": health_status["status"] == "healthy",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    with open("temp/ready.json", "w") as f:
                        json.dump(readiness_status, f, indent=2)
                    
                    time.sleep(10)  # Update every 10 seconds
                    
                except Exception as e:
                    self.logger.error(f"Health endpoint update error: {e}")
                    time.sleep(10)
        
        health_thread = threading.Thread(target=write_health_status, daemon=True)
        health_thread.start()

def main():
    """Main production deployment function"""
    
    print("=== TechCorp Customer Service AI - Production Deployment ===")
    print(f"Version: {os.getenv('APP_VERSION', '1.0.0')}")
    print(f"Environment: {os.getenv('APP_ENV', 'production')}")
    print(f"Mode: {os.getenv('APP_MODE', 'dashboard')}")
    print(f"Startup time: {datetime.now()}")
    print("=" * 60)
    
    # Initialize production orchestrator
    orchestrator = ProductionOrchestrator()
    
    try:
        # Validate environment
        if not orchestrator.validate_environment():
            print("❌ Environment validation failed")
            sys.exit(1)
        
        print("✅ Environment validation passed")
        
        # Setup health endpoints
        orchestrator.setup_health_endpoints()
        print("✅ Health check endpoints configured")
        
        # Start services
        print("🚀 Starting production services...")
        orchestrator.start_services()
        
    except Exception as e:
        orchestrator.logger.error(f"Production deployment failed: {e}")
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Shutdown initiated by user")
        orchestrator.logger.info("Shutdown completed")

if __name__ == "__main__":
    main()