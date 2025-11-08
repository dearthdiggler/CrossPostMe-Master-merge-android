read![CI](https://github.com/dearthdiggler/app/actions/workflows/ci.yml/badge.svg)

CrossPostMe.com — Local listings automation (developer README)

This repository contains a small demo stack powering the CrossPostMe web app: a FastAPI backend and a React frontend used for the UI. The copy and examples in this repo are neutralized product copy for development and do not include marketing assets.

## Quick start

Backend (FastAPI):

```powershell
# create venv, install, run dev server
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r .\app\backend\requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000 --app-dir .\app\backend
```

Frontend (React / CRA + craco):

```powershell
cd .\app\frontend
yarn install
yarn start
```

## Security & Environment Setup

**⚠️ IMPORTANT SECURITY NOTICE ⚠️**

This application handles sensitive credentials and API keys. Follow these security practices:

### Environment Configuration

1. **Copy the example environment file:**

```bash
cp app/backend/.env.example app/backend/.env
```

2. **Generate your own encryption key:**

```python
# Run this command to generate a secure encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

3. **Update your .env file with the generated key:**

```bash
CREDENTIAL_ENCRYPTION_KEY=your_generated_key_here
```

### Platform API Keys

Get API credentials from each platform:

- **eBay**: [eBay Developer Program](https://developer.ebay.com/)
- **Facebook**: [Facebook for Developers](https://developers.facebook.com/)

### Production Security

**NEVER commit real credentials to version control!**

For production deployments, use a secrets manager:

- **AWS Secrets Manager** (recommended for AWS deployments)
- **HashiCorp Vault** (for on-premise or multi-cloud)
- **GitHub Secrets** (for GitHub Actions CI/CD)
- **Azure Key Vault** (for Azure deployments)

### Git Security

If you accidentally commit secrets:

1. **Immediately rotate all exposed keys**
2. **Remove from git history using:**

   ```bash
   # Option 1: BFG Repo-Cleaner (recommended)
   git clone --mirror your-repo.git
   java -jar bfg.jar --delete-files .env your-repo.git

   # Option 2: git filter-repo
   git filter-repo --path backend/.env --invert-paths
   ```

3. **Force push the cleaned repository**
4. **Notify all team members to re-clone**

Contact for developer questions: crosspostme@gmail.com — Phone: 623-777-9969

```

```
