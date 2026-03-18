# Live Water Quality Monitoring Dashboard

A real-time Streamlit dashboard that automatically updates when water quality sensors detect changes.

## Features

- 🔄 **Real-time Updates**: Automatically refreshes when sensor values change
- 📊 **Live Charts**: Interactive time-series graphs for all parameters
- 📈 **Multiple Parameters**: Monitors pH, Temperature, TDS, and Turbidity
- 🎨 **Beautiful UI**: Modern, responsive dashboard design with gauge charts and heatmaps
- ⚙️ **Configurable**: Adjustable update intervals and data retention
- 💾 **Database Storage**: Automatically saves all readings to SQLite/PostgreSQL/MySQL database
- 📜 **Historical Data**: View and download historical sensor data
- 🧪 **Test Mode**: Test dashboard with simulated data without physical sensors
- 🤖 **ML-Powered Alerts**: Machine learning anomaly detection using Isolation Forest
- 🚨 **Smart Alert System**: Configurable thresholds with critical/warning levels
- 📊 **Enhanced Visualizations**: Heatmaps, correlation matrices, distributions, and alert timelines
- 💯 **Health Score**: Overall water quality health score (0-100)

## Prerequisites

- Python 3.8 or higher
- Water quality sensors connected via Arduino/ESP32 or similar microcontroller
- USB cable to connect sensors to your computer

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Connect your sensors:**
   - Connect your water quality sensors to an Arduino/ESP32
   - Upload sensor reading code to your microcontroller (see example below)
   - Connect the microcontroller to your computer via USB

## Quick Start - See Live Updates

### Option 1: Test with Database (Recommended for Testing)

1. **Populate database with test data:**
   ```bash
   python populate_test_data.py
   ```
   This will continuously add test readings every 5 seconds.

2. **Start the dashboard:**
   ```bash
   streamlit run water_quality_dashboard.py
   ```

3. **Configure dashboard:**
   - Enable "Database Storage" in sidebar
   - Select "Database (Latest)" as data source
   - Set update interval to 5 seconds
   - Watch values update live!

### Option 2: Use Real Sensors

1. **Start the dashboard:**
   ```bash
   streamlit run water_quality_dashboard.py
   ```

2. **Configure connection:**
   - Select "Live Sensors" as data source
   - Select your serial port from the sidebar
   - Set the baud rate (default: 9600)
   - Click "Connect to Sensors"

3. **Monitor your data:**
   - The dashboard will automatically update at the specified interval
   - View real-time metrics and historical charts
   - All readings are saved to database automatically

## Sensor Data Format

Your microcontroller should send data in one of these formats:

### Option 1: JSON Format (Recommended)
```json
{"pH": 7.2, "Temperature": 25.5, "TDS": 350, "Turbidity": 2.1}
```

### Option 2: CSV-like Format
```
pH:7.2,Temperature:25.5,TDS:350,Turbidity:2.1
```

### Option 3: Space-separated Format
```
pH:7.2 Temperature:25.5 TDS:350 Turbidity:2.1
```

## Example Arduino Code

Here's a sample Arduino sketch to get you started:

```cpp
void setup() {
  Serial.begin(9600);
  // Initialize your sensors here
}

void loop() {
  // Read sensor values
  float pH = read_pH_sensor();
  float temperature = read_temperature_sensor();
  float tds = read_tds_sensor();
  float turbidity = read_turbidity_sensor();
  
  // Send data in JSON format
  Serial.print("{");
  Serial.print("\"pH\":");
  Serial.print(pH);
  Serial.print(",\"Temperature\":");
  Serial.print(temperature);
  Serial.print(",\"TDS\":");
  Serial.print(tds);
  Serial.print(",\"Turbidity\":");
  Serial.print(turbidity);
  Serial.println("}");
  
  delay(2000); // Wait 2 seconds between readings
}
```

## Configuration Options

- **Update Interval**: How often to read sensors (1-60 seconds)
- **Max Data Points**: Number of historical readings to keep in memory (10-1000)
- **Baud Rate**: Serial communication speed (typically 9600 or 115200)
- **Database Storage**: Enable/disable automatic database storage
- **Database Type**: Choose between SQLite (local), PostgreSQL, or MySQL

## Database Storage

The dashboard automatically saves all sensor readings to a database when enabled:

### SQLite (Default - Recommended for Local Use)
- No setup required - just enable "Database Storage" in the sidebar
- Database file: `water_quality.db` (created automatically)
- Perfect for single-user, local deployments

### PostgreSQL/MySQL (For Production)
1. Enable "Database Storage" in sidebar
2. Select PostgreSQL or MySQL
3. Enter connection details (host, port, database name, username, password)
4. Click "Connect to Database"

### Database Features
- **Automatic Storage**: Every sensor reading is saved with timestamp
- **Historical Viewing**: View data from any date range
- **Statistics**: See total readings, averages, and date ranges
- **Data Export**: Download historical data as CSV
- **Data Cleanup**: Delete old data to manage database size

### Database Schema
```sql
CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    pH REAL,
    temperature REAL,
    tds REAL,
    turbidity REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### Connection Issues
- Make sure your microcontroller is connected and powered on
- Check that the correct serial port is selected
- Verify the baud rate matches your Arduino code
- On Linux/Mac, you may need to add your user to the `dialout` group:
  ```bash
  sudo usermod -a -G dialout $USER
  ```

### No Data Appearing
- Verify your sensors are working with Arduino Serial Monitor
- Check that data format matches one of the supported formats
- Ensure sensors are properly calibrated

### Port Not Found
- Unplug and reconnect your USB cable
- Check Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac)
- Try different USB ports

## Customization

You can customize the dashboard by modifying:
- **Parameter thresholds**: Edit the `get_status_color()` function
- **Displayed parameters**: Add new metrics in the dashboard code
- **Chart styling**: Modify Plotly chart configurations
- **Update logic**: Adjust the auto-refresh mechanism

## License

This project is open source and available for personal and educational use.
