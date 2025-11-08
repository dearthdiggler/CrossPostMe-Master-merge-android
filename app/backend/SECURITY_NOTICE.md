# Security Notice

## Credential Rotation Required

**⚠️ URGENT: The following credentials were previously exposed in version control and MUST be rotated immediately:**

### MongoDB Atlas

- **Action Required**: Rotate database password
- **Location**: https://cloud.mongodb.com/ -> Database Access -> Edit User
- **Affected**: `crosspostme_db_user` password was exposed
- **Steps**:
  1. Go to MongoDB Atlas Console
  2. Navigate to Database Access
  3. Find user `crosspostme_db_user`
  4. Click "Edit" and change password
  5. Update the new password in your Render.com environment variables
  6. DO NOT commit the new password to git

### Application Secrets

- **Action Required**: Generate new keys
- **Affected Keys**:
  - `SECRET_KEY` (used for session management)
  - `JWT_SECRET_KEY` (used for JWT token signing)
  - `CREDENTIAL_ENCRYPTION_KEY` (used for encrypting stored credentials)

- **Generate New Keys**:

  ```bash
  # SECRET_KEY and JWT_SECRET_KEY
  openssl rand -hex 32

  # CREDENTIAL_ENCRYPTION_KEY
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

### Update Deployment

After rotating credentials:

1. Go to Render.com dashboard: https://dashboard.render.com/
2. Select your backend service
3. Navigate to "Environment" tab
4. Update these variables with new values:
   - `MONGO_URL` (with new password)
   - `SECRET_KEY` (newly generated)
   - `JWT_SECRET_KEY` (newly generated)
   - `CREDENTIAL_ENCRYPTION_KEY` (newly generated)
5. Click "Save Changes" to trigger redeployment

### Security Best Practices Going Forward

- ✅ `.env.render` is now in `.gitignore` to prevent future exposure
- ✅ Use `.env.render.template` as a reference for required variables
- ✅ Never commit files containing actual credentials
- ✅ Use environment variables in deployment platforms directly
- ✅ Rotate credentials if you suspect any compromise
- ✅ Use different credentials for development vs production

### Notes

- Old exposed credentials are now considered compromised
- Anyone with repository access could have captured these values
- Rotation must happen ASAP to maintain security
- Keep your actual `.env.render` file local only
