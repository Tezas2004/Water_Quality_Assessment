"""
Test Data Generator
Populates database with test sensor readings that change over time
Run this script in the background while viewing the dashboard
"""

import time
import random
from datetime import datetime, timedelta
from database_manager import DatabaseManager
import sys

def generate_realistic_sensor_data(base_time=None, variation_factor=1.0):
    """
    Generate realistic sensor data with natural variations
    
    Args:
        base_time: Base timestamp (defaults to now)
        variation_factor: How much variation to add (0.0 to 1.0)
    """
    if base_time is None:
        base_time = datetime.now()
    
    # Base values (normal water quality)
    base_values = {
        'pH': 7.0,
        'Temperature': 22.0,
        'TDS': 300.0,
        'Turbidity': 2.0
    }
    
    # Add time-based variations (simulate day/night cycles, etc.)
    hour = base_time.hour
    minute = base_time.minute
    
    # Temperature varies with time of day (warmer during day)
    temp_variation = 3 * variation_factor * (0.5 + 0.5 * abs((hour - 12) / 12))
    base_values['Temperature'] += temp_variation + random.uniform(-1, 1) * variation_factor
    
    # pH slightly varies
    base_values['pH'] += random.uniform(-0.5, 0.5) * variation_factor
    
    # TDS gradually increases over time (simulating dissolved solids)
    tds_increase = (minute / 60.0) * 10 * variation_factor
    base_values['TDS'] += tds_increase + random.uniform(-20, 20) * variation_factor
    
    # Turbidity varies more randomly
    base_values['Turbidity'] += random.uniform(-0.5, 0.5) * variation_factor
    
    # Ensure values stay in reasonable ranges
    base_values['pH'] = max(0, min(14, base_values['pH']))
    base_values['Temperature'] = max(0, min(50, base_values['Temperature']))
    base_values['TDS'] = max(0, min(1000, base_values['TDS']))
    base_values['Turbidity'] = max(0, min(20, base_values['Turbidity']))
    
    return base_values

def populate_test_data(db_path='water_quality.db', interval=5, duration=None, num_readings=None):
    """
    Continuously populate database with test data
    
    Args:
        db_path: Path to SQLite database
        interval: Seconds between readings (default: 5)
        duration: How long to run in seconds (None = infinite)
        num_readings: Number of readings to generate (None = infinite)
    """
    print(f"🚀 Starting test data generator...")
    print(f"📊 Database: {db_path}")
    print(f"⏱️  Update interval: {interval} seconds")
    print(f"Press Ctrl+C to stop\n")
    
    db_manager = DatabaseManager(db_type='sqlite', db_path=db_path)
    
    start_time = datetime.now()
    reading_count = 0
    
    try:
        while True:
            # Check if we should stop
            if duration and (datetime.now() - start_time).total_seconds() >= duration:
                print(f"\n⏹️  Duration reached. Stopping...")
                break
            
            if num_readings and reading_count >= num_readings:
                print(f"\n⏹️  Generated {num_readings} readings. Stopping...")
                break
            
            # Generate test data
            sensor_data = generate_realistic_sensor_data()
            timestamp = datetime.now()
            
            # Insert into database
            db_manager.insert_reading(sensor_data, timestamp)
            reading_count += 1
            
            # Display status
            print(f"[{timestamp.strftime('%H:%M:%S')}] Reading #{reading_count}: "
                  f"pH={sensor_data['pH']:.2f}, "
                  f"Temp={sensor_data['Temperature']:.2f}°C, "
                  f"TDS={sensor_data['TDS']:.0f}ppm, "
                  f"Turb={sensor_data['Turbidity']:.2f}NTU")
            
            # Wait for next reading
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Stopped by user")
        print(f"📊 Total readings generated: {reading_count}")
    finally:
        db_manager.close()
        print("✅ Database connection closed")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate test sensor data for water quality dashboard')
    parser.add_argument('--db', type=str, default='water_quality.db', help='Database path')
    parser.add_argument('--interval', type=int, default=5, help='Seconds between readings (default: 5)')
    parser.add_argument('--duration', type=int, help='Run for N seconds then stop')
    parser.add_argument('--readings', type=int, help='Generate N readings then stop')
    
    args = parser.parse_args()
    
    populate_test_data(
        db_path=args.db,
        interval=args.interval,
        duration=args.duration,
        num_readings=args.readings
    )
