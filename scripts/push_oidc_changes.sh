#!/bin/bash

# Script to commit and push all OIDC-related changes to GitHub

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Pushing OIDC configuration changes to GitHub${NC}"
echo "==========================================="

# Move to the repository root
cd /home/guest/Desktop/notes

# Check if we're in a git repository
if [ ! -d ".git" ]; then
  echo -e "${RED}Error: Not a git repository${NC}"
  exit 1
fi

# Add all changed files
echo -e "\n1. Adding changed files..."
git add terraform/trust-policy.json
git add terraform/modules/github_cicd_oidc/main.tf
git add backend-services/.github/workflows/backend-deploy.yml
git add backend-services/scripts/verify_oidc_configuration.sh
git add terraform/fix_oidc_issues.md

# Commit the changes
echo -e "\n2. Committing changes..."
git commit -m "Fix OIDC authentication for GitHub Actions

- Update GitHub Actions workflow to include audience parameter
- Update trust policy with correct audience condition
- Configure Terraform to use data sources for existing resources
- Add verification scripts for OIDC configuration"

# Push the changes
echo -e "\n3. Pushing changes to GitHub..."
echo -e "${YELLOW}Note: This will trigger the GitHub Actions workflow${NC}"
echo "Do you want to continue? (y/n)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  if git push origin main; then
    echo -e "${GREEN}Changes pushed successfully!${NC}"
    echo -e "\n${YELLOW}Next steps:${NC}"
    echo "1. Apply the trust policy to your AWS IAM role:"
    echo "   aws iam update-assume-role-policy --role-name notes-prod-github-actions-role --policy-document file://terraform/trust-policy.json"
    echo "2. Monitor the GitHub Actions workflow to ensure OIDC authentication is working"
  else
    echo -e "${RED}Failed to push changes to GitHub${NC}"
    echo "Please check your git configuration and try again"
  fi
else
  echo -e "${YELLOW}Changes were not pushed to GitHub${NC}"
  echo "You can push the changes manually when ready"
fi
