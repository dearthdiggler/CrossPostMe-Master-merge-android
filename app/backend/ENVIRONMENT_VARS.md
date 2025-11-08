# Environment Variables & Secrets Reference

## Backend (.env, Render, Railway)

- MONGO_URL: MongoDB connection string
- DB_NAME: Database name
- SECRET_KEY: App secret (session signing)
- JWT_SECRET_KEY: JWT signing key
- CREDENTIAL_ENCRYPTION_KEY: Encryption key for credentials
- CORS_ORIGINS: Allowed frontend origins
- ACCESS_TOKEN_EXPIRE_MINUTES: JWT access token lifetime
- REFRESH_TOKEN_EXPIRE_DAYS: JWT refresh token lifetime
- MONGO_SERVER_SELECTION_TIMEOUT_MS: MongoDB connection timeout
- EBAY_APP_ID, EBAY_DEV_ID, EBAY_CERT_ID: eBay API keys
- FACEBOOK_APP_ID, FACEBOOK_APP_SECRET: Facebook API keys
- MONITORING_EMAIL, MONITORING_PASSWORD: Email monitoring credentials (optional)

## Frontend (.env, .env.local, Render)

- REACT_APP_API_URL: Backend API base URL
- REACT_APP_BACKEND_URL: Backend API base URL (alternate)
- WDS_SOCKET_PORT: WebSocket port for hot reload

## Mobile (Android/iOS)

- API base URL: Backend endpoint for mobile app
- Any mobile-specific API keys (use secure storage)

## CI/CD & Cloud

- All secrets should be set in GitHub/Render/Railway secrets, not committed
- Never expose secrets in logs or builds

## Best Practices

- Never commit real secrets to git
- Use .env.example for safe templates
- Document all required variables for each service
- Use secure vaults or platform secrets for production

---

## See .env.example files for templates

## Update this file as new variables are added
