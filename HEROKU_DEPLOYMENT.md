# Heroku Deployment - Complete Build Process

## 🌐 Your Live App

**URL:** https://swe-b-27-0f4424ee120f.herokuapp.com

---

## 📋 How Heroku Build Actually Works

When you push to Heroku (`git push heroku main`), here's what happens step-by-step:

### **Step 1: Detection**
```bash
-----> Python app detected
```
Heroku sees `requirements.txt` and `runtime.txt` → identifies as Python app

### **Step 2: Python Installation**
```bash
-----> Using Python version: python-3.12.6
-----> Installing python-3.12.6
```
Reads `runtime.txt` and installs specified Python version

### **Step 3: Dependency Installation**
```bash
-----> Installing requirements with pip
       Collecting Django==4.2.25
       Collecting psycopg2==2.9.10
       Collecting django-heroku==0.3.1
       ...
       Successfully installed 32 packages
```

Runs: `pip install -r requirements.txt`

**All packages install successfully because:**
- Heroku build servers have PostgreSQL development libraries pre-installed
- `psycopg2` compiles without issues
- Build environment has compilers, headers, etc.

### **Step 4: Static Files Collection**
```bash
-----> Running collectstatic
       169 static files copied
```

Runs: `python manage.py collectstatic --noinput`
- Gathers all CSS, JS, images from all apps
- Places them in `staticfiles/` directory
- Your app uses S3, so this step is quick

### **Step 5: Slug Compilation**
```bash
-----> Compressing...
       Done: 87.3M
-----> Launching...
```

Creates a "slug" (compressed package) containing:
- Your code
- Python 3.12.6 runtime
- All installed dependencies
- Collected static files

### **Step 6: Release**
```bash
-----> Build succeeded!
-----> Discovering process types
       Procfile declares types -> web
```

Reads `Procfile`:
```
web: gunicorn myproject.wsgi
```

### **Step 7: Dyno Startup**
```bash
Starting process with command `gunicorn myproject.wsgi`
```

Heroku starts your app with:
```bash
gunicorn myproject.wsgi \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --timeout 30
```

---

## 🔄 Environment Configuration (Automatic)

When your app starts, this code runs:

```python
# From myproject/settings.py (lines 241-242)
if django_heroku and 'HEROKU' in os.environ:
    django_heroku.settings(locals())
```

`django_heroku.settings()` automatically:

### 1. **Database Configuration**
```python
# Reads DATABASE_URL environment variable
# Converts: postgres://user:pass@host:5432/dbname
# Into Django DATABASES setting
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dbname',
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': 'host',
        'PORT': '5432',
    }
}
```

### 2. **Static Files**
```python
# Configures WhiteNoise for efficient static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = '/app/staticfiles/'
```

### 3. **Allowed Hosts**
```python
# Adds your Heroku domain automatically
ALLOWED_HOSTS = ['swe-b-27-0f4424ee120f.herokuapp.com']
```

### 4. **Security Settings**
```python
# If DEBUG=False in env:
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## 🗄️ PostgreSQL Database

### **Provisioning**
Heroku automatically creates a PostgreSQL database:

```bash
# Addon: Heroku Postgres
# Plan: Heroku Postgres Mini (free tier replacement)
# Limits: 10,000 rows, 1 GB storage
```

### **Connection**
Database credentials are in the `DATABASE_URL` environment variable:

```
postgres://username:password@ec2-xxx.compute-1.amazonaws.com:5432/database
```

**Note:** Credentials can rotate! Always use `DATABASE_URL`, never hardcode.

### **Migrations**
You must run migrations manually after deployment:

```bash
heroku run python manage.py migrate
```

Or add a release phase to `Procfile`:
```
release: python manage.py migrate
web: gunicorn myproject.wsgi
```

---

## 📁 File Storage

### **Media Files (Uploads)**
- **Profile Pictures:** AWS S3 bucket `swe-b-27-profile-pics`
- **Event Images:** AWS S3 bucket `swe-b-27-profile-pics`

Configuration (from settings.py):
```python
STORAGES = {
    'default': {
        "BACKEND": 'storages.backends.s3boto3.S3Boto3Storage',
    },
    "staticfiles": {
        "BACKEND": 'storages.backends.s3boto3.S3Boto3Storage',
    },
}
```

### **Static Files (CSS/JS)**
- Served from AWS S3 via `django-storages`
- Cached by WhiteNoise for efficiency
- CDN-like delivery

### **Why Not Use Heroku's Filesystem?**
Heroku uses **ephemeral filesystem**:
- Files are deleted on dyno restart
- Not shared between dynos
- Resets on every deploy

**Solution:** S3 for persistent storage

---

## 🔐 Environment Variables

View/set environment variables:

```bash
# View all config vars
heroku config

# Set a variable
heroku config:set DEBUG=False

# Unset a variable
heroku config:unset SOME_VAR
```

### **Current Issues in Your App** ⚠️

These are **hardcoded** in `settings.py` but should be environment variables:

```python
# Lines 28, 75-76 in settings.py
SECRET_KEY = "django-insecure-8bis..."  # ❌ Should be env var
AWS_ACCESS_KEY_ID = 'AKIAT4WRC67XVTE5SVOC'  # ❌ Should be env var
AWS_SECRET_ACCESS_KEY = 'pvnmj/KNWGvh...'  # ❌ Should be env var
DEBUG = True  # ❌ Should be False in production
```

**Fix:**
```bash
# Set on Heroku
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set AWS_ACCESS_KEY_ID="AKIAT4WRC67XVTE5SVOC"
heroku config:set AWS_SECRET_ACCESS_KEY="pvnmj/KNWGvh..."
heroku config:set DEBUG=False

# Update settings.py to read from env
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-for-local')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
```

---

## 🚀 Deployment Commands

### **Initial Setup**
```bash
# Login to Heroku
heroku login

# Add Heroku remote (if not already added)
heroku git:remote -a swe-b-27-0f4424ee120f

# Add PostgreSQL addon (if not already added)
heroku addons:create heroku-postgresql:mini
```

### **Deploying Changes**
```bash
# 1. Commit your changes
git add .
git commit -m "Your commit message"

# 2. Push to Heroku
git push heroku main

# 3. Run migrations (if database changed)
heroku run python manage.py migrate

# 4. Create superuser (first time only)
heroku run python manage.py createsuperuser
```

### **Monitoring**
```bash
# View logs
heroku logs --tail

# Check dyno status
heroku ps

# Open app in browser
heroku open

# Run Django shell
heroku run python manage.py shell

# Access database
heroku pg:psql
```

---

## 📦 What Gets Deployed

### **Included:**
- ✅ Python code (all `.py` files)
- ✅ Templates (HTML files)
- ✅ `requirements.txt` (for pip install)
- ✅ `Procfile` (process configuration)
- ✅ `runtime.txt` (Python version)
- ✅ `manage.py` (Django CLI)

### **Excluded (via `.gitignore`):**
- ❌ `venv/` (virtual environment)
- ❌ `db.sqlite3` (local database)
- ❌ `*.pyc` (compiled Python)
- ❌ `__pycache__/` (Python cache)
- ❌ Local media files (if any)

---

## 🔍 Key Files for Heroku

### **1. Procfile**
```
web: gunicorn myproject.wsgi
```
Tells Heroku how to run your app

### **2. runtime.txt**
```
python-3.12.6
```
Specifies Python version

### **3. requirements.txt**
```
Django==4.2.25
gunicorn==23.0.0
psycopg2-binary==2.9.10
django-heroku==0.3.1
...
```
Lists all dependencies

### **4. settings.py**
```python
# Lines 237-242
ALLOWED_HOSTS = ['swe-b-27-0f4424ee120f.herokuapp.com', ...]
django_heroku.settings(locals())  # Auto-configuration
```

---

## 🎯 Build Process Diagram

```
┌─────────────────────────────────────────┐
│  git push heroku main                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Heroku receives code                   │
│  - Detects Python app                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Install Python 3.12.6                  │
│  (from runtime.txt)                     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  pip install -r requirements.txt        │
│  - Django, psycopg2, gunicorn, etc.     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  python manage.py collectstatic         │
│  (gather static files)                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Create slug (compressed package)       │
│  Size: ~87 MB                           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Start dyno: gunicorn myproject.wsgi    │
│  - Load django_heroku settings          │
│  - Connect to PostgreSQL via DATABASE_URL│
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  App running at:                        │
│  https://swe-b-27-0f4424ee120f.herokuapp.com │
└─────────────────────────────────────────┘
```

---

## ⚠️ Common Issues

### **1. Application Error (500)**
**Cause:** Settings misconfiguration, missing migrations, database error

**Debug:**
```bash
heroku logs --tail
heroku run python manage.py check --deploy
```

### **2. Static Files Not Loading**
**Cause:** Collectstatic not run, S3 credentials wrong

**Fix:**
```bash
heroku run python manage.py collectstatic --noinput
# Check AWS credentials in settings.py
```

### **3. Database Migration Errors**
**Cause:** Migrations not run after deploy

**Fix:**
```bash
heroku run python manage.py migrate
heroku run python manage.py showmigrations  # Check status
```

### **4. Module Not Found**
**Cause:** Package missing from requirements.txt

**Fix:**
```bash
# Add to requirements.txt, then:
git add requirements.txt
git commit -m "Add missing dependency"
git push heroku main
```

---

## 🔄 Local vs Heroku Comparison

| Aspect | Local Development | Heroku Production |
|--------|------------------|-------------------|
| **Python** | 3.9.6 (your system) | 3.12.6 (runtime.txt) |
| **Database** | SQLite (db.sqlite3) | PostgreSQL (via DATABASE_URL) |
| **Server** | Django dev server | Gunicorn (4 workers) |
| **Port** | 8000 (manual) | Dynamic ($PORT env var) |
| **Debug** | True | Should be False |
| **Static Files** | S3 (configured) | S3 + WhiteNoise |
| **Environment** | Local filesystem | Ephemeral (resets on restart) |
| **django-heroku** | Not loaded | Loaded, configures everything |
| **HTTPS** | No (http://) | Yes (https://) |

---

## 💡 Best Practices

1. ✅ **Never hardcode secrets** - Use environment variables
2. ✅ **Set DEBUG=False** in production
3. ✅ **Run migrations** after every deploy
4. ✅ **Monitor logs** regularly: `heroku logs --tail`
5. ✅ **Use PostgreSQL locally** for production parity (optional)
6. ✅ **Test before deploy** - Run `python manage.py check --deploy`
7. ✅ **Version control** - Commit everything except secrets
8. ✅ **Add release phase** to Procfile for automatic migrations

---

## 📚 Useful Heroku Commands

```bash
# Restart app
heroku restart

# Scale dynos
heroku ps:scale web=1

# Access Django shell
heroku run python manage.py shell

# Database backup
heroku pg:backups:capture
heroku pg:backups:download

# View database info
heroku pg:info

# Check buildpack
heroku buildpacks

# View releases
heroku releases

# Rollback
heroku rollback
```

---

## 🎓 Summary

**On Heroku, your app:**
1. Runs Python 3.12.6 (not your local 3.9.6)
2. Uses PostgreSQL (not SQLite)
3. Serves via Gunicorn (not Django dev server)
4. Auto-configures via `django-heroku` package
5. Stores files on S3 (not local filesystem)
6. Resets filesystem on every restart/deploy

**The build process:**
1. Detects Python app
2. Installs Python 3.12.6
3. Installs all requirements (including psycopg2)
4. Collects static files
5. Creates compressed slug
6. Starts Gunicorn server
7. App connects to PostgreSQL via DATABASE_URL

