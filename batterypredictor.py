import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import torch
import numpy as np
import pandas as pd

# AWS IoT configuration
ENDPOINT = "a14bm3z8qkqt69-ats.iot.eu-north-1.amazonaws.com"
CLIENT_ID = "batterydatasimulator"
PATH_TO_CERT = "bdd71e13313d037b336a63e4221b9ed6d563e4914cc7236e22030499454814b3-certificate.pem.crt"
PATH_TO_KEY = "bdd71e13313d037b336a63e4221b9ed6d563e4914cc7236e22030499454814b3-private.pem.key"
PATH_TO_ROOT = "AmazonRootCA1.pem"
TOPIC = "battery/data"



# Load your trained model
model = torch.load('model.pth')
model.eval()

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

def preprocess_data(data, sequence_length=10):
    features = ['Voltage_measured', 'Current_measured', 'Temperature_measured', 'Current_charge', 'Voltage_charge']
    df = pd.DataFrame([data])
    input_data = df[features].values
    
    # Pad or truncate to ensure we have exactly 10 time steps
    if len(input_data) < sequence_length:
        input_data = np.pad(input_data, ((sequence_length - len(input_data), 0), (0, 0)), mode='edge')
    else:
        input_data = input_data[-sequence_length:]
    
    return torch.FloatTensor(input_data).unsqueeze(0)  # Add batch dimension

def predict(model, input_data):
    with torch.no_grad():
        output = model(input_data)
    return output.numpy()

def message_callback(client, userdata, message):
    payload = json.loads(message.payload.decode('utf-8'))
    print(f"Received message: {payload}")
    
    processed_input = preprocess_data(payload)
    prediction = predict(model, processed_input)
    print(f"Prediction: {prediction}")

if __name__ == "__main__":
    mqtt_client = create_mqtt_client()
    print("Connecting to AWS IoT Core...")
    mqtt_client.connect()
    print("Connected!")

    mqtt_client.subscribe(TOPIC, 1, message_callback)
    print(f"Subscribed to topic: {TOPIC}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        mqtt_client.disconnect()
        print("Disconnected!")