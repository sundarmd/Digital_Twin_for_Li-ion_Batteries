import time
import json
import random
from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# AWS IoT configuration
ENDPOINT = "your-iot-endpoint.iot.us-west-2.amazonaws.com"
CLIENT_ID = "battery_simulator"
PATH_TO_CERT = "path/to/certificate.pem.crt"
PATH_TO_KEY = "path/to/private.pem.key"
PATH_TO_ROOT = "path/to/root.pem"
TOPIC = "battery/data"

# Battery simulation parameters
INITIAL_CAPACITY = 1.85
CAPACITY_DECAY_RATE = 0.0001
CYCLE_TIME = 180  # seconds
MEASUREMENTS_PER_CYCLE = 6
MIN_TEMPERATURE = 38  # Align with ml.py temperature filter

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

def simulate_battery_data(cycle, measurement, cumulated_time):
    voltage_measured = random.uniform(3.2, 3.4)
    current_measured = random.uniform(-2.02, -2.00)
    temperature_measured = random.uniform(MIN_TEMPERATURE, MIN_TEMPERATURE + 3)
    current_charge = 1.9982
    voltage_charge = random.uniform(2.3, 2.5)
    time_elapsed = (cycle - 1) * CYCLE_TIME + (measurement * CYCLE_TIME / MEASUREMENTS_PER_CYCLE)
    capacity = INITIAL_CAPACITY - (CAPACITY_DECAY_RATE * cycle)
    ambient_temperature = 24
    timestamp = int(datetime.now().timestamp())

    return {
        "Voltage_measured": voltage_measured,
        "Current_measured": current_measured,
        "Temperature_measured": temperature_measured,
        "Current_charge": current_charge,
        "Voltage_charge": voltage_charge,
        "Time": time_elapsed,
        "Capacity": capacity,
        "id_cycle": cycle,
        "type": "discharge",
        "ambient_temperature": ambient_temperature,
        "time": timestamp,
        "Battery": "B0005",
        "Cumulated_T": cumulated_time
    }

def run_simulator(mqtt_client):
    cycle = 1
    cumulated_time = 0
    while True:
        cycle_data = []
        cycle_start_time = time.time()
        for measurement in range(MEASUREMENTS_PER_CYCLE):
            data = simulate_battery_data(cycle, measurement, cumulated_time)
            cycle_data.append(data)
            time.sleep(CYCLE_TIME / MEASUREMENTS_PER_CYCLE)
        
        # Aggregate cycle data
        max_voltage = max(d["Voltage_measured"] for d in cycle_data)
        max_temperature = max(d["Temperature_measured"] for d in cycle_data)
        cycle_time = time.time() - cycle_start_time
        cumulated_time += cycle_time

        aggregated_data = cycle_data[-1]  # Take the last measurement
        aggregated_data["Voltage_measured"] = max_voltage
        aggregated_data["Temperature_measured"] = max_temperature
        aggregated_data["Time"] = cycle_time
        aggregated_data["Cumulated_T"] = cumulated_time

        message = json.dumps(aggregated_data)
        mqtt_client.publish(TOPIC, message, 1)
        print(f"Published aggregated cycle data: {message}")
        
        cycle += 1

if __name__ == "__main__":
    mqtt_client = create_mqtt_client()
    mqtt_client.connect()
    print("MQTT client connected")
    try:
        run_simulator(mqtt_client)
    except KeyboardInterrupt:
        print("Simulator stopped")
    finally:
        mqtt_client.disconnect()
        print("MQTT client disconnected")