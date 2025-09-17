# OIDC Authentication Update

The backend deployment workflow has been updated to use OIDC (OpenID Connect) authentication exclusively instead of AWS access keys. This change improves security by eliminating the need for long-lived access keys stored as GitHub secrets.

## Required Configuration

To use the updated workflow, you must configure the following GitHub secret:

- **AWS_ROLE_ARN**: `arn:aws:iam::587294124303:role/notes-prod-github-actions-role`

## Benefits of OIDC-Only Authentication

1. **Enhanced Security**: No long-lived AWS credentials are stored in GitHub secrets
2. **Simplified Management**: No need to rotate AWS access keys regularly
3. **Auditable Access**: All access is tied to specific GitHub workflow runs
4. **Reduced Risk**: Eliminates the risk of leaked credentials

## Next Steps

If you previously used AWS access keys with this workflow, you can now safely delete the following GitHub secrets:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

These are no longer needed and removing them reduces security risks.

For more information on how OIDC authentication works with GitHub Actions and AWS, see [docs/oidc_setup.md](./docs/oidc_setup.md).
