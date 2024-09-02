import psycopg2
import os
import sys
import logging
from Digital_Twin_for_Li-ion_Batteries.config import *

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Create battery_data table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS battery_data (
            id SERIAL PRIMARY KEY,
            battery_id VARCHAR(50),
            voltage_measured FLOAT,
            current_measured FLOAT,
            temperature_measured FLOAT,
            current_charge FLOAT,
            voltage_charge FLOAT,
            time FLOAT,
            capacity FLOAT,
            id_cycle INTEGER,
            type VARCHAR(20),
            ambient_temperature FLOAT,
            year INTEGER,
            power_W FLOAT,
            energy_Wh FLOAT,
            timestamp TIMESTAMP
        )
        """)
        
        # Create analysis_results table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id SERIAL PRIMARY KEY,
            battery_id VARCHAR(50),
            soh FLOAT,
            rul FLOAT,
            anomalies JSON,
            timestamp TIMESTAMP
        )
        """)
        
        # Create digital_twin table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS digital_twin (
            id SERIAL PRIMARY KEY,
            battery_id VARCHAR(50),
            latest_data JSON,
            predicted_capacity FLOAT,
            historical_data JSON,
            timestamp TIMESTAMP
        )
        """)
        
        conn.commit()
        logger.info("Database initialization completed successfully")
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()