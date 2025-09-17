#!/bin/bash

# Script to get GitHub Actions IAM credentials from Terraform outputs
# This script helps set up the required GitHub secrets for CI/CD

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "ERROR: Terraform is not installed. Please install it first."
    exit 1
fi

# Set working directory to the Terraform directory
cd "$(dirname "$0")/../../terraform" || exit 1

# Check if we're in the right directory
if [ ! -f "main.tf" ]; then
    echo "ERROR: Not in the Terraform directory. Please run this script from the backend-services directory."
    exit 1
fi

# Get the IAM credentials from Terraform outputs
echo "Retrieving GitHub Actions IAM credentials from Terraform outputs..."

# Get access key ID
ACCESS_KEY_ID=$(terraform output -raw github_actions_access_key_id 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$ACCESS_KEY_ID" ]; then
    echo "ERROR: Failed to get access key ID from Terraform output."
    echo "Make sure you have applied the Terraform configuration and that the github_cicd module is included."
    exit 1
fi

# Get secret access key (sensitive output)
SECRET_ACCESS_KEY=$(terraform output -raw github_actions_secret_access_key 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$SECRET_ACCESS_KEY" ]; then
    echo "ERROR: Failed to get secret access key from Terraform output."
    echo "Make sure you have applied the Terraform configuration and that the github_cicd module is included."
    exit 1
fi

echo "Successfully retrieved GitHub Actions IAM credentials!"
echo
echo "AWS_ACCESS_KEY_ID: $ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY: [HIDDEN FOR SECURITY]"
echo
echo "Instructions for setting up GitHub repository secrets:"
echo "1. Go to your GitHub repository settings"
echo "2. Navigate to 'Secrets and variables' > 'Actions'"
echo "3. Add the following secrets:"
echo "   - Name: AWS_ACCESS_KEY_ID"
echo "     Value: $ACCESS_KEY_ID"
echo "   - Name: AWS_SECRET_ACCESS_KEY"
echo "     Value: [The secret key shown above]"
echo
echo "IMPORTANT: Keep these credentials secure! Do not commit them to your repository."
