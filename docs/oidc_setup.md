# Setting up OIDC with GitHub Actions

This guide explains how to set up OpenID Connect (OIDC) with GitHub Actions for secure, keyless authentication with AWS.

## What is OIDC?

OpenID Connect (OIDC) is an authentication protocol that allows GitHub Actions workflows to access AWS resources without storing long-lived AWS credentials as secrets. Instead, GitHub Actions obtains short-lived credentials by assuming an IAM role directly.

## Benefits of Using OIDC

- **Enhanced Security**: No long-lived credentials stored in GitHub secrets
- **No Credential Rotation**: No need to rotate AWS access keys regularly
- **Simplified Permissions**: Temporary credentials with specific IAM role permissions
- **Fine-grained Access Control**: Restrict which GitHub workflows can assume which roles

## Prerequisites

- AWS account with administrator access
- GitHub repository with GitHub Actions workflows
- Terraform installed locally

## Implementation Steps

### 1. Set up the OIDC Provider and IAM Role in AWS

Use the provided Terraform module in `terraform/modules/github_cicd_oidc` to set up the OIDC provider and IAM role:

```bash
cd terraform
terraform apply
```

This will create:
- An OIDC identity provider for GitHub
- An IAM role with permissions for deployment
- A trust relationship that allows your repository to assume the role

### 2. Get the Role ARN

After applying the Terraform configuration, get the IAM role ARN:

```bash
terraform output github_actions_role_arn
```

### 3. Update GitHub Secrets

Add a new repository secret in GitHub:

- **Name**: `AWS_ROLE_ARN`
- **Value**: The IAM role ARN from step 2

### 4. Update GitHub Actions Workflow

Replace the AWS credentials configuration in your workflow:

```yaml
# Old configuration with access keys
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v1
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ${{ env.AWS_REGION }}

# New configuration with OIDC
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v1
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: ${{ env.AWS_REGION }}
```

### 5. Test the Workflow

Push a change to your repository to trigger the workflow and verify that it works correctly with OIDC authentication.

## Permissions Required

The IAM role used for GitHub Actions requires the following permissions:

### ECR (Elastic Container Registry)
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:GetDownloadUrlForLayer`
- `ecr:BatchGetImage`
- `ecr:InitiateLayerUpload`
- `ecr:UploadLayerPart`
- `ecr:CompleteLayerUpload`
- `ecr:PutImage`

### ECS (Elastic Container Service)
- `ecs:DescribeServices`
- `ecs:DescribeTaskDefinition`
- `ecs:RegisterTaskDefinition`
- `ecs:UpdateService`
- `ecs:RunTask`
- `ecs:DescribeClusters`
- `ecs:ListTasks`
- `ecs:DescribeTasks`

### IAM Pass Role
- `iam:PassRole` (for task execution role and task role)

### Secrets Manager
- `secretsmanager:GetSecretValue`

### CloudFront
- `cloudfront:CreateInvalidation`
- `cloudfront:GetDistribution`

### SSM Parameter Store
- `ssm:GetParameter`
- `ssm:GetParameters`
- `ssm:GetParametersByPath`

## Troubleshooting

### Permissions Issues

If your workflow fails with an "Access Denied" error:

1. Check the IAM role trust policy
2. Verify that the correct GitHub repository is allowed to assume the role
3. Ensure the IAM role has all necessary permissions

### Authentication Issues

If the workflow fails to assume the role:

1. Verify that the `AWS_ROLE_ARN` secret is correctly set
2. Check the GitHub OIDC provider configuration in AWS
3. Make sure the OIDC provider thumbprints are up to date

## Security Considerations

1. **Scope Trust Policies**: Limit which repositories and branches can assume the role
2. **Use Condition Keys**: Add conditions to the trust policy (e.g., environment, ref)
3. **Least Privilege**: Only grant the permissions needed for the workflow
4. **Monitor Assume Role Events**: Set up CloudTrail monitoring for AssumeRoleWithWebIdentity events

## Additional Resources

- [GitHub Actions OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS IAM OIDC Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
