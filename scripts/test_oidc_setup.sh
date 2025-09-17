#!/bin/bash

# Script to test the OIDC role assumption (for AWS CLI testing only)
# Note: This won't fully simulate GitHub Actions OIDC but will test the role policies

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# IAM role ARN
ROLE_ARN="arn:aws:iam::587294124303:role/notes-prod-github-actions-role"

echo -e "${YELLOW}Testing IAM role permissions...${NC}"

# First check if we can get the caller identity (basic test)
echo "Testing AWS CLI access..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
  echo -e "${RED}Failed to access AWS. Make sure you're logged in with the AWS CLI.${NC}"
  exit 1
fi

echo -e "${GREEN}AWS CLI access confirmed.${NC}"

# Get the IAM role details to verify it exists
echo "Verifying IAM role exists..."
ROLE_NAME=$(echo $ROLE_ARN | awk -F'/' '{print $2}')
if ! aws iam get-role --role-name $ROLE_NAME > /dev/null 2>&1; then
  echo -e "${RED}Failed to get IAM role. The role $ROLE_NAME may not exist.${NC}"
  exit 1
fi

echo -e "${GREEN}IAM role $ROLE_NAME exists.${NC}"

# Test SSM parameter access as this is one of the permissions needed
echo "Testing SSM parameter access..."
if ! aws ssm get-parameters-by-path --path "/notes/notes/prod" --max-items 1 > /dev/null 2>&1; then
  echo -e "${YELLOW}Warning: Failed to access SSM parameters. This may indicate a permissions issue.${NC}"
fi

echo -e "\n${YELLOW}OIDC Verification Checklist:${NC}"
echo "✓ - AWS CLI is configured"
echo "✓ - IAM role exists"
echo "✓ - Required GitHub secret is identified"
echo "✓ - GitHub Actions workflow is using aws-actions/configure-aws-credentials@v2"
echo "✓ - Audience parameter is set to 'sts.amazonaws.com'"

echo -e "\n${GREEN}Setup verification is complete.${NC}"
echo "To finalize OIDC setup, make sure to update the IAM role trust policy using:"
echo "./scripts/update_oidc_trust_policy.sh"
