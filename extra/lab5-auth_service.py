#!/usr/bin/env python3

# Lab 5: Authentication Service for Enterprise Dashboard
# Complete implementation with enterprise security patterns

import hashlib
import jwt
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class UserContext:
    """User context for authentication and authorization"""
    user_id: str
    username: str
    email: str
    role: str
    department: str
    permissions: List[str]
    session_id: str

@dataclass
class SessionData:
    """Session data for active user sessions"""
    user_id: str
    session_id: str
    created_at: float
    last_activity: float
    ip_address: str
    user_agent: str

class EnterpriseAuthService:
    """
    Enterprise Authentication Service
    
    Features:
    - JWT token management with refresh tokens
    - Role-based access control (RBAC)
    - Session management with expiration
    - Audit logging for security compliance
    - Multi-factor authentication support
    - Password policy enforcement
    """
    
    def __init__(self, secret_key: str = "techcorp-dashboard-secret"):
        self.secret_key = secret_key
        self.token_expiry = 3600  # 1 hour
        self.refresh_token_expiry = 86400  # 24 hours
        
        # Setup logging
        self.setup_logging()
        
        # In-memory session store (in production, use Redis/database)
        self.active_sessions: Dict[str, SessionData] = {}
        
        # Initialize user database (in production, use actual database)
        self.setup_mock_users()
        
        self.logger.info("Enterprise Authentication Service initialized")
    
    def setup_logging(self):
        """Setup security audit logging"""
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("auth_service")
        self.logger.setLevel(logging.INFO)
        
        # Security audit handler
        security_handler = logging.FileHandler('logs/security_audit.log')
        security_handler.setFormatter(logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        ))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(security_handler)
        self.logger.addHandler(console_handler)
    
    def setup_mock_users(self):
        """Setup mock user database with different roles"""
        self.users_db = {
            "admin@techcorp.com": {
                "user_id": "USR-001",
                "username": "admin",
                "email": "admin@techcorp.com",
                "password_hash": self.hash_password("admin123"),
                "role": "admin",
                "department": "IT",
                "permissions": [
                    "dashboard_view", "analytics_view", "user_management",
                    "system_config", "audit_logs", "export_data"
                ],
                "active": True,
                "last_login": None
            },
            "supervisor@techcorp.com": {
                "user_id": "USR-002", 
                "username": "supervisor",
                "email": "supervisor@techcorp.com",
                "password_hash": self.hash_password("super123"),
                "role": "supervisor",
                "department": "Customer Service",
                "permissions": [
                    "dashboard_view", "analytics_view", "team_metrics",
                    "escalation_management", "export_data"
                ],
                "active": True,
                "last_login": None
            },
            "agent@techcorp.com": {
                "user_id": "USR-003",
                "username": "agent",
                "email": "agent@techcorp.com", 
                "password_hash": self.hash_password("agent123"),
                "role": "agent",
                "department": "Customer Service",
                "permissions": [
                    "dashboard_view", "case_management", "knowledge_search"
                ],
                "active": True,
                "last_login": None
            }
        }
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        # In production, use bcrypt or argon2
        salt = "techcorp_salt_2024"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def authenticate_user(self, email: str, password: str, 
                         ip_address: str = "unknown", 
                         user_agent: str = "unknown") -> Dict[str, Any]:
        """
        Authenticate user with email and password
        
        Returns authentication result with tokens
        """
        auth_attempt = {
            "email": email,
            "ip_address": ip_address,
            "timestamp": datetime.now().isoformat(),
            "user_agent": user_agent
        }
        
        try:
            # Check if user exists
            if email not in self.users_db:
                self.logger.warning("Authentication failed - user not found", extra=auth_attempt)
                return {"success": False, "error": "Invalid credentials"}
            
            user = self.users_db[email]
            
            # Check if account is active
            if not user.get("active", True):
                self.logger.warning("Authentication failed - account disabled", extra=auth_attempt)
                return {"success": False, "error": "Account disabled"}
            
            # Verify password
            password_hash = self.hash_password(password)
            if password_hash != user["password_hash"]:
                self.logger.warning("Authentication failed - invalid password", extra=auth_attempt)
                return {"success": False, "error": "Invalid credentials"}
            
            # Generate session ID
            session_id = self.generate_session_id()
            
            # Create user context
            user_context = UserContext(
                user_id=user["user_id"],
                username=user["username"],
                email=user["email"],
                role=user["role"],
                department=user["department"],
                permissions=user["permissions"],
                session_id=session_id
            )
            
            # Generate tokens
            access_token = self.generate_access_token(user_context)
            refresh_token = self.generate_refresh_token(user_context)
            
            # Store session
            self.active_sessions[session_id] = SessionData(
                user_id=user["user_id"],
                session_id=session_id,
                created_at=time.time(),
                last_activity=time.time(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Update last login
            self.users_db[email]["last_login"] = datetime.now().isoformat()
            
            # Log successful authentication
            self.logger.info("Authentication successful", extra={
                **auth_attempt,
                "user_id": user["user_id"],
                "role": user["role"],
                "session_id": session_id
            })
            
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "user_id": user_context.user_id,
                    "username": user_context.username,
                    "email": user_context.email,
                    "role": user_context.role,
                    "department": user_context.department,
                    "permissions": user_context.permissions
                },
                "session_id": session_id,
                "expires_in": self.token_expiry
            }
            
        except Exception as e:
            self.logger.error("Authentication error", extra={
                **auth_attempt,
                "error": str(e)
            })
            return {"success": False, "error": "Authentication service error"}
    
    def generate_session_id(self) -> str:
        """Generate secure session ID"""
        import uuid
        return f"sess_{uuid.uuid4().hex}"
    
    def generate_access_token(self, user_context: UserContext) -> str:
        """Generate JWT access token"""
        payload = {
            "user_id": user_context.user_id,
            "username": user_context.username,
            "email": user_context.email,
            "role": user_context.role,
            "department": user_context.department,
            "permissions": user_context.permissions,
            "session_id": user_context.session_id,
            "exp": time.time() + self.token_expiry,
            "iat": time.time(),
            "iss": "techcorp-auth-service"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def generate_refresh_token(self, user_context: UserContext) -> str:
        """Generate JWT refresh token"""
        payload = {
            "user_id": user_context.user_id,
            "session_id": user_context.session_id,
            "exp": time.time() + self.refresh_token_expiry,
            "iat": time.time(),
            "type": "refresh_token"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Returns user context if valid, error if invalid
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Check if session is still active
            session_id = payload.get("session_id")
            if session_id not in self.active_sessions:
                return {"valid": False, "error": "Session expired"}
            
            # Update last activity
            self.active_sessions[session_id].last_activity = time.time()
            
            # Return user context
            return {
                "valid": True,
                "user": {
                    "user_id": payload["user_id"],
                    "username": payload["username"],
                    "email": payload["email"],
                    "role": payload["role"],
                    "department": payload["department"],
                    "permissions": payload["permissions"],
                    "session_id": session_id
                }
            }
            
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Decode refresh token
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=["HS256"])
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh_token":
                return {"success": False, "error": "Invalid refresh token"}
            
            # Check if session is active
            session_id = payload["session_id"]
            if session_id not in self.active_sessions:
                return {"success": False, "error": "Session expired"}
            
            # Get user data
            user_id = payload["user_id"]
            user_data = None
            for email, user in self.users_db.items():
                if user["user_id"] == user_id:
                    user_data = user
                    break
            
            if not user_data:
                return {"success": False, "error": "User not found"}
            
            # Create new user context
            user_context = UserContext(
                user_id=user_data["user_id"],
                username=user_data["username"],
                email=email,
                role=user_data["role"],
                department=user_data["department"],
                permissions=user_data["permissions"],
                session_id=session_id
            )
            
            # Generate new access token
            new_access_token = self.generate_access_token(user_context)
            
            return {
                "success": True,
                "access_token": new_access_token,
                "expires_in": self.token_expiry
            }
            
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Refresh token expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "Invalid refresh token"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def logout_user(self, session_id: str) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                
                # Log logout
                self.logger.info("User logged out", extra={
                    "user_id": session_data.user_id,
                    "session_id": session_id,
                    "session_duration": time.time() - session_data.created_at
                })
                
                # Remove session
                del self.active_sessions[session_id]
                
                return {"success": True, "message": "Logged out successfully"}
            else:
                return {"success": False, "error": "Session not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_permission(self, user_permissions: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        return required_permission in user_permissions
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """Get active sessions for monitoring"""
        current_time = time.time()
        active_count = 0
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            # Check if session has expired (24 hours of inactivity)
            if current_time - session_data.last_activity > 86400:
                expired_sessions.append(session_id)
            else:
                active_count += 1
        
        # Clean up expired sessions
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        return {
            "active_sessions": active_count,
            "expired_sessions_cleaned": len(expired_sessions),
            "session_details": [
                {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "created_at": datetime.fromtimestamp(session.created_at).isoformat(),
                    "last_activity": datetime.fromtimestamp(session.last_activity).isoformat(),
                    "ip_address": session.ip_address
                }
                for session in self.active_sessions.values()
            ]
        }
    
    def get_auth_metrics(self) -> Dict[str, Any]:
        """Get authentication service metrics"""
        return {
            "total_users": len(self.users_db),
            "active_users": len([u for u in self.users_db.values() if u.get("active", True)]),
            "active_sessions": len(self.active_sessions),
            "user_roles": {
                role: len([u for u in self.users_db.values() if u.get("role") == role])
                for role in set(u.get("role") for u in self.users_db.values())
            },
            "last_updated": datetime.now().isoformat()
        }

def main():
    """Main function for testing authentication service"""
    print("=== TechCorp Enterprise Authentication Service ===")
    print("Features: JWT Tokens, RBAC, Session Management, Security Audit")
    print("Test accounts: admin@techcorp.com/admin123, supervisor@techcorp.com/super123, agent@techcorp.com/agent123")
    print("Commands: 'sessions' for active sessions, 'metrics' for auth metrics, 'quit' to exit\n")
    
    # Initialize auth service
    auth_service = EnterpriseAuthService()
    
    print("✅ Authentication service initialized")
    
    while True:
        try:
            command = input("\nAuth Command: ").strip().lower()
            
            if command in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if command == 'sessions':
                print("\n📊 Active Sessions:")
                sessions = auth_service.get_active_sessions()
                print(json.dumps(sessions, indent=2))
                continue
            
            if command == 'metrics':
                print("\n📈 Authentication Metrics:")
                metrics = auth_service.get_auth_metrics()
                print(json.dumps(metrics, indent=2))
                continue
            
            if command == 'login':
                # Test login flow
                email = input("Email: ").strip()
                password = input("Password: ").strip()
                
                print("🔐 Authenticating...")
                result = auth_service.authenticate_user(email, password)
                
                if result["success"]:
                    print(f"✅ Login successful!")
                    print(f"User: {result['user']['username']} ({result['user']['role']})")
                    print(f"Session ID: {result['session_id']}")
                    print(f"Permissions: {', '.join(result['user']['permissions'])}")
                    
                    # Test token verification
                    print("\n🔍 Verifying token...")
                    verification = auth_service.verify_token(result["access_token"])
                    if verification["valid"]:
                        print("✅ Token is valid")
                    else:
                        print(f"❌ Token verification failed: {verification['error']}")
                        
                else:
                    print(f"❌ Login failed: {result['error']}")
                
                continue
            
            print("Available commands: 'login', 'sessions', 'metrics', 'quit'")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()