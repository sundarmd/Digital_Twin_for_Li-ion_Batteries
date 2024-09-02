import json
import random
import boto3
from datetime import datetime

class BatterySimulator:
    def __init__(self):
        self.voltage = 4.0
        self.current = -2.0
        self.temperature = 24.0
        self.current_charge = 2.0
        self.voltage_charge = 3.0
        self.time = 0
        self.capacity = 1.85
        self.id_cycle = 1
        self.type = "discharge"
        self.ambient_temperature = 24
        self.year = datetime.now().year
        self.battery_id = f"B{random.randint(1000, 9999)}"

    def generate_data(self):
        data = {
            "Voltage_measured": round(self.voltage + random.uniform(-0.05, 0.05), 4),
            "Current_measured": round(self.current + random.uniform(-0.05, 0.05), 4),
            "Temperature_measured": round(self.temperature + random.uniform(-0.5, 0.5), 2),
            "Current_charge": round(self.current_charge, 4),
            "Voltage_charge": round(self.voltage_charge, 3),
            "Time": round(self.time, 3),
            "Capacity": round(self.capacity, 4),
            "id_cycle": self.id_cycle,
            "type": self.type,
            "ambient_temperature": self.ambient_temperature,
            "time": self.year,
            "Battery": self.battery_id
        }
        
        # Simulate discharge
        self.voltage -= random.uniform(0.001, 0.003)
        self.current -= random.uniform(0.0005, 0.001)
        self.temperature += random.uniform(0.01, 0.03)
        self.capacity -= random.uniform(0.0001, 0.0003)
        self.time += random.uniform(15, 20)
        
        return data

def lambda_handler(event, context):
    msk_client = boto3.client('kafka')
    
    # Replace with your actual MSK cluster ARN and topic name
    cluster_arn = "your-msk-cluster-arn"
    topic_name = "battery-data"
    
    # Get the bootstrap brokers
    response = msk_client.get_bootstrap_brokers(ClusterArn=cluster_arn)
    bootstrap_brokers = response['BootstrapBrokerString']
    
    # Create a Kafka producer
    from kafka import KafkaProducer
    producer = KafkaProducer(bootstrap_servers=bootstrap_brokers,
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    
    # Generate and send battery data
    simulator = BatterySimulator()
    for _ in range(10):  # Generate 10 data points per invocation
        battery_data = simulator.generate_data()
        producer.send(topic_name, battery_data)
    
    producer.flush()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Battery data generated and sent to MSK')
    }