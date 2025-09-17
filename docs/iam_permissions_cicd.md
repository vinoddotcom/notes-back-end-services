# IAM Permissions for CI/CD

This document describes the IAM permissions required for the CI/CD pipeline to deploy the Notes application to AWS infrastructure.

## Overview

Our CI/CD pipelines use AWS SSM Parameter Store to access resource information, ECR for container images, ECS for container orchestration, and CloudFront for CDN management. The required IAM permissions cover all these services.

## Required Permissions

The following permissions are needed for the CI/CD pipelines:

### ECR (Elastic Container Registry)

```json
{
  "Action": [
    "ecr:GetAuthorizationToken",
    "ecr:BatchCheckLayerAvailability",
    "ecr:GetDownloadUrlForLayer",
    "ecr:BatchGetImage",
    "ecr:InitiateLayerUpload",
    "ecr:UploadLayerPart",
    "ecr:CompleteLayerUpload",
    "ecr:PutImage"
  ],
  "Effect": "Allow",
  "Resource": "*"
}
```

These permissions allow the CI/CD pipeline to:
- Authenticate with ECR
- Check if layers exist in the registry
- Upload new container images
- Tag images with versions

### ECS (Elastic Container Service)

```json
{
  "Action": [
    "ecs:DescribeServices",
    "ecs:DescribeTaskDefinition",
    "ecs:RegisterTaskDefinition",
    "ecs:UpdateService",
    "ecs:RunTask",
    "ecs:DescribeClusters",
    "ecs:ListTasks",
    "ecs:DescribeTasks"
  ],
  "Effect": "Allow",
  "Resource": "*"
}
```

These permissions allow the CI/CD pipeline to:
- Get information about ECS services and tasks
- Register new task definitions
- Update services with new task definitions
- Run one-off tasks (e.g., database migrations)

### IAM Role Passing

```json
{
  "Action": [
    "iam:PassRole"
  ],
  "Effect": "Allow",
  "Resource": [
    "arn:aws:iam::*:role/notes-prod-task-execution-role",
    "arn:aws:iam::*:role/notes-prod-task-role"
  ]
}
```

This permission allows the CI/CD pipeline to:
- Pass IAM roles to ECS tasks

### Secrets Manager

```json
{
  "Action": [
    "secretsmanager:GetSecretValue"
  ],
  "Effect": "Allow",
  "Resource": "arn:aws:secretsmanager:*:*:secret:notes-prod-*"
}
```

This permission allows the CI/CD pipeline to:
- Access secrets stored in AWS Secrets Manager (e.g., database credentials)

### CloudFront

```json
{
  "Action": [
    "cloudfront:CreateInvalidation",
    "cloudfront:GetDistribution"
  ],
  "Effect": "Allow",
  "Resource": "*"
}
```

These permissions allow the CI/CD pipeline to:
- Invalidate the CloudFront cache after deployments
- Get information about CloudFront distributions

### SSM Parameter Store

```json
{
  "Action": [
    "ssm:GetParameter",
    "ssm:GetParameters",
    "ssm:GetParametersByPath"
  ],
  "Effect": "Allow",
  "Resource": [
    "arn:aws:ssm:*:*:parameter/notes/notes/prod/*",
    "arn:aws:ssm:*:*:parameter/notes/terraform/*"
  ]
}
```

These permissions allow the CI/CD pipeline to:
- Retrieve infrastructure parameters from SSM Parameter Store
- Access resource identifiers and configuration values

## Setup in AWS

These permissions are set up using the Terraform code in the `github_cicd` module. The module creates:

1. An IAM user specifically for GitHub Actions
2. An IAM policy with the above permissions
3. Access keys for authenticating with AWS

## Using in GitHub Actions

To use these permissions in GitHub Actions, add the following secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID`: The access key ID for the GitHub Actions IAM user
- `AWS_SECRET_ACCESS_KEY`: The secret access key for the GitHub Actions IAM user

Then, in your workflow file, configure AWS credentials:

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v1
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ap-south-1
```

## Security Best Practices

1. **Least Privilege**: The permissions are scoped to only what's necessary
2. **Resource Constraints**: When possible, permissions are scoped to specific resources
3. **No Admin Access**: The IAM user does not have admin access
4. **Secrets Protection**: Access keys are stored securely as GitHub secrets
5. **Regular Rotation**: Rotate access keys regularly
