# Render Deployment SSL/TLS Fix

## Problem

Getting `SSL handshake failed: [SSL: TLSV1_ALERT_INTERNAL_ERROR] tlsv1 alert internal error` when connecting to MongoDB Atlas from Render, even with Python 3.11.9.

## Root Cause

This error occurs due to:

1. **Outdated PyMongo/Motor versions** that don't handle SSL/TLS properly with Python 3.11.9
2. **Missing or outdated CA certificates** (certifi package)
3. **Implicit TLS configuration** that doesn't explicitly specify certificate paths

## Solution Applied

### 1. Updated Dependencies (`requirements.txt`)

```diff
- pymongo==4.5.0
+ pymongo==4.9.1

- motor==3.3.1
+ motor==3.6.0

+ certifi>=2024.8.30
```

**Why:**

- PyMongo 4.9.1 has better SSL/TLS handling for Python 3.11.9 (compatible with Motor 3.6.0)
- Motor 3.6.0 requires PyMongo >=4.9 and <4.10
- certifi provides up-to-date CA certificates for SSL verification

### 2. Updated `db.py` SSL Configuration

Added explicit certificate bundle configuration:

```python
import ssl
import certifi

# In client_options when use_tls is True:
client_options["tlsCAFile"] = certifi.where()
```

**Why:**

- Explicitly points MongoDB driver to certifi's CA certificate bundle
- Ensures consistent SSL/TLS behavior across platforms (local, Render, etc.)
- Fixes compatibility issues with Python 3.11.9's OpenSSL

### 3. Environment-Aware Certificate Validation (`db.py`)

Added intelligent certificate validation that adapts to the deployment environment:

**Safe Environments** (development, dev, local, test):

- Invalid certificates may be permitted for local testing with self-signed certificates
- Enables developers to test MongoDB connections without production certificates
- Use only in controlled development environments, never in production

**Production Environment**:

- Rejects invalid certificates - only accepts trusted Certificate Authorities
- Enforces strict SSL/TLS validation for security
- Uses certifi's CA bundle (`tlsCAFile = certifi.where()`) when TLS is enabled
- Ensures all MongoDB connections use properly validated certificates

This environment-aware approach balances development flexibility with production security, preventing certificate bypass in production while allowing local testing.

## Deployment Steps

### For Render.com:

1. **Ensure Python version is correct:**
   - Check `backend/runtime.txt` contains: `python-3.11.9`
   - Check `backend/.python-version` contains: `3.11.9`

2. **Update dependencies:**

   ```bash
   cd app/backend
   pip install -r requirements.txt
   ```

3. **Set environment variables in Render dashboard:**
   - `MONGO_URL`: Your MongoDB Atlas connection string (mongodb+srv://...)
   - `DB_NAME`: Your database name
   - `ENV`: `production`
   - (Optional) `MONGO_SERVER_SELECTION_TIMEOUT_MS`: `15000`

4. **Redeploy:**
   - Commit and push changes to GitHub
   - Render will automatically detect the changes and redeploy
   - Or manually trigger redeploy from Render dashboard

## Verification

After deployment, check Render logs for:

- ✅ `INFO: Application startup complete.`
- ✅ No SSL handshake errors
- ✅ MongoDB connection successful

If still failing, check:

1. MongoDB Atlas IP whitelist includes `0.0.0.0/0` (or Render's IPs)
2. MongoDB Atlas user credentials are correct
3. `MONGO_URL` environment variable is set correctly in Render
4. Database name exists and user has access

## Alternative: Test Locally First

Test the fix locally before deploying:

**PowerShell (Windows):**

```powershell
# Set required environment variables
$env:MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/dbname"
$env:DB_NAME="your_database_name"
$env:ENV="development"  # or "local" for development testing

# Navigate to backend and run checker
cd app/backend
python check_mongodb.py

# Clean up (optional)
Remove-Item Env:\MONGO_URL
Remove-Item Env:\DB_NAME
Remove-Item Env:\ENV
```

**Bash/Zsh (macOS/Linux):**

```bash
# Set required environment variables
export MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/dbname"
export DB_NAME="your_database_name"
export ENV="development"  # or "local" for development testing

# Navigate to backend and run checker
cd app/backend
python check_mongodb.py

# Clean up (optional)
unset MONGO_URL
unset DB_NAME
unset ENV
```

**Alternative: Use .env file:**
Create a `.env` file in `app/backend/` with:

```ini
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/dbname
DB_NAME=your_database_name
ENV=development
```

Then run:

```bash
cd app/backend
python check_mongodb.py
```

This will verify:

- Connection string is valid
- SSL/TLS handshake works
- Database is accessible
- Collections are readable

## Expected Behavior

With this fix:

- ✅ SSL/TLS handshake completes successfully
- ✅ MongoDB Atlas connection established
- ✅ Application starts up without errors
- ✅ API endpoints are functional

## Files Changed

1. `app/backend/requirements.txt` - Updated PyMongo, Motor, added certifi
2. `app/backend/db.py` - Added explicit SSL/TLS CA certificate configuration
3. `app/backend/.python-version` - Python 3.11.9 (already set)
4. `app/backend/runtime.txt` - Python 3.11.9 (already set)

## Technical Details

### Why certifi?

The `certifi` package provides Mozilla's carefully curated collection of Root Certificates for validating SSL/TLS connections. By explicitly using `certifi.where()`, we ensure the MongoDB driver uses these trusted certificates rather than relying on system certificates which may be outdated or missing on Render's platform.

### Why these specific versions?

- **PyMongo 4.9.1**: Latest version compatible with Motor 3.6.0 (requires <4.10), with improved SSL/TLS handling
- **Motor 3.6.0**: Latest async wrapper, compatible with PyMongo 4.9.x
- **certifi 2024.8.30+**: Recent certificate bundle with current CA roots

## Rollback Plan

If this fix doesn't work, you can rollback by:

### 1. Revert Code Changes

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# OR manually revert specific changes:
# - Restore requirements.txt to previous PyMongo/Motor versions
# - Remove `import certifi` from db.py
# - Remove `tlsCAFile` configuration from db.py
```

### 2. Verify Rollback Before Redeploying

```bash
# Confirm requirements.txt reverted
grep "pymongo" app/backend/requirements.txt
grep "motor" app/backend/requirements.txt
grep "certifi" app/backend/requirements.txt  # Should not appear

# Confirm db.py changes removed
grep "import certifi" app/backend/db.py  # Should not appear
grep "tlsCAFile" app/backend/db.py  # Should not appear
```

### 3. Redeploy

- Commit and push rollback changes to GitHub
- Render will auto-deploy, or manually trigger "Clear build cache & deploy"

### 4. Post-Rollback Validation

Run these checks to confirm rollback succeeded:

**A. Health Endpoint Check:**

```bash
# Should return 200 OK with status response
curl -i https://your-app.onrender.com/api/status

# Expected response:
# HTTP/2 200
# {"status":"ok","timestamp":"..."}
```

**B. MongoDB Connection Smoke Test:**

```bash
# Test database connection with simple read operation
curl -X POST https://your-app.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

# Or run check script locally against production:
cd app/backend
export MONGO_URL="your_production_connection_string"
export DB_NAME="your_db_name"
python check_mongodb.py
```

**C. Review Logs for Errors:**

- **Deployment logs**: Check Render dashboard → Your Service → Logs tab
  - Look for: `Successfully installed pymongo-X.X.X motor-X.X.X`
  - Confirm: No `ModuleNotFoundError` for certifi
- **Application logs**: Check for TLS/connection errors
  - ✅ Success: `Application startup complete`
  - ✅ Success: `MongoDB connection initialized`
  - ❌ Failure: `SSL handshake failed`
  - ❌ Failure: `ServerSelectionTimeoutError`

**D. Confirm No Active Alerts:**

- Check Render dashboard for any deployment or runtime alerts
- Verify no error notifications in your monitoring system (if configured)

### 5. Rollback Success Criteria

Rollback is successful when:

- ✅ Health endpoint returns 200 OK
- ✅ MongoDB connection succeeds (smoke test passes)
- ✅ No TLS/SSL errors in application logs
- ✅ No deployment errors in Render logs
- ✅ Previous PyMongo/Motor versions confirmed in deployment logs
- ✅ No certifi-related errors or warnings
- ✅ API endpoints functional (can authenticate, query data)

### 6. If Rollback Also Fails

If rolling back doesn't resolve the issue, the problem may be environmental:

1. Check MongoDB Atlas IP whitelist settings
2. Verify connection string credentials
3. Confirm MongoDB cluster is running (not paused)
4. Check [Render status page](https://status.render.com/) for platform issues
5. Review [MongoDB Atlas status](https://status.mongodb.com/) for service issues

**Note:** This is the recommended fix based on:

- PyMongo documentation
- Motor best practices
- Python 3.11+ SSL/TLS requirements
- Render deployment patterns

Rollback should only be used if this fix introduces new issues. The original SSL handshake error will likely persist after rollback.

## Next Steps After Deployment

1. Monitor Render logs for successful startup
2. Test API endpoints (e.g., `/api/status`)
3. Verify authentication works (`/api/auth/register`, `/api/auth/login`)
4. Check database operations are functional

## Support Resources

- [PyMongo TLS/SSL documentation](https://pymongo.readthedocs.io/en/stable/examples/tls.html)
- [Motor documentation](https://motor.readthedocs.io/)
- [Render Python deployment guide](https://render.com/docs/deploy-python)
- [MongoDB Atlas driver connection guide](https://www.mongodb.com/docs/atlas/driver-connection/)
