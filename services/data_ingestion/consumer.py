import json
import os
from kafka import KafkaConsumer
from datetime import datetime
import logging
import psycopg2
from psycopg2.extras import Json

logging.basicConfig(level=logging.INFO)
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

def store_data(conn, data):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO battery_data (
                voltage, current, temperature, current_charge, voltage_charge,
                time, capacity, id_cycle, type, ambient_temperature, year,
                battery_id, power, energy, timestamp, raw_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['Voltage_measured'], data['Current_measured'], data['Temperature_measured'],
            data['Current_charge'], data['Voltage_charge'], data['Time'], data['Capacity'],
            data['id_cycle'], data['type'], data['ambient_temperature'], data['time'],
            data['Battery'], data['power_W'], data['energy_Wh'], data['timestamp'],
            Json(data)
        ))
    conn.commit()

def main():
    consumer = KafkaConsumer(
        'battery-data',
        bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='battery-data-consumer',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    conn = psycopg2.connect(os.environ['DATABASE_URL'])

    try:
        for message in consumer:
            data = message.value
            if validate_battery_data(data):
                processed_data = preprocess_data(data)
                store_data(conn, processed_data)
                logger.info(f"Processed and stored data for battery {processed_data['Battery']}")
            else:
                logger.warning(f"Invalid data received: {data}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()