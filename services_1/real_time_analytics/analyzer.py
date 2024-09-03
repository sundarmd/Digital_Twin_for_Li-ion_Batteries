import json
import os
from kafka import KafkaConsumer, KafkaProducer
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
from scipy.optimize import curve_fit

class BatteryAnalyzer:
    def __init__(self):
        self.lstm_model = load_model('battery_health_lstm_model.h5')
        self.rf_model = joblib.load('battery_health_rf_model.joblib')
        self.initial_timestamp = None
        self.initial_capacity = None
        self.time_steps = 10  # Match the time steps used in training

    def preprocess_data(self, data):
        df = pd.DataFrame(data, index=[0])
        if self.initial_timestamp is None:
            self.initial_timestamp = df['timestamp'].iloc[0]
            self.initial_capacity = df['capacity'].iloc[0]
        df['cumulated_time'] = (df['timestamp'] - self.initial_timestamp).dt.total_seconds()
        return df[['voltage', 'current', 'temperature', 'cumulated_time', 'capacity']]

    def predict_capacity(self, data):
        processed_data = self.preprocess_data(data)
        
        # Prepare data for LSTM
        lstm_input = np.array([processed_data[['voltage', 'current', 'temperature', 'cumulated_time']].values[-self.time_steps:]])
        lstm_prediction = self.lstm_model.predict(lstm_input)[0][0]
        
        rf_prediction = self.rf_model.predict(processed_data[['voltage', 'current', 'temperature', 'cumulated_time']])[0]
        
        return {
            'lstm_prediction': lstm_prediction,
            'rf_prediction': rf_prediction
        }

    def calculate_soh(self, current_capacity):
        return (current_capacity / self.initial_capacity) * 100

    def capacity_fade_model(self, cycle, a, b):
        return a * np.exp(-b * cycle) + (1 - a)

    def fit_capacity_fade_model(self, cycles, capacities):
        popt, _ = curve_fit(self.capacity_fade_model, cycles, capacities)
        return popt

    def predict_rul(self, current_cycle, current_capacity, threshold=0.8):
        a, b = self.fit_capacity_fade_model(np.array([0, current_cycle]), np.array([1, current_capacity / self.initial_capacity]))
        cycle_end = -np.log((threshold - 1 + a) / a) / b
        return max(0, cycle_end - current_cycle)

    def analyze_battery_health(self, data):
        processed_data = self.preprocess_data(data)
        predictions = self.predict_capacity(processed_data)
        current_capacity = processed_data['capacity'].iloc[-1]
        current_cycle = len(processed_data)

        soh = self.calculate_soh(current_capacity)
        rul = self.predict_rul(current_cycle, current_capacity)

        return {
            'predictions': predictions,
            'soh': soh,
            'rul': rul,
            'current_capacity': current_capacity,
            'current_cycle': current_cycle
        }

def calculate_rolling_average(data, window_size=10):
    return data.rolling(window=window_size).mean()

def detect_anomalies(data, threshold=3):
    mean = np.mean(data)
    std = np.std(data)
    return np.abs(data - mean) > threshold * std

def main():
    consumer = KafkaConsumer(
        'battery-data',
        bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    producer = KafkaProducer(
        bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    analyzer = BatteryAnalyzer()
    battery_data = pd.DataFrame(columns=['voltage', 'current', 'temperature', 'capacity', 'timestamp'])

    for message in consumer:
        data = message.value
        battery_data = battery_data.append({
            'voltage': data['Voltage_measured'],
            'current': data['Current_measured'],
            'temperature': data['Temperature_measured'],
            'capacity': data['Capacity'],
            'timestamp': data['timestamp']
        }, ignore_index=True)

        if len(battery_data) >= 10:
            rolling_avg = calculate_rolling_average(battery_data)
            anomalies = detect_anomalies(battery_data)
            health_analysis = analyzer.analyze_battery_health(battery_data)

            analysis_result = {
                'battery_id': data['Battery'],
                'rolling_avg': rolling_avg.iloc[-1].to_dict(),
                'anomalies': anomalies.iloc[-1].to_dict(),
                'health_analysis': health_analysis
            }

            producer.send('battery-analysis', analysis_result)

if __name__ == "__main__":
    main()