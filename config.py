import os

# Database
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/battery_db')

# Kafka
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC_BATTERY_DATA = os.environ.get('KAFKA_TOPIC_BATTERY_DATA', 'battery-data')
KAFKA_TOPIC_ANALYSIS_RESULTS = os.environ.get('KAFKA_TOPIC_ANALYSIS_RESULTS', 'battery-analysis')
KAFKA_TOPIC_DIGITAL_TWIN = os.environ.get('KAFKA_TOPIC_DIGITAL_TWIN', 'digital-twin-data')

# AWS
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')
MSK_CLUSTER_ARN = os.environ.get('MSK_CLUSTER_ARN', 'your-msk-cluster-arn')

# API
API_HOST = os.environ.get('API_HOST', '0.0.0.0')
API_PORT = int(os.environ.get('API_PORT', 8000))

# Machine Learning
MODEL_PATH_LSTM = os.environ.get('MODEL_PATH_LSTM', 'battery_health_lstm_model.h5')
MODEL_PATH_RF = os.environ.get('MODEL_PATH_RF', 'battery_health_rf_model.joblib')

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Health Check
HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 60))  # seconds