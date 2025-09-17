# GitHub Actions OIDC Authentication Setup

This document explains the complete setup for GitHub Actions OIDC authentication with AWS.

## Files and Configuration

### 1. Trust Policy (`terraform/trust-policy.json`)
This policy defines who can assume the IAM role, with specific conditions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::587294124303:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:vinoddotcom/notes-back-end-services:*"
        }
      }
    }
  ]
}
```

The key element here is the `"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"` condition, which ensures that the audience claim in the OIDC token matches what GitHub Actions sends.

### 2. Permission Policy (`terraform/github-actions-policy.json`)
This policy defines what the role can do once assumed:

```json
{
  "Version": "2012-10-17",
  "Statement": [
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
    },
    /* Additional permissions not shown for brevity */
  ]
}
```

### 3. GitHub Actions Workflow (`.github/workflows/backend-deploy.yml`)
The workflow uses the `aws-actions/configure-aws-credentials@v2` action with the audience parameter:

```yaml
- name: Configure AWS credentials with OIDC
  uses: aws-actions/configure-aws-credentials@v2
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: ${{ env.AWS_REGION }}
    role-session-name: GitHubActions-${{ github.run_id }}
    audience: sts.amazonaws.com
```

The `audience` parameter is crucial for matching the condition in the trust policy.

### 4. Terraform Configuration (`terraform/modules/github_cicd_oidc/main.tf`)
This module uses data sources to reference existing AWS resources:

```hcl
# GitHub OIDC Provider
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

# IAM Role for GitHub Actions - use existing role
data "aws_iam_role" "github_actions" {
  name = "${var.project_name}-${var.environment}-github-actions-role"
}

# IAM Policy for GitHub Actions - use existing policy
data "aws_iam_policy" "github_actions" {
  name = "${var.project_name}-${var.environment}-github-actions-policy"
}
```

## Utility Scripts

1. **`update_github_actions_role.sh`**: Updates both the trust policy and permissions policy in AWS.
2. **`verify_oidc_configuration.sh`**: Verifies all OIDC configurations are correct.
3. **`push_oidc_changes.sh`**: Pushes all changes to GitHub.
4. **`test_oidc_setup.sh`**: Tests the OIDC setup (for AWS CLI testing only).

## Setup Steps

1. **Apply the Trust Policy**:
   ```bash
   ./scripts/update_github_actions_role.sh
   ```

2. **Verify the Configuration**:
   ```bash
   ./scripts/verify_oidc_configuration.sh
   ```

3. **Push Changes to GitHub**:
   ```bash
   ./scripts/push_oidc_changes.sh
   ```

4. **Test the OIDC Authentication**:
   Trigger the GitHub Actions workflow either by pushing a change to the main branch or using the workflow_dispatch event.

## Troubleshooting

If you encounter the "Credentials could not be loaded" error:

1. Check that the trust policy is correctly applied to the IAM role.
2. Verify that the audience parameter in the GitHub Actions workflow matches the condition in the trust policy.
3. Check that the GitHub repository name in the trust policy matches your repository.
4. Ensure that the OIDC provider is correctly set up in AWS IAM.

For other issues, check the CloudTrail logs for any permission denials or other AWS-related errors.
