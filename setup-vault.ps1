#Requires -Version 5.1
<#
.SYNOPSIS
    🔐 SECRETS VAULT SETUP SCRIPT FOR WINDOWS
    Initialize and populate the secrets vault for CrossPostMe
.DESCRIPTION
    This script creates an encrypted secrets vault using OpenSSL,
    prompts for sensitive configuration values, and creates a Python
    access library for secure secret retrieval.
#>

param()

# Colors for output (PowerShell compatible)
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"
$BLUE = "Cyan"
$NC = "White"

# Vault configuration
$VAULT_DIR = "./secrets_vault"
$VAULT_FILE = "$VAULT_DIR/secrets.enc"
$VAULT_KEY_FILE = "$VAULT_DIR/master.key"

# Function to print status
function Write-Status {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message" -ForegroundColor $BLUE
}

function Write-Success {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message" -ForegroundColor $GREEN
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message" -ForegroundColor $YELLOW
}

function Write-Error {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message" -ForegroundColor $RED
}

# Check if OpenSSL is available
function Test-OpenSSL {
    try {
        $null = Get-Command openssl -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Generate encryption key
function New-MasterKey {
    Write-Status "Generating master encryption key..."

    if (-not (Test-Path $VAULT_KEY_FILE)) {
        try {
            $key = -join ((0..31) | ForEach-Object { '{0:X2}' -f (Get-Random -Maximum 256) })
            $key | Out-File -FilePath $VAULT_KEY_FILE -Encoding ASCII -NoNewline
            Write-Success "Master key generated: $VAULT_KEY_FILE"
        }
        catch {
            Write-Error "Failed to generate master key: $_"
            exit 1
        }
    }
    else {
        Write-Warning "Master key already exists"
    }
}

# Create vault directory
function New-VaultDirectory {
    Write-Status "Creating secrets vault directory..."

    if (-not (Test-Path $VAULT_DIR)) {
        try {
            New-Item -ItemType Directory -Path $VAULT_DIR -Force | Out-Null
            Write-Success "Vault directory created: $VAULT_DIR"
        }
        catch {
            Write-Error "Failed to create vault directory: $_"
            exit 1
        }
    }
    else {
        Write-Warning "Vault directory already exists"
    }
}

# Encrypt a secret
function Protect-Secret {
    param([string]$SecretName, [string]$SecretValue)

    if ([string]::IsNullOrEmpty($SecretValue)) {
        Write-Warning "Skipping $SecretName (empty value)"
        return
    }

    try {
        $SecretValue | openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:"$VAULT_KEY_FILE" -out "$VAULT_DIR/$SecretName.enc"
        Write-Success "Encrypted: $SecretName"
    }
    catch {
        Write-Error "Failed to encrypt $SecretName`: $_"
    }
}

# Initialize vault with secrets
function Initialize-Vault {
    Write-Status "Initializing secrets vault..."

    Write-Host ""
    Write-Host "🔐 SECRETS VAULT INITIALIZATION" -ForegroundColor $GREEN
    Write-Host "================================" -ForegroundColor $GREEN
    Write-Host ""
    Write-Warning "You will be prompted to enter each secret. Press Enter to skip any secret."
    Write-Host ""

    # Supabase secrets
    $SUPABASE_URL = Read-Host "Enter SUPABASE_URL"
    $SUPABASE_ANON_KEY = Read-Host "Enter SUPABASE_ANON_KEY"
    $SUPABASE_SERVICE_ROLE_KEY = Read-Host "Enter SUPABASE_SERVICE_ROLE_KEY"

    # JWT secrets
    $SECRET_KEY = Read-Host "Enter SECRET_KEY (for JWT)"

    # Stripe secrets
    $STRIPE_SECRET_KEY = Read-Host "Enter STRIPE_SECRET_KEY"
    $STRIPE_PUBLISHABLE_KEY = Read-Host "Enter STRIPE_PUBLISHABLE_KEY"
    $STRIPE_WEBHOOK_SECRET = Read-Host "Enter STRIPE_WEBHOOK_SECRET"

    # Database secrets
    $MONGODB_URL = Read-Host "Enter MONGODB_URL"

    # Email secrets
    $SMTP_USERNAME = Read-Host "Enter SMTP_USERNAME"
    $SMTP_PASSWORD = Read-Host "Enter SMTP_PASSWORD"

    # AI secrets
    $OPENAI_API_KEY = Read-Host "Enter OPENAI_API_KEY"

    Write-Host ""
    Write-Status "Encrypting secrets..."

    # Encrypt all secrets
    Protect-Secret "supabase_url" $SUPABASE_URL
    Protect-Secret "supabase_anon_key" $SUPABASE_ANON_KEY
    Protect-Secret "supabase_service_role_key" $SUPABASE_SERVICE_ROLE_KEY
    Protect-Secret "secret_key" $SECRET_KEY
    Protect-Secret "stripe_secret_key" $STRIPE_SECRET_KEY
    Protect-Secret "stripe_publishable_key" $STRIPE_PUBLISHABLE_KEY
    Protect-Secret "stripe_webhook_secret" $STRIPE_WEBHOOK_SECRET
    Protect-Secret "mongodb_url" $MONGODB_URL
    Protect-Secret "smtp_username" $SMTP_USERNAME
    Protect-Secret "smtp_password" $SMTP_PASSWORD
    Protect-Secret "openai_api_key" $OPENAI_API_KEY

    Write-Success "All secrets encrypted and stored in vault"
}

# Test vault functionality
function Test-Vault {
    Write-Status "Testing vault functionality..."

    try {
        $testResult = & openssl enc -d -aes-256-cbc -pbkdf2 -pass file:"$VAULT_KEY_FILE" -in "$VAULT_DIR/supabase_url.enc" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Vault decryption working"
        }
        else {
            Write-Error "Vault decryption failed"
            exit 1
        }
    }
    catch {
        Write-Error "Vault decryption test failed: $_"
        exit 1
    }
}

# Create vault access library
function New-VaultLibrary {
    Write-Status "Creating vault access library..."

    $vaultPyContent = @'
#!/usr/bin/env python3
"""
🔐 SECRETS VAULT ACCESS LIBRARY

Securely access encrypted secrets from the vault.
Usage:
    from vault import get_secret
    api_key = get_secret('openai_api_key')
"""

import os
import subprocess
from pathlib import Path

class SecretsVault:
    def __init__(self, vault_dir="./secrets_vault"):
        self.vault_dir = Path(vault_dir)
        self.key_file = self.vault_dir / "master.key"

        if not self.key_file.exists():
            raise FileNotFoundError(f"Master key not found: {self.key_file}")

    def get_secret(self, secret_name):
        """Retrieve a secret from the vault."""
        secret_file = self.vault_dir / f"{secret_name}.enc"

        if not secret_file.exists():
            raise FileNotFoundError(f"Secret '{secret_name}' not found in vault")

        try:
            # Use openssl to decrypt
            result = subprocess.run([
                'openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2',
                '-pass', f'file:{self.key_file}',
                '-in', str(secret_file)
            ], capture_output=True, text=True, check=True)

            return result.stdout.strip()

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to decrypt secret '{secret_name}': {e}")

# Global vault instance
_vault = None

def get_vault():
    """Get the global vault instance."""
    global _vault
    if _vault is None:
        _vault = SecretsVault()
    return _vault

def get_secret(secret_name):
    """Convenience function to get a secret."""
    return get_vault().get_secret(secret_name)

def get_all_secrets():
    """Get all secrets as environment variables dict."""
    vault = get_vault()
    secrets = {}

    # List of all possible secrets
    secret_names = [
        'supabase_url', 'supabase_anon_key', 'supabase_service_role_key',
        'secret_key', 'stripe_secret_key', 'stripe_publishable_key',
        'stripe_webhook_secret', 'mongodb_url', 'smtp_username',
        'smtp_password', 'openai_api_key'
    ]

    for name in secret_names:
        try:
            secrets[name.upper()] = vault.get_secret(name)
        except FileNotFoundError:
            # Secret not set, skip
            continue

    return secrets

if __name__ == "__main__":
    # Test the vault
    try:
        vault = get_vault()
        print("🔐 Secrets vault is accessible")

        # Show available secrets (without revealing values)
        vault_path = Path("./secrets_vault")
        if vault_path.exists():
            secrets = list(vault_path.glob("*.enc"))
            print(f"📁 Found {len(secrets)} encrypted secrets:")
            for secret in secrets:
                print(f"  - {secret.stem}")

    except Exception as e:
        print(f"❌ Vault error: {e}")
        exit(1)
'@

    try {
        $vaultPyContent | Out-File -FilePath "vault.py" -Encoding UTF8
        Write-Success "Vault access library created: vault.py"
    }
    catch {
        Write-Error "Failed to create vault library: $_"
    }
}

# Create .gitignore for vault
function New-GitIgnore {
    Write-Status "Creating .gitignore for secrets vault..."

    if (-not (Test-Path ".gitignore")) {
        New-Item -ItemType File -Path ".gitignore" | Out-Null
    }

    $gitignoreContent = Get-Content ".gitignore" -ErrorAction SilentlyContinue
    if ($gitignoreContent -notcontains "secrets_vault/") {
        Add-Content -Path ".gitignore" -Value "# Secrets Vault - DO NOT COMMIT"
        Add-Content -Path ".gitignore" -Value "secrets_vault/"
        Add-Content -Path ".gitignore" -Value "vault.py"
        Write-Success ".gitignore updated"
    }
    else {
        Write-Warning ".gitignore already contains vault entries"
    }
}

# Main setup function
function Invoke-Main {
    Write-Host "🔐 SETTING UP SECRETS VAULT FOR WINDOWS" -ForegroundColor $GREEN
    Write-Host "=========================================" -ForegroundColor $GREEN

    # Check for OpenSSL
    if (-not (Test-OpenSSL)) {
        Write-Error "OpenSSL is required but not found. Please install OpenSSL for Windows."
        Write-Host "Download from: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor $YELLOW
        exit 1
    }

    New-VaultDirectory
    New-MasterKey
    Initialize-Vault
    Test-Vault
    New-VaultLibrary
    New-GitIgnore

    Write-Host ""
    Write-Success "🎉 SECRETS VAULT SETUP COMPLETE!"
    Write-Host ""
    Write-Status "Next steps:"
    Write-Host "1. Backup your master key: $VAULT_KEY_FILE"
    Write-Host "2. Test vault access: python vault.py"
    Write-Host "3. Update your application to use: from vault import get_secret"
    Write-Host ""
    Write-Warning "⚠️  IMPORTANT SECURITY NOTES:"
    Write-Host "  - Never commit the secrets_vault/ directory"
    Write-Host "  - Backup the master.key file securely"
    Write-Host "  - The master.key file unlocks all secrets"
    Write-Host "  - Use environment-specific vaults for production"
}

# Run main function
Invoke-Main