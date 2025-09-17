# CI/CD and SSM Parameter Integration

This document provides a detailed explanation of how the CI/CD pipeline integrates with AWS SSM Parameter Store for the Notes application deployment.

## Architecture Overview

Our CI/CD architecture uses AWS resources for deployment, with configuration information stored in SSM Parameter Store:

```
                                ┌──────────────────┐
                                │                  │
                                │ GitHub Actions   │
                                │                  │
                                └────────┬─────────┘
                                         │
                                         │ (1) Retrieve SSM Parameters
                                         ▼
┌───────────────────┐          ┌──────────────────┐           ┌──────────────────┐
│                   │          │                  │           │                  │
│ Terraform Creates ├─────────►│ SSM Parameter    │◄──────────┤ Application      │
│ Infrastructure    │          │ Store            │           │ Configuration    │
│                   │          │                  │           │                  │
└───────────────────┘          └────────┬─────────┘           └──────────────────┘
                                        │
                                        │ (2) Get Resource Info
                                        ▼
┌───────────────────┐          ┌──────────────────┐           ┌──────────────────┐
│                   │          │                  │           │                  │
│ Docker Image      ├─────────►│ ECR              │◄──────────┤ ECS Task         │
│ Build & Push      │          │ Repository       │           │ Definition       │
│                   │          │                  │           │                  │
└───────────────────┘          └────────┬─────────┘           └──────────────────┘
                                        │
                                        │ (3) Deploy
                                        ▼
                                ┌──────────────────┐
                                │                  │
                                │ ECS Service      │
                                │                  │
                                └──────────────────┘
```

## SSM Parameter Flow

1. **Infrastructure Creation**: Terraform creates AWS resources and stores their identifiers in SSM Parameter Store.
2. **CI/CD Pipeline**: GitHub Actions workflow retrieves parameters from SSM when deploying.
3. **Resource Access**: CI/CD pipeline uses the parameters to access AWS resources.

## CI/CD Pipeline Steps

### 1. Retrieve Parameters

The GitHub Actions workflow retrieves parameters from SSM:

```yaml
- name: Get SSM Parameters
  id: ssm
  run: |
    echo "ECR_REPOSITORY=$(aws ssm get-parameter --name ${SSM_PARAMETER_PATH}/backend_ecr_repository_url --query Parameter.Value --output text)" >> $GITHUB_ENV
    echo "ECS_CLUSTER=$(aws ssm get-parameter --name ${SSM_PARAMETER_PATH}/ecs_cluster_name --query Parameter.Value --output text)" >> $GITHUB_ENV
    # ...more parameters...
```

### 2. Docker Image Build and Push

Using the ECR repository URL from SSM:

```yaml
- name: Build, tag, and push image to Amazon ECR
  id: build-image
  uses: docker/build-push-action@v4
  with:
    context: .
    push: true
    tags: |
      ${{ env.ECR_REPOSITORY }}:${{ github.sha }}
      ${{ env.ECR_REPOSITORY }}:latest
```

### 3. Update Task Definition

Using the task execution role ARN from SSM:

```yaml
- name: Update task definition with new image
  id: task-def
  uses: aws-actions/amazon-ecs-render-task-definition@v1
  with:
    task-definition: task-definition.json
    container-name: ${{ env.CONTAINER_NAME }}
    image: ${{ env.ECR_REPOSITORY }}:${{ github.sha }}
```

### 4. Deploy to ECS

Using the ECS cluster and service names from SSM:

```yaml
- name: Deploy to Amazon ECS
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: ${{ steps.task-def.outputs.task-definition }}
    service: ${{ env.ECS_SERVICE }}
    cluster: ${{ env.ECS_CLUSTER }}
    wait-for-service-stability: true
```

### 5. Run Database Migrations

Using the private subnet IDs from SSM:

```yaml
- name: Run database migrations
  run: |
    # Convert comma-separated subnet IDs to proper format
    SUBNET_LIST=$(echo $PRIVATE_SUBNET_IDS | sed 's/,/","/g')
    
    aws ecs run-task \
      --cluster ${{ env.ECS_CLUSTER }} \
      --task-definition ${{ steps.task-def.outputs.task-definition }} \
      --launch-type FARGATE \
      --network-configuration "awsvpcConfiguration={subnets=[\"$SUBNET_LIST\"],securityGroups=[\"$SECURITY_GROUP_ID\"],assignPublicIp=DISABLED}" \
      --overrides '{"containerOverrides": [{"name":"backend","command": ["alembic", "upgrade", "head"]}]}'
```

## Benefits of this Approach

1. **Infrastructure as Code**: All resource configurations are defined in Terraform.
2. **Consistent Naming**: Resources have consistent naming conventions.
3. **Simplified Updates**: Update infrastructure without modifying workflows.
4. **Environment Separation**: Clear separation between environments.
5. **Reduced Errors**: No manual copying of resource identifiers.
6. **Centralized Configuration**: Single source of truth for resource information.

## Handling Changes

When infrastructure changes:

1. Update Terraform code
2. Apply changes with `terraform apply`
3. Parameters in SSM are automatically updated
4. CI/CD pipeline uses new parameter values on next run

No changes needed to the GitHub Actions workflow as it always fetches the latest parameter values.

## Testing and Validation

To ensure your CI/CD pipeline can access the required SSM parameters:

```bash
# Validate SSM parameters
./scripts/validate_ssm_params.sh

# Get GitHub credentials for CI/CD
./scripts/get_github_credentials.sh

# Set up GitHub repository with required secrets
./scripts/setup_github_cicd.sh
```

## Troubleshooting

If the CI/CD pipeline fails to retrieve SSM parameters:

1. Check IAM permissions
2. Verify parameter paths
3. Ensure the AWS region is configured correctly
4. Look for parameter naming inconsistencies

Common error patterns:
- `Parameter /notes/notes/prod/X not found`: The parameter doesn't exist
- `AccessDenied`: IAM permissions issue
- `InvalidParameter`: Incorrectly formatted parameter name

## Conclusion

The integration of CI/CD with SSM Parameter Store provides a robust, secure, and flexible deployment pipeline. This approach separates infrastructure configuration from application deployment logic, making the system more maintainable and less prone to errors.
