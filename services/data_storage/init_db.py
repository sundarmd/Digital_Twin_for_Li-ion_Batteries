import os
import psycopg2

def init_db():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS battery_data (
            id SERIAL PRIMARY KEY,
            voltage FLOAT,
            current FLOAT,
            temperature FLOAT,
            current_charge FLOAT,
            voltage_charge FLOAT,
            time FLOAT,
            capacity FLOAT,
            id_cycle INTEGER,
            type VARCHAR(50),
            ambient_temperature FLOAT,
            year INTEGER,
            battery_id VARCHAR(50),
            power FLOAT,
            energy FLOAT,
            timestamp TIMESTAMP,
            raw_data JSONB
        )
    """)

    # Add an index for faster queries
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_battery_id_timestamp ON battery_data (battery_id, timestamp)
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()