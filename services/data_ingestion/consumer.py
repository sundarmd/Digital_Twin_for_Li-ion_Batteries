from Digital_Twin_for_Li-ion_Batteries.config import *
import json
from kafka import KafkaConsumer
import psycopg2
import logging

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC_BATTERY_DATA,
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
            # Process and store the data
            # ...

            logger.info(f"Processed data for battery {data['Battery']}")
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()