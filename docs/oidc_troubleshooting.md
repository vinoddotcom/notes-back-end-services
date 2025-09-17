# OIDC Authentication Troubleshooting

If you encounter issues with OIDC authentication in GitHub Actions, use this guide to resolve them.

## Common Error: "Credentials could not be loaded"

If you see this error:
```
Error: Credentials could not be loaded, please check your action inputs: Could not load credentials from any providers
```

This usually indicates an issue with the OIDC authentication configuration.

## Solution

### 1. Update the GitHub Actions Workflow

Make sure you're using the latest version of the AWS credentials action and include the audience parameter:

```yaml
- name: Configure AWS credentials with OIDC
  uses: aws-actions/configure-aws-credentials@v2
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: ${{ env.AWS_REGION }}
    role-session-name: GitHubActions-${{ github.run_id }}
    audience: sts.amazonaws.com
```

Important changes:
- Use `v2` instead of `v1` of the action
- Add `role-session-name` parameter
- Add `audience: sts.amazonaws.com` parameter

### 2. Update the IAM Role Trust Policy

The IAM role's trust policy must explicitly allow the `sts.amazonaws.com` audience. Run the provided script to update the trust policy:

```bash
./scripts/update_oidc_trust_policy.sh
```

This script will update the trust policy to include:

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
  },
  "StringLike": {
    "token.actions.githubusercontent.com:sub": "repo:vinoddotcom/notes-back-end-services:*"
  }
}
```

### 3. Verify GitHub Repository Secret

Ensure that the `AWS_ROLE_ARN` secret in your GitHub repository is correctly set to:
```
arn:aws:iam::587294124303:role/notes-prod-github-actions-role
```

## Additional Troubleshooting

If the issue persists:

1. Check the AWS CloudTrail logs for AssumeRoleWithWebIdentity failures
2. Verify the GitHub OIDC provider is correctly configured in AWS IAM
3. Ensure that the GitHub workflow is running in the correct repository
4. Confirm that the IAM role has the necessary permissions for your workflow actions

For detailed error investigation, set up CloudWatch Logs with a subscription filter for OIDC authentication failures.
