import os
import configparser
from pathlib import Path

# Get the directory of the current file
current_dir = Path(__file__).resolve().parent

# Path to the config.ini file
config_path = current_dir / 'config.ini'

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read(config_path)

# Database
DATABASE_URL = os.environ.get('DATABASE_URL', config['Database']['DATABASE_URL'])

# Kafka
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', config['Kafka']['KAFKA_BOOTSTRAP_SERVERS'])
KAFKA_TOPIC_BATTERY_DATA = os.environ.get('KAFKA_TOPIC_BATTERY_DATA', config['Kafka']['KAFKA_TOPIC_BATTERY_DATA'])
KAFKA_TOPIC_ANALYSIS_RESULTS = os.environ.get('KAFKA_TOPIC_ANALYSIS_RESULTS', config['Kafka']['KAFKA_TOPIC_ANALYSIS_RESULTS'])
KAFKA_TOPIC_DIGITAL_TWIN = os.environ.get('KAFKA_TOPIC_DIGITAL_TWIN', config['Kafka']['KAFKA_TOPIC_DIGITAL_TWIN'])

# AWS
AWS_REGION = os.environ.get('AWS_REGION', config['AWS']['AWS_REGION'])
MSK_CLUSTER_ARN = os.environ.get('MSK_CLUSTER_ARN', config['AWS']['MSK_CLUSTER_ARN'])

# API
API_HOST = os.environ.get('API_HOST', config['API']['API_HOST'])
API_PORT = int(os.environ.get('API_PORT', config['API']['API_PORT']))

# Machine Learning
MODEL_PATH_LSTM = os.environ.get('MODEL_PATH_LSTM', config['MachineLearning']['MODEL_PATH_LSTM'])
MODEL_PATH_RF = os.environ.get('MODEL_PATH_RF', config['MachineLearning']['MODEL_PATH_RF'])

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', config['Logging']['LOG_LEVEL'])

# Health Check
HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', config['HealthCheck']['HEALTH_CHECK_INTERVAL']))

# Network
SUBNET_IDS = os.environ.get('SUBNET_IDS', config['Network']['SUBNET_IDS']).split(',')
VPC_ID = os.environ.get('VPC_ID', config['Network']['VPC_ID'])

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', config['Security']['SECRET_KEY'])