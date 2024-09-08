provider "aws" {
    region = "eu-north-1"  # Adjust to your preferred region
  }
  
  # VPC and Networking
  resource "aws_vpc" "main" {
    cidr_block           = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support   = true
    
    tags = {
      Name = "Battery Digital Twin VPC"
    }
  }
  
  resource "aws_internet_gateway" "main" {
    vpc_id = aws_vpc.main.id
  
    tags = {
      Name = "Digital Twin for Li-ion Batteries IGW"
    }
  }
  
  resource "aws_subnet" "public" {
    count                   = 2
    vpc_id                  = aws_vpc.main.id
    cidr_block              = "10.0.${count.index + 1}.0/24"
    availability_zone       = data.aws_availability_zones.available.names[count.index]
    map_public_ip_on_launch = true
  
    tags = {
      Name = "Digital Twin Public Subnet ${count.index + 1}"
    }
  }
  
  resource "aws_subnet" "private" {
    count             = 2
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.0.${count.index + 10}.0/24"
    availability_zone = data.aws_availability_zones.available.names[count.index]
  
    tags = {
      Name = "Digital Twin Private Subnet ${count.index + 1}"
    }
  }
  
  resource "aws_nat_gateway" "main" {
    allocation_id = aws_eip.nat.id
    subnet_id     = aws_subnet.public[0].id
  
    tags = {
      Name = "Digital Twin NAT Gateway"
    }
  }
  
  resource "aws_eip" "nat" {
    vpc = true
    tags = {
      Name = "Digital Twin NAT Gateway EIP"
    }
  }
  
  # Security Groups
  resource "aws_security_group" "iot_devices" {
    name        = "iot_devices"
    description = "Security group for IoT devices"
    vpc_id      = aws_vpc.main.id
  
    ingress {
      from_port   = 8883  # MQTT over TLS
      to_port     = 8883
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  
    egress {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  
    tags = {
      Name = "IoT Devices Security Group"
    }
  }
  
  # IoT Core
  resource "aws_iot_thing" "battery" {
    name = "li_ion_battery_001"
  }
  
  resource "aws_iot_policy" "battery_policy" {
    name = "battery_policy"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "iot:Connect",
            "iot:Publish",
            "iot:Subscribe",
            "iot:Receive"
          ]
          Resource = ["*"]
        }
      ]
    })
  }
  
  # DynamoDB
  resource "aws_dynamodb_table" "battery_data" {
    name           = "BatteryData"
    billing_mode   = "PAY_PER_REQUEST"
    hash_key       = "BatteryId"
    range_key      = "Timestamp"
  
    attribute {
      name = "BatteryId"
      type = "S"
    }
  
    attribute {
      name = "Timestamp"
      type = "N"
    }
  
    tags = {
      Name = "Battery Digital Twin Data"
    }
  }
  
  # MSK (Kafka)
  resource "aws_msk_cluster" "battery_data_stream" {
    cluster_name           = "battery-data-stream"
    kafka_version          = "2.8.1"
    number_of_broker_nodes = 3
  
    broker_node_group_info {
      instance_type   = "kafka.t3.small"
      client_subnets  = aws_subnet.private[*].id
      security_groups = [aws_security_group.msk.id]
    }
  
    encryption_info {
      encryption_at_rest_kms_key_arn = aws_kms_key.msk.arn
    }
  
    tags = {
      Name = "Battery Data Stream"
    }
  }
  
  # ECS
  resource "aws_ecs_cluster" "main" {
    name = "battery-digital-twin-cluster"
  
    setting {
      name  = "containerInsights"
      value = "enabled"
    }
  }
  
  resource "aws_ecs_task_definition" "data_ingestion" {
    family                   = "data-ingestion"
    network_mode             = "awsvpc"
    requires_compatibilities = ["FARGATE"]
    cpu                      = "256"
    memory                   = "512"
  
    container_definitions = jsonencode([
      {
        name  = "data-ingestion"
        image = "${aws_ecr_repository.data_ingestion.repository_url}:latest"
        portMappings = [
          {
            containerPort = 80
            hostPort      = 80
          }
        ]
      }
    ])
  }
  
  resource "aws_ecs_service" "data_ingestion" {
    name            = "data-ingestion"
    cluster         = aws_ecs_cluster.main.id
    task_definition = aws_ecs_task_definition.data_ingestion.arn
    launch_type     = "FARGATE"
    desired_count   = 1
  
    network_configuration {
      subnets         = aws_subnet.private[*].id
      security_groups = [aws_security_group.ecs_tasks.id]
    }
  }
  
  # Lambda
  resource "aws_lambda_function" "data_generator" {
    filename      = "lambda_function.zip"
    function_name = "battery-data-generator"
    role          = aws_iam_role.lambda_exec.arn
    handler       = "lambda_function.lambda_handler"
    runtime       = "python3.8"
  
    environment {
      variables = {
        IOT_ENDPOINT = aws_iot_endpoint.main.endpoint_address
      }
    }
  }
  
  # API Gateway
  resource "aws_api_gateway_rest_api" "battery_api" {
    name        = "battery-digital-twin-api"
    description = "API for Battery Digital Twin"
  }
  
  # SageMaker
  resource "aws_sagemaker_notebook_instance" "ml_notebook" {
    name          = "battery-ml-notebook"
    role_arn      = aws_iam_role.sagemaker_exec.arn
    instance_type = "ml.t2.medium"
  }
  
  # S3 Buckets
  resource "aws_s3_bucket" "data_lake" {
    bucket = "battery-digital-twin-data-lake"
    acl    = "private"
  
    versioning {
      enabled = true
    }
  
    server_side_encryption_configuration {
      rule {
        apply_server_side_encryption_by_default {
          sse_algorithm = "AES256"
        }
      }
    }
  }
  
  resource "aws_s3_bucket" "model_artifacts" {
    bucket = "battery-digital-twin-model-artifacts"
    acl    = "private"
  
    versioning {
      enabled = true
    }
  
    server_side_encryption_configuration {
      rule {
        apply_server_side_encryption_by_default {
          sse_algorithm = "AES256"
        }
      }
    }
  }
  
  # Cognito
  resource "aws_cognito_user_pool" "main" {
    name = "battery-digital-twin-users"
  
    password_policy {
      minimum_length    = 8
      require_lowercase = true
      require_numbers   = true
      require_symbols   = true
      require_uppercase = true
    }
  
    auto_verified_attributes = ["email"]
  }
  
  resource "aws_cognito_user_pool_client" "main" {
    name         = "battery-digital-twin-client"
    user_pool_id = aws_cognito_user_pool.main.id
  
    generate_secret = true
    explicit_auth_flows = [
      "ALLOW_USER_PASSWORD_AUTH",
      "ALLOW_REFRESH_TOKEN_AUTH"
    ]
  }
  
  # ElastiCache
  resource "aws_elasticache_cluster" "main" {
    cluster_id           = "battery-digital-twin-cache"
    engine               = "redis"
    node_type            = "cache.t3.micro"
    num_cache_nodes      = 1
    parameter_group_name = "default.redis6.x"
    port                 = 6379
    subnet_group_name    = aws_elasticache_subnet_group.main.name
    security_group_ids   = [aws_security_group.elasticache.id]
  }
  
  resource "aws_elasticache_subnet_group" "main" {
    name       = "battery-digital-twin-cache-subnet"
    subnet_ids = aws_subnet.private[*].id
  }
  
  # RDS
  resource "aws_db_instance" "main" {
    identifier           = "battery-digital-twin-db"
    engine               = "postgres"
    engine_version       = "13.7"
    instance_class       = "db.t3.micro"
    allocated_storage    = 20
    storage_type         = "gp2"
    username             = "admin"
    password             = var.db_password  # Use a variable for sensitive data
    db_subnet_group_name = aws_db_subnet_group.main.name
    vpc_security_group_ids = [aws_security_group.rds.id]
    skip_final_snapshot  = true
  }
  
  resource "aws_db_subnet_group" "main" {
    name       = "battery-digital-twin-db-subnet"
    subnet_ids = aws_subnet.private[*].id
  }
  
  # CloudWatch
  resource "aws_cloudwatch_log_group" "battery_logs" {
    name = "/aws/battery-digital-twin"
    retention_in_days = 30
  }
  
  # IAM Roles (simplified, expand as needed)
  resource "aws_iam_role" "lambda_exec" {
    name = "battery_lambda_role"
    assume_role_policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "lambda.amazonaws.com"
          }
        }
      ]
    })
  }
  
  resource "aws_iam_role" "sagemaker_exec" {
    name = "battery_sagemaker_role"
    assume_role_policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "sagemaker.amazonaws.com"
          }
        }
      ]
    })
  }
  
  # KMS for encryption
  resource "aws_kms_key" "battery_data" {
    description = "KMS key for battery data encryption"
    deletion_window_in_days = 30
  }
  
  # Outputs
  output "vpc_id" {
    value = aws_vpc.main.id
  }
  
  output "public_subnet_ids" {
    value = aws_subnet.public[*].id
  }
  
  output "private_subnet_ids" {
    value = aws_subnet.private[*].id
  }
  
  output "ecs_cluster_name" {
    value = aws_ecs_cluster.main.name
  }
  
  output "dynamodb_table_name" {
    value = aws_dynamodb_table.battery_data.name
  }
  
  output "s3_data_lake_bucket" {
    value = aws_s3_bucket.data_lake.id
  }
  
  output "cognito_user_pool_id" {
    value = aws_cognito_user_pool.main.id
  }
  
  output "rds_endpoint" {
    value = aws_db_instance.main.endpoint
  }

