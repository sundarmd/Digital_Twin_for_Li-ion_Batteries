output "eks_cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "eks_cluster_name" {
  description = "Kubernetes Cluster Name"
  value       = module.eks.cluster_id
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.battery_db.endpoint
}

output "msk_bootstrap_brokers" {
  description = "MSK cluster bootstrap brokers"
  value       = aws_msk_cluster.battery_kafka.bootstrap_brokers
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.battery_data.id
}