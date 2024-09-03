import os
import configparser

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

# AWS
AWS_REGION = os.environ.get('AWS_REGION', config['AWS']['REGION'])

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