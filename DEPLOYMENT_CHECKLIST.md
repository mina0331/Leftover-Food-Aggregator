# Deployment Checklist - Community Guidelines Feature

## Files to Commit for Heroku

### Core Feature Files (REQUIRED):
```bash
# 1. Model changes
git add profiles/models.py

# 2. Migration file (CRITICAL - database will break without this)
git add profiles/migrations/0014_profile_has_seen_welcome.py

# 3. Views logic
git add profiles/views.py

# 4. Signal fixes
git add profiles/signals.py

# 5. URL routing
git add myproject/urls.py

# 6. Welcome template
git add profiles/templates/profilepage/welcome.html

# 7. Settings fix (django_heroku optional import)
git add myproject/settings.py

# 8. Gitignore (optional but recommended)
git add .gitignore
```

### Documentation Files (OPTIONAL - won't affect deployment):
```bash
git add LOCAL_SETUP.md
git add HEROKU_DEPLOYMENT.md
```

### Do NOT Commit:
```bash
# .DS_Store - Mac system file
# db.sqlite3 - local database (not used in production)
```

---

## Deployment Commands

### Step 1: Stage the files
```bash
cd /Users/haarikanandula/project-b-27

# Add all required files
git add profiles/models.py
git add profiles/migrations/0014_profile_has_seen_welcome.py
git add profiles/views.py
git add profiles/signals.py
git add myproject/urls.py
git add myproject/settings.py
git add profiles/templates/profilepage/welcome.html
git add .gitignore

# Optional: Add documentation
git add LOCAL_SETUP.md HEROKU_DEPLOYMENT.md
```

### Step 2: Commit the changes
```bash
git commit -m "Add community guidelines welcome screen for first-time users

- Add has_seen_welcome field to Profile model
- Create welcome screen with guidelines acknowledgment
- Fix IntegrityError by adding defaults to all get_or_create calls
- Update post-login flow to show welcome screen for new users
- Add /welcome/ route"
```

### Step 3: Push to GitHub (if using)
```bash
git push origin main
```

### Step 4: Deploy to Heroku
```bash
# Set Heroku CLI path
export PATH="/opt/homebrew/bin:$PATH"

# Push to Heroku
git push heroku main
```

### Step 5: Run migrations on Heroku (CRITICAL!)
```bash
/opt/homebrew/bin/heroku run python manage.py migrate -a swe-b-27
```

### Step 6: Verify deployment
```bash
# Check logs
/opt/homebrew/bin/heroku logs --tail -a swe-b-27

# Open app
/opt/homebrew/bin/heroku open -a swe-b-27
```

---

## Why Migration is Critical

The migration file `0014_profile_has_seen_welcome.py` adds the `has_seen_welcome` column to the database.

**Without running the migration on Heroku:**
- New users will get IntegrityError
- Existing code expects the field to exist
- App will crash on login

**After running migration:**
- PostgreSQL database will have the new column
- All existing profiles will have `has_seen_welcome=False`
- New users can log in successfully

---

## Testing After Deployment

1. Visit: https://swe-b-27-0f4424ee120f.herokuapp.com
2. Log in with a new Google account
3. Should see community guidelines welcome screen
4. Check the "acknowledge" box and click Continue
5. Should proceed to role selection (if new) or profile

---

## Rollback (if something goes wrong)

```bash
# View releases
/opt/homebrew/bin/heroku releases -a swe-b-27

# Rollback to previous version
/opt/homebrew/bin/heroku rollback -a swe-b-27
```

---

## Database Differences

**Local (SQLite):**
- Migration already applied
- Field exists in db.sqlite3

**Heroku (PostgreSQL):**
- Needs migration after deploy
- Must run: `heroku run python manage.py migrate -a swe-b-27`

---

## Summary

**Minimum files to commit:**
1. profiles/models.py
2. profiles/migrations/0014_profile_has_seen_welcome.py ← CRITICAL
3. profiles/views.py
4. profiles/signals.py
5. myproject/urls.py
6. myproject/settings.py
7. profiles/templates/profilepage/welcome.html

**After deploying, MUST run:**
```bash
/opt/homebrew/bin/heroku run python manage.py migrate -a swe-b-27
```

