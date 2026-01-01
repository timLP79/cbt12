# CBT Assessment - Deployment Guide

**Last Updated:** 2025-12-31
**Platforms:** AWS Elastic Beanstalk (Primary) | Render.com (Alternative)
**Database:** PostgreSQL (RDS for AWS, Render Postgres for Render)
**Production Server:** Gunicorn
**CI/CD:** GitHub Actions (AWS) | Auto-deploy (Render)

---

## 📋 Table of Contents

1. [Deployment Options](#deployment-options)
2. [AWS Elastic Beanstalk Deployment](#aws-elastic-beanstalk-deployment-primary)
3. [Render.com Deployment](#rendercom-deployment-alternative)
4. [Database Initialization](#database-initialization)
5. [Testing Deployment](#testing-deployment)
6. [Troubleshooting](#troubleshooting)
7. [Post-Deployment](#post-deployment)

---

## Deployment Options

This application supports two deployment platforms:

### Option 1: AWS Elastic Beanstalk (Primary - Recommended)
- **Pros:** Professional CI/CD with GitHub Actions, scalable, industry-standard
- **Cons:** Requires AWS account setup, slightly more complex initial setup
- **Cost:** Free tier available (12 months for new AWS accounts)
- **Auto-deploy:** Yes (via GitHub Actions on push to main)

### Option 2: Render.com (Alternative)
- **Pros:** Simple setup, good for quick demos
- **Cons:** Free tier has cold start delays, less control
- **Cost:** Free tier available
- **Auto-deploy:** Yes (on push to main)

**Current Production Deployment:** AWS Elastic Beanstalk
- **URL:** http://cbt12-env.eba-hfvqnv3s.us-east-1.elasticbeanstalk.com/
- **Region:** us-east-1
- **Database:** RDS PostgreSQL (ebdb)

---

## AWS Elastic Beanstalk Deployment (Primary)

### Prerequisites

**Before deploying to AWS:**

- ✅ AWS account created
- ✅ GitHub repository with code
- ✅ All functionality tested locally
- ✅ AWS CLI installed (optional, for troubleshooting)

---

### Step 1: Configuration Files

The following files are required for AWS deployment (already configured):

#### `Procfile` (project root)
Tells Elastic Beanstalk how to start the application:
```
web: gunicorn run:app --bind :8000 --workers 3 --threads 2
```

#### `.ebextensions/python.config`
Configures Python environment:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: run:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
    FLASK_ENV: "production"
```

#### `.ebignore`
Excludes unnecessary files from deployment:
```
venv/
__pycache__/
*.pyc
instance/
.env
.git/
tests/
init_db.py
create_test_data.py
add_sample_assessment.py
```

#### `.github/workflows/deploy.yml`
GitHub Actions workflow for automatic deployment:
```yaml
name: Deploy to AWS Elastic Beanstalk

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Generate deployment package
        run: zip -r deploy.zip . -x '*.git*' '*venv*' '*__pycache__*' '*.pyc' 'instance/*'

      - name: Deploy to Elastic Beanstalk
        uses: einaregilsson/beanstalk-deploy@v21
        with:
          aws_access_key: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws_secret_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          application_name: CBT12
          environment_name: CBT12-env
          version_label: ${{ github.sha }}
          region: us-east-1
          deployment_package: deploy.zip
```

---

### Step 2: AWS Elastic Beanstalk Environment Setup

1. **Sign in to AWS Console** (https://console.aws.amazon.com)

2. **Navigate to Elastic Beanstalk**

3. **Create Application:**
   - Click "Create Application"
   - Application name: `CBT12`
   - Platform: Python 3.12
   - Application code: Sample application (will be replaced)

4. **Configure Service Access:**
   - **Create new service role** (if first time):
     - Trusted entity: Elastic Beanstalk
     - Use case: Customize → Select Elastic Beanstalk services
   - **Create EC2 instance profile** (if first time):
     - Trusted entity: EC2
     - Use case: Elastic Beanstalk → Select all Elastic Beanstalk roles
   - Select both in the configuration

5. **Configure Networking:**
   - VPC: Default
   - Public IP: Enabled
   - Instance subnets: Select available subnets

6. **Configure Database:**
   - Enable database: ✅
   - Engine: PostgreSQL
   - Engine version: 15.8
   - Instance class: db.t3.micro (free tier)
   - Storage: 20 GB
   - Username: postgres
   - Password: [Choose secure password]
   - Retention: Delete (for development)

7. **Review and Create**
   - Wait 10-15 minutes for environment creation

---

### Step 3: Configure Environment Variables

After environment is created:

1. **Navigate to:** Elastic Beanstalk → CBT12-env → Configuration → Updates, monitoring, and logging → Edit

2. **Add Environment Properties:**
   - `DATABASE_URL`: `postgresql://postgres:[password]@[endpoint]:5432/ebdb`
     - Get endpoint from: Configuration → Database → Endpoint
   - `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
   - `PYTHONPATH`: `/var/app/current:$PYTHONPATH`
   - `FLASK_ENV`: `production`

3. **Save and Apply**

**Note:** DATABASE_URL format:
```
postgresql://postgres:YOUR_PASSWORD@awseb-e-xxx-stack-awsebrdsdatabase-xxx.region.rds.amazonaws.com:5432/ebdb
```

---

### Step 4: Set Up GitHub Actions

1. **Create IAM User for GitHub Actions:**
   - Go to: IAM → Users → Create user
   - Username: `github-actions-deployer`
   - Attach policies:
     - `AWSElasticBeanstalkWebTier`
     - `AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy`
   - Create access key → Application running outside AWS
   - **Save Access Key ID and Secret Access Key**

2. **Add Secrets to GitHub Repository:**
   - Go to: GitHub repo → Settings → Secrets and variables → Actions
   - Add secrets:
     - `AWS_ACCESS_KEY_ID`: [Your access key ID]
     - `AWS_SECRET_ACCESS_KEY`: [Your secret access key]
     - `AWS_REGION`: `us-east-1`

---

### Step 5: Deploy via GitHub Actions

**Every push to `main` branch automatically deploys!**

1. **Make changes locally**
2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

3. **Monitor deployment:**
   - GitHub → Actions tab
   - Watch workflow progress
   - Deployment takes 5-10 minutes

4. **Verify deployment:**
   - Check Elastic Beanstalk console
   - Environment health should be "Ok" (green)
   - Visit: http://cbt12-env.eba-hfvqnv3s.us-east-1.elasticbeanstalk.com/

---

### Step 6: Initialize Database (Pending)

**Database initialization still required - follow instructions in [Database Initialization](#database-initialization) section.**

---

## Render.com Deployment (Alternative)

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

### For AWS Elastic Beanstalk

**Two options for initializing the AWS database:**

#### Option 1: Using EB CLI (if installed)

1. **Install EB CLI** (if not already installed):
   ```bash
   pip install awsebcli
   ```

2. **SSH into the instance:**
   ```bash
   eb ssh CBT12-env
   ```

3. **Navigate to application directory:**
   ```bash
   cd /var/app/current
   source /var/app/venv/*/bin/activate
   ```

4. **Run initialization scripts:**
   ```bash
   python init_db.py
   python create_test_data.py
   python add_sample_assessment.py
   exit
   ```

#### Option 2: Using AWS Systems Manager (Session Manager)

1. Go to **EC2 Console** → **Instances**
2. Find instance with name containing `CBT12-env`
3. Click **Connect** → **Session Manager** → **Connect**
4. Run commands:
   ```bash
   cd /var/app/current
   source /var/app/venv/*/bin/activate
   python init_db.py
   python create_test_data.py
   python add_sample_assessment.py
   ```

**Expected output:**
```
Database tables created!
12 steps added to database!
Created test users:
  - TEST001: David Fisher
  - TEST002: John Doe
Created test admins:
  - ADMIN001: Tim Palacios
  - ADMIN002: Sandra Riggs
```

---

### For Render.com

#### Option A: Using Render Shell (Recommended)

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

### For AWS Elastic Beanstalk

**Your URL:** `http://cbt12-env.eba-hfvqnv3s.us-east-1.elasticbeanstalk.com/`

**Test participant login:**
- Go to: `http://cbt12-env.eba-hfvqnv3s.us-east-1.elasticbeanstalk.com/login`
- Login as: `TEST001` / `Test123!`
- Try starting an assessment

**Test admin login:**
- Go to: `http://cbt12-env.eba-hfvqnv3s.us-east-1.elasticbeanstalk.com/admin/login`
- Login as: `ADMIN001` / `Admin123!`
- View pending assessments

---

### For Render.com

**Your URL:** `https://cbt-assessment-XXXX.onrender.com`

**Test participant login:**
- Go to: `https://your-app.onrender.com/login`
- Login as: `TEST001` / `Test123!`
- Try starting an assessment

**Test admin login:**
- Go to: `https://your-app.onrender.com/admin/login`
- Login as: `ADMIN001` / `Admin123!`
- View pending assessments

---

### Common Testing Steps

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

### AWS Elastic Beanstalk Issues

#### Issue: Procfile Parse Error

**Error:** `failed to generate rsyslog file with error Procfile could not be parsed`

**Solution:** Ensure Procfile command is on a single line:
```
web: gunicorn run:app --bind :8000 --workers 3 --threads 2
```

**NOT** split across multiple lines.

---

#### Issue: GitHub Actions Workflow YAML Error

**Error:** `You have an error in your yaml syntax on line X`

**Solution:** Check YAML indentation:
- Top-level keys (`on:`, `jobs:`) must have NO indentation
- Nested keys must be indented with 2 spaces per level
- Use spaces, NOT tabs

---

#### Issue: CloudFormation Stack in Failed State

**Error:** `The stack is in 'UPDATE_ROLLBACK_FAILED' state`

**Solution:**
1. Go to CloudFormation console
2. Find stack: `awseb-e-XXXXX-stack`
3. Click "Stack actions" → "Continue update rollback"
4. Wait for stack to reach stable state
5. **Never rename database identifiers** - it breaks CloudFormation links

---

#### Issue: Deployment Successful but App Returns 500 Error

**Check logs:**
1. Elastic Beanstalk → CBT12-env → Logs
2. Click "Request Logs" → "Last 100 Lines"
3. Download and check `eb-engine.log` and `/var/log/web.stdout.log`

**Common causes:**
- Missing environment variables (DATABASE_URL, SECRET_KEY)
- Database connection failed
- Python import errors
- Gunicorn binding issues

---

#### Issue: DATABASE_URL Not Available in SSH Session

**Error:** `relation "users" does not exist` after running init scripts

**Cause:** Environment variables set in EB console are available to the application but not to SSH sessions

**Solution:**
1. Get DATABASE_URL: `eb printenv` (from local terminal)
2. SSH into instance: `eb ssh CBT12-env`
3. Export manually: `export DATABASE_URL="postgresql://..."`
4. Run scripts with `-E` flag: `sudo -E /var/app/venv/staging-*/bin/python init_db.py`

The `-E` flag preserves environment variables when using sudo.

---

### Render.com Issues

#### Issue: Build Failed

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

### AWS Elastic Beanstalk

**AWS URLs:**
- Console: https://console.aws.amazon.com
- EB Dashboard: https://console.aws.amazon.com/elasticbeanstalk
- Docs: https://docs.aws.amazon.com/elasticbeanstalk

**Your App:**
- Application: CBT12
- Environment: CBT12-env
- URL: http://cbt12-env.eba-hfvqnv3s.us-east-1.elasticbeanstalk.com/
- Region: us-east-1
- Database: RDS PostgreSQL (ebdb)
- Participant login: `/login`
- Admin login: `/admin/login`

**Test Credentials:**
- Participant: TEST001 / Test123!
- Admin: ADMIN001 / Admin123!

**GitHub Actions:**
- Workflow: `.github/workflows/deploy.yml`
- Triggers: Push to `main` branch
- Monitor: GitHub → Actions tab

**Useful EB CLI Commands:**
```bash
# View application status
eb status CBT12-env

# View logs
eb logs CBT12-env

# SSH into instance
eb ssh CBT12-env

# Deploy manually
eb deploy CBT12-env
```

---

### Render.com

**Render URLs:**
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs

**Your App:**
- URL: `https://cbt-assessment-XXXX.onrender.com`
- Participant login: `/login`
- Admin login: `/admin/login`

**Test Credentials:**
- Participant: TEST001 / Test123!
- Admin: ADMIN001 / Admin123!

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

### AWS Elastic Beanstalk Checklist

**Pre-deployment:**
- [x] PostgreSQL support added to config.py
- [x] requirements.txt includes psycopg2-binary and gunicorn
- [x] Procfile created (single line format)
- [x] .ebextensions/python.config created
- [x] .ebignore created
- [x] Code committed and pushed to GitHub
- [x] .gitignore excludes .env and secrets

**AWS Setup:**
- [x] AWS account created
- [x] Elastic Beanstalk application created (CBT12)
- [x] RDS PostgreSQL database configured
- [x] Environment variables set (DATABASE_URL, SECRET_KEY)
- [x] IAM user created for GitHub Actions
- [x] IAM policies attached (WebTier, ManagedUpdates)
- [x] Access keys generated

**GitHub Actions:**
- [x] GitHub Secrets added (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
- [x] Workflow file created (.github/workflows/deploy.yml)
- [x] Initial deployment successful
- [x] Environment health: Ok (green)

**Post-deployment:**
- [x] Database initialized (init_db.py run remotely) - **COMPLETE**
- [x] Test users created - **COMPLETE**
- [x] Sample assessment added - **COMPLETE**
- [x] Participant flow tested - **COMPLETE**
- [x] Admin flow tested - **COMPLETE**
- [x] Complete workflow verified - **COMPLETE**

---

### Render.com Checklist

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
- [ ] Admin flow tested
- [ ] Complete workflow verified
- [ ] URL shared with colleague

---

**Current Status:** ✅ AWS Elastic Beanstalk deployment COMPLETE! Application fully operational with production database initialized and tested.

**Production URL:** http://cbt12-env.eba-hfvqnv3s.us-east-1.elasticbeanstalk.com/

**Questions?** Refer to AWS or Render.com documentation, or check the troubleshooting section above.
