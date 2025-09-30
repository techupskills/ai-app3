#!/usr/bin/env python3

# Lab 5: Dashboard Components for Enterprise Streamlit App
# Complete implementation with reusable enterprise components

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

class MetricsCard:
    """Reusable metrics card component"""
    
    @staticmethod
    def render(title: str, value: str, delta: Optional[str] = None, 
               delta_color: str = "normal", help_text: Optional[str] = None):
        """Render a metrics card with optional delta"""
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if help_text:
                st.metric(label=title, value=value, delta=delta, 
                         delta_color=delta_color, help=help_text)
            else:
                st.metric(label=title, value=value, delta=delta, delta_color=delta_color)

class ChartComponents:
    """Reusable chart components for enterprise dashboards"""
    
    @staticmethod
    def render_line_chart(data: pd.DataFrame, x_col: str, y_col: str, 
                         title: str, color_col: Optional[str] = None) -> None:
        """Render line chart with enterprise styling"""
        
        fig = px.line(data, x=x_col, y=y_col, color=color_col,
                     title=title,
                     color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Arial, sans-serif",
            title_font_size=16,
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_bar_chart(data: pd.DataFrame, x_col: str, y_col: str, 
                        title: str, orientation: str = 'v') -> None:
        """Render bar chart with enterprise styling"""
        
        if orientation == 'h':
            fig = px.bar(data, y=x_col, x=y_col, title=title, orientation='h')
        else:
            fig = px.bar(data, x=x_col, y=y_col, title=title)
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Arial, sans-serif",
            title_font_size=16,
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_pie_chart(data: pd.DataFrame, values_col: str, names_col: str, 
                        title: str) -> None:
        """Render pie chart with enterprise styling"""
        
        fig = px.pie(data, values=values_col, names=names_col, title=title,
                    color_discrete_sequence=px.colors.qualitative.Set3)
        
        fig.update_layout(
            font_family="Arial, sans-serif",
            title_font_size=16
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_gauge_chart(value: float, title: str, max_value: float = 100,
                          threshold_colors: Dict[str, float] = None) -> None:
        """Render gauge chart for KPI monitoring"""
        
        if threshold_colors is None:
            threshold_colors = {"red": 30, "yellow": 70, "green": 100}
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            delta={'reference': max_value * 0.8},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, threshold_colors["red"]], 'color': "lightgray"},
                    {'range': [threshold_colors["red"], threshold_colors["yellow"]], 'color': "yellow"},
                    {'range': [threshold_colors["yellow"], threshold_colors["green"]], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75, 'value': threshold_colors["red"]
                }
            }
        ))
        
        fig.update_layout(font={'color': "darkblue", 'family': "Arial"})
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_heatmap(data: pd.DataFrame, x_col: str, y_col: str, 
                      values_col: str, title: str) -> None:
        """Render heatmap for pattern analysis"""
        
        pivot_data = data.pivot_table(values=values_col, index=y_col, columns=x_col, aggfunc='sum')
        
        fig = px.imshow(pivot_data, 
                       title=title,
                       color_continuous_scale='Blues',
                       aspect="auto")
        
        fig.update_layout(
            font_family="Arial, sans-serif",
            title_font_size=16
        )
        
        st.plotly_chart(fig, use_container_width=True)

class DataTableComponents:
    """Reusable data table components"""
    
    @staticmethod
    def render_interactive_table(data: pd.DataFrame, title: str,
                               searchable_columns: List[str] = None,
                               sortable: bool = True) -> pd.DataFrame:
        """Render interactive data table with search and sort"""
        
        st.subheader(title)
        
        # Search functionality
        if searchable_columns:
            search_term = st.text_input("🔍 Search", key=f"search_{title}")
            if search_term:
                mask = data[searchable_columns].astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False)
                ).any(axis=1)
                data = data[mask]
        
        # Column selection
        if len(data.columns) > 10:
            selected_columns = st.multiselect(
                "Select columns to display",
                data.columns.tolist(),
                default=data.columns.tolist()[:5],
                key=f"columns_{title}"
            )
            if selected_columns:
                data = data[selected_columns]
        
        # Display table
        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(format="%.2f") 
                for col in data.select_dtypes(include=[np.number]).columns
            }
        )
        
        return data
    
    @staticmethod
    def render_summary_table(data: Dict[str, Any], title: str) -> None:
        """Render summary statistics table"""
        
        st.subheader(title)
        
        summary_df = pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
        summary_df.index.name = 'Metric'
        
        st.dataframe(summary_df, use_container_width=True)

class FilterComponents:
    """Reusable filter components for dashboards"""
    
    @staticmethod
    def render_date_range_filter(key: str = "date_range") -> tuple:
        """Render date range filter"""
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=30),
                key=f"{key}_start"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=datetime.now(),
                key=f"{key}_end"
            )
        
        return start_date, end_date
    
    @staticmethod
    def render_multiselect_filter(options: List[str], label: str, 
                                 default: List[str] = None, 
                                 key: str = None) -> List[str]:
        """Render multiselect filter"""
        
        if default is None:
            default = options
        
        return st.multiselect(label, options, default=default, key=key)
    
    @staticmethod
    def render_slider_filter(min_val: float, max_val: float, 
                           label: str, step: float = 1.0,
                           key: str = None) -> tuple:
        """Render range slider filter"""
        
        return st.slider(
            label,
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            step=step,
            key=key
        )

class AlertComponents:
    """Alert and notification components"""
    
    @staticmethod
    def render_success_alert(message: str) -> None:
        """Render success alert"""
        st.success(f"✅ {message}")
    
    @staticmethod
    def render_warning_alert(message: str) -> None:
        """Render warning alert"""
        st.warning(f"⚠️ {message}")
    
    @staticmethod
    def render_error_alert(message: str) -> None:
        """Render error alert"""
        st.error(f"❌ {message}")
    
    @staticmethod
    def render_info_alert(message: str) -> None:
        """Render info alert"""
        st.info(f"ℹ️ {message}")
    
    @staticmethod
    def render_kpi_alert(metric_name: str, current_value: float, 
                        threshold: float, comparison: str = "above") -> None:
        """Render KPI-based alert"""
        
        if comparison == "above" and current_value > threshold:
            st.success(f"✅ {metric_name}: {current_value:.2f} (Above threshold: {threshold:.2f})")
        elif comparison == "below" and current_value < threshold:
            st.success(f"✅ {metric_name}: {current_value:.2f} (Below threshold: {threshold:.2f})")
        else:
            st.warning(f"⚠️ {metric_name}: {current_value:.2f} (Threshold: {threshold:.2f})")

class ExportComponents:
    """Export and download components"""
    
    @staticmethod
    def render_csv_download(data: pd.DataFrame, filename: str, 
                          label: str = "Download CSV") -> None:
        """Render CSV download button"""
        
        csv = data.to_csv(index=False)
        st.download_button(
            label=label,
            data=csv,
            file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    @staticmethod
    def render_json_download(data: Dict[str, Any], filename: str,
                           label: str = "Download JSON") -> None:
        """Render JSON download button"""
        
        json_str = json.dumps(data, indent=2, default=str)
        st.download_button(
            label=label,
            data=json_str,
            file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

class LayoutComponents:
    """Layout and UI components"""
    
    @staticmethod
    def render_sidebar_logo(logo_url: str = None) -> None:
        """Render sidebar logo"""
        
        with st.sidebar:
            if logo_url:
                st.image(logo_url, width=200)
            else:
                st.markdown("# 🏢 TechCorp")
                st.markdown("*Enterprise Dashboard*")
    
    @staticmethod
    def render_page_header(title: str, subtitle: str = None) -> None:
        """Render page header with title and subtitle"""
        
        st.title(title)
        if subtitle:
            st.markdown(f"*{subtitle}*")
        st.divider()
    
    @staticmethod
    def render_tabs(tab_names: List[str]) -> object:
        """Render tab container"""
        
        return st.tabs(tab_names)
    
    @staticmethod
    def render_columns(num_columns: int, gap: str = "small") -> List[object]:
        """Render column layout"""
        
        return st.columns(num_columns, gap=gap)
    
    @staticmethod
    def render_expander(title: str, expanded: bool = False) -> object:
        """Render expandable section"""
        
        return st.expander(title, expanded=expanded)
    
    @staticmethod
    def render_container() -> object:
        """Render container for grouping elements"""
        
        return st.container()

class FormComponents:
    """Form input components"""
    
    @staticmethod
    def render_text_input(label: str, placeholder: str = "", 
                         key: str = None) -> str:
        """Render text input field"""
        
        return st.text_input(label, placeholder=placeholder, key=key)
    
    @staticmethod
    def render_number_input(label: str, min_value: float = None,
                          max_value: float = None, value: float = None,
                          key: str = None) -> float:
        """Render number input field"""
        
        return st.number_input(label, min_value=min_value, max_value=max_value,
                              value=value, key=key)
    
    @staticmethod
    def render_selectbox(label: str, options: List[str], 
                        index: int = 0, key: str = None) -> str:
        """Render select dropdown"""
        
        return st.selectbox(label, options, index=index, key=key)
    
    @staticmethod
    def render_submit_button(label: str = "Submit", 
                           key: str = None) -> bool:
        """Render submit button"""
        
        return st.button(label, key=key, type="primary")

def generate_sample_data() -> Dict[str, pd.DataFrame]:
    """Generate sample data for component testing"""
    
    # Generate sample metrics data
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    metrics_data = pd.DataFrame({
        'date': dates,
        'total_queries': np.random.randint(100, 500, len(dates)),
        'response_time': np.random.normal(2.5, 0.5, len(dates)),
        'satisfaction_score': np.random.normal(4.2, 0.3, len(dates))
    })
    
    # Generate sample category data
    categories = ['Billing', 'Technical', 'Account', 'General']
    category_data = pd.DataFrame({
        'category': categories,
        'count': np.random.randint(50, 200, len(categories)),
        'avg_resolution_time': np.random.normal(15, 5, len(categories))
    })
    
    # Generate sample agent data
    agents = ['Agent A', 'Agent B', 'Agent C', 'Agent D', 'Agent E']
    agent_data = pd.DataFrame({
        'agent': agents,
        'cases_handled': np.random.randint(20, 80, len(agents)),
        'avg_rating': np.random.normal(4.0, 0.4, len(agents)),
        'response_time': np.random.normal(3.0, 1.0, len(agents))
    })
    
    return {
        'metrics': metrics_data,
        'categories': category_data,
        'agents': agent_data
    }

def main():
    """Main function demonstrating dashboard components"""
    st.set_page_config(
        page_title="TechCorp Dashboard Components",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render layout components
    LayoutComponents.render_sidebar_logo()
    LayoutComponents.render_page_header(
        "TechCorp Dashboard Components",
        "Enterprise-grade reusable components for Streamlit dashboards"
    )
    
    # Generate sample data
    sample_data = generate_sample_data()
    
    # Create tabs for different component types
    tabs = LayoutComponents.render_tabs([
        "📈 Charts", "📊 Metrics", "📋 Tables", 
        "🔍 Filters", "🚨 Alerts", "📤 Export"
    ])
    
    with tabs[0]:  # Charts tab
        st.header("Chart Components")
        
        col1, col2 = LayoutComponents.render_columns(2)
        
        with col1:
            ChartComponents.render_line_chart(
                sample_data['metrics'], 'date', 'total_queries',
                'Daily Query Volume'
            )
            
            ChartComponents.render_pie_chart(
                sample_data['categories'], 'count', 'category',
                'Query Categories'
            )
        
        with col2:
            ChartComponents.render_bar_chart(
                sample_data['agents'], 'agent', 'cases_handled',
                'Cases Handled by Agent'
            )
            
            ChartComponents.render_gauge_chart(
                85.5, "Customer Satisfaction", 100
            )
    
    with tabs[1]:  # Metrics tab
        st.header("Metrics Components")
        
        col1, col2, col3, col4 = LayoutComponents.render_columns(4)
        
        with col1:
            MetricsCard.render(
                "Total Queries", "1,234", "+12%", "normal",
                "Total customer queries processed today"
            )
        
        with col2:
            MetricsCard.render(
                "Avg Response Time", "2.3s", "-5%", "inverse",
                "Average response time for queries"
            )
        
        with col3:
            MetricsCard.render(
                "Satisfaction Score", "4.2/5", "+0.1", "normal",
                "Customer satisfaction rating"
            )
        
        with col4:
            MetricsCard.render(
                "Active Agents", "8", "+1", "normal",
                "Number of agents currently online"
            )
    
    with tabs[2]:  # Tables tab
        st.header("Table Components")
        
        DataTableComponents.render_interactive_table(
            sample_data['agents'],
            "Agent Performance",
            searchable_columns=['agent']
        )
        
        summary_stats = {
            "Total Agents": len(sample_data['agents']),
            "Avg Cases/Agent": sample_data['agents']['cases_handled'].mean(),
            "Best Rating": sample_data['agents']['avg_rating'].max(),
            "Avg Response Time": f"{sample_data['agents']['response_time'].mean():.1f}s"
        }
        
        DataTableComponents.render_summary_table(summary_stats, "Summary Statistics")
    
    with tabs[3]:  # Filters tab
        st.header("Filter Components")
        
        col1, col2 = LayoutComponents.render_columns(2)
        
        with col1:
            start_date, end_date = FilterComponents.render_date_range_filter()
            st.write(f"Selected range: {start_date} to {end_date}")
            
            selected_categories = FilterComponents.render_multiselect_filter(
                ['Billing', 'Technical', 'Account', 'General'],
                "Select Categories",
                key="category_filter"
            )
            st.write(f"Selected categories: {selected_categories}")
        
        with col2:
            rating_range = FilterComponents.render_slider_filter(
                1.0, 5.0, "Rating Range", 0.1, "rating_filter"
            )
            st.write(f"Rating range: {rating_range[0]:.1f} - {rating_range[1]:.1f}")
    
    with tabs[4]:  # Alerts tab
        st.header("Alert Components")
        
        AlertComponents.render_success_alert("System is operating normally")
        AlertComponents.render_warning_alert("Response time is above average")
        AlertComponents.render_error_alert("Connection to database failed")
        AlertComponents.render_info_alert("Maintenance scheduled for tonight")
        
        AlertComponents.render_kpi_alert("Customer Satisfaction", 4.2, 4.0, "above")
        AlertComponents.render_kpi_alert("Response Time", 3.5, 3.0, "below")
    
    with tabs[5]:  # Export tab
        st.header("Export Components")
        
        col1, col2 = LayoutComponents.render_columns(2)
        
        with col1:
            st.subheader("Agent Data Export")
            ExportComponents.render_csv_download(
                sample_data['agents'], "agent_performance"
            )
        
        with col2:
            st.subheader("Summary Export")
            ExportComponents.render_json_download(
                summary_stats, "summary_statistics"
            )

if __name__ == "__main__":
    main()