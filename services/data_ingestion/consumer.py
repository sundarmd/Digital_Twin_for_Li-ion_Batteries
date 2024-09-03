from kafka import KafkaConsumer
import json
import psycopg2
import logging
from config import KAFKA_BOOTSTRAP_SERVERS, DATABASE_URL, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def main():
    consumer = KafkaConsumer(
        'battery-data',
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
        auto_offset_reset='earliest',
        group_id='battery-data-consumer',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for message in consumer:
        data = message.value
        try:
            cur.execute("""
                INSERT INTO battery_data 
                (battery_id, voltage, current, temperature, capacity, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data['Battery'],
                data['Voltage_measured'],
                data['Current_measured'],
                data['Temperature_measured'],
                data['Capacity'],
                data['timestamp']
            ))
            conn.commit()
            logger.info(f"Processed data for battery {data['Battery']}")
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()