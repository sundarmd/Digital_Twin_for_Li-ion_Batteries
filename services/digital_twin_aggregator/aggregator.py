import json
from kafka import KafkaConsumer, KafkaProducer
import psycopg2
import joblib
import os

class DigitalTwinAggregator:
    def __init__(self):
        self.model = joblib.load('battery_health_model.joblib')
        self.db_conn = psycopg2.connect(os.environ['DATABASE_URL'])

    def get_historical_data(self, battery_id):
        with self.db_conn.cursor() as cur:
            cur.execute("""
                SELECT voltage, current, temperature, capacity
                FROM battery_data
                WHERE battery_id = %s
                ORDER BY timestamp DESC
                LIMIT 100
            """, (battery_id,))
            return cur.fetchall()

    def predict_health(self, data):
        return self.model.predict([[data['voltage'], data['current'], data['temperature']]])[0]

    def aggregate_data(self, real_time_data, historical_data):
        latest_data = {
            'voltage': real_time_data['Voltage_measured'],
            'current': real_time_data['Current_measured'],
            'temperature': real_time_data['Temperature_measured'],
        }
        predicted_capacity = self.predict_health(latest_data)
        
        return {
            'battery_id': real_time_data['Battery'],
            'timestamp': real_time_data['timestamp'],
            'latest_data': latest_data,
            'predicted_capacity': predicted_capacity,
            'historical_data': historical_data
        }

def main():
    consumer = KafkaConsumer(
        'battery-data',
        bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
        auto_offset_reset='earliest',
        group_id='digital-twin-aggregator',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    producer = KafkaProducer(
        bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    aggregator = DigitalTwinAggregator()

    for message in consumer:
        real_time_data = message.value
        battery_id = real_time_data['Battery']
        historical_data = aggregator.get_historical_data(battery_id)
        aggregated_data = aggregator.aggregate_data(real_time_data, historical_data)
        
        producer.send('digital-twin-data', aggregated_data)

if __name__ == "__main__":
    main()