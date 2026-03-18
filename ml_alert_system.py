"""
ML-based Alert System for Water Quality Monitoring
Uses anomaly detection and threshold-based alerts
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class WaterQualityAlertSystem:
    """ML-based alert system for water quality monitoring"""
    
    def __init__(self):
        """Initialize the alert system"""
        self.isolation_forest = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Default thresholds (can be customized)
        self.thresholds = {
            'pH': {'min': 6.5, 'max': 8.5, 'critical_min': 6.0, 'critical_max': 9.0},
            'Temperature': {'min': 15.0, 'max': 30.0, 'critical_min': 10.0, 'critical_max': 35.0},
            'TDS': {'min': 0, 'max': 500, 'critical_min': 0, 'critical_max': 1000},
            'Turbidity': {'min': 0, 'max': 5.0, 'critical_min': 0, 'critical_max': 10.0}
        }
        
        # Alert history
        self.alert_history = []
    
    def update_thresholds(self, thresholds: Dict):
        """Update alert thresholds"""
        self.thresholds.update(thresholds)
    
    def train_model(self, historical_data: pd.DataFrame):
        """
        Train the anomaly detection model on historical data
        
        Args:
            historical_data: DataFrame with columns ['pH', 'Temperature', 'TDS', 'Turbidity']
        """
        if len(historical_data) < 10:
            # Not enough data to train, use threshold-based only
            self.is_trained = False
            return
        
        try:
            # Prepare features
            features = historical_data[['pH', 'Temperature', 'TDS', 'Turbidity']].values
            
            # Remove any NaN values
            features = features[~np.isnan(features).any(axis=1)]
            
            if len(features) < 10:
                self.is_trained = False
                return
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train isolation forest
            self.isolation_forest.fit(features_scaled)
            self.is_trained = True
            
        except Exception as e:
            print(f"Error training model: {e}")
            self.is_trained = False
    
    def check_threshold_alerts(self, sensor_data: Dict[str, float]) -> List[Dict]:
        """
        Check if sensor values exceed thresholds
        
        Args:
            sensor_data: Dictionary with sensor values
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        timestamp = datetime.now()
        
        for param, value in sensor_data.items():
            if param not in self.thresholds:
                continue
            
            threshold = self.thresholds[param]
            
            # Check critical alerts
            if value < threshold['critical_min'] or value > threshold['critical_max']:
                severity = 'critical'
                message = f"{param} is CRITICAL: {value:.2f} (Normal: {threshold['min']:.2f}-{threshold['max']:.2f})"
            # Check warning alerts
            elif value < threshold['min'] or value > threshold['max']:
                severity = 'warning'
                message = f"{param} is OUT OF RANGE: {value:.2f} (Normal: {threshold['min']:.2f}-{threshold['max']:.2f})"
            else:
                continue
            
            alert = {
                'timestamp': timestamp,
                'parameter': param,
                'value': value,
                'severity': severity,
                'message': message,
                'threshold_min': threshold['min'],
                'threshold_max': threshold['max']
            }
            
            alerts.append(alert)
            self.alert_history.append(alert)
        
        return alerts
    
    def detect_anomaly(self, sensor_data: Dict[str, float]) -> Tuple[bool, float]:
        """
        Detect anomalies using ML model
        
        Args:
            sensor_data: Dictionary with sensor values
            
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if not self.is_trained:
            return False, 0.0
        
        try:
            # Prepare features
            features = np.array([[
                sensor_data.get('pH', 7.0),
                sensor_data.get('Temperature', 22.0),
                sensor_data.get('TDS', 300.0),
                sensor_data.get('Turbidity', 2.0)
            ]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict anomaly
            prediction = self.isolation_forest.predict(features_scaled)[0]
            anomaly_score = self.isolation_forest.score_samples(features_scaled)[0]
            
            # -1 means anomaly, 1 means normal
            is_anomaly = prediction == -1
            
            return is_anomaly, float(anomaly_score)
            
        except Exception as e:
            print(f"Error detecting anomaly: {e}")
            return False, 0.0
    
    def analyze_reading(self, sensor_data: Dict[str, float]) -> Dict:
        """
        Complete analysis of a sensor reading
        
        Args:
            sensor_data: Dictionary with sensor values
            
        Returns:
            Dictionary with analysis results
        """
        # Check threshold-based alerts
        threshold_alerts = self.check_threshold_alerts(sensor_data)
        
        # Detect ML-based anomalies
        is_anomaly, anomaly_score = self.detect_anomaly(sensor_data)
        
        # Calculate overall health score (0-100)
        health_score = self.calculate_health_score(sensor_data)
        
        # Determine overall status
        if threshold_alerts:
            # Check if any critical alerts
            has_critical = any(a['severity'] == 'critical' for a in threshold_alerts)
            overall_status = 'critical' if has_critical else 'warning'
        elif is_anomaly:
            overall_status = 'anomaly'
        elif health_score >= 80:
            overall_status = 'good'
        elif health_score >= 60:
            overall_status = 'fair'
        else:
            overall_status = 'poor'
        
        return {
            'timestamp': datetime.now(),
            'sensor_data': sensor_data,
            'threshold_alerts': threshold_alerts,
            'is_anomaly': is_anomaly,
            'anomaly_score': anomaly_score,
            'health_score': health_score,
            'overall_status': overall_status
        }
    
    def calculate_health_score(self, sensor_data: Dict[str, float]) -> float:
        """
        Calculate overall water quality health score (0-100)
        
        Args:
            sensor_data: Dictionary with sensor values
            
        Returns:
            Health score from 0-100
        """
        scores = []
        
        for param, value in sensor_data.items():
            if param not in self.thresholds:
                continue
            
            threshold = self.thresholds[param]
            min_val = threshold['min']
            max_val = threshold['max']
            critical_min = threshold['critical_min']
            critical_max = threshold['critical_max']
            
            # Calculate score for this parameter
            if value < critical_min or value > critical_max:
                # Critical range - score 0-20
                if value < critical_min:
                    score = max(0, 20 * (value / critical_min))
                else:
                    score = max(0, 20 * ((critical_max * 2 - value) / critical_max))
            elif value < min_val or value > max_val:
                # Warning range - score 20-60
                if value < min_val:
                    score = 20 + 40 * ((value - critical_min) / (min_val - critical_min))
                else:
                    score = 20 + 40 * ((critical_max - value) / (critical_max - max_val))
            else:
                # Normal range - score 60-100
                if value <= (min_val + max_val) / 2:
                    score = 60 + 40 * ((value - min_val) / ((max_val - min_val) / 2))
                else:
                    score = 60 + 40 * ((max_val - value) / ((max_val - min_val) / 2))
            
            scores.append(max(0, min(100, score)))
        
        # Return average score
        return sum(scores) / len(scores) if scores else 50.0
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get alerts from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [a for a in self.alert_history if a['timestamp'] >= cutoff]
    
    def get_alert_statistics(self) -> Dict:
        """Get statistics about alerts"""
        if not self.alert_history:
            return {
                'total_alerts': 0,
                'critical_alerts': 0,
                'warning_alerts': 0,
                'alerts_by_parameter': {}
            }
        
        recent_alerts = self.get_recent_alerts(24)
        
        critical_count = sum(1 for a in recent_alerts if a['severity'] == 'critical')
        warning_count = sum(1 for a in recent_alerts if a['severity'] == 'warning')
        
        alerts_by_param = {}
        for alert in recent_alerts:
            param = alert['parameter']
            alerts_by_param[param] = alerts_by_param.get(param, 0) + 1
        
        return {
            'total_alerts': len(recent_alerts),
            'critical_alerts': critical_count,
            'warning_alerts': warning_count,
            'alerts_by_parameter': alerts_by_param
        }
