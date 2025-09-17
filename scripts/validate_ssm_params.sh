#!/bin/bash

# Script to validate SSM parameters needed for CI/CD
# This script helps validate that all required SSM parameters are properly set up

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Set default region
AWS_REGION=${AWS_REGION:-"ap-south-1"}

# SSM Parameter path
SSM_PARAMETER_PATH="/notes/notes/prod"

# List of required parameters
REQUIRED_PARAMS=(
    "backend_ecr_repository_url"
    "ecs_cluster_name"
    "backend_service_name"
    "task_execution_role_arn"
    "task_role_arn"
    "db_secret_arn"
    "private_subnet_ids"
)

echo -e "${YELLOW}Validating SSM parameters for CI/CD...${NC}"
echo "Region: $AWS_REGION"
echo "Parameter Path: $SSM_PARAMETER_PATH"
echo ""

MISSING_PARAMS=0
TOTAL_PARAMS=${#REQUIRED_PARAMS[@]}
FOUND_PARAMS=0

for param in "${REQUIRED_PARAMS[@]}"; do
    full_param_name="${SSM_PARAMETER_PATH}/${param}"
    echo -n "Checking $full_param_name... "
    
    value=$(aws ssm get-parameter --name "$full_param_name" --region "$AWS_REGION" --query "Parameter.Value" --output text 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$value" ]; then
        echo -e "${GREEN}✓ FOUND${NC}"
        echo "  Value: ${value:0:30}${value:30:1000000}" | sed 's/\(.\{30\}\).*$/\1.../' 
        FOUND_PARAMS=$((FOUND_PARAMS + 1))
    else
        echo -e "${RED}✗ MISSING${NC}"
        MISSING_PARAMS=$((MISSING_PARAMS + 1))
    fi
done

echo ""
echo "Summary:"
echo "-------"
echo -e "Found parameters: ${GREEN}$FOUND_PARAMS${NC}"
echo -e "Missing parameters: ${RED}$MISSING_PARAMS${NC}"
echo -e "Total required parameters: ${YELLOW}$TOTAL_PARAMS${NC}"
echo ""

if [ $MISSING_PARAMS -eq 0 ]; then
    echo -e "${GREEN}All required SSM parameters are set up!${NC}"
    exit 0
else
    echo -e "${RED}Some required SSM parameters are missing.${NC}"
    echo "Please make sure all required parameters are created in SSM Parameter Store."
    echo "These parameters should be created by the Terraform deployment."
    exit 1
fi
