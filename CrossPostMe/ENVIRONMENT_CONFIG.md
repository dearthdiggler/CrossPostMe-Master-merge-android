# Environment Configuration

This application uses environment-specific configuration files to manage settings safely across different deployment environments.

## Configuration Files

- `.env.development` - Development environment settings
- `.env.production` - Production environment settings
- `.env` - Default/fallback configuration (should match production for deployed instances)

## Environment Variables

### Required Variables

- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins
- `SECRET_KEY` - Application secret key
- `JWT_SECRET_KEY` - JWT token secret
- `CREDENTIAL_ENCRYPTION_KEY` - Key for encrypting stored credentials
- `NODE_ENV` - Environment type (`development`, `production`)

### CORS Configuration

**⚠️ Security Notice**: The `CORS_ORIGINS` setting is critical for security.

- **Development**: Can include `localhost` and local development URLs
- **Production**: Must specify exact allowed domains, **never use wildcard `*`**

Examples:

```bash
# Development
CORS_ORIGINS="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"

# Production
CORS_ORIGINS="https://crosspostme-frontend.onrender.com,https://www.crosspostme.com,https://crosspostme.com"
```

## Configuration Validation

The application validates configuration at startup and will fail to start if:

1. `CORS_ORIGINS` contains wildcard `*` in production
2. Required secrets are missing or use development placeholders in production
3. Critical environment variables are not set

## Usage

Set the `NODE_ENV` environment variable to control which configuration file is loaded:

```bash
# Development
NODE_ENV=development npm start

# Production
NODE_ENV=production npm start
```

If `NODE_ENV` is not set, the application defaults to development mode.

## Optional Services

### Metrics Poller

- `METRICS_POLL_INTERVAL` - Poll interval in seconds (default 300). The metrics poller is a background worker skeleton at `worker/metrics_poller.py`. Implement platform adapters and provide API credentials for each platform to enable real metric collection.

### Server-side Mermaid Rendering

- To enable the `/api/ads/render/svg` endpoint, install Mermaid CLI (`mmdc`). This requires Node.js. Example:

```bash
npm install -g @mermaid-js/mermaid-cli
```

If `mmdc` is not installed the render endpoint returns 501 with guidance to install it.
