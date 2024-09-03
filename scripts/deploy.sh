#!/bin/bash

# Set variables
AWS_ACCOUNT_ID="your-aws-account-id"
AWS_REGION="us-west-2"
ECR_REPO_NAME="battery-digital-twin"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push Docker images for each service
services=("api_gateway" "data_generator" "data_ingestion" "digital_twin_aggregator" "ml_pipeline" "real_time_analytics")

for service in "${services[@]}"
do
    # Build Docker image
    docker build -t $ECR_REPO_NAME:$service ./services/$service

    # Tag image for ECR
    docker tag $ECR_REPO_NAME:$service $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$service

    # Push image to ECR
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$service
done

echo "Deployment complete!"