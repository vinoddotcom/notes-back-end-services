#!/bin/bash

# Script to verify GitHub OIDC workflow setup

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}GitHub Actions OIDC Configuration Verification${NC}"
echo "========================================"

# 1. Check workflow file
WORKFLOW_FILE="../.github/workflows/backend-deploy.yml"
echo -e "\n1. Checking GitHub Actions workflow file..."

if [ -f "$WORKFLOW_FILE" ]; then
  echo -e "${GREEN}✓ Workflow file exists${NC}"
  
  # Check if the workflow contains the audience parameter
  if grep -q "audience: sts.amazonaws.com" "$WORKFLOW_FILE"; then
    echo -e "${GREEN}✓ Audience parameter is correctly set in the workflow${NC}"
  else
    echo -e "${RED}✗ Audience parameter is missing or incorrect in the workflow${NC}"
    echo "  Please add 'audience: sts.amazonaws.com' to the aws-actions/configure-aws-credentials step"
  fi
else
  echo -e "${RED}✗ Workflow file not found at $WORKFLOW_FILE${NC}"
fi

# 2. Check trust policy file
TRUST_POLICY_FILE="../../terraform/trust-policy.json"
echo -e "\n2. Checking trust policy file..."

if [ -f "$TRUST_POLICY_FILE" ]; then
  echo -e "${GREEN}✓ Trust policy file exists${NC}"
  
  # Check if the trust policy contains the audience condition
  if grep -q "token.actions.githubusercontent.com:aud" "$TRUST_POLICY_FILE" && grep -q "sts.amazonaws.com" "$TRUST_POLICY_FILE"; then
    echo -e "${GREEN}✓ Audience condition is correctly set in the trust policy${NC}"
  else
    echo -e "${RED}✗ Audience condition is missing or incorrect in the trust policy${NC}"
    echo "  Please add the StringEquals condition with token.actions.githubusercontent.com:aud: sts.amazonaws.com"
  fi
else
  echo -e "${RED}✗ Trust policy file not found at $TRUST_POLICY_FILE${NC}"
fi

# 3. Check terraform module
TERRAFORM_MODULE="../../terraform/modules/github_cicd_oidc/main.tf"
echo -e "\n3. Checking terraform module..."

if [ -f "$TERRAFORM_MODULE" ]; then
  echo -e "${GREEN}✓ Terraform module exists${NC}"
  
  # Check if the module uses data sources
  if grep -q "data \"aws_iam_openid_connect_provider\"" "$TERRAFORM_MODULE" && \
     grep -q "data \"aws_iam_role\"" "$TERRAFORM_MODULE" && \
     grep -q "data \"aws_iam_policy\"" "$TERRAFORM_MODULE"; then
    echo -e "${GREEN}✓ Terraform module correctly uses data sources${NC}"
  else
    echo -e "${RED}✗ Terraform module is not using data sources correctly${NC}"
    echo "  Please update the module to use data sources for existing resources"
  fi
else
  echo -e "${RED}✗ Terraform module not found at $TERRAFORM_MODULE${NC}"
fi

echo -e "\n${YELLOW}Summary of Actions Required:${NC}"
echo "1. Apply the trust policy to your AWS IAM role:"
echo "   aws iam update-assume-role-policy --role-name notes-prod-github-actions-role --policy-document file://terraform/trust-policy.json"
echo "2. Trigger the GitHub Actions workflow to test the OIDC authentication"

echo -e "\n${GREEN}Configuration verification complete!${NC}"
