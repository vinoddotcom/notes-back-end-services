# SSM Parameters for CI/CD

This document explains how AWS SSM Parameter Store is used in the CI/CD pipeline for the Notes application.

## Overview

AWS Systems Manager Parameter Store (SSM) is used as a centralized store for configuration data in our infrastructure. The CI/CD pipeline retrieves resource information from SSM to deploy applications without hardcoding values in workflows.

## Parameter Structure

We use a hierarchical structure for our parameters:

```
/notes/                          # Root namespace
  └── terraform/                 # Terraform-managed parameters
      ├── ecr/                   # ECR-related parameters
      ├── ecs/                   # ECS-related parameters
      ├── vpc/                   # VPC-related parameters
      └── database/              # Database-related parameters
  └── notes/                     # Application-specific parameters
      └── prod/                  # Production environment
          ├── backend_ecr_repository_url
          ├── ecs_cluster_name
          ├── backend_service_name
          ├── task_execution_role_arn
          ├── task_role_arn
          ├── db_secret_arn
          └── private_subnet_ids
```

## Key Parameters Used in CI/CD

| Parameter Name | Description | Example Value |
|----------------|-------------|--------------|
| `/notes/notes/prod/backend_ecr_repository_url` | ECR repository URL for backend images | `123456789012.dkr.ecr.ap-south-1.amazonaws.com/notes-prod-backend` |
| `/notes/notes/prod/ecs_cluster_name` | Name of the ECS cluster | `notes-prod-cluster` |
| `/notes/notes/prod/backend_service_name` | Name of the backend ECS service | `notes-prod-backend-service` |
| `/notes/notes/prod/task_execution_role_arn` | ARN of the ECS task execution role | `arn:aws:iam::123456789012:role/notes-prod-task-execution-role` |
| `/notes/notes/prod/task_role_arn` | ARN of the ECS task role | `arn:aws:iam::123456789012:role/notes-prod-task-role` |
| `/notes/notes/prod/db_secret_arn` | ARN of the database credentials secret | `arn:aws:secretsmanager:ap-south-1:123456789012:secret:notes-prod-db-credentials` |
| `/notes/notes/prod/private_subnet_ids` | Comma-separated list of private subnet IDs | `subnet-abc123,subnet-def456` |

## How Parameters are Created

These parameters are created by the Terraform code in `ssm_module.tf`. The module creates two sets of parameters:
1. **Terraform State Parameters**: Information about the Terraform state itself
2. **Infrastructure Parameters**: Information about the infrastructure resources

## How Parameters are Used in CI/CD

In the GitHub Actions workflow, we retrieve these parameters using the AWS CLI:

```yaml
- name: Get SSM Parameters
  id: ssm
  run: |
    echo "Getting SSM parameters for deployment..."
    echo "ECR_REPOSITORY=$(aws ssm get-parameter --name ${SSM_PARAMETER_PATH}/backend_ecr_repository_url --query Parameter.Value --output text)" >> $GITHUB_ENV
    echo "ECS_CLUSTER=$(aws ssm get-parameter --name ${SSM_PARAMETER_PATH}/ecs_cluster_name --query Parameter.Value --output text)" >> $GITHUB_ENV
    echo "ECS_SERVICE=$(aws ssm get-parameter --name ${SSM_PARAMETER_PATH}/backend_service_name --query Parameter.Value --output text)" >> $GITHUB_ENV
    # ... more parameters ...
```

## Benefits of Using SSM

1. **Decoupling**: Separates infrastructure configuration from application code
2. **Centralization**: Single source of truth for resource information
3. **Security**: Sensitive information can be stored as secure strings
4. **Versioning**: Parameters maintain a version history
5. **Auditability**: Changes to parameters are tracked in CloudTrail
6. **Flexibility**: No need to update workflows when resource names or ARNs change

## Validating Parameters

To validate that all required SSM parameters are set up correctly for CI/CD, run:

```bash
./scripts/validate_ssm_params.sh
```

This script checks if all the required parameters exist in the SSM Parameter Store and reports any missing parameters.

## Troubleshooting

If CI/CD fails due to parameter issues, check:

1. The parameter exists in SSM Parameter Store
2. The IAM user has permission to access the parameter
3. The parameter is in the correct format
4. The parameter path is correct in the workflow

Common errors include:
- `ParameterNotFound`: The parameter doesn't exist
- `AccessDeniedException`: The IAM user doesn't have permission to access the parameter
