provider "aws" {
  region = "eu-north-1"
}

# IoT Core
resource "aws_iot_thing" "battery_twin" {
  name = "batterydigitaltwin"
}

resource "aws_iot_policy" "battery_twin_policy" {
  name = "batterydigitaltwin_policy"
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

# EC2 Instance
resource "aws_instance" "data_processor" {
  ami           = "ami-XXXXXXXXXXXXXXX"  # Redacted AMI ID
  instance_type = "m5.xlarge"
  tags = {
    Name = "batterydigitaltwin_processor"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "data_bucket" {
  bucket = "digitaltwinbattery"
}

# Redshift Cluster
resource "aws_redshift_cluster" "battery_data_warehouse" {
  cluster_identifier = "digitaltwinbattery"
  database_name      = "dev"
  master_username    = "XXXXXXXXXXXX"  # Redacted username
  master_password    = "XXXXXXXXXXXX"  # Redacted password
  node_type          = "dc2.large"
  cluster_type       = "single-node"
}

# SageMaker Notebook Instance
resource "aws_sagemaker_notebook_instance" "battery_ml" {
  name          = "digitaltwinbattery"
  role_arn      = aws_iam_role.sagemaker_role.arn
  instance_type = "ml.m5.xlarge"
}

resource "aws_iam_role" "sagemaker_role" {
  name = "batterydigitaltwin_sagemaker_role"
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

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "battery_logs" {
  name = "/aws/batterydigitaltwin"
}

# QuickSight
resource "aws_quicksight_account_subscription" "quicksight" {
  account_name        = "digitaltwinbattery"
  authentication_method = "IAM_AND_QUICKSIGHT"
  edition             = "ENTERPRISE"
  notification_email  = "sundardas80XXXXXXX"  # Redacted email domain
}

# IAM roles and policies
resource "aws_iam_role" "batterydigitaltwin_role" {
  name = "digitaltwinbattery"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# VPC and Security Groups
resource "aws_default_vpc" "default" {}

resource "aws_security_group" "allow_internal" {
  name        = "allow_internal"
  description = "Allow internal traffic"
  vpc_id      = aws_default_vpc.default.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [aws_default_vpc.default.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
