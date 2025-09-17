#!/bin/bash

# Setup script for initializing CI/CD on a GitHub repository
# This script helps to set up the required GitHub secrets for the CI/CD pipeline

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

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

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    echo "Visit https://aws.amazon.com/cli/ for installation instructions."
    exit 1
fi

# Set working directory to the Terraform directory
cd "$(dirname "$0")/../../terraform" || exit 1

# Check if we're in the right directory
if [ ! -f "main.tf" ]; then
    echo -e "${RED}Not in the Terraform directory. Please run this script from the backend-services directory.${NC}"
    exit 1
fi

echo -e "${YELLOW}Setting up CI/CD for GitHub repository...${NC}"
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

# Get IAM credentials from Terraform output
echo -e "\n${YELLOW}Retrieving GitHub Actions IAM credentials from Terraform outputs...${NC}"

# Get access key ID
ACCESS_KEY_ID=$(terraform output -raw github_actions_access_key_id 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$ACCESS_KEY_ID" ]; then
    echo -e "${RED}Failed to get access key ID from Terraform output.${NC}"
    echo "Make sure you have applied the Terraform configuration and that the github_cicd module is included."
    exit 1
fi

# Get secret access key (sensitive output)
SECRET_ACCESS_KEY=$(terraform output -raw github_actions_secret_access_key 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$SECRET_ACCESS_KEY" ]; then
    echo -e "${RED}Failed to get secret access key from Terraform output.${NC}"
    echo "Make sure you have applied the Terraform configuration and that the github_cicd module is included."
    exit 1
fi

# Set AWS region
AWS_REGION=${AWS_REGION:-"ap-south-1"}

# Set up GitHub repository secrets
echo -e "\n${YELLOW}Setting up GitHub repository secrets...${NC}"

# Set AWS_ACCESS_KEY_ID secret
echo "Setting AWS_ACCESS_KEY_ID secret..."
echo "$ACCESS_KEY_ID" | gh secret set AWS_ACCESS_KEY_ID --repo "$REPO_NAME"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to set AWS_ACCESS_KEY_ID secret.${NC}"
    exit 1
fi

# Set AWS_SECRET_ACCESS_KEY secret
echo "Setting AWS_SECRET_ACCESS_KEY secret..."
echo "$SECRET_ACCESS_KEY" | gh secret set AWS_SECRET_ACCESS_KEY --repo "$REPO_NAME"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to set AWS_SECRET_ACCESS_KEY secret.${NC}"
    exit 1
fi

# Set AWS_REGION secret
echo "Setting AWS_REGION secret..."
echo "$AWS_REGION" | gh secret set AWS_REGION --repo "$REPO_NAME"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to set AWS_REGION secret.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Successfully set up GitHub repository secrets for CI/CD!${NC}"
echo -e "${GREEN}Your repository is now ready for CI/CD with AWS.${NC}"
echo ""
echo "The following secrets have been set:"
echo "- AWS_ACCESS_KEY_ID"
echo "- AWS_SECRET_ACCESS_KEY"
echo "- AWS_REGION: $AWS_REGION"
echo ""
echo "To trigger the CI/CD pipeline, push changes to the main branch or use the GitHub Actions UI."
