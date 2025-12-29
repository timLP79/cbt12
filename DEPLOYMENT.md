# CBT Assessment - Deployment Guide

**Last Updated:** 2025-12-28
**Platform:** Render.com (Free Tier)
**Database:** PostgreSQL
**Production Server:** Gunicorn

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Preparation](#pre-deployment-preparation)
3. [Render.com Setup](#rendercom-setup)
4. [Database Initialization](#database-initialization)
5. [Testing Deployment](#testing-deployment)
6. [Troubleshooting](#troubleshooting)
7. [Post-Deployment](#post-deployment)

---

## Prerequisites

**Before deploying, ensure you have:**

- ✅ Phase 3 complete (clinician portal functional)
- ✅ Code committed and pushed to GitHub
- ✅ GitHub repository is public (or Render has access)
- ✅ All functionality tested locally
- ✅ Render.com account (free - sign up at https://render.com)

---

## Pre-Deployment Preparation

### Step 1: Update `requirements.txt`

Add PostgreSQL driver and production web server:

```bash
# Add these lines to requirements.txt:
psycopg2-binary==2.9.9
gunicorn==21.2.0
```

**Complete requirements.txt should include:**
```
Flask==3.1.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.0.1
python-dotenv==1.0.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
```

---

### Step 2: Update `config.py` for Cloud Database

**Modify `config.py` to support environment variables:**

```python
import os

# Get the base directory of the app
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database URI - supports both PostgreSQL (cloud) and SQLite (local)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "instance", "cbt_assessment.db")}'

    # Handle Render's postgres:// vs postgresql:// URL format
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    # Ensure SECRET_KEY is set in production
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("No SECRET_KEY set for production environment")
```

**Key changes:**
- Uses `DATABASE_URL` environment variable for cloud
- Falls back to SQLite for local development
- Handles Render's URL format (postgres:// → postgresql://)
- Enforces SECRET_KEY in production

---

### Step 3: Create Environment Variables File (Local Testing)

**Create `.env` file** (add to `.gitignore`!):

```bash
# .env (for local PostgreSQL testing - OPTIONAL)
DATABASE_URL=postgresql://localhost/cbt_assessment
SECRET_KEY=your-dev-secret-key-here
```

**Update `.gitignore` to exclude `.env`:**
```
.env
*.pyc
__pycache__/
instance/
venv/
```

---

### Step 4: Create `render.yaml` (Optional - Automated Config)

**Create `render.yaml` in project root:**

```yaml
services:
  - type: web
    name: cbt-assessment
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn run:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.14
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: cbt-assessment-db
          property: connectionString

databases:
  - name: cbt-assessment-db
    databaseName: cbt_assessment
    user: cbt_user
    plan: free
```

**Note:** You can configure via web interface instead of using this file.

---

### Step 5: Commit Changes

```bash
git add requirements.txt config.py .gitignore
git commit -m "Prepare for deployment: Add PostgreSQL and Gunicorn support"
git push origin main
```

---

## Render.com Setup

### Step 1: Sign Up / Log In

1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub (recommended - automatic repo access)

---

### Step 2: Create PostgreSQL Database

**Order matters! Create database FIRST, then web service.**

1. **Click "New +" → "PostgreSQL"**
2. **Configure database:**
   - **Name:** `cbt-assessment-db`
   - **Database:** `cbt_assessment`
   - **User:** `cbt_user`
   - **Region:** Oregon (or closest to you)
   - **PostgreSQL Version:** 15 (default)
   - **Plan:** Free

3. **Click "Create Database"**
4. **Wait for creation** (~2 minutes)
5. **Copy "Internal Database URL"**
   - Format: `postgresql://user:password@hostname/database`
   - You'll need this for the web service

---

### Step 3: Create Web Service

1. **Click "New +" → "Web Service"**
2. **Connect GitHub repository:**
   - Authorize Render to access GitHub
   - Select `cbt-assessment` repository
   - Click "Connect"

3. **Configure web service:**
   - **Name:** `cbt-assessment`
   - **Region:** Oregon (same as database)
   - **Branch:** `main`
   - **Root Directory:** (leave blank)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
   - **Plan:** Free

4. **Advanced Settings → Environment Variables:**

   **Add these two variables:**

   **Variable 1:**
   - **Key:** `DATABASE_URL`
   - **Value:** [Paste Internal Database URL from Step 2]

   **Variable 2:**
   - **Key:** `SECRET_KEY`
   - **Value:** [Generate random string - example: `k8f9h23fh92fh923fh9f23h9f2h3f`]

   **To generate SECRET_KEY:**
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Click "Create Web Service"**

---

### Step 4: Wait for Deployment

**Render will now:**
1. Clone your GitHub repository
2. Install dependencies from `requirements.txt`
3. Start Gunicorn web server
4. Assign you a URL: `https://cbt-assessment-XXXX.onrender.com`

**Watch the logs** for any errors. First deployment takes ~5 minutes.

**Success indicators:**
- Build log shows: "Build successful"
- Deploy log shows: "Starting service with 'gunicorn run:app'"
- Service status: "Live" (green)

---

## Database Initialization

**Your database is empty!** You need to initialize it.

### Option A: Using Render Shell (Recommended)

1. **Go to your web service** on Render dashboard
2. **Click "Shell" tab** (top right)
3. **Run initialization commands:**

```bash
# Create database tables
python init_db.py

# Create test users and clinicians
python create_test_data.py

# Add sample assessment (optional)
python add_sample_assessment.py
```

**Expected output:**
```
Database tables created!
12 steps added to database!
Created test users:
  - TEST001: David Fisher
  - TEST002: John Doe
Created test clinicians:
  - CLIN001: Tim Palacios
  - CLIN002: Sandra Riggs
```

---

### Option B: Using SSH (Alternative)

If shell doesn't work:

```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# Get shell access
render shell cbt-assessment

# Then run init commands as above
```

---

## Testing Deployment

### Step 1: Access Your App

**Your URL:** `https://cbt-assessment-XXXX.onrender.com`

**Test participant login:**
- Go to: `https://your-app.onrender.com/login`
- Login as: `TEST001` / `password123`
- Try starting an assessment

**Test clinician login:**
- Go to: `https://your-app.onrender.com/clinician/login`
- Login as: `CLIN001` / `clinician123`
- View pending assessments

---

### Step 2: Verify Database

**Check that data persists:**
1. Complete an assessment as participant
2. Log out and log back in
3. Verify status still shows "Pending Review"
4. Log in as clinician
5. Verify you can see the submitted assessment

**If data disappears after logout:** Database connection issue - check `DATABASE_URL` environment variable.

---

### Step 3: Test Complete Workflow

**End-to-end test:**
1. ✅ Participant logs in
2. ✅ Starts assessment
3. ✅ Answers all questions
4. ✅ Sees "Pending Review" status
5. ✅ Clinician logs in
6. ✅ Sees pending assessment
7. ✅ Reviews responses
8. ✅ Approves assessment
9. ✅ Participant can now start next step

---

## Troubleshooting

### Issue: Build Failed

**Error:** `Could not find requirements.txt`

**Solution:** Ensure `requirements.txt` is in project root and committed to Git.

---

### Issue: Application Error (500)

**Error:** "Application failed to respond"

**Check logs:**
1. Go to Render dashboard → your service
2. Click "Logs" tab
3. Look for Python errors

**Common causes:**
- Missing environment variable (DATABASE_URL, SECRET_KEY)
- Database connection failed
- Import error in code

---

### Issue: Database Connection Failed

**Error:** `FATAL: database "cbt_assessment" does not exist`

**Solution:**
1. Check DATABASE_URL is correct
2. Ensure database was created first
3. Verify connection string format: `postgresql://` (not `postgres://`)

---

### Issue: Static Files Not Loading

**Error:** CSS/images not showing

**Solution:** Flask serves static files automatically. Check:
1. Files are in `app/static/` folder
2. Templates reference: `{{ url_for('static', filename='..') }}`

---

### Issue: Cold Start Delay

**Behavior:** First request after inactivity is very slow (~30 seconds)

**Explanation:** Render's free tier "spins down" after 15 minutes of inactivity.

**Solution:**
- Expected behavior on free tier
- Upgrade to paid plan for always-on service
- Or accept the delay (only affects first request)

---

## Post-Deployment

### Step 1: Share with Colleague

**Send them:**
1. **URL:** `https://your-app.onrender.com`
2. **Test credentials:**
   - Participant: TEST001 / password123
   - Clinician: CLIN001 / clinician123
3. **Brief instructions:**
   - "Log in as participant, complete assessment"
   - "Log in as clinician, approve assessment"
   - "Log back in as participant, verify you can start Step 2"

---

### Step 2: Monitor Usage

**Render dashboard shows:**
- Request count
- Response times
- Error rates
- Build history

**Check logs regularly** for errors or issues.

---

### Step 3: Future Updates

**To deploy updates:**

1. **Make changes locally**
2. **Test locally**
3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```
4. **Render auto-deploys!** (if auto-deploy enabled)
5. **Watch logs** for successful deployment

**Manual deploy:**
- Go to Render dashboard → your service
- Click "Manual Deploy" → "Deploy latest commit"

---

## Optional: Local PostgreSQL Testing

**Before cloud deployment, test with PostgreSQL locally.**

### Using Docker (Easiest)

```bash
# Start PostgreSQL container
docker run --name cbt-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=cbt_assessment \
  -p 5432:5432 \
  -d postgres:15

# Create .env file
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cbt_assessment" > .env

# Install PostgreSQL driver
pip install psycopg2-binary

# Initialize database
python init_db.py
python create_test_data.py

# Run app with PostgreSQL
python run.py

# Stop container when done
docker stop cbt-postgres
docker rm cbt-postgres
```

---

## Security Checklist

**Before production use:**

- [ ] SECRET_KEY is set via environment variable (not hardcoded)
- [ ] DATABASE_URL is set via environment variable
- [ ] `.env` file is in `.gitignore`
- [ ] No passwords or secrets in code
- [ ] HTTPS enabled (Render provides this automatically)
- [ ] CSRF protection enabled (add Flask-WTF for forms)
- [ ] Input validation on all forms
- [ ] SQL injection protection (SQLAlchemy handles this)

---

## Quick Reference

**Render URLs:**
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs

**Your App:**
- URL: `https://cbt-assessment-XXXX.onrender.com`
- Participant login: `/login`
- Clinician login: `/clinician/login`

**Test Credentials:**
- Participant: TEST001 / password123
- Clinician: CLIN001 / clinician123

**Useful Commands:**
```bash
# View logs
render logs cbt-assessment

# Shell access
render shell cbt-assessment

# Restart service
render restart cbt-assessment
```

---

## Deployment Checklist

**Pre-deployment:**
- [ ] Phase 3 complete and tested
- [ ] PostgreSQL support added to config.py
- [ ] requirements.txt includes psycopg2-binary and gunicorn
- [ ] Code committed and pushed to GitHub
- [ ] .gitignore excludes .env and secrets

**Deployment:**
- [ ] Render.com account created
- [ ] PostgreSQL database created
- [ ] DATABASE_URL copied
- [ ] Web service created and linked to GitHub
- [ ] Environment variables set (DATABASE_URL, SECRET_KEY)
- [ ] Deployment successful (service shows "Live")

**Post-deployment:**
- [ ] Database initialized (init_db.py run remotely)
- [ ] Test users created
- [ ] Sample assessment added
- [ ] Participant flow tested
- [ ] Clinician flow tested
- [ ] Complete workflow verified
- [ ] URL shared with colleague

---

**Ready to deploy? Follow this guide step-by-step after Phase 3 is complete!**

**Questions?** Refer to Render.com documentation or check the troubleshooting section above.
