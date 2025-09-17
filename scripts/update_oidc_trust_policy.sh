#!/bin/bash

# Script to update the IAM role trust policy for GitHub OIDC authentication

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# IAM role name
ROLE_NAME="notes-prod-github-actions-role"

echo -e "${YELLOW}Updating IAM role trust policy for GitHub OIDC authentication...${NC}"

# Create the trust policy JSON file
cat > trust-policy.json << 'EOF'
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
EOF

# Update the IAM role trust policy
if aws iam update-assume-role-policy --role-name $ROLE_NAME --policy-document file://trust-policy.json; then
  echo -e "${GREEN}Successfully updated IAM role trust policy for $ROLE_NAME${NC}"
  echo "The role now accepts the 'sts.amazonaws.com' audience for OIDC authentication."
else
  echo -e "${RED}Failed to update IAM role trust policy.${NC}"
  echo "Please check the role name and your AWS credentials."
  exit 1
fi

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Ensure you have added the AWS_ROLE_ARN secret to your GitHub repository"
echo "2. Make sure the GitHub Actions workflow is using aws-actions/configure-aws-credentials@v2"
echo "3. Ensure the 'audience' parameter is set to 'sts.amazonaws.com' in the workflow"

echo -e "\n${GREEN}Trust policy has been updated successfully!${NC}"
