#!/bin/bash

# Script to update both trust policy and permissions policy for GitHub OIDC authentication

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# IAM role name
ROLE_NAME="notes-prod-github-actions-role"
POLICY_NAME="notes-prod-github-actions-policy"

echo -e "${YELLOW}Updating IAM role configuration for GitHub Actions...${NC}"

# Step 1: Update the trust policy
echo -e "\n${YELLOW}Step 1: Updating IAM role trust policy...${NC}"
if aws iam update-assume-role-policy --role-name $ROLE_NAME --policy-document file://../terraform/trust-policy.json; then
  echo -e "${GREEN}✓ Successfully updated IAM role trust policy${NC}"
  echo "  The role now accepts the 'sts.amazonaws.com' audience for OIDC authentication"
else
  echo -e "${RED}✗ Failed to update IAM role trust policy${NC}"
  echo "  Please check the role name and your AWS credentials"
  echo "  You may need to manually update the policy in the AWS Console"
  echo "  Policy file: ../terraform/trust-policy.json"
fi

# Step 2: Update or create the permissions policy
echo -e "\n${YELLOW}Step 2: Updating IAM policy permissions...${NC}"

# Check if the policy exists
if aws iam get-policy --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/$POLICY_NAME &>/dev/null; then
  echo "  Policy exists, updating policy version..."
  
  # Create a new policy version
  if aws iam create-policy-version --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/$POLICY_NAME \
    --policy-document file://../terraform/github-actions-policy.json --set-as-default; then
    echo -e "${GREEN}✓ Successfully updated IAM policy permissions${NC}"
  else
    echo -e "${RED}✗ Failed to update IAM policy${NC}"
    echo "  Please check the policy name and your AWS credentials"
  fi
else
  echo "  Policy doesn't exist, creating new policy..."
  
  # Create a new policy
  if aws iam create-policy --policy-name $POLICY_NAME \
    --policy-document file://../terraform/github-actions-policy.json; then
    echo -e "${GREEN}✓ Successfully created IAM policy${NC}"
    
    # Attach policy to role
    aws iam attach-role-policy --role-name $ROLE_NAME \
      --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/$POLICY_NAME
    echo -e "${GREEN}✓ Successfully attached policy to role${NC}"
  else
    echo -e "${RED}✗ Failed to create IAM policy${NC}"
    echo "  Please check your AWS credentials"
  fi
fi

echo -e "\n${GREEN}IAM configuration complete!${NC}"
echo -e "Next steps:"
echo "1. Push the updated workflow file to GitHub"
echo "2. Trigger the GitHub Actions workflow to test the OIDC authentication"
echo "3. Check the workflow logs for any errors"
