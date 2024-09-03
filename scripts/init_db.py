import psycopg2
from config import DATABASE_URL

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS battery_data (
            id SERIAL PRIMARY KEY,
            battery_id VARCHAR(50),
            voltage FLOAT,
            current FLOAT,
            temperature FLOAT,
            capacity FLOAT,
            timestamp TIMESTAMP
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()