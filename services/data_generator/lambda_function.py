import json
import random
from kafka import KafkaProducer
import os
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class BatterySimulator:
    def __init__(self):
        self.voltage = 3.7  # Initial voltage
        self.current = 0.5  # Initial current
        self.temperature = 25  # Initial temperature
        self.capacity = 100  # Initial capacity

    def generate_data(self):
        self.voltage += random.uniform(-0.1, 0.1)
        self.current += random.uniform(-0.05, 0.05)
        self.temperature += random.uniform(-0.5, 0.5)
        self.capacity -= random.uniform(0, 0.1)

        return {
            "Battery": f"B{random.randint(1000, 9999)}",
            "Voltage_measured": round(self.voltage, 2),
            "Current_measured": round(self.current, 2),
            "Temperature_measured": round(self.temperature, 2),
            "Capacity": round(self.capacity, 2),
            "timestamp": datetime.now().isoformat()
        }

def lambda_handler(event, context):
    producer = KafkaProducer(
        bootstrap_servers=os.environ['KAFKA_BOOTSTRAP_SERVERS'].split(','),
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    simulator = BatterySimulator()
    for _ in range(10):  # Generate 10 data points per invocation
        battery_data = simulator.generate_data()
        producer.send('battery-data', battery_data)
    
    producer.flush()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Battery data generated and sent to Kafka')
    }