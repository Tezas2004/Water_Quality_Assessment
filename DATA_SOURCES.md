# Data Source Explanation

## Where Do the Sensor Values Come From?

The dashboard reads sensor values through the following data flow:

```
Physical Sensors → Arduino/Microcontroller → USB Serial Port → Python → Dashboard
```

### Complete Data Flow:

1. **Physical Sensors** (pH, Temperature, TDS, Turbidity sensors)
   - Connected to Arduino pins (analog or digital)
   - Continuously measure water quality parameters

2. **Arduino/Microcontroller**
   - Reads analog/digital values from sensors
   - Converts raw readings to actual values (pH, °C, ppm, NTU)
   - Sends data via Serial communication (USB cable)
   - Format: `{"pH": 7.2, "Temperature": 25.5, "TDS": 350, "Turbidity": 2.1}`

3. **USB Serial Port** (COM3, /dev/ttyUSB0, etc.)
   - Physical connection between Arduino and computer
   - Transmits data at specified baud rate (9600, 115200, etc.)

4. **Python (`sensor_reader.py`)**
   - Uses `pyserial` library to read from Serial port
   - Parses incoming data (JSON, CSV, or space-separated format)
   - Returns dictionary with sensor values

5. **Streamlit Dashboard (`water_quality_dashboard.py`)**
   - Calls `sensor_reader.read_sensors()` every N seconds
   - Displays values in real-time
   - Updates charts and metrics automatically

## Current Implementation

**Line 129 in `water_quality_dashboard.py`:**
```python
sensor_values = st.session_state.sensor_reader.read_sensors()
```

**Line 57-61 in `sensor_reader.py`:**
```python
if self.serial_connection.in_waiting > 0:
    line = self.serial_connection.readline().decode('utf-8').strip()
    if line:
        return self._parse_sensor_data(line)
```

This reads directly from the Serial port where your Arduino is sending data.

## Alternative Data Sources

If you don't have physical sensors yet, you can modify the code to read from:

### Option 1: CSV File
```python
# Read from CSV file
df = pd.read_csv('sensor_data.csv')
latest = df.iloc[-1].to_dict()
```

### Option 2: Database (SQLite, MySQL, PostgreSQL)
```python
# Read from database
import sqlite3
conn = sqlite3.connect('sensor_data.db')
df = pd.read_sql("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1", conn)
```

### Option 3: REST API
```python
# Read from API endpoint
import requests
response = requests.get('http://your-api.com/sensors/latest')
sensor_values = response.json()
```

### Option 4: MQTT Broker (IoT)
```python
# Subscribe to MQTT topic
import paho.mqtt.client as mqtt
# Receive messages from MQTT broker
```

### Option 5: Mock/Test Data (for development)
See the updated dashboard code - it now includes a "Test Mode" option!

## Testing Without Sensors

The dashboard now includes a **Test Mode** that generates simulated sensor data. This is useful for:
- Testing the dashboard UI
- Development without hardware
- Demonstrations
- Learning how the system works

Enable Test Mode in the sidebar to use simulated data.
