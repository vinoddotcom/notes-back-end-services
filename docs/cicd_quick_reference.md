# CI/CD Quick Reference Guide

This guide provides quick reference information for the CI/CD pipeline setup for the Notes application.

## Important Paths

| Resource | Path |
|----------|------|
| Backend Workflow | `.github/workflows/backend-deploy.yml` |
| IAM Permissions Doc | `docs/iam_permissions_cicd.md` |
| SSM Parameters Doc | `docs/ssm_parameters_cicd.md` |
| CI/CD Integration Doc | `docs/cicd_ssm_integration.md` |
| Task Definition Template | `examples/cicd/task-definition-template.json` |

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/get_github_credentials.sh` | Get IAM credentials for GitHub Actions | `./scripts/get_github_credentials.sh` |
| `scripts/validate_ssm_params.sh` | Validate SSM parameters | `./scripts/validate_ssm_params.sh` |
| `scripts/test_ssm_params.sh` | Test SSM parameter retrieval | `./scripts/test_ssm_params.sh` |
| `scripts/setup_github_cicd.sh` | Set up GitHub repo with secrets | `./scripts/setup_github_cicd.sh` |

## SSM Parameter Structure

```
/notes/                          
  └── terraform/                 
      ├── ecr/                   
      ├── ecs/                   
      ├── vpc/                   
      └── database/              
  └── notes/                     
      └── prod/                  
          ├── backend_ecr_repository_url
          ├── ecs_cluster_name
          ├── backend_service_name
          ├── task_execution_role_arn
          ├── task_role_arn
          ├── db_secret_arn
          └── private_subnet_ids
```

## GitHub Secrets

| Secret Name | Purpose |
|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key for GitHub Actions |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for GitHub Actions |
| `AWS_REGION` | AWS region (e.g., `ap-south-1`) |

## Common AWS CLI Commands

```bash
# List all SSM parameters in the path
aws ssm get-parameters-by-path --path /notes/notes/prod --recursive

# Get a specific parameter
aws ssm get-parameter --name /notes/notes/prod/ecs_cluster_name

# Describe ECS service
aws ecs describe-services --cluster <cluster-name> --services <service-name>

# List ECS tasks
aws ecs list-tasks --cluster <cluster-name> --service-name <service-name>

# Get ECR login password
aws ecr get-login-password
```

## CI/CD Workflow Steps

1. **Checkout code**
2. **Configure AWS credentials**
3. **Get SSM parameters**
4. **Login to ECR**
5. **Build and push Docker image**
6. **Update task definition**
7. **Deploy to ECS**
8. **Run database migrations**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Access denied to SSM | Check IAM permissions |
| Parameter not found | Verify parameter exists in SSM |
| ECR login failed | Check AWS credentials and region |
| Task definition update failed | Check task execution role ARN |
| ECS deployment failed | Check service and cluster names |
| Migration task failed | Check subnet IDs and security group |

## References

- [AWS SSM Documentation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Amazon ECS Documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- [Terraform Documentation](https://www.terraform.io/docs)
