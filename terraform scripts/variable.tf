# General
variable "project_name" {
  description = "Name of the project, used in resource naming"
  default     = "battery-digital-twin"
}

variable "region" {
  description = "AWS region to deploy resources"
  default     = "eu-north-1"
}

# VPC and Networking
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

# ECS
variable "ecs_task_cpu" {
  description = "CPU units for the ECS task"
  default     = "256"
}

variable "ecs_task_memory" {
  description = "Memory for the ECS task"
  default     = "512"
}

# RDS
variable "db_instance_class" {
  description = "Instance class for the RDS instance"
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for the RDS instance in GB"
  default     = 20
}

variable "db_engine_version" {
  description = "Engine version for the RDS instance"
  default     = "13.7"
}

variable "db_username" {
  description = "Username for the database"
  default     = "admin"
}

variable "db_password" {
  description = "Password for the database"
  type        = string
  sensitive   = true
}

# ElastiCache
variable "cache_node_type" {
  description = "Node type for the ElastiCache cluster"
  default     = "cache.t3.micro"
}

variable "cache_engine_version" {
  description = "Engine version for the ElastiCache cluster"
  default     = "6.x"
}

# Lambda
variable "lambda_runtime" {
  description = "Runtime for the Lambda function"
  default     = "python3.8"
}

# SageMaker
variable "sagemaker_notebook_instance_type" {
  description = "Instance type for the SageMaker notebook"
  default     = "ml.t2.medium"
}

# S3
variable "s3_force_destroy" {
  description = "Boolean to force destruction of S3 buckets"
  default     = false
}

# MSK (Kafka)
variable "kafka_version" {
  description = "Version of Kafka to use for MSK cluster"
  default     = "2.8.1"
}

variable "kafka_instance_type" {
  description = "Instance type for the MSK brokers"
  default     = "kafka.t3.small"
}

# Cognito
variable "cognito_password_min_length" {
  description = "Minimum length for Cognito user pool passwords"
  default     = 8
}

# KMS
variable "kms_deletion_window_in_days" {
  description = "Duration in days after which the KMS key is deleted after destruction of the resource"
  default     = 30
}

# CloudWatch
variable "log_retention_in_days" {
  description = "Number of days to retain CloudWatch logs"
  default     = 30
}

# Tags
variable "common_tags" {
  description = "Common tags to be applied to all resources"
  type        = map(string)
  default     = {
    Project     = "Battery Digital Twin"
    Environment = "Development"
  }
}

