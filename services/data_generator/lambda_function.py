import json
import random
import boto3
import os
from datetime import datetime, timedelta

def generate_battery_data():
    return {
        "timestamp": datetime.now().isoformat(),
        "voltage": np.random.uniform(3.6, 4.2),
        "current": np.random.uniform(0, 2),
        "temperature": np.random.uniform(20, 40),
        "state_of_charge": np.random.uniform(0, 100),
        "capacity": np.random.uniform(2000, 3000)  # Added capacity field
    }

def lambda_handler(event, context):
    client = boto3.client('kafka')
    
    data = generate_battery_data()
    
    response = client.produce(
        ClusterArn='your-cluster-arn',
        TopicName='battery_data',
        Messages=[
            {
                'Value': json.dumps(data).encode('utf-8')
            },
        ]
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data sent to Kafka successfully')
    }