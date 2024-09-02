import json
import os
from kafka import KafkaConsumer, KafkaProducer
import logging
from statistics import mean, stdev
import numpy as np
from scipy.optimize import curve_fit
from kafka.errors import KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatteryAnalyzer:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.data_window = []
        self.initial_capacity = None  # This needs to be set

    def update_window(self, data):
        self.data_window.append(data)
        if len(self.data_window) > self.window_size:
            self.data_window.pop(0)

    def calculate_statistics(self):
        if not self.data_window:
            return None

        voltage_values = [d['Voltage_measured'] for d in self.data_window]
        current_values = [d['Current_measured'] for d in self.data_window]
        temperature_values = [d['Temperature_measured'] for d in self.data_window]

        return {
            'voltage_avg': mean(voltage_values),
            'voltage_std': stdev(voltage_values) if len(voltage_values) > 1 else 0,
            'current_avg': mean(current_values),
            'current_std': stdev(current_values) if len(current_values) > 1 else 0,
            'temperature_avg': mean(temperature_values),
            'temperature_std': stdev(temperature_values) if len(temperature_values) > 1 else 0,
        }

    def detect_anomalies(self, data, stats):
        anomalies = []
        if abs(data['Voltage_measured'] - stats['voltage_avg']) > 2 * stats['voltage_std']:
            anomalies.append('Voltage anomaly detected')
        if abs(data['Current_measured'] - stats['current_avg']) > 2 * stats['current_std']:
            anomalies.append('Current anomaly detected')
        if abs(data['Temperature_measured'] - stats['temperature_avg']) > 2 * stats['temperature_std']:
            anomalies.append('Temperature anomaly detected')
        return anomalies

    def capacity_fade_model(self, cycle, a, b, c):
        return a * np.exp(-b * cycle) + c

    def fit_capacity_fade_model(self, cycles, capacities):
        popt, _ = curve_fit(self.capacity_fade_model, cycles, capacities, p0=[1, 0.001, 0.8])
        return popt

    def predict_rul(self, current_cycle, current_capacity, threshold=0.8):
        cycles = np.array([0, current_cycle])
        capacities = np.array([1, current_capacity / self.initial_capacity])
        a, b, c = self.fit_capacity_fade_model(cycles, capacities)
        cycle_end = -np.log((threshold - c) / a) / b
        return max(0, cycle_end - current_cycle)

def main():
    try:
        consumer = KafkaConsumer(
            'battery-data',
            bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
            auto_offset_reset='earliest',
            group_id='battery-analyzer',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        producer = KafkaProducer(
            bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

        analyzer = BatteryAnalyzer()

        for message in consumer:
            data = message.value
            analyzer.update_window(data)
            stats = analyzer.calculate_statistics()

            if stats:
                anomalies = analyzer.detect_anomalies(data, stats)
                analysis_result = {
                    'battery_id': data['Battery'],
                    'timestamp': data['timestamp'],
                    'statistics': stats,
                    'anomalies': anomalies
                }
                producer.send('battery-analysis', analysis_result)
                logger.info(f"Analyzed data for battery {data['Battery']}")

    except KafkaError as e:
        logger.error(f"Kafka error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if consumer:
            consumer.close()
        if producer:
            producer.close()

if __name__ == "__main__":
    main()