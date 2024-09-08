# Digital Twin for Li-ion Batteries

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Setup Instructions](#setup-instructions)
5. [Features](#features)
6. [Future Enhancements](#future-enhancements)
7. [Project Cost](#project-cost)

## Project Overview

This project implements a digital twin for a Lithium-ion battery system using AWS cloud services. It simulates IoT device data, processes it in real-time, applies machine learning for predictive analytics, and visualizes the results. The system demonstrates proficiency in cloud architecture, real-time data processing, IoT systems, and machine learning integration.

Key features:

- Real-time IoT data simulation and ingestion
- Scalable data processing pipeline
- Machine learning integration for battery life prediction
- Interactive data visualizations
- Infrastructure as Code (IaC) using Terraform
- Monitoring and logging with Amazon CloudWatch

## Architecture

The project utilizes a serverless architecture on AWS, leveraging the following services:

- AWS IoT Core
- Terraform for IaC
- Amazon CloudWatch
- Amazon QuickSight
- Amazon SageMaker
- Amazon Redshift
- Amazon S3
- Amazon EC2

![image](https://github.com/user-attachments/assets/7005b734-ed69-4844-bf32-988b12dc5e84)
[click here to know how to create diagrams like this](https://github.com/sundarmd/Standalone-Visualizations/blob/main/Digital%20Twin%20for%20Li%20ion%20Batteries/Digital_Twin_Architecture.ipynb)

## Components

| Component | Purpose | Data Sources | Data Sent |
|-----------|---------|--------------|-----------|
| IoT Devices / Data Simulator | Simulate real-time battery data | Battery sensors/ scripts to simulate sensor data | Raw battery data (voltage, current, temperature, etc.) via MQTT |
| AWS IoT Core | Manage IoT device connections and data ingestion | IoT Devices/ scripts simulating IoT devices | Raw battery data to EC2 |
| EC2 - Data Processor | Process and transform raw data | AWS IoT Core | Processed data to Redshift |
| Amazon Redshift | Store processed data | EC2 | Processed data to QuickSight |
| Amazon SageMaker | Train and host ML models | S3 (training data) | ML model predictions to EC2 |
| Amazon QuickSight | Create and host data visualizations | Redshift | Visualizations to users |
| Terraform | Manage infrastructure as code | N/A | Resource definitions to AWS |
| Amazon CloudWatch | Monitor and log system performance | All AWS services | Alerts, logs to administrators |

## Setup Instructions

### Create a notebook on Amazon SageMaker

![image](https://github.com/user-attachments/assets/6e9ba5fb-4b19-40e4-ace5-939c65894a96)

### Open Jupyter Notebook

![image](https://github.com/user-attachments/assets/04285565-56e6-4d6c-b3ee-97aea6ac61f6)

### Train the model with historical data stored in S3 bucket

![image](https://github.com/user-attachments/assets/e4a9368c-f0f6-4874-b808-dac197a5c890)

### in case you want to use the model directly within the EC2 instance, you can move the model.tar.gz file to your EC2 instance from the corresponding output folder of the sagemaker instance and unzip it to obtain the model.pth file

![image](https://github.com/user-attachments/assets/a8d127f5-8dc5-4168-b14a-c49a2b72f94d)

![image](https://github.com/user-attachments/assets/fc57b2a2-d57b-44b2-a7cf-4b23966abe7c)

### Make sure your EC2 instance has all these files

![image](https://github.com/user-attachments/assets/ceffb2c0-63c0-43ab-9976-96c781cf254b)

### Subscribe to battery/data topic on MQTT test client

![image](https://github.com/user-attachments/assets/016310df-1932-4614-99dd-792605fff3c2)

### Run the batterydatasimulator.py and the batterydatapredictor.py simulatenously

![image](https://github.com/user-attachments/assets/3fae0879-58f3-4119-807b-6b0bfe825e0b)

### Verify the data being loaded in the Redshift table

![image](https://github.com/user-attachments/assets/6055edb1-25ec-4312-983f-a64c68bac2c9)

### Connect the Redshift table to Quicksight to generate Real Time Visualization for Analysis and Monitoring

![image](https://github.com/user-attachments/assets/c9851ced-04d3-4c4f-b71f-2e350a6dff4c)


## Features

### Data Processing and Machine Learning
- Real-time data ingestion from simulated IoT devices
- Machine learning model trained on SageMaker for battery life prediction
- Data processing on EC2 instance

### Visualizations

QuickSight dashboards provide the following visualizations:

1. Real-time battery voltage, current, and temperature
2. Battery capacity over time and cycle number
3. Predicted vs actual capacity degradation
4. Temperature distribution across battery cycles

### Deployment

The project uses Terraform for infrastructure as code:

1. Infrastructure defined in Terraform configuration files
2. Terraform provisions and manages AWS resources
3. Changes to infrastructure managed through version control

### Monitoring and Maintenance

- CloudWatch is used for monitoring all AWS services
- CloudWatch Alarms are set up for critical metrics (e.g., battery temperature exceeding thresholds)
- CloudWatch Logs collect logs from all services for troubleshooting

### Future Enhancements

1. Implement anomaly detection using Amazon SageMaker
2. Add support for multiple battery types
3. Implement a web-based dashboard for real-time monitoring
4. Integrate with a physical battery testing setup for real-world data
5. Implement containerization using Docker and container orchestration with Kubernetes
6. Develop a CI/CD pipeline for automated testing and deployment
7. Explore cloud-agnostic solutions for portability across different cloud providers
