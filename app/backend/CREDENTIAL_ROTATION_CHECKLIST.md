# Credential Rotation Checklist

## ⚠️ IMMEDIATE ACTION REQUIRED

Your MongoDB credentials and application secrets were previously exposed in git history and must be rotated immediately.

## Steps to Complete (In Order)

### 1. Rotate MongoDB Atlas Password ⏰ URGENT

- [ ] Go to <https://cloud.mongodb.com/>
- [ ] Sign in to your account
- [ ] Navigate to: Security → Database Access
- [ ] Find user: `crosspostme_db_user`
- [ ] Click "Edit" button
- [ ] Click "Edit Password"
- [ ] Choose "Autogenerate Secure Password" or enter a strong password
- [ ] **COPY THE NEW PASSWORD** (you'll need it in step 3)
- [ ] Click "Update User"

### 2. Generate New Application Secrets

Run these commands in PowerShell or Git Bash:

```powershell
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32

# Generate CREDENTIAL_ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Copy each output** - you'll need them in the next step.

### 3. Update Render.com Environment Variables

- [ ] Go to <https://dashboard.render.com/>
- [ ] Sign in and select your backend service
- [ ] Click "Environment" in the left sidebar
- [ ] Update these variables with your NEW values:

  **MONGO_URL**:

  ```text
  mongodb+srv://crosspostme_db_user:NEW_PASSWORD_FROM_STEP_1@cluster0.fkup1pl.mongodb.net/crosspostme_production
  ```

  (Replace `NEW_PASSWORD_FROM_STEP_1` with the password you copied)

  **SECRET_KEY**:

  ```text
  (Paste the first openssl output from step 2)
  ```

  **JWT_SECRET_KEY**:

  ```text
  (Paste the second openssl output from step 2)
  ```

  **CREDENTIAL_ENCRYPTION_KEY**:

  ```text
  (Paste the python/Fernet output from step 2)
  ```

- [ ] Click "Save Changes"
- [ ] Wait for automatic redeployment (2-3 minutes)

### 4. Verify Deployment

- [ ] Check Render deployment logs for successful startup
- [ ] Test backend API endpoint: `https://YOUR_RENDER_URL.onrender.com/api/status`
- [ ] If you see `{"status": "ok"}`, the backend is working!

### 5. Update Local Environment (Optional)

If you run the backend locally, update your local `.env` file (NOT the `.env.render`):

- [ ] Copy `backend/.env.render.template` to `backend/.env`
- [ ] Fill in with your NEW credentials
- [ ] Never commit the `.env` file to git

## What Was Fixed

✅ **Removed exposed credentials** from `backend/.env.render`  
✅ **Added `.env.render` to `.gitignore`** to prevent future exposure  
✅ **Created template file** (`backend/.env.render.template`) as a reference  
✅ **Committed security fixes** to git repository (commits: 917b52e, 1ad23fa)

## Why This Matters

- The old credentials were visible in git history
- Anyone with repository access could have seen them
- Compromised credentials could allow:
  - Unauthorized database access
  - Session hijacking
  - JWT token forgery
  - Credential decryption
- Rotation eliminates this risk

## Timeline

- **Exposed**: October 16, 2025 (commits prior to 917b52e)
- **Fixed**: October 16, 2025 (commit 917b52e)
- **Must Rotate By**: IMMEDIATELY

## Questions?

If you need help:

1. Check `backend/SECURITY_NOTICE.md` for detailed instructions
2. Check `backend/.env.render.template` for variable format
3. MongoDB Atlas docs: <https://docs.atlas.mongodb.com/>
4. Render docs: <https://render.com/docs/environment-variables>

## After Rotation

Once you've rotated all credentials and updated Render:

- [x] Git repository is now secure (no exposed credentials)
- [ ] MongoDB password rotated
- [ ] Application secrets rotated
- [ ] Render environment variables updated
- [ ] Backend deployment successful
- [ ] API endpoints tested and working

---

**Status**: 🔴 ACTION REQUIRED - Credentials must be rotated ASAP
