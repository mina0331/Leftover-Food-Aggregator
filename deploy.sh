#!/bin/bash
# Deployment script for community guidelines feature

echo "🚀 Deploying Community Guidelines Feature to Heroku"
echo "=================================================="
echo ""

# Change to project directory
cd /Users/haarikanandula/project-b-27

# Stage required files
echo "📦 Staging files..."
git add profiles/models.py
git add profiles/migrations/0014_profile_has_seen_welcome.py
git add profiles/views.py
git add profiles/signals.py
git add myproject/urls.py
git add profiles/templates/profilepage/welcome.html
git add .gitignore

# Optional documentation
git add LOCAL_SETUP.md HEROKU_DEPLOYMENT.md DEPLOYMENT_CHECKLIST.md 2>/dev/null

echo "✅ Files staged"
echo ""

# Show what will be committed
echo "📋 Files to be committed:"
git diff --cached --name-only
echo ""

# Commit
echo "💾 Committing changes..."
git commit -m "Add community guidelines welcome screen for first-time users

- Add has_seen_welcome field to Profile model
- Create welcome screen with guidelines acknowledgment
- Fix IntegrityError by adding defaults to all get_or_create calls
- Update post-login flow to show welcome screen for new users
- Add /welcome/ route"

if [ $? -ne 0 ]; then
    echo "❌ Commit failed or nothing to commit"
    exit 1
fi

echo "✅ Changes committed"
echo ""

# Push to GitHub (if configured)
echo "🔄 Pushing to GitHub..."
git push origin main 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Pushed to GitHub"
else
    echo "⚠️  GitHub push skipped (not configured or failed)"
fi
echo ""

# Deploy to Heroku
echo "🚢 Deploying to Heroku..."
export PATH="/opt/homebrew/bin:$PATH"
git push heroku main

if [ $? -ne 0 ]; then
    echo "❌ Heroku deployment failed"
    exit 1
fi

echo "✅ Deployed to Heroku"
echo ""

# Run migrations
echo "🔧 Running migrations on Heroku..."
/opt/homebrew/bin/heroku run python manage.py migrate -a swe-b-27

if [ $? -ne 0 ]; then
    echo "❌ Migration failed"
    exit 1
fi

echo "✅ Migrations completed"
echo ""

# Check deployment
echo "📊 Checking deployment status..."
/opt/homebrew/bin/heroku ps -a swe-b-27
echo ""

echo "=================================================="
echo "✨ Deployment complete!"
echo ""
echo "🌐 Visit: https://swe-b-27-0f4424ee120f.herokuapp.com"
echo "📝 View logs: /opt/homebrew/bin/heroku logs --tail -a swe-b-27"
echo "=================================================="

