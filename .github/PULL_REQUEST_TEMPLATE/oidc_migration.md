# OIDC Authentication Migration

## Description
This PR updates the GitHub Actions workflow to use OIDC authentication exclusively, removing the option to use AWS access keys.

## Required Actions
- [ ] Add the AWS_ROLE_ARN secret to the GitHub repository with value `arn:aws:iam::587294124303:role/notes-prod-github-actions-role`
- [ ] Remove AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY secrets from the repository (after confirming OIDC works)

## Benefits
- Enhanced security with keyless authentication
- Elimination of long-lived credentials
- Simplified access management
- Automatic token expiration

## Documentation
- See [OIDC Migration Guide](./docs/oidc_migration.md) for details
- See [OIDC Setup Documentation](./docs/oidc_setup.md) for configuration information
