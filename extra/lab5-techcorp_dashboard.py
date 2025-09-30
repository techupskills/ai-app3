#!/usr/bin/env python3

# Lab 5: TechCorp Customer Service Dashboard
# Complete implementation with enterprise authentication and components

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
import sys
import os

# Import our enterprise components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth_service import EnterpriseAuthService, UserContext
from dashboard_components import (
    MetricsCard, ChartComponents, DataTableComponents, 
    FilterComponents, AlertComponents, ExportComponents, 
    LayoutComponents
)

# Configure page
st.set_page_config(
    page_title="TechCorp Customer Service Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DashboardDataService:
    """Service for generating and managing dashboard data"""
    
    def __init__(self):
        self.cache_duration = 300  # 5 minutes
        self._last_update = 0
        self._cached_data = {}
    
    def get_real_time_metrics(self) -> dict:
        """Get real-time system metrics"""
        current_time = time.time()
        
        # Return cached data if still fresh
        if current_time - self._last_update < self.cache_duration and self._cached_data:
            return self._cached_data
        
        # Generate fresh data
        base_time = datetime.now()
        
        metrics = {
            "total_queries_today": np.random.randint(800, 1200),
            "active_conversations": np.random.randint(15, 45),
            "avg_response_time": round(np.random.normal(2.8, 0.4), 2),
            "customer_satisfaction": round(np.random.normal(4.1, 0.2), 1),
            "resolution_rate": round(np.random.normal(92.5, 2.0), 1),
            "escalation_rate": round(np.random.normal(8.5, 1.5), 1),
            "agents_online": np.random.randint(12, 20),
            "queue_length": np.random.randint(0, 8),
            "last_updated": base_time.isoformat()
        }
        
        # Cache the data
        self._cached_data = metrics
        self._last_update = current_time
        
        return metrics
    
    def get_hourly_data(self, hours: int = 24) -> pd.DataFrame:
        """Generate hourly performance data"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        time_range = pd.date_range(start=start_time, end=end_time, freq='H')
        
        data = []
        for timestamp in time_range:
            # Simulate different patterns based on time of day
            hour = timestamp.hour
            if 9 <= hour <= 17:  # Business hours
                base_queries = np.random.randint(40, 80)
                base_response_time = np.random.normal(2.2, 0.3)
            elif 18 <= hour <= 22:  # Evening
                base_queries = np.random.randint(20, 40)
                base_response_time = np.random.normal(2.8, 0.4)
            else:  # Night/early morning
                base_queries = np.random.randint(5, 20)
                base_response_time = np.random.normal(3.2, 0.5)
            
            data.append({
                'timestamp': timestamp,
                'hour': timestamp.strftime('%H:00'),
                'queries': max(0, base_queries),
                'response_time': max(0.5, base_response_time),
                'satisfaction': np.random.normal(4.1, 0.3),
                'agents_active': np.random.randint(3, 15)
            })
        
        return pd.DataFrame(data)
    
    def get_category_data(self) -> pd.DataFrame:
        """Get query category breakdown"""
        categories = [
            'Technical Support', 'Billing Inquiry', 'Account Management',
            'Product Information', 'Complaint Resolution', 'General Inquiry'
        ]
        
        # Simulate realistic distribution
        weights = [0.25, 0.20, 0.15, 0.15, 0.15, 0.10]
        total_queries = np.random.randint(800, 1200)
        
        data = []
        for i, category in enumerate(categories):
            count = int(total_queries * weights[i] * np.random.normal(1.0, 0.1))
            avg_time = np.random.normal(12, 3) + (i * 2)  # Different complexity
            satisfaction = np.random.normal(4.0, 0.3)
            
            data.append({
                'category': category,
                'count': max(1, count),
                'avg_resolution_time': max(1, round(avg_time, 1)),
                'avg_satisfaction': max(1, round(satisfaction, 1)),
                'percentage': round((count / total_queries) * 100, 1)
            })
        
        return pd.DataFrame(data)
    
    def get_agent_performance(self) -> pd.DataFrame:
        """Get agent performance data"""
        agents = [
            'Sarah Johnson', 'Michael Chen', 'Emily Rodriguez', 'David Kim',
            'Jessica Brown', 'Robert Taylor', 'Amanda Wilson', 'James Martinez'
        ]
        
        data = []
        for agent in agents:
            cases = np.random.randint(15, 45)
            rating = np.random.normal(4.0, 0.4)
            response_time = np.random.normal(2.5, 0.8)
            resolution_rate = np.random.normal(90, 8)
            
            data.append({
                'agent': agent,
                'cases_handled': cases,
                'avg_rating': max(1, min(5, round(rating, 1))),
                'avg_response_time': max(0.5, round(response_time, 1)),
                'resolution_rate': max(70, min(100, round(resolution_rate, 1))),
                'status': np.random.choice(['Online', 'Busy', 'Away'], p=[0.7, 0.2, 0.1])
            })
        
        return pd.DataFrame(data)

class SessionManager:
    """Manage user sessions and authentication"""
    
    @staticmethod
    def initialize_auth():
        """Initialize authentication service"""
        if 'auth_service' not in st.session_state:
            st.session_state.auth_service = EnterpriseAuthService()
    
    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    @staticmethod
    def get_user():
        """Get current user context"""
        return st.session_state.get('user')
    
    @staticmethod
    def login(email: str, password: str) -> bool:
        """Login user"""
        auth_result = st.session_state.auth_service.authenticate_user(email, password)
        
        if auth_result['success']:
            st.session_state.user = auth_result['user']
            st.session_state.access_token = auth_result['access_token']
            st.session_state.session_id = auth_result['session_id']
            return True
        else:
            st.session_state.error = auth_result['error']
            return False
    
    @staticmethod
    def logout():
        """Logout user"""
        if 'session_id' in st.session_state:
            st.session_state.auth_service.logout_user(st.session_state.session_id)
        
        # Clear session state
        for key in ['user', 'access_token', 'session_id']:
            if key in st.session_state:
                del st.session_state[key]

def render_login_page():
    """Render login page"""
    LayoutComponents.render_page_header(
        "TechCorp Customer Service Dashboard",
        "Please login to access the dashboard"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("### 🔐 Login")
            
            # Display test accounts
            with st.expander("Test Accounts", expanded=True):
                st.markdown("""
                **Administrator:** admin@techcorp.com / admin123
                **Supervisor:** supervisor@techcorp.com / super123  
                **Agent:** agent@techcorp.com / agent123
                """)
            
            # Login form
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="user@techcorp.com")
                password = st.text_input("Password", type="password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_button = st.form_submit_button("Login", type="primary")
                with col2:
                    if st.form_submit_button("Demo Login"):
                        email = "admin@techcorp.com"
                        password = "admin123"
                        login_button = True
                
                if login_button:
                    if email and password:
                        with st.spinner("Authenticating..."):
                            if SessionManager.login(email, password):
                                st.success("Login successful! Redirecting...")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Login failed: {st.session_state.get('error', 'Unknown error')}")
                    else:
                        st.error("Please enter both email and password")

def render_dashboard():
    """Render main dashboard"""
    user = SessionManager.get_user()
    
    # Sidebar
    with st.sidebar:
        LayoutComponents.render_sidebar_logo()
        
        st.markdown(f"### Welcome, {user['username']}")
        st.markdown(f"**Role:** {user['role'].title()}")
        st.markdown(f"**Department:** {user['department']}")
        
        st.divider()
        
        # Navigation
        page = st.selectbox(
            "Navigation",
            ["Dashboard", "Analytics", "Agents", "Reports"] if user['role'] == 'admin' 
            else ["Dashboard", "Analytics"] if user['role'] == 'supervisor'
            else ["Dashboard"]
        )
        
        st.divider()
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=True)
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout"):
            SessionManager.logout()
            st.rerun()
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Main content
    if page == "Dashboard":
        render_main_dashboard(user)
    elif page == "Analytics":
        render_analytics_page(user)
    elif page == "Agents":
        render_agents_page(user)
    elif page == "Reports":
        render_reports_page(user)

def render_main_dashboard(user: dict):
    """Render main dashboard view"""
    LayoutComponents.render_page_header(
        "Customer Service Dashboard",
        f"Real-time overview • Last updated: {datetime.now().strftime('%H:%M:%S')}"
    )
    
    # Initialize data service
    data_service = DashboardDataService()
    
    # Get real-time metrics
    metrics = data_service.get_real_time_metrics()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        MetricsCard.render(
            "Total Queries Today", 
            str(metrics['total_queries_today']),
            f"+{np.random.randint(5, 15)}%",
            "normal"
        )
    
    with col2:
        MetricsCard.render(
            "Avg Response Time",
            f"{metrics['avg_response_time']}s",
            f"-{np.random.randint(2, 8)}%",
            "inverse"
        )
    
    with col3:
        MetricsCard.render(
            "Satisfaction Score",
            f"{metrics['customer_satisfaction']}/5",
            f"+{np.random.randint(1, 5)}%",
            "normal"
        )
    
    with col4:
        MetricsCard.render(
            "Active Conversations",
            str(metrics['active_conversations']),
            f"{np.random.randint(2, 8)} new",
            "normal"
        )
    
    st.divider()
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly query volume
        hourly_data = data_service.get_hourly_data(12)  # Last 12 hours
        
        fig = px.line(hourly_data, x='hour', y='queries',
                     title='Query Volume - Last 12 Hours')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category breakdown
        category_data = data_service.get_category_data()
        
        fig = px.pie(category_data, values='count', names='category',
                    title='Query Categories Today')
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # System status and alerts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Performance Indicators")
        
        # Performance gauges
        subcol1, subcol2 = st.columns(2)
        
        with subcol1:
            ChartComponents.render_gauge_chart(
                metrics['resolution_rate'], 
                "Resolution Rate (%)", 
                100
            )
        
        with subcol2:
            ChartComponents.render_gauge_chart(
                100 - metrics['escalation_rate'],
                "First Contact Resolution (%)",
                100
            )
    
    with col2:
        st.subheader("🚨 System Status")
        
        # System alerts based on metrics
        if metrics['queue_length'] > 5:
            AlertComponents.render_warning_alert(
                f"High queue length: {metrics['queue_length']} customers waiting"
            )
        else:
            AlertComponents.render_success_alert("Queue length normal")
        
        if metrics['avg_response_time'] > 3.0:
            AlertComponents.render_warning_alert(
                f"Response time above target: {metrics['avg_response_time']}s"
            )
        else:
            AlertComponents.render_success_alert("Response times on target")
        
        if metrics['agents_online'] < 10:
            AlertComponents.render_warning_alert(
                f"Low agent availability: {metrics['agents_online']} online"
            )
        else:
            AlertComponents.render_success_alert(
                f"Agent availability good: {metrics['agents_online']} online"
            )
        
        # Real-time stats
        st.markdown("**Real-time Stats:**")
        st.markdown(f"• Agents Online: {metrics['agents_online']}")
        st.markdown(f"• Queue Length: {metrics['queue_length']}")
        st.markdown(f"• Escalation Rate: {metrics['escalation_rate']}%")

def render_analytics_page(user: dict):
    """Render analytics page"""
    LayoutComponents.render_page_header("Analytics", "Detailed performance analysis")
    
    # Date range filter
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    data_service = DashboardDataService()
    
    # Detailed charts
    col1, col2 = st.columns(2)
    
    with col1:
        hourly_data = data_service.get_hourly_data(24)
        ChartComponents.render_line_chart(
            hourly_data, 'timestamp', 'response_time',
            'Response Time Trend (24h)'
        )
    
    with col2:
        ChartComponents.render_line_chart(
            hourly_data, 'timestamp', 'satisfaction',
            'Customer Satisfaction Trend (24h)'
        )
    
    # Category analysis
    category_data = data_service.get_category_data()
    DataTableComponents.render_interactive_table(
        category_data, "Category Performance Analysis"
    )

def render_agents_page(user: dict):
    """Render agents page (admin only)"""
    LayoutComponents.render_page_header("Agent Management", "Monitor and manage agent performance")
    
    data_service = DashboardDataService()
    agent_data = data_service.get_agent_performance()
    
    # Agent performance table
    DataTableComponents.render_interactive_table(
        agent_data, "Agent Performance", ['agent']
    )
    
    # Export functionality
    ExportComponents.render_csv_download(agent_data, "agent_performance")

def render_reports_page(user: dict):
    """Render reports page (admin only)"""
    LayoutComponents.render_page_header("Reports", "Generate and export reports")
    
    st.info("📋 Report generation functionality - coming soon!")

def main():
    """Main application function"""
    # Initialize session
    SessionManager.initialize_auth()
    
    # Route based on authentication status
    if not SessionManager.is_authenticated():
        render_login_page()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()