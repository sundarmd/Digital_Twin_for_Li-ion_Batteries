provider "aws" {
  region = "us-west-2"
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "battery-digital-twin-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "battery-digital-twin-cluster"
  cluster_version = "1.21"
  subnets         = module.vpc.private_subnets
  vpc_id          = module.vpc.vpc_id

  node_groups = {
    example = {
      desired_capacity = 2
      max_capacity     = 3
      min_capacity     = 1

      instance_type = "t3.medium"
    }
  }
}

resource "aws_db_instance" "battery_db" {
  identifier           = "battery-digital-twin-db"
  engine               = "postgres"
  engine_version       = "13.4"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_type         = "gp2"
  username             = "admin"
  password             = "your-secure-password"
  db_name              = "battery_data"
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  subnet_id            = module.vpc.private_subnets[0]
  skip_final_snapshot  = true
}

resource "aws_security_group" "rds_sg" {
  name        = "battery-digital-twin-rds-sg"
  description = "Security group for RDS instance"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }
}

resource "aws_msk_cluster" "battery_kafka" {
  cluster_name           = "battery-digital-twin-kafka"
  kafka_version          = "2.8.0"
  number_of_broker_nodes = 3

  broker_node_group_info {
    instance_type   = "kafka.t3.small"
    client_subnets  = module.vpc.private_subnets
    security_groups = [aws_security_group.kafka_sg.id]
  }
}

resource "aws_security_group" "kafka_sg" {
  name        = "battery-digital-twin-kafka-sg"
  description = "Security group for MSK cluster"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }
}

resource "aws_s3_bucket" "battery_data" {
  bucket = "battery-digital-twin-data"
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