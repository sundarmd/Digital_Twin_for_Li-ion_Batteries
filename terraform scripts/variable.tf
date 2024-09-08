variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "The name of the project, used as a prefix for many resources"
  type        = string
  default     = "digitaltwinbattery"
}

variable "ec2_instance_type" {
  description = "The instance type for the EC2 data processor"
  type        = string
  default     = "m5.xlarge"
}

variable "ec2_ami_id" {
  description = "The AMI ID for the EC2 instance"
  type        = string
  default     = "ami-XXXXXXXXXXXXXXX"  # Replace with actual AMI ID
}

variable "redshift_node_type" {
  description = "The node type for the Redshift cluster"
  type        = string
  default     = "dc2.large"
}

variable "redshift_cluster_type" {
  description = "The cluster type for Redshift"
  type        = string
  default     = "single-node"
}

variable "redshift_database_name" {
  description = "The name of the initial database in Redshift"
  type        = string
  default     = "dev"
}

variable "redshift_master_username" {
  description = "The master username for Redshift"
  type        = string
  default     = "XXXXXXXXXXXX"  # Replace with actual username
}

variable "redshift_master_password" {
  description = "The master password for Redshift"
  type        = string
  default     = "XXXXXXXXXXXX"  # Replace with actual password
}

variable "sagemaker_instance_type" {
  description = "The instance type for the SageMaker notebook"
  type        = string
  default     = "ml.m5.xlarge"
}

variable "quicksight_edition" {
  description = "The edition of QuickSight to use"
  type        = string
  default     = "ENTERPRISE"
}

variable "quicksight_notification_email" {
  description = "The email address for QuickSight notifications"
  type        = string
  default     = "sundardas80XXXXXXX"  # Replace with actual email
}
