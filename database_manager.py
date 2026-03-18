"""
Database Manager Module
Handles storage and retrieval of sensor readings
Supports SQLite (default) and PostgreSQL/MySQL
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

class DatabaseManager:
    """Manages database operations for sensor readings"""
    
    def __init__(self, db_type: str = 'sqlite', db_path: str = 'water_quality.db', 
                 host: str = None, port: int = None, database: str = None, 
                 user: str = None, password: str = None):
        """
        Initialize database manager
        
        Args:
            db_type: 'sqlite', 'postgresql', or 'mysql'
            db_path: Path to SQLite database file (for SQLite only)
            host: Database host (for PostgreSQL/MySQL)
            port: Database port (for PostgreSQL/MySQL)
            database: Database name (for PostgreSQL/MySQL)
            user: Database user (for PostgreSQL/MySQL)
            password: Database password (for PostgreSQL/MySQL)
        """
        self.db_type = db_type.lower()
        self.db_path = db_path
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection"""
        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            elif self.db_type == 'postgresql':
                try:
                    import psycopg2
                    self.connection = psycopg2.connect(
                        host=self.host,
                        port=self.port,
                        database=self.database,
                        user=self.user,
                        password=self.password
                    )
                except ImportError:
                    raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
            elif self.db_type == 'mysql':
                try:
                    import pymysql
                    self.connection = pymysql.connect(
                        host=self.host,
                        port=self.port,
                        database=self.database,
                        user=self.user,
                        password=self.password
                    )
                except ImportError:
                    raise ImportError("pymysql not installed. Install with: pip install pymysql")
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    def _create_tables(self):
        """Create tables if they don't exist"""
        cursor = self.connection.cursor()
        
        if self.db_type == 'sqlite':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    pH REAL,
                    temperature REAL,
                    tds REAL,
                    turbidity REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on timestamp for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_readings(timestamp)
            """)
            
        elif self.db_type == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    pH REAL,
                    temperature REAL,
                    tds REAL,
                    turbidity REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_readings(timestamp)
            """)
            
        elif self.db_type == 'mysql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    pH FLOAT,
                    temperature FLOAT,
                    tds FLOAT,
                    turbidity FLOAT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_timestamp (timestamp)
                )
            """)
        
        self.connection.commit()
    
    def insert_reading(self, sensor_data: Dict[str, float], timestamp: Optional[datetime] = None) -> int:
        """
        Insert a sensor reading into the database
        
        Args:
            sensor_data: Dictionary with sensor values (pH, Temperature, TDS, Turbidity)
            timestamp: Timestamp for the reading (defaults to current time)
            
        Returns:
            ID of the inserted record
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Normalize key names (handle both 'Temperature' and 'temperature')
        ph = sensor_data.get('pH') or sensor_data.get('ph')
        temperature = sensor_data.get('Temperature') or sensor_data.get('temperature')
        tds = sensor_data.get('TDS') or sensor_data.get('tds')
        turbidity = sensor_data.get('Turbidity') or sensor_data.get('turbidity')
        
        cursor = self.connection.cursor()
        
        if self.db_type == 'sqlite':
            cursor.execute("""
                INSERT INTO sensor_readings (timestamp, pH, temperature, tds, turbidity)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, ph, temperature, tds, turbidity))
        else:
            cursor.execute("""
                INSERT INTO sensor_readings (timestamp, pH, temperature, tds, turbidity)
                VALUES (%s, %s, %s, %s, %s)
            """, (timestamp, ph, temperature, tds, turbidity))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_latest_readings(self, limit: int = 100) -> pd.DataFrame:
        """
        Get the latest sensor readings
        
        Args:
            limit: Maximum number of readings to return
            
        Returns:
            DataFrame with sensor readings
        """
        query = f"""
            SELECT id, timestamp, pH, temperature, tds, turbidity, created_at
            FROM sensor_readings
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        
        df = pd.read_sql_query(query, self.connection)
        
        # Rename columns for consistency
        df = df.rename(columns={
            'temperature': 'Temperature',
            'tds': 'TDS',
            'turbidity': 'Turbidity'
        })
        
        # Convert timestamp to datetime if it's a string
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df.sort_values('timestamp')
    
    def get_readings_by_date_range(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Get readings within a date range
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            
        Returns:
            DataFrame with sensor readings
        """
        if self.db_type == 'sqlite':
            query = """
                SELECT id, timestamp, pH, temperature, tds, turbidity, created_at
                FROM sensor_readings
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """
            params = (start_date, end_date)
        else:
            query = """
                SELECT id, timestamp, pH, temperature, tds, turbidity, created_at
                FROM sensor_readings
                WHERE timestamp BETWEEN %s AND %s
                ORDER BY timestamp ASC
            """
            params = (start_date, end_date)
        
        df = pd.read_sql_query(query, self.connection, params=params)
        
        # Rename columns
        df = df.rename(columns={
            'temperature': 'Temperature',
            'tds': 'TDS',
            'turbidity': 'Turbidity'
        })
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about stored readings
        
        Returns:
            Dictionary with statistics
        """
        query = """
            SELECT 
                COUNT(*) as total_readings,
                MIN(timestamp) as first_reading,
                MAX(timestamp) as last_reading,
                AVG(pH) as avg_ph,
                AVG(temperature) as avg_temperature,
                AVG(tds) as avg_tds,
                AVG(turbidity) as avg_turbidity
            FROM sensor_readings
        """
        
        df = pd.read_sql_query(query, self.connection)
        
        if len(df) > 0:
            stats = df.iloc[0].to_dict()
            return {
                'total_readings': int(stats.get('total_readings', 0)),
                'first_reading': stats.get('first_reading'),
                'last_reading': stats.get('last_reading'),
                'avg_ph': round(stats.get('avg_ph', 0), 2),
                'avg_temperature': round(stats.get('avg_temperature', 0), 2),
                'avg_tds': round(stats.get('avg_tds', 0), 2),
                'avg_turbidity': round(stats.get('avg_turbidity', 0), 2)
            }
        else:
            return {
                'total_readings': 0,
                'first_reading': None,
                'last_reading': None,
                'avg_ph': 0,
                'avg_temperature': 0,
                'avg_tds': 0,
                'avg_turbidity': 0
            }
    
    def delete_old_readings(self, days_to_keep: int = 30):
        """
        Delete readings older than specified days
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        cursor = self.connection.cursor()
        
        if self.db_type == 'sqlite':
            cursor.execute("DELETE FROM sensor_readings WHERE timestamp < ?", (cutoff_date,))
        else:
            cursor.execute("DELETE FROM sensor_readings WHERE timestamp < %s", (cutoff_date,))
        
        deleted_count = cursor.rowcount
        self.connection.commit()
        return deleted_count
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
