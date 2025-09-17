# CI/CD Pipeline Setup

This document outlines the Continuous Integration and Continuous Deployment (CI/CD) pipeline setup for the Notes application.

## Overview

The CI/CD pipeline uses GitHub Actions to build, test, and deploy the application to AWS infrastructure. The pipeline is configured to use AWS SSM Parameter Store for retrieving resource information, making it flexible and environment-aware.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  GitHub Actions │────▶│   AWS Services  │────▶│   Deployment    │
│   Workflows     │     │   (ECR, ECS)    │     │   Environment   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  IAM Permissions│     │ SSM Parameters  │     │ CloudFormation  │
│   & Secrets     │     │  & Secrets      │     │    Templates    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Workflow Files

- **Backend Deployment**: `.github/workflows/backend-deploy.yml`
- **Frontend Deployment**: `.github/workflows/frontend-deploy.yml` (future)

## IAM Permissions

The GitHub Actions workflow uses an IAM user with specific permissions to interact with AWS resources. These permissions are defined in the `github_cicd` Terraform module.

Required permissions include:
- Amazon ECR: Push and pull images
- Amazon ECS: Update services, task definitions
- AWS SSM: Read parameters
- AWS Secrets Manager: Read secrets
- AWS IAM: PassRole for task execution
- Amazon CloudFront: Create invalidations (for frontend)

## SSM Parameters

The workflow uses AWS SSM Parameter Store to retrieve information about deployed resources. This approach provides a single source of truth and enables updating resources without modifying workflows.

Key parameters used in workflows:
- `/notes/terraform/ecr/repository_url`
- `/notes/terraform/ecs/cluster_name`
- `/notes/terraform/ecs/service_name`
- `/notes/terraform/vpc/security_group_id`
- `/notes/terraform/vpc/subnet_ids`
- `/notes/terraform/vpc/private_subnet_ids`
- `/notes/terraform/ecs/execution_role_arn`
- `/notes/terraform/database/endpoint`

## Setting Up GitHub Secrets

The following secrets need to be configured in your GitHub repository:

1. `AWS_ACCESS_KEY_ID`: IAM user's access key ID
2. `AWS_SECRET_ACCESS_KEY`: IAM user's secret access key
3. `AWS_REGION`: AWS region (e.g., ap-south-1)
4. `DATABASE_URL` (optional): Database connection string (if not retrieved from SSM)

Use the provided script to get the IAM credentials:
```
./scripts/get_github_credentials.sh
```

## Workflow Execution

The backend workflow performs the following steps:
1. Checkout code
2. Configure AWS credentials
3. Retrieve resource information from SSM
4. Log in to Amazon ECR
5. Build and push Docker image
6. Update ECS task definition
7. Deploy to ECS

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [Amazon ECS Deployment](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-external.html)
