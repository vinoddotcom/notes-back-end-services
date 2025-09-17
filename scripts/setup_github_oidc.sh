#!/bin/bash

# Script to set up GitHub OIDC authentication
# This script helps set up the required GitHub secrets for CI/CD with OIDC

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}ERROR: Terraform is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if the GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) is not installed. Please install it first.${NC}"
    echo "Visit https://cli.github.com/ for installation instructions."
    exit 1
fi

# Check if logged in to GitHub
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}You need to login to GitHub CLI first.${NC}"
    echo "Run 'gh auth login' to authenticate."
    exit 1
fi

# Set working directory to the Terraform directory
cd "$(dirname "$0")/../../terraform" || exit 1

# Check if we're in the right directory
if [ ! -f "main.tf" ]; then
    echo -e "${RED}ERROR: Not in the Terraform directory. Please run this script from the backend-services directory.${NC}"
    exit 1
fi

echo -e "${YELLOW}Setting up OIDC authentication for GitHub Actions...${NC}"
echo ""

# Ask for GitHub repository name
read -p "Enter GitHub repository name (e.g., username/repo): " REPO_NAME

# Validate repository format
if [[ ! $REPO_NAME =~ .+/.+ ]]; then
    echo -e "${RED}Invalid repository format. Please use the format 'username/repo'.${NC}"
    exit 1
fi

# Check if repository exists
if ! gh repo view "$REPO_NAME" &> /dev/null; then
    echo -e "${RED}Repository not found: $REPO_NAME${NC}"
    echo "Please check the repository name and try again."
    exit 1
fi

echo -e "\n${GREEN}Repository found: $REPO_NAME${NC}"

# Ask if Terraform should be applied
read -p "Do you want to apply Terraform to create the OIDC provider and IAM role? (y/n): " APPLY_TERRAFORM

if [[ "$APPLY_TERRAFORM" == "y" || "$APPLY_TERRAFORM" == "Y" ]]; then
    echo -e "\n${YELLOW}Applying Terraform configuration...${NC}"
    terraform apply -target=module.github_cicd_oidc
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Terraform apply failed. Please check the errors and try again.${NC}"
        exit 1
    fi
fi

# Get the IAM role ARN
echo -e "\n${YELLOW}Getting IAM role ARN from Terraform output...${NC}"
ROLE_ARN=$(terraform output -raw github_actions_role_arn 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$ROLE_ARN" ]; then
    echo -e "${RED}Failed to get role ARN from Terraform output.${NC}"
    echo "Make sure you have applied the Terraform configuration and that the github_cicd_oidc module is included."
    exit 1
fi

# Set up GitHub repository secrets
echo -e "\n${YELLOW}Setting up GitHub repository secrets...${NC}"

# Set AWS_ROLE_ARN secret
echo "Setting AWS_ROLE_ARN secret..."
echo "$ROLE_ARN" | gh secret set AWS_ROLE_ARN --repo "$REPO_NAME"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to set AWS_ROLE_ARN secret.${NC}"
    exit 1
fi

# Set AWS_REGION secret
AWS_REGION=${AWS_REGION:-"ap-south-1"}
echo "Setting AWS_REGION secret..."
echo "$AWS_REGION" | gh secret set AWS_REGION --repo "$REPO_NAME"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to set AWS_REGION secret.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Successfully set up GitHub repository secrets for OIDC authentication!${NC}"
echo -e "${GREEN}Your repository is now ready for CI/CD with AWS using OIDC.${NC}"
echo ""
echo "The following secrets have been set:"
echo "- AWS_ROLE_ARN: $ROLE_ARN"
echo "- AWS_REGION: $AWS_REGION"
echo ""
echo "To trigger the CI/CD pipeline, push changes to the main branch or use the GitHub Actions UI."
echo ""
echo "IMPORTANT: Make sure your GitHub Actions workflow is configured to use OIDC authentication:"
echo ""
echo "      - name: Configure AWS credentials"
echo "        uses: aws-actions/configure-aws-credentials@v1"
echo "        with:"
echo "          role-to-assume: \${{ secrets.AWS_ROLE_ARN }}"
echo "          aws-region: \${{ env.AWS_REGION }}"
