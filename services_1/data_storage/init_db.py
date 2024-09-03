import psycopg2
import os

def init_db():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS battery_data (
            id SERIAL PRIMARY KEY,
            voltage REAL,
            current REAL,
            temperature REAL,
            current_charge REAL,
            voltage_charge REAL,
            time REAL,
            capacity REAL,
            id_cycle INTEGER,
            type TEXT,
            ambient_temperature REAL,
            year INTEGER,
            battery_id TEXT,
            power REAL,
            energy REAL,
            timestamp TIMESTAMP,
            raw_data JSONB
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()