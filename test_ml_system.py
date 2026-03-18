"""
Test script for ML Alert System
Tests the ML model, alerts, and visualizations
"""

from ml_alert_system import WaterQualityAlertSystem
from database_manager import DatabaseManager
from visualizations import (
    create_gauge_chart, create_health_score_gauge,
    create_heatmap_chart, create_correlation_matrix,
    create_parameter_distribution
)
import pandas as pd

print("🧪 Testing ML Alert System...")
print("=" * 50)

# Initialize alert system
alert_system = WaterQualityAlertSystem()
print("✅ Alert system initialized")

# Load test data from database
print("\n📊 Loading test data from database...")
db_manager = DatabaseManager()
readings = db_manager.get_latest_readings(limit=20)

if len(readings) < 10:
    print(f"⚠️  Only {len(readings)} readings found. Need at least 10 for ML training.")
    print("   Run: python populate_test_data.py --readings 20")
else:
    print(f"✅ Loaded {len(readings)} readings from database")
    
    # Train the model
    print("\n🤖 Training ML model...")
    alert_system.train_model(readings)
    if alert_system.is_trained:
        print("✅ Model trained successfully!")
    else:
        print("⚠️  Model training failed or insufficient data")
    
    # Test with normal values
    print("\n📈 Testing with normal values...")
    normal_data = {
        'pH': 7.2,
        'Temperature': 22.5,
        'TDS': 300,
        'Turbidity': 2.0
    }
    analysis = alert_system.analyze_reading(normal_data)
    print(f"   Health Score: {analysis['health_score']:.1f}/100")
    print(f"   Status: {analysis['overall_status']}")
    print(f"   Alerts: {len(analysis['threshold_alerts'])}")
    print(f"   Anomaly: {analysis['is_anomaly']}")
    
    # Test with warning values
    print("\n⚠️  Testing with warning values (pH out of range)...")
    warning_data = {
        'pH': 9.0,  # Above normal threshold
        'Temperature': 22.5,
        'TDS': 300,
        'Turbidity': 2.0
    }
    analysis = alert_system.analyze_reading(warning_data)
    print(f"   Health Score: {analysis['health_score']:.1f}/100")
    print(f"   Status: {analysis['overall_status']}")
    print(f"   Alerts: {len(analysis['threshold_alerts'])}")
    for alert in analysis['threshold_alerts']:
        print(f"     - {alert['severity'].upper()}: {alert['message']}")
    
    # Test with critical values
    print("\n🔴 Testing with critical values (multiple parameters out of range)...")
    critical_data = {
        'pH': 5.5,  # Critical low
        'Temperature': 40.0,  # Critical high
        'TDS': 1200,  # Critical high
        'Turbidity': 12.0  # Critical high
    }
    analysis = alert_system.analyze_reading(critical_data)
    print(f"   Health Score: {analysis['health_score']:.1f}/100")
    print(f"   Status: {analysis['overall_status']}")
    print(f"   Alerts: {len(analysis['threshold_alerts'])}")
    for alert in analysis['threshold_alerts']:
        print(f"     - {alert['severity'].upper()}: {alert['message']}")
    
    # Test visualizations
    print("\n📊 Testing visualizations...")
    try:
        gauge_fig = create_gauge_chart(7.2, 0, 14, "pH Level", "", 6.5, 8.5)
        print("✅ Gauge chart created successfully")
        
        health_fig = create_health_score_gauge(85.5)
        print("✅ Health score gauge created successfully")
        
        heatmap_fig = create_heatmap_chart(readings, hours=24)
        print("✅ Heatmap created successfully")
        
        corr_fig = create_correlation_matrix(readings)
        print("✅ Correlation matrix created successfully")
        
        dist_fig = create_parameter_distribution(readings)
        print("✅ Distribution charts created successfully")
        
    except Exception as e:
        print(f"❌ Visualization error: {e}")
    
    # Test alert statistics
    print("\n📈 Alert Statistics:")
    stats = alert_system.get_alert_statistics()
    print(f"   Total Alerts (24h): {stats['total_alerts']}")
    print(f"   Critical Alerts: {stats['critical_alerts']}")
    print(f"   Warning Alerts: {stats['warning_alerts']}")
    if stats['alerts_by_parameter']:
        print("   Alerts by Parameter:")
        for param, count in stats['alerts_by_parameter'].items():
            print(f"     - {param}: {count}")

print("\n" + "=" * 50)
print("✅ Testing complete!")
print("\n💡 Next steps:")
print("   1. Start dashboard: streamlit run water_quality_dashboard.py")
print("   2. Enable 'Database Storage' in sidebar")
print("   3. Select 'Database (Latest)' as data source")
print("   4. Enable 'ML Alerts' in sidebar")
print("   5. Watch the dashboard update with ML alerts and visualizations!")

db_manager.close()
