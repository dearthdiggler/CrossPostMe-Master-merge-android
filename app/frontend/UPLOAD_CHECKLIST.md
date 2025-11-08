# 🚀 CrossPostMe Upload Checklist - October 2025

## 🆕 Latest Updates

- ✅ **LeadService**: Intelligent 3-tier lead matching (email, phone, fuzzy)
- ✅ **Improved Spam Detection**: Regex patterns, 10-char threshold
- ✅ **Database Indexes**: Compound indexes for performance
- ✅ **Updated Branding**: Color-coded logo (Cross-Blue, Post-Purple, Me-Pink)
- ✅ **Better Error Handling**: Custom exceptions, comprehensive logging

## 📦 Complete Upload Package

### ✅ Core Application Files (UPDATED)

- [x] `app/` - Complete application directory
- [x] `app/backend/` - FastAPI backend (Python) **[UPDATED]**
  - [x] `services/` - **[NEW]** Business logic layer (LeadService)
  - [x] `routes/messages.py` - **[UPDATED]** Spam detection + LeadService
  - [x] `automation/base.py` - **[UPDATED]** Custom exceptions
  - [x] `automation/email_monitor.py` - **[UPDATED]** Better logging
  - [x] `scripts/setup_db.py` - **[UPDATED]** Creates compound indexes
- [x] `app/frontend/` - React frontend (Node.js) **[UPDATED]**
  - [x] `src/components/Login.jsx` - **[UPDATED]** Loading state
  - [x] `src/lib/api.js` - **[UPDATED]** Simplified docs
  - [x] `build/` - Production build output **[CRITICAL TO UPLOAD]**

  ## Deploying the build to Hostinger

  Two options are provided:
  1. GitHub Actions (recommended): a workflow has been added at `.github/workflows/deploy-hostinger-ftp.yml`. To use it, add the following repository secrets in GitHub: `HOSTINGER_FTP_HOST`, `HOSTINGER_FTP_USER`, `HOSTINGER_FTP_PASS`. Then trigger the workflow from the Actions tab (or push a commit and dispatch).

  2. Local upload script: use `scripts/upload-to-hostinger.ps1` to upload from your machine. It prefers WinSCP (if installed) and falls back to a simple FTP uploader.

  If you want me to upload immediately from this environment, provide Hostinger FTP credentials now. Otherwise, add the secrets and trigger the workflow in GitHub.

### ✅ Configuration Files

- [x] `app/backend/.env.example` - Environment variables template
- [x] `app/backend/requirements.txt` - Python dependencies
- [x] `app/frontend/package.json` - Node.js dependencies
- [x] `DEPLOYMENT_PACKAGE.md` - Complete deployment guide **[UPDATED]**

### ✅ Documentation (NEW)

- [x] `LEAD-SERVICE-DOCUMENTATION.md` - **[NEW]** LeadService architecture
- [x] `SPAM-DETECTION-IMPROVEMENTS.md` - **[NEW]** Spam detection guide
- [x] `DEPLOYMENT-GUIDE.md` - Detailed deployment instructions
- [x] `HOSTINGER-DEPLOYMENT.md` - Hostinger-specific guide

### ✅ Deployment Scripts

- [x] `quick-deploy.ps1` - Windows PowerShell setup script
- [x] `quick-deploy.sh` - Linux/Mac bash setup script
- [x] `START-ALL.ps1` - Start both backend and frontend (Windows)
- [x] `START-ALL.bat` - Start both backend and frontend (Windows)

### ✅ Docker Support (Optional)

- [x] `Dockerfile.backend` - Backend containerization
- [x] `Dockerfile.frontend` - Frontend containerization
- [x] `docker-compose.yml` - Full stack orchestration
- [x] `Procfile` - Heroku deployment

---

## 🚀 Quick Start Instructions

### For Windows Users:

```powershell
# 1. Upload all files to your server
# 2. Run the setup script
.\quick-deploy.ps1

# 3. Start the application
.\START-ALL.ps1
```

### For Linux/Mac Users:

```bash
# 1. Upload all files to your server
# 2. Make scripts executable
chmod +x quick-deploy.sh

# 3. Run setup
./quick-deploy.sh

# 4. Start backend manually:
cd app/backend && source .venv/bin/activate && uvicorn server:app --host 0.0.0.0 --port 8000

# 5. Start frontend:
cd app/frontend && yarn start
```

---

## 🔧 Manual Setup (If Scripts Don't Work)

### Backend Setup:

```bash
cd app/backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Frontend Setup:

```bash
cd app/frontend
yarn install
yarn build  # for production
# Or yarn start for development
```

---

## 🌐 Production Deployment Options

### Option 1: Simple VPS/Server

1. Upload all files via FTP/SFTP
2. Run `quick-deploy.ps1` or `quick-deploy.sh`
3. Configure reverse proxy (nginx/Apache)
4. Set up SSL certificates

### Option 2: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Option 3: Cloud Platforms

- **Heroku**: Use included `Procfile`
- **Vercel**: Deploy frontend directly from `app/frontend/`
- **Railway**: One-click deploy with environment variables
- **AWS/DigitalOcean**: Standard Docker deployment

---

## ⚠️ CRITICAL: Before Upload

### 1. Environment Security

- Generate unique `SECRET_KEY` and `CREDENTIAL_ENCRYPTION_KEY`
- Set up MongoDB with proper authentication
- Configure `CORS_ORIGINS` for your domain

### 2. Platform API Keys (Optional)

- eBay Developer Account: https://developer.ebay.com/
- Facebook Developer Account: https://developers.facebook.com/

### 3. Database Setup

- MongoDB 4.4+ required
- Update `MONGO_URL` in `.env`
- Ensure network connectivity

---

## 📁 What Gets Uploaded

### Required Files (CRITICAL):

```
app/
├── backend/
│   ├── server.py                    ⚠️ CRITICAL
│   ├── auth.py                      ⚠️ CRITICAL
│   ├── db.py                        ⚠️ CRITICAL
│   ├── models.py                    ⚠️ CRITICAL
│   ├── requirements.txt             ⚠️ CRITICAL
│   ├── .env.example                 ⚠️ CRITICAL (rename to .env)
│   ├── routes/                      ⚠️ ENTIRE FOLDER
│   │   ├── __init__.py
│   │   ├── ads.py
│   │   ├── ai.py
│   │   ├── auth.py
│   │   ├── messages.py              🆕 UPDATED
│   │   └── platforms.py
│   ├── services/                    🆕 NEW FOLDER
│   │   ├── __init__.py
│   │   └── lead_service.py          🆕 NEW FILE
│   ├── automation/                  ⚠️ ENTIRE FOLDER
│   │   ├── __init__.py
│   │   ├── base.py                  🆕 UPDATED
│   │   ├── credentials.py
│   │   ├── craigslist.py
│   │   ├── ebay.py
│   │   ├── facebook.py
│   │   ├── offerup.py
│   │   ├── email_monitor.py         🆕 UPDATED
│   │   └── message_scrapers.py      🆕 UPDATED
│   └── scripts/
│       └── setup_db.py              🆕 UPDATED (run after upload!)
└── frontend/
    └── build/                       ⚠️ BUILD OUTPUT ONLY
        ├── index.html               ⚠️ CRITICAL
        ├── static/                  ⚠️ ENTIRE FOLDER
        │   ├── css/
        │   └── js/
        └── asset-manifest.json
```

### ❌ DO NOT Upload:

```
❌ .git/                      (version control)
❌ .venv/ or venv/            (virtual environment)
❌ node_modules/              (frontend dependencies)
❌ __pycache__/               (Python cache)
❌ *.pyc                      (compiled Python)
❌ test_*.py                  (test files)
❌ cleanup_test_data.py       (test utilities)
❌ app/frontend/src/          (source - only upload build/)
❌ app/frontend/public/       (source - only upload build/)
```

### Helpful Files (Recommended):

```
DEPLOYMENT_PACKAGE.md                 📚 Complete guide
LEAD-SERVICE-DOCUMENTATION.md         📚 NEW - LeadService info
SPAM-DETECTION-IMPROVEMENTS.md        📚 NEW - Spam detection
DEPLOYMENT-GUIDE.md                   📚 Detailed instructions
HOSTINGER-DEPLOYMENT.md               📚 Hostinger-specific
quick-deploy.ps1                      🔧 Windows setup
quick-deploy.sh                       🔧 Linux/Mac setup
START-ALL.ps1                         🚀 Start services
docker-compose.yml                    🐳 Docker deployment
```

---

## 🎯 Post-Upload Critical Steps

### 1. Build Frontend BEFORE Upload

```powershell
cd app\frontend
yarn install
yarn build
# ⚠️ Verify app\frontend\build\ folder exists before uploading
```

### 2. After Upload - Setup Database (CRITICAL!)

```bash
cd /path/to/backend
python scripts/setup_db.py

# Expected output:
# ✅ Created compound index on (user_id, platform, contact_email)
# ✅ Created compound index on (user_id, platform, contact_phone)
# ✅ Created compound index on (user_id, platform, contact_name)
# ✅ Created index on content_hash
# ✅ Database setup complete!
```

### 3. Configure .env File

```bash
cd /path/to/backend
cp .env.example .env
nano .env

# Set these CRITICAL values:
SECRET_KEY=your-super-secret-jwt-key-here
MONGO_URL=mongodb://localhost:27017
DB_NAME=crosspostme_production
CORS_ORIGINS=https://yourdomain.com
```

Generate secrets:

```bash
# JWT Secret
openssl rand -hex 32

# Encryption Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 🎯 Success Criteria

After upload, you should be able to:

- [x] Access backend health check: `http://yourserver:8000/api/status`
- [x] View API docs: `http://yourserver:8000/docs`
- [x] View frontend application: `http://yourserver` (or port 3000 for dev)
- [x] See color-coded logo: Cross (Blue), Post (Purple), Me (Pink)
- [x] Register and login users
- [x] Create and manage ads
- [x] Connect platform accounts
- [x] Database indexes verified (run `db.leads.getIndexes()` in MongoDB)
- [x] LeadService working (messages automatically deduplicate into leads)

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section in `DEPLOYMENT_PACKAGE.md`
2. Verify all environment variables are set
3. Ensure MongoDB is running and accessible
4. Check server logs for detailed error messages

**You're ready to upload! 🎉**
