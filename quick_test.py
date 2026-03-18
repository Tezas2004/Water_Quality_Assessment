"""
Quick Test - Populate database with initial test data
Run this once to add some test data, then use populate_test_data.py for continuous updates
"""

from database_manager import DatabaseManager
from datetime import datetime, timedelta
import random

def quick_populate(db_path='water_quality.db', num_readings=20):
    """Quickly populate database with test readings"""
    print(f"📊 Populating database with {num_readings} test readings...")
    
    db_manager = DatabaseManager(db_type='sqlite', db_path=db_path)
    
    base_time = datetime.now() - timedelta(minutes=num_readings)
    
    for i in range(num_readings):
        # Generate test data with variations
        timestamp = base_time + timedelta(minutes=i)
        
        sensor_data = {
            'pH': round(7.0 + random.uniform(-0.5, 0.5), 2),
            'Temperature': round(22.0 + random.uniform(-2, 2), 2),
            'TDS': round(300 + random.uniform(-50, 50), 0),
            'Turbidity': round(2.0 + random.uniform(-0.5, 0.5), 2)
        }
        
        db_manager.insert_reading(sensor_data, timestamp)
        print(f"✓ Added reading {i+1}/{num_readings}: pH={sensor_data['pH']:.2f}, Temp={sensor_data['Temperature']:.2f}°C")
    
    db_manager.close()
    print(f"\n✅ Successfully added {num_readings} test readings!")
    print("🚀 Now run: python populate_test_data.py")

if __name__ == "__main__":
    import sys
    num_readings = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    quick_populate(num_readings=num_readings)
