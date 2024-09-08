import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import numpy as np
import pandas as pd
import boto3
import redshift_connector

# AWS IoT configuration
ENDPOINT = "a14bXXXXXXXXXXt69-ats.iot.eu-north-1.amazonaws.com"
CLIENT_ID = "batterydatasimulator"
PATH_TO_CERT = "bdd71e133XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXd030499454814b3-certificate.pem.crt"
PATH_TO_KEY = "bdd71e1331XXXXXXXXXXXXXXXXXXXXXXXXXXXXXcc7236e22030499454814b3-private.pem.key"
PATH_TO_ROOT = "AmazonRootCA1.pem"
TOPIC = "battery/data"

# Redshift configuration
REDSHIFT_HOST = "default-workgroup.5XXXXXXXXXX1.eu-north-1.redshift-serverless.amazonaws.com"
REDSHIFT_PORT = 5439
REDSHIFT_DB = "dev"

# SageMaker endpoint configuration
SAGEMAKER_ENDPOINT = "pytorch-training-2024-09-06-11-48-21-242"

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name='eu-north-1')

def create_mqtt_client():
    mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
    mqtt_client.configureEndpoint(ENDPOINT, 8883)
    mqtt_client.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
    mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
    mqtt_client.configureOfflinePublishQueueing(-1)
    mqtt_client.configureDrainingFrequency(2)
    mqtt_client.configureConnectDisconnectTimeout(10)
    mqtt_client.configureMQTTOperationTimeout(5)
    return mqtt_client

def connect_to_redshift():
    try:
        conn = redshift_connector.connect(
            host=REDSHIFT_HOST,
            database=REDSHIFT_DB,
            port=REDSHIFT_PORT,
            iam=True,
            cluster_identifier='default-workgroup',
            region='eu-north-1'
        )
        print("Connected to Redshift successfully!")
        return conn
    except Exception as e:
        print(f"Error connecting to Redshift: {e}")
        return None

def insert_into_redshift(conn, data, data_type):
    with conn.cursor() as cur:
        query = """
        INSERT INTO battery_data 
        (timestamp, voltage_measured, current_measured, temperature_measured, 
         current_charge, voltage_charge, capacity, data_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['timestamp'],
            data['Voltage_measured'],
            data['Current_measured'],
            data['Temperature_measured'],
            data['Current_charge'],
            data['Voltage_charge'],
            data.get('Capacity', None),  # Use None if Capacity is not present
            data_type
        )
        cur.execute(query, values)
    conn.commit()

def preprocess_data(data):
    features = ['Voltage_measured', 'Current_measured', 'Temperature_measured', 'Current_charge', 'Voltage_charge']
    df = pd.DataFrame([data])
    input_data = df[features].values
    return input_data.tolist()

def predict(input_data):
    try:
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Body=json.dumps(input_data)
        )
        result = json.loads(response['Body'].read().decode())
        return result
    except Exception as e:
        print(f"Prediction failed: {e}")
        return None

def message_callback(client, userdata, message):
    payload = json.loads(message.payload.decode('utf-8'))
    print(f"Received message: {payload}")
    
    # Insert simulated data
    insert_into_redshift(redshift_conn, payload, 'simulated')
    print("Inserted simulated data into Redshift")
    
    # Preprocess data for prediction
    processed_input = preprocess_data(payload)
    
    # Get prediction from SageMaker endpoint
    prediction = predict(processed_input)
    
    if prediction is not None:
        # Create predicted data dictionary
        predicted_data = payload.copy()
        predicted_data['Capacity'] = prediction[0]  
        
        # Insert predicted data
        insert_into_redshift(redshift_conn, predicted_data, 'predicted')
        print("Inserted predicted data into Redshift")
    else:
        print("Skipped inserting predicted data due to prediction failure")

if __name__ == "__main__":
    mqtt_client = create_mqtt_client()
    print("Connecting to AWS IoT Core...")
    mqtt_client.connect()
    print("Connected!")

    redshift_conn = connect_to_redshift()
    if redshift_conn is None:
        print("Failed to connect to Redshift. Exiting.")
        exit(1)

    mqtt_client.subscribe(TOPIC, 1, message_callback)
    print(f"Subscribed to topic: {TOPIC}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        mqtt_client.disconnect()
        redshift_conn.close()
        print("Disconnected!")
