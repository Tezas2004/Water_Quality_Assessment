# ML Alert System & Enhanced Visualizations

## 🤖 Machine Learning Features

### Anomaly Detection
- **Isolation Forest Algorithm**: Detects unusual patterns in sensor readings
- **Auto-training**: Model automatically trains when enough historical data is available (10+ readings)
- **Anomaly Scoring**: Provides anomaly scores to quantify how unusual readings are

### Alert System
- **Threshold-based Alerts**: 
  - **Critical**: Values exceed critical thresholds
  - **Warning**: Values exceed normal thresholds but within critical range
- **ML Anomaly Alerts**: Detects unusual patterns even when within thresholds
- **Configurable Thresholds**: Adjust thresholds for each parameter in the sidebar

### Health Score
- **Overall Health Score (0-100)**: Calculated based on all parameters
  - 80-100: Good ✅
  - 60-80: Fair ⚠️
  - Below 60: Poor ❌
- **Status Indicators**: Visual status badges with emojis

## 📊 Enhanced Visualizations

### 1. Parameter Gauge Charts
- **Real-time Gauges**: Visual gauge charts for each parameter
- **Color-coded**: Green (normal), Orange (warning), Red (critical)
- **Threshold Indicators**: Visual markers for threshold limits

### 2. Overall Health Score Gauge
- **Large Gauge Display**: Prominent health score visualization
- **Status Display**: Current status with emoji indicators
- **Anomaly Score**: Shows ML-detected anomaly scores

### 3. Parameter Heatmap
- **24-hour Heatmap**: Color-coded heatmap showing parameter values over time
- **Easy Pattern Recognition**: Quickly identify trends and anomalies
- **Time-based Visualization**: See how parameters change throughout the day

### 4. Correlation Matrix
- **Parameter Relationships**: See how parameters correlate with each other
- **Color-coded**: Red (negative correlation), Blue (positive correlation)
- **Statistical Analysis**: Understand parameter interdependencies

### 5. Value Distributions
- **Histogram Charts**: Distribution of values for each parameter
- **Pattern Analysis**: Understand normal value ranges
- **Outlier Detection**: Visual identification of unusual values

### 6. Alert Timeline
- **Visual Timeline**: See when alerts occurred
- **Severity Indicators**: Different markers for critical/warning/anomaly alerts
- **Alert Statistics**: Summary of alerts in last 24 hours
- **Parameter Breakdown**: See which parameters trigger most alerts

## 🚨 Alert Types

### Critical Alerts
- Triggered when values exceed critical thresholds
- Displayed with red 🔴 indicators
- Requires immediate attention

### Warning Alerts
- Triggered when values exceed normal thresholds
- Displayed with orange 🟡 indicators
- Monitor closely

### ML Anomaly Alerts
- Triggered by ML model detecting unusual patterns
- Displayed with purple 🤖 indicators
- May indicate emerging issues

## ⚙️ Configuration

### Setting Thresholds
1. Enable "ML Alerts" in sidebar
2. Adjust threshold values:
   - **pH**: Min/Max values (default: 6.5-8.5)
   - **Temperature**: Min/Max in °C (default: 15-30)
   - **TDS**: Max value in ppm (default: 500)
   - **Turbidity**: Max value in NTU (default: 5.0)

### Training the Model
- **Automatic**: Model trains automatically when 10+ readings available
- **Manual**: Click "🔄 Train ML Model" button in sidebar
- **Data Requirement**: Needs at least 10 historical readings

## 📈 Using the Visualizations

### Heatmap Tab
- View parameter values as color-coded heatmap
- Identify time periods with issues
- See patterns over 24-hour period

### Correlation Tab
- Understand relationships between parameters
- Identify which parameters move together
- Use for predictive insights

### Distributions Tab
- See value distributions for each parameter
- Identify normal ranges
- Spot outliers visually

### Alert Timeline Tab
- View all alerts chronologically
- See alert statistics
- Understand alert frequency by parameter

## 💡 Best Practices

1. **Train Model Regularly**: Retrain when you have new data patterns
2. **Adjust Thresholds**: Set thresholds based on your specific water source
3. **Monitor Health Score**: Keep an eye on overall health trends
4. **Review Correlations**: Understand parameter relationships
5. **Check Alert Timeline**: Review alerts to identify patterns

## 🔧 Technical Details

### ML Model
- **Algorithm**: Isolation Forest (scikit-learn)
- **Contamination**: 10% (expects 10% anomalies)
- **Features**: pH, Temperature, TDS, Turbidity
- **Scaling**: StandardScaler for feature normalization

### Alert Logic
1. Check threshold-based alerts first
2. Run ML anomaly detection
3. Calculate health score
4. Determine overall status
5. Display alerts and visualizations

### Performance
- **Training Time**: < 1 second for 100 readings
- **Prediction Time**: < 10ms per reading
- **Memory Usage**: Minimal (model size ~50KB)
