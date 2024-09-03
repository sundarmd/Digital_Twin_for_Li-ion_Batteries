import json
import random
import boto3
from datetime import datetime
from kafka import KafkaProducer
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class BatterySimulator:
    # ... (existing code remains the same)

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