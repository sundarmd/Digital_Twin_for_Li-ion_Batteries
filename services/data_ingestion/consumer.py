import json
import os
import time
from kafka import KafkaConsumer
from datetime import datetime
import logging
import psycopg2
from psycopg2.extras import Json
from kafka.errors import KafkaError
from Digital_Twin_for_Li-ion_Batteries.config import *

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def validate_battery_data(data):
    required_fields = [
        "Voltage_measured", "Current_measured", "Temperature_measured",
        "Current_charge", "Voltage_charge", "Time", "Capacity",
        "id_cycle", "type", "ambient_temperature", "time", "Battery"
    ]
    return all(field in data for field in required_fields)

def preprocess_data(data):
    numeric_fields = [
        "Voltage_measured", "Current_measured", "Temperature_measured",
        "Current_charge", "Voltage_charge", "Time", "Capacity",
        "id_cycle", "ambient_temperature", "time"
    ]
    for field in numeric_fields:
        data[field] = float(data[field])
    
    data['id_cycle'] = int(data['id_cycle'])
    data['time'] = int(data['time'])
    
    data['power_W'] = data['Voltage_measured'] * abs(data['Current_measured'])
    data['energy_Wh'] = data['power_W'] * (data['Time'] / 3600)
    
    data['timestamp'] = datetime.now().isoformat()
    
    return data

def health_check():
    try:
        # Check Kafka connection
        consumer = KafkaConsumer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
            group_id='health_check',
            consumer_timeout_ms=5000
        )
        consumer.close()

        # Check database connection
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()

        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

def main():
    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC_BATTERY_DATA,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=False
            )

            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()

            last_health_check = time.time()

            for message in consumer:
                try:
                    data = message.value
                    if not validate_battery_data(data):
                        logger.error(f"Invalid data received: {data}")
                        continue

                    processed_data = preprocess_data(data)

                    cur.execute("""
                        INSERT INTO battery_data (
                            battery_id, voltage_measured, current_measured, temperature_measured,
                            current_charge, voltage_charge, time, capacity, id_cycle, type,
                            ambient_temperature, year, power_W, energy_Wh, timestamp
                        ) VALUES (
                            %(Battery)s, %(Voltage_measured)s, %(Current_measured)s, %(Temperature_measured)s,
                            %(Current_charge)s, %(Voltage_charge)s, %(Time)s, %(Capacity)s, %(id_cycle)s, %(type)s,
                            %(ambient_temperature)s, %(time)s, %(power_W)s, %(energy_Wh)s, %(timestamp)s
                        )
                    """, processed_data)
                    conn.commit()
                    logger.info(f"Processed and stored data for battery {data['Battery']}")
                    consumer.commit()

                    # Perform health check at regular intervals
                    if time.time() - last_health_check > HEALTH_CHECK_INTERVAL:
                        if not health_check():
                            raise Exception("Health check failed")
                        last_health_check = time.time()

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    conn.rollback()

        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
            if consumer:
                consumer.close()

        logger.info("Restarting consumer after error...")
        time.sleep(10)  # Wait before attempting to reconnect

if __name__ == "__main__":
    main()