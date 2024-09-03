import json
import os
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import Json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def store_data(conn, data):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO battery_data (
                voltage, current, temperature, current_charge, voltage_charge,
                time, capacity, id_cycle, type, ambient_temperature, year,
                battery_id, power, energy, timestamp, raw_data
            ) VALUES (
                %(Voltage_measured)s, %(Current_measured)s, %(Temperature_measured)s,
                %(Current_charge)s, %(Voltage_charge)s, %(Time)s, %(Capacity)s,
                %(id_cycle)s, %(type)s, %(ambient_temperature)s, %(time)s,
                %(Battery)s, %(power_W)s, %(energy_Wh)s, %(timestamp)s, %(raw_data)s
            )
        """, {**data, 'raw_data': Json(data)})
    conn.commit()

def main():
    consumer = KafkaConsumer(
        'battery-data',
        bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    conn = get_db_connection()

    for message in consumer:
        data = message.value
        try:
            store_data(conn, data)
            logger.info(f"Stored data for battery {data['Battery']}")
        except Exception as e:
            logger.error(f"Error storing data: {str(e)}")

if __name__ == "__main__":
    main()