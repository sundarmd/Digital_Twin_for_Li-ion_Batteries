module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "battery-digital-twin-cluster"
  cluster_version = "1.21"
  subnets         = ["subnet-abcde012", "subnet-bcde012a"]
  vpc_id          = "vpc-1234556abcdef"

  node_groups = {
    example = {
      desired_capacity = 2
      max_capacity     = 3
      min_capacity     = 1

      instance_type = "t3.medium"
    }
  }
}