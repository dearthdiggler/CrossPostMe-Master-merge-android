# 🔐 SECRETS VAULT

A secure, encrypted secrets management system for CrossPostMe.

## Overview

The Secrets Vault provides encrypted storage for sensitive configuration data including:
- Database credentials
- API keys
- JWT secrets
- Payment processor keys
- Email service credentials

## Security Features

- **AES-256 Encryption**: All secrets encrypted with OpenSSL AES-256-CBC
- **PBKDF2 Key Derivation**: Strong key derivation with salt
- **Access Control**: Master key required for decryption
- **No Plaintext Storage**: Secrets never stored in plaintext
- **Environment Isolation**: Separate vaults for different environments

## Quick Start

### 1. Initialize Vault
```bash
./setup-vault.sh
```

### 2. Test Vault Access
```bash
python3 vault.py
```

### 3. Use in Application
```python
from vault import get_secret

api_key = get_secret('openai_api_key')
db_url = get_secret('mongodb_url')
```

## Vault Structure

```
secrets_vault/
├── master.key          # 🔑 Master encryption key (BACKUP SECURELY!)
├── supabase_url.enc    # Encrypted secrets
├── supabase_anon_key.enc
├── secret_key.enc
├── stripe_secret_key.enc
└── ...
```

## Supported Secrets

| Secret Name | Description | Environment Variable |
|-------------|-------------|---------------------|
| `supabase_url` | Supabase project URL | `SUPABASE_URL` |
| `supabase_anon_key` | Supabase anonymous key | `SUPABASE_ANON_KEY` |
| `supabase_service_role_key` | Supabase service role key | `SUPABASE_SERVICE_ROLE_KEY` |
| `secret_key` | JWT signing secret | `SECRET_KEY` |
| `stripe_secret_key` | Stripe secret key | `STRIPE_SECRET_KEY` |
| `stripe_publishable_key` | Stripe publishable key | `STRIPE_PUBLISHABLE_KEY` |
| `stripe_webhook_secret` | Stripe webhook secret | `STRIPE_WEBHOOK_SECRET` |
| `mongodb_url` | MongoDB connection URL | `MONGODB_URL` |
| `smtp_username` | SMTP username | `SMTP_USERNAME` |
| `smtp_password` | SMTP password | `SMTP_PASSWORD` |
| `openai_api_key` | OpenAI API key | `OPENAI_API_KEY` |

## API Reference

### `get_secret(name, default=None)`
Retrieve a secret from the vault.

```python
from vault import get_secret

# Get a secret
api_key = get_secret('openai_api_key')

# With fallback
api_key = get_secret('openai_api_key', 'fallback-key')
```

### `get_all_secrets()`
Get all secrets as environment variable dict.

```python
from vault import get_all_secrets

secrets = get_all_secrets()
# Returns: {'OPENAI_API_KEY': 'sk-...', 'SECRET_KEY': 'abc123...'}
```

### `load_secrets_to_env()`
Load all vault secrets into environment variables.

```python
from vault import load_secrets_to_env

load_secrets_to_env()
# Now os.environ has all secrets
```

## Security Best Practices

### 🔐 Master Key Management
- **Backup Securely**: Store master.key in a secure location (password manager, HSM)
- **Never Commit**: master.key is in .gitignore for a reason
- **Environment Separation**: Use different master keys for dev/staging/prod
- **Access Control**: Limit who has access to the master key

### 🛡️ Operational Security
- **Principle of Least Privilege**: Only store secrets your app needs
- **Regular Rotation**: Rotate secrets regularly, especially API keys
- **Audit Access**: Monitor who accesses the vault
- **Secure Transmission**: Never transmit secrets over insecure channels

### 🚨 Emergency Procedures
- **Key Loss**: If master.key is lost, all secrets must be regenerated
- **Compromise**: Immediately rotate all secrets and generate new master key
- **Backup**: Maintain encrypted backups of the vault directory

## Environment-Specific Vaults

For different environments, create separate vault directories:

```bash
# Development vault
VAULT_DIR=./secrets_vault_dev ./setup-vault.sh

# Production vault
VAULT_DIR=./secrets_vault_prod ./setup-vault.sh
```

Then specify the vault directory in your application:

```python
vault = SecretsVault(vault_dir="./secrets_vault_prod")
```

## Troubleshooting

### "Master key not found"
- Run `./setup-vault.sh` to initialize the vault
- Check that `secrets_vault/master.key` exists
- Ensure proper file permissions (600)

### "Secret not found in vault"
- Check that the secret was set during vault initialization
- Verify the secret name matches exactly
- Run `python3 vault.py` to list available secrets

### "Decryption failed"
- Verify the master key is correct
- Check file permissions on vault files
- Ensure OpenSSL is installed and accessible

## Integration Status

✅ **Application Integration Complete:**
- Server startup loads vault secrets
- Supabase client uses vault credentials
- JWT authentication uses vault secret key
- Stripe payments use vault API keys
- All routes support vault secrets with environment fallback

## Migration from Environment Variables

The vault system is designed for seamless migration:

1. **Parallel Operation**: Vault secrets override environment variables
2. **Graceful Fallback**: If vault unavailable, falls back to .env
3. **Zero Downtime**: Can migrate secrets incrementally
4. **Rollback Ready**: Can disable vault and return to .env-only

## Compliance

This vault system helps meet security requirements for:
- **SOC 2**: Encrypted secret storage
- **PCI DSS**: Secure payment credentials
- **GDPR**: Encrypted personal data
- **ISO 27001**: Information security management

---

**Status**: 🔐 SECRETS SECURELY VAULTED
**Security Level**: HIGH
**Encryption**: AES-256-CBC with PBKDF2