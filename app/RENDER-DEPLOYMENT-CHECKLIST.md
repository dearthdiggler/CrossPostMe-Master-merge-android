# Render Deployment Checklist - SSL/TLS Fix

## Current Issue

Getting `SSL handshake failed: [SSL: TLSV1_ALERT_INTERNAL_ERROR] tlsv1 alert internal error` when deploying to Render.

## Root Cause

Outdated PyMongo/Motor versions in the deployed environment don't handle SSL/TLS properly with Python 3.11.9 and MongoDB Atlas.

## Solution Summary

We've updated the codebase with:

- ✅ PyMongo 4.9.1 (was 4.5.0) - compatible with Motor 3.6.0
- ✅ Motor 3.6.0 (was 3.3.1)
- ✅ Added certifi for CA certificates
- ✅ Enhanced SSL/TLS configuration in `db.py`
- ✅ Python 3.11.9 runtime specified

## Pre-Deployment Checklist

### 1. Verify Local Files Are Updated

Check that these files have the latest changes. Navigate to your app directory first.

**PowerShell (Windows):**

```powershell
# Navigate to your app directory
cd ./app

# Check requirements.txt has updated versions
Select-String -Path "backend/requirements.txt" -Pattern "pymongo==4.9.1"
Select-String -Path "backend/requirements.txt" -Pattern "motor==3.6.0"
Select-String -Path "backend/requirements.txt" -Pattern "certifi"

# Check runtime files
Get-Content backend/runtime.txt  # Should show: python-3.11.9
Get-Content backend/.python-version  # Should show: 3.11.9

# Check db.py has certifi import
Select-String -Path "backend/db.py" -Pattern "import certifi"
Select-String -Path "backend/db.py" -Pattern 'tlsCAFile.*certifi.where'
```

**Bash/Zsh (macOS/Linux):**

```bash
# Navigate to your app directory
cd ./app

# Check requirements.txt has updated versions
grep "pymongo==4.9.1" backend/requirements.txt
grep "motor==3.6.0" backend/requirements.txt
grep "certifi" backend/requirements.txt

# Check runtime files
cat backend/runtime.txt  # Should show: python-3.11.9
cat backend/.python-version  # Should show: 3.11.9

# Check db.py has certifi import
grep "import certifi" backend/db.py
grep "tlsCAFile.*certifi.where" backend/db.py
```

### 2. Commit and Push Changes to GitHub

**IMPORTANT**: Render deploys from your GitHub repository. You MUST commit and push all changes.

**Git commands (cross-platform):**

```bash
# Navigate to your app directory
cd ./app

# Check git status
git status

# Add all modified files
git add backend/requirements.txt
git add backend/db.py
git add backend/routes/auth.py
git add backend/check_mongodb.py
git add RENDER-SSL-FIX.md
git add RENDER-DEPLOYMENT-CHECKLIST.md

# Commit with descriptive message
git commit -m "fix(deployment): Upgrade PyMongo/Motor and add SSL/TLS configuration for Render

- Upgrade PyMongo to 4.9.1 for better SSL/TLS handling (compatible with Motor 3.6.0)
- Upgrade Motor to 3.6.0 for compatibility
- Add certifi package for up-to-date CA certificates
- Configure explicit tlsCAFile using certifi
- Enhanced environment security (whitelist safe envs)
- Remove PII from all authentication logs
- Fix MongoDB connection issues on Render with Python 3.11.9

Fixes SSL handshake TLSV1_ALERT_INTERNAL_ERROR on Render deployment"

# Ensure you're on main branch before pushing
git checkout main

# Push to GitHub
git push origin main
```

### 3. Verify Render Environment Variables

In Render Dashboard, ensure these environment variables are set:

**Required:**

- ✅ `MONGO_URL`: Your MongoDB Atlas connection string (mongodb+srv://...)
- ✅ `DB_NAME`: Your database name (e.g., `crosspostme_prod`)
- ✅ `ENV`: Set to `production` (NOT development)
- ✅ `SECRET_KEY`: Your application secret key
- ✅ `JWT_SECRET_KEY`: Your JWT signing key

**Optional but Recommended:**

- `MONGO_SERVER_SELECTION_TIMEOUT_MS`: `20000` (20 seconds for cold starts)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
- `REFRESH_TOKEN_EXPIRE_DAYS`: `7`

**DO NOT SET (unless testing):**

- ❌ `MONGO_TLS_ALLOW_INVALID_CERTS`: Should NOT be set in production
- ❌ `ALLOW_INVALID_CERTS_FOR_TESTING`: Should NOT be set in production
- ❌ `MONGO_TLS_OVERRIDE`: Should NOT be set (auto-detected)

If you need to allow invalid certs for local testing with self-signed servers, only set `MONGO_TLS_ALLOW_INVALID_CERTS=true` and `ALLOW_INVALID_CERTS_FOR_TESTING=true` while `ENV` is a safe environment (development/dev/local/test). Remove them afterward.

### 4. Verify MongoDB Atlas Configuration

In MongoDB Atlas Dashboard:

1. **Network Access (IP Whitelist)**:
   - **Option A (Development/Testing Only)**: Allow access from anywhere: `0.0.0.0/0`
     - ⚠️ **Security Warning**: This allows access from any IP address globally
     - Use only for initial testing, then replace with specific IPs
   - **Option B (Recommended for Production)**: Add Render's specific IP addresses
     - Check [Render's documentation](https://render.com/docs/static-outbound-ip-addresses) for current IPs
     - More secure - only allows access from known Render servers

2. **Database Access (Users)**:
   - Verify user exists with correct username/password
   - Ensure user has `readWrite` role on your database
   - Password should match what's in your `MONGO_URL`

3. **Database Deployment**:
   - Cluster should be running (not paused)
   - Connection string should be `mongodb+srv://` format

### 5. Trigger Render Deployment

Option A: **Automatic Deployment** (if enabled):

- Render auto-deploys when you push to `main` branch
- Wait 2-5 minutes for deployment to start

Option B: **Manual Deployment**:

1. Go to Render Dashboard
2. Select your web service
3. Click "Manual Deploy" → "Deploy latest commit"
4. Click "Clear build cache & deploy" (recommended for dependency changes)

### 6. Monitor Deployment Logs

Watch the deployment logs in Render for:

**Expected Success Messages:**

```text
==> Installing dependencies from requirements.txt
==> Successfully installed pymongo-4.9.1 motor-3.6.0 certifi-2024.8.30
==> Running 'uvicorn server:app --host 0.0.0.0 --port $PORT'
INFO:     Started server process [XX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXX
```

**Look out for:**

- ✅ PyMongo 4.9.1 installation confirmed
- ✅ Motor 3.6.0 installation confirmed
- ✅ certifi installation confirmed
- ✅ "Application startup complete" message
- ✅ No SSL handshake errors

**Red Flags:**

- ❌ Still shows pymongo-4.5.0 or motor-3.3.1
- ❌ SSL handshake failed errors
- ❌ ModuleNotFoundError for certifi
- ❌ Application startup failed

### 7. Test Deployment

Once deployed successfully:

```bash
# Test health endpoint
curl https://your-app.onrender.com/api/status

# Expected response:
# {"status": "ok", "timestamp": "..."}

# Test registration (optional)
curl -X POST https://your-app.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'
```

## Troubleshooting

### Issue: Dependencies Not Updated

**Symptoms:**

- Logs still show `pymongo-4.5.0` or `motor-3.3.1`
- Same SSL errors persist

**Solution:**

1. Clear Render build cache: "Manual Deploy" → "Clear build cache & deploy"
2. Verify `requirements.txt` was committed and pushed to GitHub
3. Check Render is pulling from correct branch (`main`)

### Issue: Still Getting SSL Errors After Deployment

**Symptoms:**

- `SSL handshake failed: [SSL: TLSV1_ALERT_INTERNAL_ERROR]`
- Even with updated dependencies

**Possible Causes & Solutions:**

1. **Wrong MongoDB Connection String**:
   - Verify `MONGO_URL` in Render env vars
   - Should be `mongodb+srv://` format for Atlas
   - Test connection string locally first

2. **MongoDB Atlas IP Whitelist**:
   - ⚠️ **SECURITY WARNING - TEMPORARY TESTING ONLY**: Add `0.0.0.0/0` to allow all IPs
   - ⚠️ **NEVER use `0.0.0.0/0` in production** - this allows access from anywhere on the internet
   - After testing is complete, **IMMEDIATELY** remove `0.0.0.0/0` and add only specific IP ranges
   - Alternative (recommended): Add Render's specific IP addresses (check Render docs for current IPs)
   - Document who made the change and when it should be reverted

3. **Invalid Credentials**:
   - Double-check username/password in connection string
   - Ensure user has proper database permissions in Atlas

4. **Cluster Paused or Down**:
   - Verify MongoDB Atlas cluster is running
   - Check Atlas dashboard for cluster health

### Issue: Environment Variable Not Set

**Symptoms:**

- KeyError or missing environment variable errors
- Unexpected behavior

**Solution:**

1. Go to Render Dashboard → Your Service → Environment
2. Add missing variables
3. Save changes (this triggers auto-redeploy)

### Issue: certifi Module Not Found

**Symptoms:**

- `ModuleNotFoundError: No module named 'certifi'`

**Solution:**

1. Verify `certifi>=2024.8.30` is in `requirements.txt`
2. Commit and push changes
3. Clear build cache and redeploy

## Post-Deployment Verification

### Check Application Logs

Look for these success indicators:

```text
✅ MongoDB connection initialized
✅ Database indexes created successfully
✅ Application startup complete
✅ Uvicorn running on http://0.0.0.0:PORT
```

### Test Database Connection

Use your MongoDB checker script locally pointing to production:

**PowerShell (Windows):**

```powershell
# Temporarily set production env vars
$env:MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net/dbname"
$env:DB_NAME="your_db_name"

# Run checker (from app directory)
cd backend
python check_mongodb.py

# Clean up
Remove-Item Env:\MONGO_URL
Remove-Item Env:\DB_NAME
```

**Bash/Zsh (macOS/Linux):**

```bash
# Temporarily set production env vars
export MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net/dbname"
export DB_NAME="your_db_name"

# Run checker (from app directory)
cd backend
python check_mongodb.py

# Clean up
unset MONGO_URL
unset DB_NAME
```

### Monitor Application Health

1. **Health Check**: Visit `https://your-app.onrender.com/api/status`
2. **Logs**: Monitor Render logs for any errors
3. **Performance**: Check response times are acceptable
4. **Database**: Verify data is being written/read correctly

## Rollback Plan

If deployment fails and you need to rollback:

1. **Option A: Revert via Git**:

   ```bash
   git revert HEAD
   git push origin main
   # Render will auto-deploy previous version
   ```

2. **Option B: Manual Rollback in Render**:
   - Render Dashboard → Your Service → "Rollback"
   - Select previous successful deployment
   - Click "Rollback to this version"

## Success Criteria

Deployment is successful when:

- ✅ No SSL handshake errors in logs
- ✅ "Application startup complete" message appears
- ✅ Health endpoint responds: `https://your-app.onrender.com/api/status`
- ✅ Can register/login users successfully
- ✅ Database operations work (create, read, update, delete)
- ✅ No error messages in Render logs

## Next Steps After Successful Deployment

1. **Test all API endpoints**
2. **Verify authentication flow** (register, login, logout, token refresh)
3. **Check database operations** are working
4. **Monitor logs** for first 24 hours
5. **Set up monitoring/alerts** (optional but recommended)
6. **Document production URLs** for your team
7. **Update API documentation** with production URLs

## Support Resources

If issues persist:

- [Render Deployment Troubleshooting](https://render.com/docs/troubleshooting-deploys)
- [MongoDB Atlas Connection Issues](https://www.mongodb.com/docs/atlas/troubleshoot-connection/)
- [PyMongo SSL/TLS Documentation](https://pymongo.readthedocs.io/en/stable/examples/tls.html)
- Check `RENDER-SSL-FIX.md` for detailed technical background

---

**Remember**: Always test changes locally before deploying to production!
