#!/bin/bash

# Script for manually running the SSM parameter fetch steps from CI/CD
# This is useful for testing or debugging the SSM parameter integration

# Set environment variables
AWS_REGION=${AWS_REGION:-"ap-south-1"}
SSM_PARAMETER_PATH="/notes/notes/prod"
PROJECT_NAME="notes"
ENVIRONMENT="prod"

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    echo "Visit https://aws.amazon.com/cli/ for installation instructions."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}AWS credentials are not configured or are invalid.${NC}"
    echo "Run 'aws configure' to set up your AWS credentials."
    exit 1
fi

echo -e "${YELLOW}Getting SSM parameters for deployment...${NC}"
echo "AWS Region: $AWS_REGION"
echo "SSM Parameter Path: $SSM_PARAMETER_PATH"
echo ""

# Function to get a parameter and display its value
get_parameter() {
    local param_name=$1
    local env_var_name=$2
    
    echo -n "Getting $param_name... "
    
    value=$(aws ssm get-parameter --name "${SSM_PARAMETER_PATH}/${param_name}" --region "$AWS_REGION" \
        --query Parameter.Value --output text 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$value" ]; then
        export $env_var_name="$value"
        echo -e "${GREEN}✓${NC}"
        echo "  ${env_var_name}=${value}"
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "  Parameter not found or access denied"
    fi
}

# Get all parameters used in CI/CD
get_parameter "backend_ecr_repository_url" "ECR_REPOSITORY"
get_parameter "ecs_cluster_name" "ECS_CLUSTER"
get_parameter "backend_service_name" "ECS_SERVICE"
get_parameter "task_execution_role_arn" "TASK_EXECUTION_ROLE"
get_parameter "task_role_arn" "TASK_ROLE"
get_parameter "db_secret_arn" "DB_SECRET_ARN"
get_parameter "private_subnet_ids" "PRIVATE_SUBNET_IDS"

# Output the parameters that would be set in GitHub Actions
echo ""
echo -e "${YELLOW}Parameters that would be set in GitHub Actions:${NC}"
echo ""
echo "ECR_REPOSITORY=$ECR_REPOSITORY"
echo "ECS_CLUSTER=$ECS_CLUSTER"
echo "ECS_SERVICE=$ECS_SERVICE"
echo "TASK_EXECUTION_ROLE=$TASK_EXECUTION_ROLE"
echo "TASK_ROLE=$TASK_ROLE"
echo "DB_SECRET_ARN=$DB_SECRET_ARN"
echo "PRIVATE_SUBNET_IDS=$PRIVATE_SUBNET_IDS"

# Test formatting the subnet IDs like in the GitHub Actions workflow
if [ -n "$PRIVATE_SUBNET_IDS" ]; then
    echo ""
    echo -e "${YELLOW}Testing subnet ID formatting for ECS run-task:${NC}"
    SUBNET_LIST=$(echo $PRIVATE_SUBNET_IDS | sed 's/,/","/g')
    echo "Formatted subnet list: [\"$SUBNET_LIST\"]"
fi

echo ""
echo -e "${GREEN}Done!${NC}"
