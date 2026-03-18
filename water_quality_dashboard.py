"""
Live Water Quality Monitoring Dashboard
Updates automatically when sensor values change
"""

import streamlit as st
import time
import pandas as pd
from datetime import datetime, timedelta
from sensor_reader import SensorReader
from database_manager import DatabaseManager
from ml_alert_system import WaterQualityAlertSystem
from visualizations import (
    create_gauge_chart, create_health_score_gauge, 
    create_heatmap_chart, create_alert_timeline,
    create_correlation_matrix, create_parameter_distribution
)
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import os
import requests

# Page configuration
st.set_page_config(
    page_title="Water Quality Monitor",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = []
if 'sensor_reader' not in st.session_state:
    st.session_state.sensor_reader = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'test_mode' not in st.session_state:
    st.session_state.test_mode = False
if 'test_base_values' not in st.session_state:
    st.session_state.test_base_values = {
        'pH': 7.0,
        'Temperature': 22.0,
        'TDS': 300.0,
        'Turbidity': 2.0
    }
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = None
if 'db_enabled' not in st.session_state:
    st.session_state.db_enabled = True
if 'data_source' not in st.session_state:
    st.session_state.data_source = "Database (Latest)"  # Default to database for demo
if 'firebase_app' not in st.session_state:
    st.session_state.firebase_app = None
if 'firebase_connected' not in st.session_state:
    st.session_state.firebase_connected = False
if 'firebase_url' not in st.session_state:
    st.session_state.firebase_url = "https://water-assessment-8a577-default-rtdb.asia-southeast1.firebasedatabase.app/"
if 'firebase_cred_path' not in st.session_state:
    st.session_state.firebase_cred_path = "firebase-adminsdk.json"
if 'firebase_node' not in st.session_state:
    st.session_state.firebase_node = "/"
if 'alert_system' not in st.session_state:
    st.session_state.alert_system = WaterQualityAlertSystem()
if 'ml_analysis' not in st.session_state:
    st.session_state.ml_analysis = []

# Custom CSS for brighter, modern styling
st.markdown("""
    <style>
    /* App background and typography */
    .stApp {
        background: radial-gradient(circle at top left, #f3efe6 0, #e8e1d6 100%);
        color: #0f172a;
    }
    html, body {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
                     "Segoe UI", sans-serif;
    }

    /* Global container tweaks */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* App header */
    .app-header {
        background: linear-gradient(120deg, #2563eb, #22c55e);
        border-radius: 1.25rem;
        padding: 1.4rem 1.7rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 18px 35px rgba(15, 23, 42, 0.25);
        color: #f9fafb;
    }
    .app-header-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .app-header-icon {
        width: 3.1rem;
        height: 3.1rem;
        border-radius: 1rem;
        background: rgba(15, 23, 42, 0.22);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
    }
    .app-header-title {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .app-header-subtitle {
        margin: 0.1rem 0 0;
        font-size: 0.90rem;
        opacity: 0.9;
    }
    .app-header-right {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        align-items: flex-end;
        font-size: 0.80rem;
    }
    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.25);
        font-size: 0.78rem;
    }
    .pill-dot {
        width: 0.5rem;
        height: 0.5rem;
        border-radius: 999px;
        background: #22c55e;
        box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.35);
    }

    /* Sidebar styling (solid grey) */
    [data-testid="stSidebar"] {
        background-color: #e5e7eb;
        color: #111827;
        border-right: 1px solid rgba(148, 163, 184, 0.6);
    }
    [data-testid="stSidebar"] * {
        color: #111827 !important;
    }
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] label {
        font-size: 0.83rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        color: #9ca3af !important;
    }

    /* Input fields background */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
    }
    div[data-baseweb="input"] > div {
        background-color: #ffffff !important;
    }
    div[data-baseweb="input"] input {
        background-color: #ffffff !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
    }

    /* Metric cards / status text */
    .metric-card {
        background: rgba(255, 255, 255, 0.6);
        padding: 1rem;
        border-radius: 0.9rem;
        border: 1px solid rgba(148, 163, 184, 0.4);
        box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
    }
    .status-good {
        color: #16a34a;
        font-weight: 600;
    }
    .status-warning {
        color: #ca8a04;
        font-weight: 600;
    }
    .status-danger {
        color: #dc2626;
        font-weight: 600;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.1rem 0.55rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.04);
        font-size: 0.78rem;
    }

    /* Tabs accent */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 0.35rem 0.9rem;
        background-color: rgba(148, 163, 184, 0.12);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg, #2563eb, #22c55e) !important;
        color: #f9fafb !important;
    }
    </style>
""", unsafe_allow_html=True)

def get_status_color(value, min_good, max_good):
    """Determine status color based on value range"""
    if min_good <= value <= max_good:
        return "status-good"
    elif value < min_good * 0.8 or value > max_good * 1.2:
        return "status-danger"
    else:
        return "status-warning"

def format_timestamp(timestamp):
    """Format timestamp for display"""
    if timestamp:
        return timestamp.strftime("%H:%M:%S")
    return "N/A"

def generate_test_data():
    """Generate simulated sensor data for testing"""
    # Add small random variations to simulate real sensor readings
    return {
        'pH': round(st.session_state.test_base_values['pH'] + random.uniform(-0.3, 0.3), 2),
        'Temperature': round(st.session_state.test_base_values['Temperature'] + random.uniform(-2, 2), 2),
        'TDS': round(st.session_state.test_base_values['TDS'] + random.uniform(-50, 50), 0),
        'Turbidity': round(st.session_state.test_base_values['Turbidity'] + random.uniform(-0.5, 0.5), 2)
    }

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")

# Data Source Selection (moved up)
st.sidebar.markdown("---")
st.sidebar.subheader("📡 Data Source")

data_source = st.sidebar.radio(
    "Select Data Source",
    options=["Live Sensors", "Database (Latest)", "Firebase Cloud", "Test Mode"],
    index=["Live Sensors", "Database (Latest)", "Firebase Cloud", "Test Mode"].index(st.session_state.data_source) if st.session_state.data_source in ["Live Sensors", "Database (Latest)", "Firebase Cloud", "Test Mode"] else 1,
    help="Choose where to read sensor data from"
)
st.session_state.data_source = data_source

# Update test mode based on data source selection
if st.session_state.data_source == "Test Mode":
    st.session_state.test_mode = True
else:
    st.session_state.test_mode = False

if st.session_state.data_source == "Test Mode":
    st.sidebar.info("Test Mode: Using simulated sensor data")
    st.sidebar.markdown("### Adjust Test Values")
    st.session_state.test_base_values['pH'] = st.sidebar.slider(
        "Base pH", 0.0, 14.0, st.session_state.test_base_values['pH'], 0.1
    )
    st.session_state.test_base_values['Temperature'] = st.sidebar.slider(
        "Base Temperature (°C)", 0.0, 50.0, st.session_state.test_base_values['Temperature'], 1.0
    )
    st.session_state.test_base_values['TDS'] = st.sidebar.slider(
        "Base TDS (ppm)", 0, 1000, int(st.session_state.test_base_values['TDS']), 10
    )
    st.session_state.test_base_values['Turbidity'] = st.sidebar.slider(
        "Base Turbidity (NTU)", 0.0, 20.0, st.session_state.test_base_values['Turbidity'], 0.1
    )
elif st.session_state.data_source == "Firebase Cloud":
    st.sidebar.info("Cloud Mode: Reading public Firebase Realtime DB")
    st.sidebar.markdown("### Firebase Settings")
    
    st.session_state.firebase_url = st.sidebar.text_input("Database URL", value=st.session_state.firebase_url, help="e.g. https://your-project-id.firebaseio.com/")
    st.session_state.firebase_node = st.sidebar.text_input("Data Node Path", value=st.session_state.firebase_node, help="Node path where sensor values are stored e.g. /sensors/latest")
    
    if st.sidebar.button("Connect to Firebase"):
        try:
            if not st.session_state.firebase_url:
                st.sidebar.error("Database URL is required")
            else:
                # Format URL for REST API
                base_url = st.session_state.firebase_url.rstrip('/')
                node_path = st.session_state.firebase_node.strip('/')
                
                # Test connection by fetching data
                test_url = f"{base_url}/{node_path}.json"
                response = requests.get(test_url, timeout=5)
                
                if response.status_code == 200:
                    st.session_state.firebase_connected = True
                    st.sidebar.success("✅ Connected to Firebase")
                elif response.status_code == 401:
                    st.sidebar.error("Permission Denied: Ensure database rules are set to public read")
                    st.session_state.firebase_connected = False
                else:
                    st.sidebar.error(f"Error {response.status_code}: {response.text}")
                    st.session_state.firebase_connected = False
        except Exception as e:
            st.sidebar.error(f"Firebase connection error: {str(e)}")
            st.session_state.firebase_connected = False
elif st.session_state.data_source == "Live Sensors":
    # Serial port selection (only show when not in test mode)
    available_ports = SensorReader.list_ports()
    selected_port = st.sidebar.selectbox(
        "Select Serial Port",
        options=available_ports,
        index=0 if available_ports else None
    )

if st.session_state.data_source == "Live Sensors":
    baud_rate = st.sidebar.number_input(
        "Baud Rate",
        min_value=9600,
        max_value=115200,
        value=9600,
        step=9600
    )
else:
    baud_rate = 9600  # Dummy value for test mode

# Database Configuration
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Database Settings")

st.session_state.db_enabled = st.sidebar.checkbox(
    "Enable Database Storage",
    value=st.session_state.db_enabled,
    help="Store all sensor readings in database"
)

if st.session_state.db_enabled:
    db_type = st.sidebar.selectbox(
        "Database Type",
        options=['sqlite', 'postgresql', 'mysql'],
        index=0,
        help="SQLite is recommended for local use"
    )
    
    if db_type == 'sqlite':
        db_path = st.sidebar.text_input(
            "Database Path",
            value="water_quality.db",
            help="Path to SQLite database file"
        )
        
        # Initialize SQLite database automatically
        if st.session_state.db_manager is None:
            try:
                st.session_state.db_manager = DatabaseManager(db_type='sqlite', db_path=db_path)
                st.sidebar.success("✅ Database connected")
            except Exception as e:
                st.sidebar.error(f"Database error: {str(e)}")
                st.session_state.db_manager = None
        elif hasattr(st.session_state.db_manager, 'db_path') and st.session_state.db_manager.db_path != db_path:
            # Reconnect if path changed
            try:
                st.session_state.db_manager.close()
                st.session_state.db_manager = DatabaseManager(db_type='sqlite', db_path=db_path)
                st.sidebar.success("✅ Database reconnected")
            except Exception as e:
                st.sidebar.error(f"Database error: {str(e)}")
                st.session_state.db_manager = None
        else:
            st.sidebar.success("✅ Database connected")
    else:
        st.sidebar.info(f"{db_type.capitalize()} configuration:")
        db_host = st.sidebar.text_input("Host", value="localhost")
        db_port = st.sidebar.number_input("Port", value=5432 if db_type == 'postgresql' else 3306)
        db_name = st.sidebar.text_input("Database Name", value="water_quality")
        db_user = st.sidebar.text_input("Username", value="")
        db_password = st.sidebar.text_input("Password", type="password", value="")
        
        if st.sidebar.button("Connect to Database"):
            try:
                if st.session_state.db_manager:
                    st.session_state.db_manager.close()
                st.session_state.db_manager = DatabaseManager(
                    db_type=db_type,
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password
                )
                st.sidebar.success("✅ Database connected")
            except Exception as e:
                st.sidebar.error(f"Connection failed: {str(e)}")
                st.session_state.db_manager = None
else:
    if st.session_state.db_manager:
        st.session_state.db_manager.close()
        st.session_state.db_manager = None

# Update interval
update_interval = st.sidebar.slider(
    "Update Interval (seconds)",
    min_value=1,
    max_value=60,
    value=5 if st.session_state.data_source == "Database (Latest)" else 2,
    step=1
)

# Max data points to keep
max_data_points = st.sidebar.number_input(
    "Max Data Points",
    min_value=10,
    max_value=1000,
    value=100,
    step=10
)

# ML Alert System Configuration
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 ML Alert System")

ml_enabled = st.sidebar.checkbox(
    "Enable ML Alerts",
    value=True,
    help="Use machine learning for anomaly detection"
)

if ml_enabled:
    st.sidebar.markdown("### Alert Thresholds")
    
    # pH Thresholds
    ph_min = st.sidebar.number_input("pH Min", 0.0, 14.0, 6.5, 0.1)
    ph_max = st.sidebar.number_input("pH Max", 0.0, 14.0, 8.5, 0.1)
    
    # Temperature Thresholds
    temp_min = st.sidebar.number_input("Temp Min (°C)", 0.0, 50.0, 15.0, 1.0)
    temp_max = st.sidebar.number_input("Temp Max (°C)", 0.0, 50.0, 30.0, 1.0)
    
    # TDS Thresholds
    tds_max = st.sidebar.number_input("TDS Max (ppm)", 0, 2000, 500, 10)
    
    # Turbidity Thresholds
    turb_max = st.sidebar.number_input("Turbidity Max (NTU)", 0.0, 50.0, 5.0, 0.1)
    
    # Update thresholds
    st.session_state.alert_system.update_thresholds({
        'pH': {'min': ph_min, 'max': ph_max, 'critical_min': ph_min - 0.5, 'critical_max': ph_max + 0.5},
        'Temperature': {'min': temp_min, 'max': temp_max, 'critical_min': temp_min - 5, 'critical_max': temp_max + 5},
        'TDS': {'min': 0, 'max': tds_max, 'critical_min': 0, 'critical_max': tds_max * 2},
        'Turbidity': {'min': 0, 'max': turb_max, 'critical_min': 0, 'critical_max': turb_max * 2}
    })
    
    # Train model button
    if st.sidebar.button("🔄 Train ML Model"):
        if st.session_state.db_manager:
            try:
                hist_data = st.session_state.db_manager.get_latest_readings(limit=100)
                if len(hist_data) >= 10:
                    st.session_state.alert_system.train_model(hist_data)
                    st.sidebar.success("✅ Model trained successfully!")
                else:
                    st.sidebar.warning("⚠️ Need at least 10 readings to train model")
            except Exception as e:
                st.sidebar.error(f"Training error: {str(e)}")
        else:
            st.sidebar.warning("⚠️ Connect to database first")

# Connect/Disconnect button (only show when Live Sensors is selected)
if st.session_state.data_source == "Live Sensors":
    if st.session_state.sensor_reader is None:
        if st.sidebar.button("🔌 Connect to Sensors", type="primary"):
            try:
                st.session_state.sensor_reader = SensorReader(selected_port, baud_rate)
                st.sidebar.success(f"Connected to {selected_port}")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Connection failed: {str(e)}")
    else:
        if st.sidebar.button("🔌 Disconnect"):
            st.session_state.sensor_reader.close()
            st.session_state.sensor_reader = None
            st.sidebar.info("Disconnected")
            st.rerun()
else:
    # In test mode, disconnect any existing sensor connection
    if st.session_state.sensor_reader:
        st.session_state.sensor_reader.close()
        st.session_state.sensor_reader = None

# Main dashboard header
st.markdown(
    """
    <div class="app-header">
        <div class="app-header-left">
            <div class="app-header-icon">💧</div>
            <div>
                <h1 class="app-header-title">Water Quality Monitor</h1>
                <p class="app-header-subtitle">ML‑POWERED WATER ANALYTICS</p>
            </div>
        </div>
        <div class="app-header-right">
            <div class="pill-badge">
                <span class="pill-dot"></span>
                <span>Live dashboard</span>
            </div>
            <span>Data source: <strong>{source}</strong></span>
        </div>
    </div>
    """.format(
        source=st.session_state.data_source
    ),
    unsafe_allow_html=True,
)

# Auto-refresh mechanism
should_read_data = (
    st.session_state.data_source == "Test Mode" or 
    (st.session_state.data_source == "Live Sensors" and st.session_state.sensor_reader) or 
    (st.session_state.data_source == "Database (Latest)" and st.session_state.db_manager) or
    (st.session_state.data_source == "Firebase Cloud" and st.session_state.firebase_connected)
)

if should_read_data:
    # Check if it's time to update
    current_time = datetime.now()
    should_update = (
        st.session_state.last_update is None or
        (current_time - st.session_state.last_update).total_seconds() >= update_interval
    )
    
    if should_update:
        try:
            # Read sensor data based on selected source
            if st.session_state.data_source == "Database (Latest)":
                # Read latest reading from database
                if st.session_state.db_manager:
                    db_df = st.session_state.db_manager.get_latest_readings(limit=1)
                    if len(db_df) > 0:
                        latest_row = db_df.iloc[-1]
                        sensor_values = {
                            'pH': float(latest_row.get('pH', 0)),
                            'Temperature': float(latest_row.get('Temperature', 0)),
                            'TDS': float(latest_row.get('TDS', 0)),
                            'Turbidity': float(latest_row.get('Turbidity', 0))
                        }
                        # Use timestamp from database
                        current_time = pd.to_datetime(latest_row['timestamp'])
                    else:
                        sensor_values = None
                else:
                    sensor_values = None
            elif st.session_state.data_source == "Firebase Cloud":
                if st.session_state.firebase_connected:
                    try:
                        base_url = st.session_state.firebase_url.rstrip('/')
                        node_path = st.session_state.firebase_node.strip('/')
                        req_url = f"{base_url}/{node_path}.json"
                        
                        response = requests.get(req_url, timeout=5)
                        if response.status_code == 200:
                            fb_data = response.json()
                            if fb_data and isinstance(fb_data, dict):
                                sensor_values = {
                                    'pH': float(fb_data.get('pH', fb_data.get('ph', 0))),
                                    'Temperature': float(fb_data.get('Temperature', fb_data.get('temperature', fb_data.get('temp', 0)))),
                                    'TDS': float(fb_data.get('TDS', fb_data.get('tds', 0))),
                                    'Turbidity': float(fb_data.get('Turbidity', fb_data.get('turbidity', fb_data.get('turbidity_ntu', 0))))
                                }
                            else:
                                sensor_values = None
                        else:
                            sensor_values = None
                    except Exception as e:
                        print(f"Firebase fetch error: {e}")
                        sensor_values = None
                else:
                    sensor_values = None
            elif st.session_state.test_mode:
                # Generate test data
                sensor_values = generate_test_data()
            else:
                # Read from real sensors
                sensor_values = st.session_state.sensor_reader.read_sensors() if st.session_state.sensor_reader else None
            
            if sensor_values:
                # Add timestamp
                sensor_values['timestamp'] = current_time
                
                # ML Analysis
                if ml_enabled:
                    # Auto-train model if we have enough data and it's not trained
                    if not st.session_state.alert_system.is_trained and st.session_state.db_manager:
                        try:
                            hist_data = st.session_state.db_manager.get_latest_readings(limit=50)
                            if len(hist_data) >= 10:
                                st.session_state.alert_system.train_model(hist_data)
                        except:
                            pass
                    
                    analysis = st.session_state.alert_system.analyze_reading(sensor_values)
                    st.session_state.ml_analysis.append(analysis)
                    # Keep only recent analyses
                    if len(st.session_state.ml_analysis) > max_data_points:
                        st.session_state.ml_analysis = st.session_state.ml_analysis[-max_data_points:]
                
                # Save to database if enabled (only if not reading from database)
                if st.session_state.db_enabled and st.session_state.db_manager and st.session_state.data_source != "Database (Latest)":
                    try:
                        st.session_state.db_manager.insert_reading(sensor_values, current_time)
                    except Exception as e:
                        st.sidebar.warning(f"Database save error: {str(e)}")
                
                # Append to session state
                st.session_state.sensor_data.append(sensor_values)
                
                # Keep only recent data points
                if len(st.session_state.sensor_data) > max_data_points:
                    st.session_state.sensor_data = st.session_state.sensor_data[-max_data_points:]
                
                st.session_state.last_update = current_time
                
        except Exception as e:
            st.error(f"Error reading sensors: {str(e)}")

# Display current readings
if st.session_state.sensor_data:
    latest_data = st.session_state.sensor_data[-1]
    
    # ML Analysis and Alerts Section
    if ml_enabled and st.session_state.ml_analysis:
        latest_analysis = st.session_state.ml_analysis[-1]
        
        # Alert Display
        if latest_analysis['threshold_alerts'] or latest_analysis['is_anomaly']:
            st.markdown("### 🚨 Active Alerts")
            
            # Critical alerts
            critical_alerts = [a for a in latest_analysis['threshold_alerts'] if a['severity'] == 'critical']
            if critical_alerts:
                for alert in critical_alerts:
                    st.error(f"🔴 **CRITICAL**: {alert['message']}")
            
            # Warning alerts
            warning_alerts = [a for a in latest_analysis['threshold_alerts'] if a['severity'] == 'warning']
            if warning_alerts:
                for alert in warning_alerts:
                    st.warning(f"🟡 **WARNING**: {alert['message']}")
            
            # ML Anomaly detection
            if latest_analysis['is_anomaly']:
                st.warning(f"🤖 **ML ANOMALY DETECTED**: Unusual pattern detected (Score: {latest_analysis['anomaly_score']:.2f})")
        
        # Health Score Gauge
        st.markdown("### 📊 Overall Health Score")
        health_col1, health_col2 = st.columns([2, 1])
        with health_col1:
            health_fig = create_health_score_gauge(latest_analysis['health_score'])
            st.plotly_chart(health_fig, use_container_width=True)
        with health_col2:
            status_emoji = {
                'good': '✅',
                'fair': '⚠️',
                'poor': '❌',
                'warning': '🟡',
                'critical': '🔴',
                'anomaly': '🤖'
            }
            status = latest_analysis['overall_status']
            st.metric("Status", f"{status_emoji.get(status, '❓')} {status.upper()}")
            st.metric("Health Score", f"{latest_analysis['health_score']:.1f}/100")
            if latest_analysis['is_anomaly']:
                st.metric("Anomaly Score", f"{latest_analysis['anomaly_score']:.2f}")
        
        st.markdown("---")
    
    # Parameter Gauge Charts
    st.markdown("### 📈 Parameter Gauges")
    gauge_col1, gauge_col2 = st.columns(2)
    gauge_col3, gauge_col4 = st.columns(2)
    
    thresholds = st.session_state.alert_system.thresholds
    
    with gauge_col1:
        ph_fig = create_gauge_chart(
            latest_data.get('pH', 0),
            min_val=0, max_val=14,
            title="pH Level",
            unit="",
            threshold_low=thresholds['pH']['min'],
            threshold_high=thresholds['pH']['max']
        )
        st.plotly_chart(ph_fig, use_container_width=True)
    
    with gauge_col2:
        temp_fig = create_gauge_chart(
            latest_data.get('Temperature', 0),
            min_val=0, max_val=50,
            title="Temperature",
            unit="°C",
            threshold_low=thresholds['Temperature']['min'],
            threshold_high=thresholds['Temperature']['max']
        )
        st.plotly_chart(temp_fig, use_container_width=True)
    
    with gauge_col3:
        tds_fig = create_gauge_chart(
            latest_data.get('TDS', 0),
            min_val=0, max_val=1000,
            title="TDS",
            unit="ppm",
            threshold_low=None,
            threshold_high=thresholds['TDS']['max']
        )
        st.plotly_chart(tds_fig, use_container_width=True)
    
    with gauge_col4:
        turb_fig = create_gauge_chart(
            latest_data.get('Turbidity', 0),
            min_val=0, max_val=20,
            title="Turbidity",
            unit="NTU",
            threshold_low=None,
            threshold_high=thresholds['Turbidity']['max']
        )
        st.plotly_chart(turb_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # pH Level
    ph_value = latest_data.get('pH', 0)
    ph_status = get_status_color(ph_value, 6.5, 8.5)
    with col1:
        st.metric(
            label="pH Level",
            value=f"{ph_value:.2f}",
            delta=None
        )
    
    # Temperature
    temp_value = latest_data.get('Temperature', 0)
    temp_status = get_status_color(temp_value, 15, 30)
    with col2:
        st.metric(
            label="Temperature (°C)",
            value=f"{temp_value:.2f}",
            delta=None
        )
    
    # TDS (Total Dissolved Solids)
    tds_value = latest_data.get('TDS', 0)
    tds_status = get_status_color(tds_value, 0, 500)
    with col3:
        st.metric(
            label="TDS (ppm)",
            value=f"{tds_value:.0f}",
            delta=None
        )
    
    # Turbidity
    turbidity_value = latest_data.get('Turbidity', 0)
    turbidity_status = get_status_color(turbidity_value, 0, 5)
    with col4:
        st.metric(
            label="Turbidity (NTU)",
            value=f"{turbidity_value:.2f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Last update time
    st.caption(f"Last updated: {format_timestamp(st.session_state.last_update)}")
    
    # Create time series charts
    if len(st.session_state.sensor_data) > 1:
        df = pd.DataFrame(st.session_state.sensor_data)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('pH Level', 'Temperature (°C)', 'TDS (ppm)', 'Turbidity (NTU)'),
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # pH Chart
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['pH'],
                mode='lines+markers',
                name='pH',
                line=dict(color='#1f77b4', width=2)
            ),
            row=1, col=1
        )
        
        # Temperature Chart
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['Temperature'],
                mode='lines+markers',
                name='Temperature',
                line=dict(color='#ff7f0e', width=2)
            ),
            row=1, col=2
        )
        
        # TDS Chart
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['TDS'],
                mode='lines+markers',
                name='TDS',
                line=dict(color='#2ca02c', width=2)
            ),
            row=2, col=1
        )
        
        # Turbidity Chart
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['Turbidity'],
                mode='lines+markers',
                name='Turbidity',
                line=dict(color='#d62728', width=2)
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text="Real-time Water Quality Parameters",
            title_x=0.5,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#0f172a")
        )
        
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=2)
        fig.update_yaxes(title_text="pH", row=1, col=1)
        fig.update_yaxes(title_text="°C", row=1, col=2)
        fig.update_yaxes(title_text="ppm", row=2, col=1)
        fig.update_yaxes(title_text="NTU", row=2, col=2)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("📊 Recent Readings")
        display_df = df.tail(10)[['timestamp', 'pH', 'Temperature', 'TDS', 'Turbidity']].copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Enhanced Visualizations
    st.markdown("---")
    st.subheader("📊 Enhanced Analytics")
    
    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs(["Heatmap", "Correlation", "Distributions", "Alert Timeline"])
    
    with viz_tab1:
        st.markdown("### Parameter Heatmap (Last 24 Hours)")
        if len(st.session_state.sensor_data) > 1:
            df_viz = pd.DataFrame(st.session_state.sensor_data)
            heatmap_fig = create_heatmap_chart(df_viz, hours=24)
            st.plotly_chart(heatmap_fig, use_container_width=True)
        else:
            st.info("Need more data points for heatmap visualization")
    
    with viz_tab2:
        st.markdown("### Parameter Correlation Matrix")
        if len(st.session_state.sensor_data) > 2:
            df_viz = pd.DataFrame(st.session_state.sensor_data)
            corr_fig = create_correlation_matrix(df_viz)
            st.plotly_chart(corr_fig, use_container_width=True)
        else:
            st.info("Need more data points for correlation analysis")
    
    with viz_tab3:
        st.markdown("### Value Distributions")
        if len(st.session_state.sensor_data) > 5:
            df_viz = pd.DataFrame(st.session_state.sensor_data)
            dist_fig = create_parameter_distribution(df_viz)
            st.plotly_chart(dist_fig, use_container_width=True)
        else:
            st.info("Need more data points for distribution analysis")
    
    with viz_tab4:
        st.markdown("### Alert Timeline")
        if ml_enabled and st.session_state.alert_system.alert_history:
            recent_alerts = st.session_state.alert_system.get_recent_alerts(hours=24)
            if recent_alerts:
                alert_timeline_fig = create_alert_timeline(recent_alerts)
                st.plotly_chart(alert_timeline_fig, use_container_width=True)
                
                # Alert Statistics
                alert_stats = st.session_state.alert_system.get_alert_statistics()
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("Total Alerts (24h)", alert_stats['total_alerts'])
                with stat_col2:
                    st.metric("Critical Alerts", alert_stats['critical_alerts'])
                with stat_col3:
                    st.metric("Warning Alerts", alert_stats['warning_alerts'])
                
                # Alerts by parameter
                if alert_stats['alerts_by_parameter']:
                    st.markdown("#### Alerts by Parameter")
                    for param, count in alert_stats['alerts_by_parameter'].items():
                        st.write(f"- **{param}**: {count} alerts")
            else:
                st.success("✅ No alerts in the last 24 hours!")
        else:
            st.info("Enable ML Alerts to see alert timeline")
    
    # Database Statistics and Historical Data
    if st.session_state.db_enabled and st.session_state.db_manager:
        st.markdown("---")
        st.subheader("💾 Database Information")
        
        try:
            stats = st.session_state.db_manager.get_statistics()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Readings", f"{stats['total_readings']:,}")
            with col2:
                if stats['first_reading']:
                    st.metric("First Reading", pd.to_datetime(stats['first_reading']).strftime("%Y-%m-%d"))
                else:
                    st.metric("First Reading", "N/A")
            with col3:
                if stats['last_reading']:
                    st.metric("Last Reading", pd.to_datetime(stats['last_reading']).strftime("%Y-%m-%d"))
                else:
                    st.metric("Last Reading", "N/A")
            with col4:
                st.metric("Avg pH", f"{stats['avg_ph']:.2f}")
            
            # Historical Data Viewer
            with st.expander("📊 View Historical Data from Database"):
                days_back = st.slider("Days to look back", 1, 30, 7)
                start_date = datetime.now() - timedelta(days=days_back)
                end_date = datetime.now()
                
                if st.button("Load Historical Data"):
                    try:
                        hist_df = st.session_state.db_manager.get_readings_by_date_range(start_date, end_date)
                        
                        if len(hist_df) > 0:
                            st.success(f"Loaded {len(hist_df)} readings from database")
                            
                            # Display historical charts
                            fig_hist = make_subplots(
                                rows=2, cols=2,
                                subplot_titles=('pH Level', 'Temperature (°C)', 'TDS (ppm)', 'Turbidity (NTU)'),
                                vertical_spacing=0.12,
                                horizontal_spacing=0.1
                            )
                            
                            fig_hist.add_trace(
                                go.Scatter(x=hist_df['timestamp'], y=hist_df['pH'], mode='lines+markers', name='pH', line=dict(color='#1f77b4')),
                                row=1, col=1
                            )
                            fig_hist.add_trace(
                                go.Scatter(x=hist_df['timestamp'], y=hist_df['Temperature'], mode='lines+markers', name='Temperature', line=dict(color='#ff7f0e')),
                                row=1, col=2
                            )
                            fig_hist.add_trace(
                                go.Scatter(x=hist_df['timestamp'], y=hist_df['TDS'], mode='lines+markers', name='TDS', line=dict(color='#2ca02c')),
                                row=2, col=1
                            )
                            fig_hist.add_trace(
                                go.Scatter(x=hist_df['timestamp'], y=hist_df['Turbidity'], mode='lines+markers', name='Turbidity', line=dict(color='#d62728')),
                                row=2, col=2
                            )
                            
                            fig_hist.update_layout(height=600, showlegend=False, title_text=f"Historical Data ({days_back} days)")
                            fig_hist.update_xaxes(title_text="Time", row=2, col=1)
                            fig_hist.update_xaxes(title_text="Time", row=2, col=2)
                            
                            st.plotly_chart(fig_hist, use_container_width=True)
                            
                            # Display data table
                            display_hist_df = hist_df[['timestamp', 'pH', 'Temperature', 'TDS', 'Turbidity']].copy()
                            display_hist_df['timestamp'] = display_hist_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                            st.dataframe(display_hist_df, use_container_width=True, hide_index=True)
                            
                            # Download button
                            csv = display_hist_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Historical Data as CSV",
                                data=csv,
                                file_name=f"water_quality_data_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.info("No data found in the selected date range.")
                    except Exception as e:
                        st.error(f"Error loading historical data: {str(e)}")
                
                # Cleanup old data
                st.markdown("### Database Maintenance")
                days_to_keep = st.number_input("Keep data for (days)", min_value=1, max_value=365, value=30)
                if st.button("🗑️ Delete Old Data"):
                    try:
                        deleted = st.session_state.db_manager.delete_old_readings(days_to_keep)
                        st.success(f"Deleted {deleted} old readings")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting data: {str(e)}")
        except Exception as e:
            st.error(f"Database error: {str(e)}")
    
    # Auto-refresh
    time.sleep(update_interval)
    st.rerun()
    
else:
    if st.session_state.data_source == "Database (Latest)":
        if st.session_state.db_manager:
            st.info("📊 Reading from database. Make sure test data generator is running!")
            st.markdown("""
            ### To see live updates:
            1. Open a terminal and run: `python populate_test_data.py`
            2. The dashboard will automatically show new readings every 5 seconds
            3. Watch the values change in real-time!
            """)
        else:
            st.warning("⚠️ Database not connected. Enable database storage in the sidebar.")
    elif st.session_state.test_mode:
        st.info("🧪 Test Mode Active - Generating simulated sensor data. Adjust values in the sidebar.")
    else:
        st.info("👆 Please connect to sensors using the sidebar to start monitoring, or select 'Database (Latest)' to view test data.")
        st.markdown("""
        ### Expected Sensor Data Format
        The sensors should send data in the following format (one line per reading):
        ```
        pH:7.2,Temperature:25.5,TDS:350,Turbidity:2.1
        ```
        
        Or JSON format:
        ```json
        {"pH": 7.2, "Temperature": 25.5, "TDS": 350, "Turbidity": 2.1}
        ```
        
        ### Data Source Flow:
        1. **Physical Sensors** → Connected to Arduino pins
        2. **Arduino** → Reads sensors and sends via Serial (USB)
        3. **Serial Port** → Transmits data to your computer
        4. **Python (`sensor_reader.py`)** → Reads from Serial port
        5. **Dashboard** → Displays values in real-time
        
        See `DATA_SOURCES.md` for more details!
        """)
