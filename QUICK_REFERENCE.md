# CrossPostMe - Quick Reference Card

**Print this or keep it handy!**

---

## 🎯 Where Am I? (Start Here)

```powershell
./start-session.ps1          # Shows you where you are
```

---

## 📁 Key Files

| File                       | Purpose            | Update Frequency |
| -------------------------- | ------------------ | ---------------- |
| `PROJECT_STATUS.md`        | Big picture status | Weekly           |
| `DAILY_LOG.md`             | Daily work notes   | Every session    |
| `app/backend/TODO.md`      | Technical tasks    | As needed        |
| `HOW_TO_TRACK_PROGRESS.md` | Tracking guide     | Reference        |

---

## 🚀 Essential Commands

### Start Working

```powershell
./start-session.ps1                    # Get oriented
code DAILY_LOG.md                      # Set today's focus
```

### Development

```powershell
# Backend
cd app/backend && .\.venv\Scripts\Activate.ps1
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd app/frontend && yarn start

# Full stack
docker-compose up --build
```

### Testing

```powershell
./run-backend-tests.ps1                # Backend tests
./run-frontend-tests.ps1               # Frontend tests
./run-playwright-tests.ps1             # E2E tests
```

### Git Workflow

```powershell
git status                             # What changed?
git log --oneline -10                  # Recent commits
git add -A && git commit -m "message"  # Commit all
git push                               # Push to remote
```

### End Working

```powershell
./end-session.ps1                      # Wrap up session
code DAILY_LOG.md                      # Document what you did
```

---

## 🔥 Emergency Commands

### Something Broken?

```powershell
# Check backend health
curl https://www.crosspostme.com/api/health

# Check frontend
curl https://www.crosspostme.com

# Check MongoDB connection
node test-mongo.js

# View backend logs
docker-compose logs backend

# Restart everything
docker-compose down && docker-compose up --build
```

### Need to Rollback?

```powershell
# View recent commits
git log --oneline -10

# Revert last commit (keep changes)
git reset HEAD~1

# Revert last commit (discard changes)
git reset --hard HEAD~1

# Deploy previous version
# 1. Find the commit hash
# 2. Push to main (Render auto-deploys)
```

---

## 📊 Project Components

| Component               | URL/Location                         | Health Check   |
| ----------------------- | ------------------------------------ | -------------- |
| **Production Backend**  | https://www.crosspostme.com/api      | /api/health    |
| **Production Frontend** | https://www.crosspostme.com          | Check homepage |
| **API Docs**            | https://www.crosspostme.com/api/docs | Swagger UI     |
| **MongoDB**             | Atlas cluster                        | test-mongo.js  |
| **GitHub Actions**      | Repository → Actions tab             | Check badges   |

---

## 🔐 Environment Files

```
app/backend/.env              # Backend secrets (NEVER commit!)
app/backend/.env.example      # Backend template
app/frontend/.env             # Frontend secrets (NEVER commit!)
app/frontend/.env.example     # Frontend template
```

**Generate encryption key:**

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 📞 Contacts & Resources

- **Email:** crosspostme@gmail.com
- **Phone:** 623-777-9969
- **Render Dashboard:** https://dashboard.render.com
- **GitHub Repo:** Check .git/config for URL
- **MongoDB Atlas:** https://cloud.mongodb.com

---

## 🎯 Daily Workflow (Simple)

1. **Start:** `./start-session.ps1`
2. **Focus:** Add entry to `DAILY_LOG.md`
3. **Work:** Code, commit often
4. **Document:** Update logs as you go
5. **End:** `./end-session.ps1`

---

## 🐛 Common Issues

### Can't connect to MongoDB

1. Check `.env` has correct `MONGO_CONNECTIONSTRING`
2. Verify IP whitelist in MongoDB Atlas
3. Run `node test-mongo.js` to diagnose
4. Check `app/backend/tls_probe.py` for TLS issues

### Backend won't start

1. Activate venv: `.\.venv\Scripts\Activate.ps1`
2. Install deps: `pip install -r requirements.txt`
3. Check `.env` file exists
4. Check port 8000 not already in use

### Frontend won't start

1. Install deps: `yarn install`
2. Check Node version (need 14+)
3. Clear cache: `rm -rf node_modules && yarn install`
4. Check port 3000 not already in use

### Deployment failed

1. Check GitHub Actions logs
2. Verify all secrets set in GitHub/Render
3. Check recent commits for breaking changes
4. Review deployment checklist in PROJECT_STATUS.md

---

## 💡 Pro Tips

- **Commit often:** Small commits are easier to revert
- **Use branches:** Create feature branches for new work
- **Test locally:** Always test before pushing
- **Document as you go:** Don't wait until end of day
- **Read the logs:** DAILY_LOG.md tells you what's next
- **Keep it simple:** Don't overthink the tracking

---

## 🎓 Learn More

- `HOW_TO_TRACK_PROGRESS.md` - Detailed tracking guide
- `PROJECT_STATUS.md` - Full project status
- `app/README.md` - Main project README
- `MONITORING_AND_DOCS.md` - Monitoring setup

---

**Last Updated:** 2025-10-27

**Quick tip:** Bookmark this file or print it out for easy reference!
