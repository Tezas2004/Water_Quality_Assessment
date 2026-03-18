"""
Sensor Reader Module
Handles serial communication with water quality sensors
"""

import serial
import serial.tools.list_ports
import json
import re
from typing import Dict, Optional, List

class SensorReader:
    """Reads sensor data from serial port"""
    
    def __init__(self, port: str, baud_rate: int = 9600):
        """
        Initialize sensor reader
        
        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0' or 'COM3')
            baud_rate: Baud rate for serial communication
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection = None
        self.connect()
    
    def connect(self):
        """Establish serial connection"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            # Wait for connection to stabilize
            import time
            time.sleep(2)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {str(e)}")
    
    def read_sensors(self) -> Optional[Dict[str, float]]:
        """
        Read sensor data from serial port
        
        Returns:
            Dictionary with sensor readings or None if no data available
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            return None
        
        try:
            # Read line from serial port
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode('utf-8').strip()
                
                if line:
                    return self._parse_sensor_data(line)
            
            return None
            
        except Exception as e:
            print(f"Error reading sensors: {str(e)}")
            return None
    
    def _parse_sensor_data(self, data: str) -> Dict[str, float]:
        """
        Parse sensor data from string
        
        Supports multiple formats:
        1. JSON: {"pH": 7.2, "Temperature": 25.5, "TDS": 350, "Turbidity": 2.1}
        2. CSV-like: pH:7.2,Temperature:25.5,TDS:350,Turbidity:2.1
        3. Space-separated: pH:7.2 Temperature:25.5 TDS:350 Turbidity:2.1
        
        Args:
            data: Raw sensor data string
            
        Returns:
            Dictionary with parsed sensor values
        """
        sensor_data = {}
        
        # Try JSON format first
        try:
            json_data = json.loads(data)
            if isinstance(json_data, dict):
                return {k: float(v) for k, v in json_data.items()}
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Try CSV-like format: pH:7.2,Temperature:25.5
        try:
            # Split by comma or space
            parts = re.split(r'[, ]+', data)
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    try:
                        sensor_data[key] = float(value)
                    except ValueError:
                        continue
        except Exception:
            pass
        
        # Ensure we have default values for common parameters
        defaults = {
            'pH': 7.0,
            'Temperature': 20.0,
            'TDS': 0.0,
            'Turbidity': 0.0
        }
        
        # Merge with defaults (only add missing keys)
        for key, default_value in defaults.items():
            if key not in sensor_data:
                sensor_data[key] = default_value
        
        return sensor_data
    
    def close(self):
        """Close serial connection"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.serial_connection = None
    
    @staticmethod
    def list_ports() -> List[str]:
        """
        List all available serial ports
        
        Returns:
            List of available port names
        """
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        
        # If no ports found, return common port names for user to try
        if not port_list:
            import platform
            system = platform.system()
            if system == 'Darwin':  # macOS
                return ['/dev/tty.usbserial-*', '/dev/tty.usbmodem*', '/dev/cu.*']
            elif system == 'Linux':
                return ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyAMA0']
            elif system == 'Windows':
                return ['COM1', 'COM3', 'COM5', 'COM7']
        
        return port_list
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
