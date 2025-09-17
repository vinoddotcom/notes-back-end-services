# Backend Deployment Instructions

Follow these steps to deploy the backend API to api.vinod.digital:

## Prerequisites

1. All infrastructure must be deployed using Terraform
2. GitHub repository must be set up at https://github.com/vinoddotcom/notes-back-end-services

## Authentication Options

You can use one of two authentication methods to connect GitHub Actions to AWS:

### Option 1: IAM User with Access Keys (Standard Method)

1. Run the GitHub credentials script to get the IAM credentials:

```bash
./scripts/get_github_credentials.sh
```

2. Add the following secrets to the GitHub repository:
   - `AWS_ACCESS_KEY_ID`: The IAM access key ID
   - `AWS_SECRET_ACCESS_KEY`: The IAM secret access key
   - `AWS_REGION`: ap-south-1

You can use the GitHub CLI to set these secrets:

```bash
gh secret set AWS_ACCESS_KEY_ID -b "AKIAYRPLVFEHTYMJJF3W" --repo vinoddotcom/notes-back-end-services
gh secret set AWS_SECRET_ACCESS_KEY -b "your-secret-key" --repo vinoddotcom/notes-back-end-services
gh secret set AWS_REGION -b "ap-south-1" --repo vinoddotcom/notes-back-end-services
```

### Option 2: OIDC Authentication (Recommended Secure Method)

1. Apply the Terraform configuration for OIDC:

```bash
cd terraform
terraform apply
```

2. Get the IAM role ARN from the Terraform output:

```bash
terraform output github_actions_role_arn
```

3. Add the following secrets to the GitHub repository:
   - `AWS_ROLE_ARN`: The IAM role ARN from the output
   - `AWS_REGION`: ap-south-1

```bash
gh secret set AWS_ROLE_ARN -b "arn:aws:iam::587294124303:role/notes-prod-github-actions-role" --repo vinoddotcom/notes-back-end-services
gh secret set AWS_REGION -b "ap-south-1" --repo vinoddotcom/notes-back-end-services
```

For detailed instructions on OIDC setup, see [OIDC Setup Guide](./docs/oidc_setup.md).

## Deploy the Backend

1. Push the code to the main branch of the GitHub repository:

```bash
git add .
git commit -m "Initial backend deployment"
git push origin main
```

2. The GitHub Actions workflow will automatically:
   - Run tests
   - Build a Docker image
   - Push the image to ECR
   - Deploy to ECS
   - Run database migrations

3. Monitor the deployment in the "Actions" tab of your GitHub repository

## Verify the Deployment

1. Check if the API is accessible at https://api.vinod.digital/health
2. You should see a response like:
```json
{"status":"ok","service":"notes-backend"}
```

## Troubleshooting

If the deployment fails:

1. Check the GitHub Actions logs for errors
2. Verify that all SSM parameters exist:
```bash
./scripts/validate_ssm_params.sh
```
3. Test the SSM parameter retrieval:
```bash
./scripts/test_ssm_params.sh
```

## Next Steps

Once the backend is deployed, you can start working on the frontend, which will be deployed to notes.vinod.digital.
